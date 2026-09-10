"""End-to-end API tests using FastAPI TestClient. Runs the whole backend
in-process — no server needed. Covers auth, catalog, progress, revision,
assistant, health, and security."""
import os, sys, tempfile, importlib

# isolate the store to a temp dir + deterministic secret
os.environ["ALGO_DATA_DIR"] = tempfile.mkdtemp(prefix="algolotl_test_")
os.environ["ALGO_SECRET_KEY"] = "test-secret-please-change"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from fastapi.testclient import TestClient
from app.main import app  # noqa: E402

client = TestClient(app)
P = 0
F = 0


def ok(name, cond):
    global P, F
    if cond:
        P += 1
    else:
        F += 1
        print("  ✗", name)


# ---- health ----
r = client.get("/api/health/live"); ok("health live", r.status_code == 200 and r.json()["status"] == "ok")
r = client.get("/api/health/ready"); ok("health ready has 150 problems", r.json().get("problems") == 150)

# ---- catalog + notion views ----
r = client.get("/api/catalog")
data = r.json()
ok("catalog 150 problems", data["meta"]["total"] == 150)
ok("catalog has patterns", len(data["patterns"]) == 18)
ok("catalog has ds groups", len(data["ds"]) == 18)
r = client.get("/api/notion/patterns"); ok("notion/patterns ok", "arrays-hashing" in r.json())
r = client.get("/api/notion/ds"); ok("notion/ds ok", len(r.json()) == 18)

# ---- problem detail w/ flagship viz ----
r = client.get("/api/problems/two-sum")
ts = r.json()
ok("two-sum has approaches", ts["approaches"] and len(ts["approaches"]) == 2)
ok("two-sum brute frames", len(ts["approaches"][0]["frames"]) > 1)
ok("two-sum hash frames", len(ts["approaches"][1]["frames"]) > 1)
ok("two-sum quickshot present", bool(ts["quickshot"]))
# verify the simulated answer actually reaches the pair [0,1] for [3,2,4,7,11] target 9? (2+7)
last = ts["approaches"][1]["frames"][-1]
ok("hash sim finds pair", last["hi"].get("pair") is not None)

# ---- filters ----
r = client.get("/api/problems?pattern=two-pointers"); ok("filter by pattern", r.json()["count"] == 5)
r = client.get("/api/problems?difficulty=Hard"); ok("filter by difficulty Hard", r.json()["count"] > 0)
r = client.get("/api/problems?day=1"); ok("filter by day 1", r.json()["count"] == 7)

# ---- auth: register -> me -> login ----
r = client.post("/api/auth/register", json={"email": "t@a.dev", "name": "Tharun", "password": "supersecret1"})
ok("register 201", r.status_code == 201)
tok = r.json()["access_token"]
ok("register returns token", bool(tok))
ok("register returns user", r.json()["user"]["email"] == "t@a.dev")

h = {"Authorization": f"Bearer {tok}"}
r = client.get("/api/auth/me", headers=h); ok("me works with token", r.json()["email"] == "t@a.dev")
r = client.get("/api/auth/me"); ok("me rejects no token", r.status_code == 401)
r = client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}); ok("me rejects bad token", r.status_code == 401)

# duplicate email
r = client.post("/api/auth/register", json={"email": "t@a.dev", "name": "X", "password": "supersecret1"})
ok("duplicate email 409", r.status_code == 409)
# weak password rejected by pydantic
r = client.post("/api/auth/register", json={"email": "z@a.dev", "name": "Z", "password": "short"})
ok("weak password 422", r.status_code == 422)

# login wrong password
r = client.post("/api/auth/login", json={"email": "t@a.dev", "password": "wrongpass1"})
ok("wrong password 401", r.status_code == 401)
# login right
r = client.post("/api/auth/login", json={"email": "t@a.dev", "password": "supersecret1"})
ok("login 200", r.status_code == 200 and bool(r.json()["access_token"]))

# demo account
r = client.post("/api/auth/demo"); ok("demo login works", r.status_code == 200)
demo_tok = r.json()["access_token"]

# ---- progress + revision ----
r = client.post("/api/progress/status", json={"problem_id": "two-sum", "status": "Solved Solo"}, headers=h)
ok("set status solo", r.json()["ok"])
r = client.post("/api/progress/status", json={"problem_id": "3sum", "status": "Needs Revision"}, headers=h)
ok("set status needs-revision", r.json()["ok"])
r = client.get("/api/progress", headers=h)
pj = r.json()
ok("progress solved counts", pj["stats"]["solved"] == 1)
ok("needs-revision auto-added to queue", "3sum" in pj["revision"])
r = client.get("/api/progress/revision/today", headers=h)
ok("revision today lists 3sum", any(p["id"] == "3sum" for p in r.json()["problems"]))
# toggle revision off
r = client.post("/api/progress/revision", json={"problem_id": "3sum", "on": False}, headers=h)
r = client.get("/api/progress", headers=h); ok("revision removed", "3sum" not in r.json()["revision"])
# progress requires auth
r = client.get("/api/progress"); ok("progress needs auth", r.status_code == 401)

# ---- assistant (offline tutor, no key) ----
r = client.post("/api/assistant", json={"question": "how do I start?", "problem_id": "two-sum"}, headers=h)
aj = r.json()
ok("assistant offline source", aj["source"] == "offline-tutor")
ok("assistant answers with content", "Two Sum" in aj["answer"])
r = client.post("/api/assistant", json={"question": "explain sliding window"}, headers=h)
ok("assistant generic pattern tip", "window" in r.json()["answer"].lower())
r = client.post("/api/assistant", json={"question": "hi"}); ok("assistant needs auth", r.status_code == 401)

# ---- security headers ----
r = client.get("/api/health/live")
ok("X-Content-Type-Options header", r.headers.get("x-content-type-options") == "nosniff")
ok("X-Frame-Options header", r.headers.get("x-frame-options") == "DENY")

# ---- password hashing sanity ----
from app.core.security import hash_password, verify_password, create_token, verify_token
hpw = hash_password("hunter2pass")
ok("password verifies", verify_password("hunter2pass", hpw))
ok("wrong password fails", not verify_password("nope", hpw))
t = create_token("uid123", "sec", 60)
ok("jwt roundtrip", verify_token(t, "sec")["sub"] == "uid123")
ok("jwt wrong secret fails", verify_token(t, "other") is None)

print(f"\n{'✅ ALL API TESTS PASSED' if F==0 else '❌ FAILURES'}: {P} passed, {F} failed")
sys.exit(0 if F == 0 else 1)
