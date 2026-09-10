// Algolotl SPA — hash router, pages, and the AI assistant widget.
(function () {
  const app = document.getElementById("app");
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  let DATA = null; // catalog
  let PROG = null; // progress

  const NAV = [
    ["#/", "Home"], ["#/tracker", "30-Day Plan"], ["#/problems", "Problems"],
    ["#/ds", "Notion · DS"], ["#/patterns", "Notion · Patterns"],
    ["#/revision", "Revision"], ["#/about", "About"], ["#/me", "Me"],
  ];

  function chrome(inner) {
    const active = (location.hash || "#/").split("?")[0];
    const user = API.getUser();
    const right = user
      ? `<div class="user-chip">🦎 ${esc(user.name)} <button class="btn small" id="logout">Logout</button></div>`
      : `<a class="btn small primary" href="#/login">Log in</a>`;
    return `
    <header><div class="wrap">
      <a class="logo" href="#/"><span class="lot">🦎</span><span class="grad">Algolotl</span></a>
      <nav>${NAV.map(([h, l]) => `<a href="${h}" class="${active === h ? "active" : ""}">${l}</a>`).join("")}</nav>
      ${right}
    </div></header>
    <main><div class="wrap">${inner}</div></main>
    <footer>Algolotl 🦎 · pattern-first DSA · ${DATA ? DATA.meta.total : 150} problems · 30-day plan · line-by-line visualizers</footer>
    <button class="fab" id="fab" title="Ask the AI tutor">💬</button>
    <div class="assistant glass" id="assistant">
      <div class="ah">🦎 AI Tutor <button class="btn small" id="a-close">✕</button></div>
      <div class="amsgs" id="a-msgs"><div class="m a">Hey! I'm your DSA tutor. Ask me about any pattern, or open a problem and ask "how do I start?"</div></div>
      <div class="ain"><input id="a-in" placeholder="Ask a doubt…"><button class="btn primary small" id="a-send">Send</button></div>
    </div>`;
  }

  // ---------- pages ----------
  function pageHome() {
    const solved = PROG?.stats?.solved ?? 0;
    return `
    <div class="glass hero">
      <div class="mascot">🦎</div>
      <p class="clue">pattern-first · Java · 30 days · 150 problems</p>
      <h1>Crack DSA the <span class="grad">smart</span> way</h1>
      <p class="muted" style="max-width:640px;margin:12px auto">
        Solve <b>120–150 curated problems in 30 days</b>, organized by pattern. Every flagship
        problem has an <b>image-clear, line-by-line visualizer</b> — watch the array, the pointers,
        and the program's memory update step by step. Two Notion boards (by data structure &amp; by
        pattern), daily revision, and an AI tutor.</p>
      <div class="row" style="justify-content:center;margin-top:18px">
        <a class="btn primary" href="#/tracker">Start the 30-Day Plan →</a>
        <a class="btn" href="#/problems">Browse Problems</a>
        ${API.isAuthed() ? "" : `<a class="btn" href="#/login">Log in / Demo</a>`}
      </div>
    </div>
    <div class="grid g4" style="margin-top:16px">
      <div class="glass stat"><div class="k grad">${DATA.meta.total}</div><div class="l">Problems</div></div>
      <div class="glass stat"><div class="k grad">30</div><div class="l">Day Plan</div></div>
      <div class="glass stat"><div class="k grad">${Object.keys(DATA.patterns).length}</div><div class="l">Patterns</div></div>
      <div class="glass stat"><div class="k grad">${solved}</div><div class="l">You Solved</div></div>
    </div>
    <div class="grid g3" style="margin-top:14px">
      <div class="glass pad"><h3 style="margin:0 0 6px">🎬 See it, don't memorize it</h3><p class="muted" style="font-size:13px">Line-by-line Java with live array + memory state — like watching the algorithm think.</p></div>
      <div class="glass pad"><h3 style="margin:0 0 6px">🧩 Pattern-first</h3><p class="muted" style="font-size:13px">Recognition clues + quick-shot notes so you know which technique a problem needs.</p></div>
      <div class="glass pad"><h3 style="margin:0 0 6px">🔁 Spaced revision</h3><p class="muted" style="font-size:13px">Yesterday's hard ones resurface daily so patterns actually stick.</p></div>
    </div>`;
  }

  function statusOf(id) { return PROG?.progress?.[id]?.status ?? "Not Started"; }
  function isDone(id) { return ["Solved Solo", "Solved w/ Hint"].includes(statusOf(id)); }

  function pageTracker() {
    let html = `<h1>🗓️ 30-Day Plan</h1>
      <p class="muted">Daily routine: <b>~5 new + revision</b>. ${API.isAuthed() ? "Progress syncs to your account." : `<a class="link" href="#/login">Log in</a> to sync across devices (works locally otherwise).`}</p>`;
    for (const d of DATA.dayMeta) {
      const ps = DATA.problems.filter(p => p.day === d.day);
      html += `<div class="glass pad" style="margin-bottom:10px">
        <div class="row" style="justify-content:space-between;align-items:center">
          <b>Day ${d.day} · ${esc(d.topic)}</b><span class="pill">${ps.length ? ps.length + " problems" : "review"}</span>
        </div>`;
      if (ps.length) {
        html += `<table style="margin-top:8px"><tbody>${ps.map(p => `
          <tr class="${isDone(p.id) ? "done" : ""}">
            <td style="width:22px"><input class="checkbox" type="checkbox" ${isDone(p.id) ? "checked" : ""} data-done="${p.id}"></td>
            <td><a class="link" href="#/p/${p.id}">${esc(p.title)}</a></td>
            <td><span class="badge ${p.difficulty}">${p.difficulty}</span></td>
            <td class="muted">${esc(p.patternName)}</td>
            <td class="muted" style="font-size:11px">${esc(statusOf(p.id))}</td>
          </tr>`).join("")}</tbody></table>`;
      } else {
        html += `<p class="muted" style="margin:8px 0 0;font-size:13px">Revisit weak patterns & yesterday's hard problems (see the <a class="link" href="#/revision">Revision</a> tab).</p>`;
      }
      html += `</div>`;
    }
    return html;
  }

  function problemCard(p) {
    return `<a class="glass pad" href="#/p/${p.id}" style="display:block">
      <div class="row" style="justify-content:space-between"><b>${esc(p.title)}</b><span class="badge ${p.difficulty}">${p.difficulty}</span></div>
      <div class="muted" style="font-size:12px;margin-top:2px">Day ${p.day} · ${esc(p.patternName)}</div>
      ${p.hasViz ? `<div class="pill" style="margin-top:8px">🎬 visualizer</div>` : `<div class="pill" style="margin-top:8px">🔗 links</div>`}
    </a>`;
  }

  function pageProblems() {
    const q = new URLSearchParams(location.hash.split("?")[1] || "");
    const diff = q.get("diff") || "All", pat = q.get("pat") || "All";
    let list = DATA.problems.filter(p => (diff === "All" || p.difficulty === diff) && (pat === "All" || p.pattern === pat));
    return `<h1>Problems <span class="muted" style="font-size:14px">(${list.length})</span></h1>
      <div class="row" style="margin:12px 0">
        <select style="max-width:150px" id="f-diff">${["All", "Easy", "Medium", "Hard"].map(d => `<option ${d === diff ? "selected" : ""}>${d}</option>`).join("")}</select>
        <select style="max-width:220px" id="f-pat"><option value="All" ${pat === "All" ? "selected" : ""}>All patterns</option>
          ${Object.entries(DATA.patterns).map(([k, v]) => `<option value="${k}" ${k === pat ? "selected" : ""}>${esc(v.name)}</option>`).join("")}</select>
      </div>
      <div class="notecol">${list.map(problemCard).join("")}</div>`;
  }

  function notionView(groups, title, subtitle) {
    let html = `<h1>${title}</h1><p class="muted">${subtitle}</p>`;
    for (const [key, g] of Object.entries(groups)) {
      const ps = g.ids.map(id => DATA.problems.find(p => p.id === id));
      const done = ps.filter(p => isDone(p.id)).length;
      html += `<div class="glass pad" style="margin-bottom:10px">
        <div class="row" style="justify-content:space-between;align-items:center">
          <b>${esc(g.name)}</b><span class="pill">${done}/${ps.length} solved</span>
        </div>
        <div class="notecol" style="margin-top:10px">${ps.map(problemCard).join("")}</div>
      </div>`;
    }
    return html;
  }

  function pageDS() { return notionView(DATA.ds, "🗃️ Notion · by Data Structure", "Grouped by the underlying data structure — great for building DS intuition."); }
  function pagePatterns() { return notionView(DATA.patterns, "🧩 Notion · by Pattern", "Grouped by solving pattern — this is how you hit 120–150 in 30 days."); }

  async function pageRevision() {
    const rev = await API.revisionToday();
    let html = `<h1>🔁 Daily Revision</h1><p class="muted">Yesterday's hard ones come back so patterns stick. Flag any problem as “Needs Revision” to add it here.</p>`;
    if (!rev.problems.length) html += `<div class="glass pad muted">Nothing to revise yet. Mark tough problems “Needs Revision” on their page. 🎉</div>`;
    else html += `<div class="notecol">${rev.problems.map(problemCard).join("")}</div>`;
    return html;
  }

  function pageAbout() {
    return `<h1>About Algolotl 🦎</h1>
      <div class="glass pad">
        <p>Algolotl is a <b>pattern-first DSA learning platform</b> built for beginners who code in Java.
        The goal: <b>solve 120–150 curated problems in 30 days</b> by mastering the ~18 patterns that
        unlock everything else.</p>
        <h2>What makes it different</h2>
        <ul class="muted" style="line-height:1.9">
          <li>🎬 <b>Line-by-line visualizers</b> — watch the array, pointers, and program memory change step by step.</li>
          <li>🧩 <b>Two Notion boards</b> — one by data structure, one by pattern.</li>
          <li>⚡ <b>Quick-shot notes</b> before each approach so you learn the DS first.</li>
          <li>🔁 <b>Daily revision</b> of the previous day's hard problems.</li>
          <li>🤖 <b>AI tutor</b> for doubts (offline tutor built-in; plug an API key for full LLM).</li>
          <li>🔐 <b>Accounts + live progress</b> synced across devices.</li>
        </ul>
        <h2>Resources it's built from</h2>
        <div class="row">
          <a class="btn small" target="_blank" href="https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/">Striver A2Z ↗</a>
          <a class="btn small" target="_blank" href="https://neetcode.io/roadmap">NeetCode 150 ↗</a>
          <a class="btn small" target="_blank" href="https://leetcode.com/studyplan/">LeetCode ↗</a>
        </div>
      </div>`;
  }
 function pageAboutMe() {
    return `
    <div class="glass hero" style="padding:34px 20px">
      <div class="mascot">👨‍💻</div>
      <h1>Hi, I'm <span class="grad">Tharun</span></h1>
      <p class="muted" style="max-width:620px;margin:10px auto">
        Backend engineer who loves clean, config-driven systems — Node.js, Fastify,
        Kafka, MongoDB, Redis and event-driven architecture. I built Algolotl to
        master DSA patterns the visual way and to help anyone crack 120–150 problems
        in 30 days. 🦎</p>
      <div class="row" style="justify-content:center;margin-top:16px">
        <a class="btn" target="_blank" href="https://github.com/">GitHub ↗</a>
        <a class="btn" target="_blank" href="https://www.linkedin.com/">LinkedIn ↗</a>
        <a class="btn" href="mailto:you@example.com">Email ✉️</a>
      </div>
    </div>

    <div class="grid g3" style="margin-top:16px">
      <div class="glass pad">
        <h3 style="margin:0 0 6px">🛠️ Stack I love</h3>
        <p class="muted" style="font-size:13px">Node.js · Fastify · TypeScript ·
        Kafka · MongoDB · Redis · Debezium CDC · Docker.</p>
      </div>
      <div class="glass pad">
        <h3 style="margin:0 0 6px">🎯 Why Algolotl</h3>
        <p class="muted" style="font-size:13px">Patterns beat memorization. Seeing the
        array, pointers, and memory move made everything click — so I turned that into
        a platform.</p>
      </div>
      <div class="glass pad">
        <h3 style="margin:0 0 6px">🚀 Currently</h3>
        <p class="muted" style="font-size:13px">Building event-driven backends and
        leveling up system design — one pattern at a time.</p>
      </div>
    </div>

    <div class="glass pad" style="margin-top:16px">
      <h2 style="margin-top:0">My 30-day promise</h2>
      <p class="muted">Show up daily, learn the pattern first, revise yesterday's hard
      ones, and let the visualizer do the teaching. Anyone landing here can do the same.
      Let's get it. 💪</p>
      <a class="btn primary" href="#/tracker">Start the plan →</a>
    </div>`;
  }  

  function pageLogin() {
    return `<div class="authwrap glass pad">
      <div style="text-align:center"><div class="mascot">🦎</div><h1 style="margin:6px 0">Welcome to Algolotl</h1><p class="muted" style="font-size:13px">Track your 30-day journey across devices.</p></div>
      <div class="tabline" style="margin-top:16px"><button id="tab-login" class="active">Log in</button><button id="tab-reg">Sign up</button></div>
      <div id="auth-form"></div>
      <div class="row" style="margin-top:14px;justify-content:center">
        <button class="btn" id="demo-btn">✨ Try demo (no signup)</button>
      </div>
      <p class="muted" style="font-size:11px;text-align:center;margin-top:14px">
        🔐 Passwords hashed with PBKDF2 · JWT sessions · Google OAuth ready (see README).</p>
    </div>`;
  }

  function renderAuthForm(mode) {
    const box = document.getElementById("auth-form");
    if (!box) return;
    box.innerHTML = mode === "reg"
      ? `<div class="grid"><input id="au-name" placeholder="Name"><input id="au-email" placeholder="Email" type="email"><input id="au-pass" placeholder="Password (min 8 chars)" type="password"><button class="btn primary" id="au-go">Create account</button></div><div class="err" id="au-err"></div>`
      : `<div class="grid"><input id="au-email" placeholder="Email" type="email"><input id="au-pass" placeholder="Password" type="password"><button class="btn primary" id="au-go">Log in</button></div><div class="err" id="au-err"></div>`;
    document.getElementById("au-go").onclick = async () => {
      const err = document.getElementById("au-err"); err.textContent = "";
      try {
        const email = document.getElementById("au-email").value.trim();
        const pass = document.getElementById("au-pass").value;
        if (mode === "reg") await API.register(email, document.getElementById("au-name").value.trim(), pass);
        else await API.login(email, pass);
        location.hash = "#/tracker";
      } catch (e) { err.textContent = e.data?.detail || e.message || "Failed. Check your details."; }
    };
  }

  async function pageProblem(id) {
    const p = DATA.problems.find(x => x.id === id);
    if (!p) return `<p>Not found. <a class="link" href="#/problems">Back</a></p>`;
    const st = statusOf(id);
    const STATUSES = ["Attempted", "Solved w/ Hint", "Solved Solo", "Needs Revision"];
    let html = `<a class="link" href="#/problems" style="font-size:12px">← Problems</a>`;
    if (p.quickshot) {
      html += `<div class="quickshot" style="margin:10px 0"><div class="qh">⚡ Quick-shot — read this first</div><div style="font-size:14px">${esc(p.quickshot)}</div></div>`;
    }
    html += `<div id="viz-mount"></div>`;
    html += `<h2>✅ Track your progress</h2><div class="row" id="status-row">
      ${STATUSES.map(s => `<button class="btn small ${s === st ? "primary" : ""}" data-status="${s}">${s}</button>`).join("")}
      <a class="btn small" target="_blank" href="${p.links.leetcode}">Open on LeetCode ↗</a>
    </div><div class="muted" id="status-msg" style="font-size:12px;margin-top:6px"></div>`;
    return html;
  }

  // ---------- AI assistant ----------
  function wireAssistant() {
    const fab = document.getElementById("fab");
    const panel = document.getElementById("assistant");
    if (!fab) return;
    fab.onclick = () => panel.classList.toggle("open");
    const close = document.getElementById("a-close"); if (close) close.onclick = () => panel.classList.remove("open");
    const send = document.getElementById("a-send"), input = document.getElementById("a-in"), msgs = document.getElementById("a-msgs");
    async function go() {
      const q = input.value.trim(); if (!q) return;
      input.value = "";
      msgs.innerHTML += `<div class="m u">${esc(q)}</div>`;
      msgs.innerHTML += `<div class="m a" id="a-loading">…</div>`;
      msgs.scrollTop = msgs.scrollHeight;
      const pid = (location.hash.startsWith("#/p/")) ? location.hash.slice(4).split("?")[0] : null;
      try {
        const r = await API.ask(q, pid);
        document.getElementById("a-loading").outerHTML = `<div class="m a">${esc(r.answer)}</div>`;
      } catch {
        document.getElementById("a-loading").outerHTML = `<div class="m a">Sorry, I couldn't answer that right now.</div>`;
      }
      msgs.scrollTop = msgs.scrollHeight;
    }
    if (send) send.onclick = go;
    if (input) input.onkeydown = (e) => { if (e.key === "Enter") go(); };
  }

  // ---------- router ----------
  async function render() {
    if (!DATA) DATA = await API.catalog();
    PROG = await API.getProgress();
    const h = location.hash || "#/";
    let inner, mountProblem = null;
    if (h.startsWith("#/p/")) { const id = h.slice(4).split("?")[0]; inner = await pageProblem(id); mountProblem = id; }
    else if (h.startsWith("#/tracker")) inner = pageTracker();
    else if (h.startsWith("#/problems")) inner = pageProblems();
    else if (h.startsWith("#/ds")) inner = pageDS();
    else if (h.startsWith("#/patterns")) inner = pagePatterns();
    else if (h.startsWith("#/revision")) inner = await pageRevision();
    else if (h.startsWith("#/about")) inner = pageAbout();
    else if (h.startsWith("#/me")) inner = pageAboutMe();
    else if (h.startsWith("#/login")) inner = pageLogin();
    else inner = pageHome();

    app.innerHTML = chrome(inner);
    window.scrollTo(0, 0);
    wireAssistant();

    // logout
    const lo = document.getElementById("logout"); if (lo) lo.onclick = () => { API.logout(); location.hash = "#/"; render(); };

    // login page wiring
    if (h.startsWith("#/login")) {
      renderAuthForm("login");
      document.getElementById("tab-login").onclick = (e) => { setActive(e); renderAuthForm("login"); };
      document.getElementById("tab-reg").onclick = (e) => { setActive(e); renderAuthForm("reg"); };
      document.getElementById("demo-btn").onclick = async () => { try { await API.demo(); location.hash = "#/tracker"; } catch { alert("Demo needs the backend running."); } };
      function setActive(e) { document.querySelectorAll(".tabline button").forEach(b => b.classList.remove("active")); e.target.classList.add("active"); }
    }

    // problems filters
    const fd = document.getElementById("f-diff"), fp = document.getElementById("f-pat");
    if (fd) fd.onchange = () => go2(fd.value, fp.value);
    if (fp) fp.onchange = () => go2(fd.value, fp.value);
    function go2(diff, pat) { const q = new URLSearchParams(); if (diff !== "All") q.set("diff", diff); if (pat !== "All") q.set("pat", pat); location.hash = "#/problems" + (q.toString() ? "?" + q : ""); }

    // tracker checkboxes
    app.querySelectorAll("[data-done]").forEach(cb => cb.onchange = async () => {
      await API.setStatus(cb.dataset.done, cb.checked ? "Solved Solo" : "Not Started");
      PROG = await API.getProgress(); render();
    });

    // problem detail: mount visualizer + status buttons
    if (mountProblem) {
      const p = DATA.problems.find(x => x.id === mountProblem);
      const mount = document.getElementById("viz-mount");
      if (mount && p) Visualizer.mount(mount, p);
      app.querySelectorAll("[data-status]").forEach(b => b.onclick = async () => {
        await API.setStatus(mountProblem, b.dataset.status);
        PROG = await API.getProgress();
        document.getElementById("status-msg").textContent = `Saved: ${b.dataset.status}` + (b.dataset.status === "Needs Revision" ? " · added to Revision" : "");
        app.querySelectorAll("[data-status]").forEach(x => x.classList.toggle("primary", x === b));
      });
    }
  }

  window.addEventListener("hashchange", render);
  render();
})();
