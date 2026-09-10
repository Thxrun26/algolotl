# 🦎 Algolotl — Pattern-first DSA in 30 days

**Solve 120–150 curated DSA problems in 30 days by mastering patterns**, not by grinding blindly.
Algolotl is a full learning platform: **line-by-line visualizers** (watch the array, pointers, and
program memory change like in a debugger), **two Notion boards** (by data structure & by pattern),
**daily revision**, **accounts + live progress**, and an **AI tutor**.

Built by a "chief-architect + senior full-stack" plan → code → test → deploy.

- **Backend:** Python **FastAPI** (async, Pydantic-validated, auto OpenAPI docs)
- **Frontend:** zero-build static (instant load, deploys anywhere)
- **Auth:** email+password (PBKDF2 + JWT) with a one-click **Demo** account; Google OAuth ready
- **Data:** 150-problem catalog (NeetCode-150 set) mapped across 30 days
- **Tested:** 43 API + 42 route + 36 headless-render checks — **121 green**

---

## 🧭 Why "Algolotl"?
`algorithm + axolotl` 🦎 — a friendly, unique, brandable name (great for a `algolotl.dev` domain).
Genz, memorable, and definitely not another "…code" clone.

---

## ⚡ Run locally (2 ways)

### Option A — one command (recommended)
```bash
./run.sh
```
This generates the dataset, creates a venv, installs deps, sets a random secret, and starts the
server at **http://localhost:8000** (API docs at **/docs**).

### Option B — manual
```bash
# 1) build the problem dataset (creates backend/app/data/problems.json + web/data/problems.js)
python3 scripts/generate.py

# 2) backend
cd backend
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ALGO_SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))")
python3 -m uvicorn app.main:app --reload --port 8000
```
Open **http://localhost:8000**. Click **✨ Try demo** to jump straight in.

> The frontend also works fully offline (progress saved in the browser) if you ever open
> `web/index.html` directly, but running the backend unlocks accounts + cross-device sync.

---

## ☁️ Deploy (pick one)

### Render.com (one file, included)
Push to GitHub, then "New → Blueprint" and point at the repo. `render.yaml` provisions the web
service, a persistent disk for progress, and a generated secret. Done → you get a public HTTPS URL.

### Docker (anywhere: Fly.io, Railway, Cloud Run, a VPS)
```bash
docker build -t algolotl .
docker run -p 8000:8000 -e ALGO_SECRET_KEY=$(openssl rand -hex 32) -v algolotl_data:/data algolotl
```

