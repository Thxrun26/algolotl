"""Serve the real app via FastAPI TestClient and verify every static asset,
SPA route, and API journey the UI depends on actually loads."""
import os, sys, tempfile
os.environ["ALGO_DATA_DIR"] = tempfile.mkdtemp(prefix="algolotl_fe_")
os.environ["ALGO_SECRET_KEY"] = "fe-test-secret"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
P = F = 0
def ok(n, cond):
    global P, F
    if cond: P += 1
    else: F += 1; print("  ✗", n)

# ---- static shell + assets load (these are what the browser fetches) ----
r = c.get("/"); ok("index.html served", r.status_code == 200 and "Algolotl" in r.text)
ok("index references data/api/viz/app", all(s in r.text for s in ["data/problems.js","js/api.js","js/visualizer.js","js/app.js"]))
for asset in ["/static/assets/styles.css","/static/data/problems.js","/static/js/api.js","/static/js/visualizer.js","/static/js/app.js"]:
    r = c.get(asset); ok(f"asset {asset} 200", r.status_code == 200)

# data embed sanity
r = c.get("/static/data/problems.js")
ok("problems.js sets window.ALGO", r.text.startswith("window.ALGO ="))
ok("problems.js has 150", '"total": 150' in r.text or '"total":150' in r.text)

# ---- SPA fallback: any unknown path returns the shell (hash routing) ----
for route in ["/tracker","/problems","/about","/login","/p/two-sum","/ds","/patterns","/revision"]:
    r = c.get(route); ok(f"SPA route {route} -> shell", r.status_code == 200 and "id=\"app\"" in r.text)

# ---- the API journeys the UI calls on each page ----
ok("GET /api/catalog (home/tracker/problems/notion)", c.get("/api/catalog").json()["meta"]["total"] == 150)
ok("GET /api/notion/ds (Notion·DS page)", len(c.get("/api/notion/ds").json()) == 18)
ok("GET /api/notion/patterns (Notion·Patterns page)", len(c.get("/api/notion/patterns").json()) == 18)
ok("GET /api/problems/two-sum (detail+viz)", c.get("/api/problems/two-sum").json()["hasViz"] is True)

# demo login journey (the 'Try demo' button)
r = c.post("/api/auth/demo"); tok = r.json()["access_token"]; h = {"Authorization": f"Bearer {tok}"}
ok("demo login (UI button)", r.status_code == 200)
# tracker checkbox -> setStatus
ok("status save (tracker checkbox)", c.post("/api/progress/status", json={"problem_id":"two-sum","status":"Solved Solo"}, headers=h).json()["ok"])
# needs revision -> revision page
c.post("/api/progress/status", json={"problem_id":"3sum","status":"Needs Revision"}, headers=h)
ok("revision page journey", any(p["id"]=="3sum" for p in c.get("/api/progress/revision/today", headers=h).json()["problems"]))
# assistant (chat widget)
ok("assistant widget journey", c.post("/api/assistant", json={"question":"how do I start?","problem_id":"two-sum"}, headers=h).status_code == 200)

# ---- OpenAPI docs (the 'list all endpoints' requirement) ----
spec = c.get("/openapi.json").json()
paths = list(spec["paths"].keys())
need = ["/api/auth/register","/api/auth/login","/api/auth/me","/api/auth/demo",
        "/api/catalog","/api/problems","/api/problems/{pid}","/api/notion/patterns","/api/notion/ds",
        "/api/progress","/api/progress/status","/api/progress/revision","/api/progress/revision/today",
        "/api/assistant","/api/health/live","/api/health/ready"]
for p in need:
    ok(f"openapi lists {p}", p in paths)
ok("docs page loads", c.get("/docs").status_code == 200)

print(f"\n{'✅ ALL FRONTEND/ROUTE TESTS PASSED' if F==0 else '❌ FAILURES'}: {P} passed, {F} failed")
sys.exit(0 if F==0 else 1)
