// The image-style visualizer: approach tabs · player · visual flow with
// highlighted array + pointers · what-happened/why-matters · Idea/Problem/Code.
window.Visualizer = (function () {
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const MEM_DOTS = ["#22c55e", "#f59e0b", "#f472b6", "#38bdf8"];

  function mount(el, problem) {
    if (!problem.approaches || !problem.approaches.length) {
      el.innerHTML = `<div class="glass pad muted">No animated visualizer authored for this problem yet — it's config-driven, so it can be added without code changes. Use the resource links to study it.</div>`;
      return;
    }
    let ai = 0;       // approach index
    let fi = 0;       // frame index
    let playing = false, timer = null;
    let sideTab = "idea";
    let editing = false;

    const approach = () => problem.approaches[ai];
    const frames = () => approach().frames;
    const frame = () => frames()[fi];

    function stop() { if (timer) { clearInterval(timer); timer = null; } playing = false; }
    function play() {
      if (playing) { stop(); draw(); return; }
      playing = true;
      timer = setInterval(() => {
        if (fi >= frames().length - 1) { stop(); draw(); return; }
        fi++; draw();
      }, 1100);
    }

    function cellClass(idx, hi) {
      const c = [];
      if (hi.pair && hi.pair.includes(idx)) c.push("first");
      if (hi.first === idx) c.push("first");
      if (hi.second === idx) c.push("second");
      if ((hi.passed || []).includes(idx)) c.push("passed");
      if ((hi.stored || []).includes(idx)) c.push("stored");
      if ((hi.window || []).includes(idx)) c.push("win");
      return c.join(" ");
    }
    function ptrLabels(idx, hi) {
      if (!hi.ptr) return "";
      const colors = { l: "#14b8a6", r: "#f472b6", lo: "#14b8a6", mid: "#f59e0b", hi: "#f472b6" };
      return Object.entries(hi.ptr).filter(([, v]) => v === idx)
        .map(([k]) => `<span style="color:${colors[k] || "#22c55e"}">${k}↓</span>`).join(" ");
    }

    function arrbox() {
      const f = frame();
      return `<div class="arrbox">${f.arr.map((v, i) => `
        <div class="cell">
          <div class="idx">${i}</div>
          <div class="ptrs">${ptrLabels(i, f.hi)}</div>
          <div class="val ${cellClass(i, f.hi)}">${esc(v)}</div>
        </div>`).join("")}</div>
        <div class="legend">
          <span><span class="sw" style="background:rgba(34,197,94,.5)"></span>first / pair</span>
          <span><span class="sw" style="background:rgba(245,158,11,.5)"></span>second</span>
          <span><span class="sw" style="background:rgba(20,184,166,.5)"></span>stored</span>
          <span><span class="sw" style="background:rgba(56,189,248,.5)"></span>window</span>
          <span><span class="sw" style="background:#233033"></span>passed / not visited</span>
        </div>`;
    }

    function memCards() {
      const f = frame();
      return `<div class="memtitle">🗄️ Memory: what the program is holding</div>
        <div class="memgrid">${f.memory.map((m, i) => `
          <div class="memcard">
            <div class="ml"><span class="dot" style="background:${MEM_DOTS[i % 4]}"></span>${esc(m.label)}</div>
            <div class="mv">${esc(m.value)}</div>
            <div class="ms">${esc(m.sub)}</div>
          </div>`).join("")}</div>`;
    }

    function codeBlock() {
      const f = frame();
      const lines = approach().java.split("\n");
      const body = editing
        ? `<textarea class="editor" id="viz-editor">${esc(problem._userCode?.[approach().key] ?? approach().java)}</textarea>
           <div class="row" style="margin-top:8px">
             <button class="btn small" id="viz-save">💾 Save</button>
             <button class="btn small" id="viz-reset">↺ Reset</button>
             <button class="btn small" id="viz-view">👁 View walkthrough</button></div>`
        : `<div class="code">${lines.map((ln, i) =>
            `<div class="ln ${i === (f.line - 1) ? "hl" : ""}"><span class="no">${i + 1}</span><span class="src">${esc(ln) || " "}</span></div>`
          ).join("")}</div>
           <div class="row" style="margin-top:8px"><button class="btn small" id="viz-edit">✏️ Try it yourself</button></div>`;
      return body;
    }

    function sidePanel() {
      const a = approach();
      if (sideTab === "code") return codeBlock();
      if (sideTab === "problem") {
        return `<p style="font-size:14px">${esc(problem.dsExplainer || "Study this problem, then try the approaches.")}</p>
          <div class="row" style="margin-top:10px">
            <a class="btn small" target="_blank" href="${problem.links.leetcode}">LeetCode ↗</a>
            <a class="btn small" target="_blank" href="${problem.links.neetcode}">NeetCode ↗</a>
            <a class="btn small" target="_blank" href="${problem.links.striver}">Striver ↗</a>
          </div>`;
      }
      // idea
      return `<div class="idea-h">💡 The idea in plain words</div>
        <div class="idea-name">${esc(a.name)}</div>
        <p class="muted" style="font-size:14px">${esc(a.idea)}</p>
        <ol class="steps">${a.steps.map(s => `<li>${esc(s)}</li>`).join("")}</ol>
        ${memCards()}`;
    }

    function draw() {
      const f = frame();
      const total = frames().length;
      const counter = f.counter || { label: "step", cur: fi + 1, max: total };
      el.innerHTML = `
      <div class="viz-top">
        <div class="viz-title">
          <div class="row" style="align-items:center;gap:10px">
            <h1>${esc(problem.title)}</h1><span class="badge ${problem.difficulty}">${problem.difficulty}</span>
          </div>
          <p>${esc(problem.patternName)} · ${esc(problem.ds)}</p>
        </div>
        <div class="appr-tabs">
          ${problem.approaches.map((a, i) => `<button class="${i === ai ? "active" : ""}" data-appr="${i}">
            <span>${i + 1}</span> ${esc(a.name)} <span class="bo">${esc(a.bigO)}</span></button>`).join("")}
        </div>
      </div>

      <div class="player">
        <div class="icn" id="v-first" title="First">⏮</div>
        <div class="icn" id="v-prev" title="Prev">◀</div>
        <div class="icn play" id="v-play">${playing ? "❚❚ Pause" : "▶ Play"}</div>
        <div class="icn" id="v-next" title="Next">▶</div>
        <div class="icn" id="v-last" title="Last">⏭</div>
        <div class="icn" id="v-reset" title="Reset">↻</div>
        <div class="counter">
          <span>${esc(counter.label)} <b>${counter.cur}</b>/${counter.max}</span>
          <span>${fi + 1} / ${total}</span>
        </div>
      </div>
      <div class="progbar">${frames().map((_, i) => `<div class="seg ${i <= fi ? "on" : ""}"></div>`).join("")}</div>

      <div class="viz-cols">
        <div>
          <div class="glass pad">
            <div class="idea-h">🔲 Visual flow</div>
            ${arrbox()}
          </div>
          <div class="glass pad setup" style="margin-top:12px">
            <h3>${esc(f.what.split(".")[0])}.</h3>
            <div class="wjh">
              <div class="card"><div class="t">🎯 What just happened</div><div style="font-size:13px">${esc(f.what)}</div></div>
              <div class="card"><div class="t">💡 Why it matters</div><div style="font-size:13px">${esc(f.why)}</div></div>
            </div>
          </div>
        </div>
        <div class="glass pad">
          <div class="side-tabs">
            <button data-side="idea" class="${sideTab === "idea" ? "active" : ""}">💡 Idea</button>
            <button data-side="problem" class="${sideTab === "problem" ? "active" : ""}">📖 Problem</button>
            <button data-side="code" class="${sideTab === "code" ? "active" : ""}">&lt;/&gt; Code</button>
          </div>
          ${sidePanel()}
        </div>
      </div>`;

      // wire controls
      el.querySelectorAll("[data-appr]").forEach(b => b.onclick = () => { stop(); ai = +b.dataset.appr; fi = 0; draw(); });
      el.querySelectorAll("[data-side]").forEach(b => b.onclick = () => { sideTab = b.dataset.side; draw(); });
      el.querySelector("#v-first").onclick = () => { stop(); fi = 0; draw(); };
      el.querySelector("#v-prev").onclick = () => { stop(); fi = Math.max(0, fi - 1); draw(); };
      el.querySelector("#v-next").onclick = () => { stop(); fi = Math.min(total - 1, fi + 1); draw(); };
      el.querySelector("#v-last").onclick = () => { stop(); fi = total - 1; draw(); };
      el.querySelector("#v-reset").onclick = () => { stop(); fi = 0; draw(); };
      el.querySelector("#v-play").onclick = () => play();
      const edit = el.querySelector("#viz-edit"); if (edit) edit.onclick = () => { editing = true; draw(); };
      const view = el.querySelector("#viz-view"); if (view) view.onclick = () => { editing = false; draw(); };
      const save = el.querySelector("#viz-save"); if (save) save.onclick = () => {
        problem._userCode = problem._userCode || {};
        problem._userCode[approach().key] = el.querySelector("#viz-editor").value;
        localStorage.setItem("algolotl.code." + problem.id + "." + approach().key, problem._userCode[approach().key]);
      };
      const reset = el.querySelector("#viz-reset"); if (reset) reset.onclick = () => {
        localStorage.removeItem("algolotl.code." + problem.id + "." + approach().key);
        if (problem._userCode) delete problem._userCode[approach().key];
        el.querySelector("#viz-editor").value = approach().java;
      };
    }

    // hydrate any saved user code
    problem._userCode = {};
    problem.approaches.forEach(a => {
      const saved = localStorage.getItem("algolotl.code." + problem.id + "." + a.key);
      if (saved) problem._userCode[a.key] = saved;
    });

    draw();
  }

  return { mount };
})();
