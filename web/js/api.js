// API client. Talks to the FastAPI backend when available; gracefully falls
// back to localStorage-only mode so the app works even opened as a static file.
window.API = (function () {
  const TOKEN_KEY = "algolotl.token";
  const USER_KEY = "algolotl.user";
  const LOCAL_PROGRESS = "algolotl.progress";
  const LOCAL_REV = "algolotl.revision";

  const base = ""; // same-origin when served by FastAPI
  const getToken = () => localStorage.getItem(TOKEN_KEY);
  const setToken = (t) => t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY);
  const getUser = () => { try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; } };
  const setUser = (u) => u ? localStorage.setItem(USER_KEY, JSON.stringify(u)) : localStorage.removeItem(USER_KEY);
  const lget = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
  const lset = (k, v) => localStorage.setItem(k, JSON.stringify(v));

  async function req(path, opts = {}) {
    const headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
    const t = getToken();
    if (t) headers.Authorization = "Bearer " + t;
    const res = await fetch(base + path, Object.assign({}, opts, { headers }));
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw Object.assign(new Error(data.detail || "Request failed"), { status: res.status, data });
    return data;
  }

  // ---- auth ----
  async function register(email, name, password) {
    const d = await req("/api/auth/register", { method: "POST", body: JSON.stringify({ email, name, password }) });
    setToken(d.access_token); setUser(d.user); return d.user;
  }
  async function login(email, password) {
    const d = await req("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    setToken(d.access_token); setUser(d.user); return d.user;
  }
  async function demo() {
    const d = await req("/api/auth/demo", { method: "POST" });
    setToken(d.access_token); setUser(d.user); return d.user;
  }
  function logout() { setToken(null); setUser(null); }
  const isAuthed = () => !!getToken();

  // ---- catalog (prefers embedded window.ALGO for instant load) ----
  async function catalog() {
    if (window.ALGO) return window.ALGO;
    return await req("/api/catalog");
  }

  // ---- progress (backend if authed, else localStorage) ----
  async function getProgress() {
    if (isAuthed()) {
      try { return await req("/api/progress"); } catch { /* fall through */ }
    }
    const prog = lget(LOCAL_PROGRESS, {});
    const rev = lget(LOCAL_REV, {});
    const SOLVED = ["Solved Solo", "Solved w/ Hint"];
    const solved = Object.values(prog).filter(v => SOLVED.includes(v.status)).length;
    return { progress: prog, revision: Object.keys(rev), stats: { solved, tracked: Object.keys(prog).length, revisionCount: Object.keys(rev).length } };
  }
  async function setStatus(problem_id, status, note = "") {
    if (isAuthed()) {
      try { return await req("/api/progress/status", { method: "POST", body: JSON.stringify({ problem_id, status, note }) }); } catch { /* fall */ }
    }
    const prog = lget(LOCAL_PROGRESS, {}); prog[problem_id] = { status, note, ts: Date.now() }; lset(LOCAL_PROGRESS, prog);
    if (status === "Needs Revision") { const r = lget(LOCAL_REV, {}); r[problem_id] = Date.now(); lset(LOCAL_REV, r); }
    return { ok: true };
  }
  async function toggleRevision(problem_id, on) {
    if (isAuthed()) { try { return await req("/api/progress/revision", { method: "POST", body: JSON.stringify({ problem_id, on }) }); } catch { } }
    const r = lget(LOCAL_REV, {}); if (on) r[problem_id] = Date.now(); else delete r[problem_id]; lset(LOCAL_REV, r); return { ok: true };
  }
  async function revisionToday() {
    if (isAuthed()) { try { return await req("/api/progress/revision/today"); } catch { } }
    const r = lget(LOCAL_REV, {}); const data = await catalog();
    const byId = Object.fromEntries(data.problems.map(p => [p.id, p]));
    const ids = Object.entries(r).sort((a, b) => b[1] - a[1]).map(([id]) => id);
    return { count: ids.length, problems: ids.map(id => byId[id]).filter(Boolean) };
  }

  // ---- assistant ----
  async function ask(question, problem_id = null) {
    if (isAuthed()) {
      try { return await req("/api/assistant", { method: "POST", body: JSON.stringify({ question, problem_id }) }); } catch { }
    }
    // offline mini-tutor when no backend/login
    const data = await catalog();
    const p = problem_id ? data.problems.find(x => x.id === problem_id) : null;
    let ans = "Log in to unlock the full AI tutor. ";
    if (p) ans += `\n\n${p.title} — ${p.patternName}. ` + (p.quickshot || "");
    else ans += "Ask me about a pattern like sliding window, two pointers, binary search, DP, or backtracking.";
    return { answer: ans, source: "offline-tutor" };
  }

  return { getToken, getUser, register, login, demo, logout, isAuthed,
           catalog, getProgress, setStatus, toggleRevision, revisionToday, ask };
})();