### From VS Code
Install the **Render**/**Railway** extension (or the Docker extension) and deploy the folder, or
just `git push` to a repo connected to Render. Set `ALGO_SECRET_KEY` and (optionally)
`ALGO_CORS_ORIGINS=https://yourdomain`.

**Production checklist**
- [ ] `ALGO_ENVIRONMENT=production`
- [ ] `ALGO_SECRET_KEY` = 64-char random hex (never commit it)
- [ ] `ALGO_CORS_ORIGINS=https://yourdomain`
- [ ] Persistent volume mounted at `ALGO_DATA_DIR`
- [ ] (optional) `ALGO_OPENAI_API_KEY` for the full LLM tutor
- [ ] (optional) Google OAuth creds (below)

---

## 🔐 Security notes (honest)
Implemented best-practices — **no one can promise "zero vulnerabilities", but here's what's done:**
- **Passwords:** PBKDF2-HMAC-SHA256, per-user salt, 200k rounds, constant-time compare (stdlib — no
  vulnerable third-party crypto).
- **Sessions:** signed HS256 JWTs with expiry; verified in constant time.
- **Input validation:** every request body is a Pydantic model (rejects bad/oversized input → 422).
- **Headers:** `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`,
  `Permissions-Policy`, and HSTS in production.
- **CORS:** locked to your origins in prod.
- **Authz:** every progress/assistant route requires a valid bearer token; users only see their data.

### Enabling Google OAuth (optional, production)
1. Create OAuth credentials in Google Cloud Console; add your redirect URI.
2. Set `ALGO_GOOGLE_CLIENT_ID` / `ALGO_GOOGLE_CLIENT_SECRET`.
3. Add `authlib` and a `/api/auth/google` route (a stub interface is documented in
   `backend/app/api/auth.py`). The email+password + demo flows work today without it.

---

## 🗺️ How to use it
1. **Log in** (or **Try demo**).
2. **30-Day Plan** → each day lists ~5 problems by pattern. Tick them off (syncs live).
3. Open a problem → read the **⚡ Quick-shot** (learn the DS first), then the **🎬 visualizer**:
   - Switch **approach tabs** (e.g. *Brute Force O(n²)* ↔ *Hash Map O(n)*).
   - **Play / step** through — watch the array cells, pointers, and the **memory cards** update, with
     **What just happened / Why it matters** on every step.
   - Read the **Idea → Problem → Code** panel; hit **✏️ Try it yourself** to edit the Java (saved locally).
4. Mark **Needs Revision** on tough ones → they appear in **🔁 Revision** the next day.
5. Use the two **Notion boards** (by **Data Structure** and by **Pattern**) to study by theme.
6. Stuck? Tap the **💬 AI tutor** (bottom-right) and ask "how do I start?".

---

## 🔌 API endpoints
Interactive docs live at **`/docs`** (Swagger) and **`/redoc`**. Full list:

### Auth
| Method | Path | Body | Auth | Purpose |
|---|---|---|---|---|
| POST | `/api/auth/register` | `{email,name,password}` | – | Create account → returns JWT |
| POST | `/api/auth/login` | `{email,password}` | – | Log in → returns JWT |
| POST | `/api/auth/demo` | – | – | One-click demo account |
| GET  | `/api/auth/me` | – | ✅ | Current user |

### Problems & Notion views
| Method | Path | Query | Purpose |
|---|---|---|---|
| GET | `/api/catalog` | – | Full dataset (problems, patterns, ds, 30-day meta) |
| GET | `/api/problems` | `pattern,ds,difficulty,day` | Filtered list |
| GET | `/api/problems/{pid}` | – | One problem (+ visualizer approaches) |
| GET | `/api/notion/patterns` | – | Notion board grouped by pattern |
| GET | `/api/notion/ds` | – | Notion board grouped by data structure |

### Progress & revision (auth required)
| Method | Path | Body | Purpose |
|---|---|---|---|
| GET  | `/api/progress` | – | Your progress + stats |
| POST | `/api/progress/status` | `{problem_id,status,note}` | Set a problem's status |
| POST | `/api/progress/revision` | `{problem_id,on}` | Add/remove from revision |
| GET  | `/api/progress/revision/today` | – | Today's revision queue |

### Assistant & health
| Method | Path | Body | Purpose |
|---|---|---|---|
| POST | `/api/assistant` | `{question,problem_id?}` | AI tutor (LLM if key set, else offline) |
| GET  | `/api/health/live` | – | Liveness |
| GET  | `/api/health/ready` | – | Readiness (checks catalog) |

---

## 🧪 Tests (run them yourself)
```bash
# backend API journeys (auth, catalog, progress, revision, assistant, security, crypto)
python3 tests/test_api.py

# static serving + SPA routes + OpenAPI endpoint coverage
python3 tests/test_frontend.py

# headless DOM render of every page + the visualizer mount
node tests/render.mjs
```
All three suites pass (**43 + 42 + 36 = 121 checks**).

---

## ➕ Add problems / visualizers (pure config)
- **Catalog (all 150):** edit `scripts/catalog.py` — one row `(slug, title, difficulty, pattern)`.
- **Rich visualizer:** add a simulator in `scripts/frames.py` (it *runs the algorithm* and records
  frames, so steps are always correct) and register the problem in `scripts/flagship.py`.
- Then `python3 scripts/generate.py` and refresh. Everything (tracker, Notion, filters, detail page)
  updates automatically.

---

## 📁 Structure
```
algolotl/
├─ backend/app/
│  ├─ main.py              # FastAPI app: routers, CORS, security headers, static mount, health
│  ├─ core/               # config (Pydantic) · security (JWT+PBKDF2) · store (JSON, swappable)
│  ├─ models/schemas.py   # Pydantic request/response contracts
│  └─ api/                # auth · problems · progress · assistant · deps
├─ web/                   # zero-build frontend
│  ├─ index.html
│  ├─ assets/styles.css
│  └─ js/{api,visualizer,app}.js
├─ scripts/               # catalog.py · frames.py · flagship.py · generate.py
├─ tests/                 # test_api.py · test_frontend.py · render.mjs
├─ Dockerfile · render.yaml · run.sh · README.md
```

---

## 📚 Resources it maps to
- **Striver A2Z / SDE Sheet** — takeuforward.org
- **NeetCode 150** — neetcode.io/roadmap
- **LeetCode** — Blind 75 → NeetCode 150 → Top Interview 150
- **Cracking the Coding Interview** — approach & thinking

Anyone — not just Tharun — can land on this page and go from newbie to 120–150 problems, pattern by
pattern, in 30 days. 🦎🔥
