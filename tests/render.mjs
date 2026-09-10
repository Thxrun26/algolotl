// Headless DOM harness: loads the real frontend JS with stubbed browser
// globals, navigates every route, and asserts pages render + visualizer mounts
// without throwing. Runs in offline mode (localStorage), so no fetch needed.
import { readFileSync } from "node:fs";

// ---- minimal DOM ----
function makeEl() {
  const el = {
    _html: "", children: [], onclick: null, onchange: null, onkeydown: null,
    value: "", textContent: "", classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    dataset: {}, style: {},
    get innerHTML() { return this._html; },
    set innerHTML(v) { this._html = v; },
    querySelector() { return makeEl(); },
    querySelectorAll() { return []; },
    appendChild() {}, setAttribute() {}, addEventListener() {},
    scrollTop: 0, scrollHeight: 0,
  };
  return el;
}
const elements = { app: makeEl() };
globalThis.window = { ALGO: null, addEventListener() {}, scrollTo() {} };
globalThis.document = {
  getElementById: (id) => (elements[id] ??= makeEl()),
  querySelector: () => makeEl(),
  querySelectorAll: () => [],
  createElement: () => makeEl(),
};
const store = {};
globalThis.localStorage = {
  getItem: (k) => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
  removeItem: (k) => { delete store[k]; },
};
globalThis.fetch = async () => ({ ok: true, json: async () => ({}) });
globalThis.location = { hash: "#/" };
globalThis.alert = () => {};

// ---- load real source in-order ----
eval(readFileSync(new URL("../web/data/problems.js", import.meta.url), "utf8")); // window.ALGO
eval(readFileSync(new URL("../web/js/api.js", import.meta.url), "utf8"));        // window.API
eval(readFileSync(new URL("../web/js/visualizer.js", import.meta.url), "utf8")); // window.Visualizer
// app.js is an IIFE that calls render() at load; give it the globals it needs.
globalThis.API = window.API; globalThis.Visualizer = window.Visualizer;
eval(readFileSync(new URL("../web/js/app.js", import.meta.url), "utf8"));

let P = 0, F = 0;
const ok = (n, c) => { if (c) P++; else { F++; console.log("  ✗", n); } };
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function nav(hash) {
  globalThis.location.hash = hash;
  window.dispatchEvent ? null : null;
  // app.js listens on window hashchange; call its render via re-eval? Instead
  // we trigger by dispatching — but our stub ignores listeners. So re-run app.
  // Simpler: the app added a 'hashchange' listener; emulate by re-loading app render.
  await triggerRender();
  await sleep(20);
}

// Re-expose render by re-evaluating app.js each nav is heavy; instead capture
// render through the hashchange listener we DID capture:
let _render = null;
globalThis.window.addEventListener = (ev, fn) => { if (ev === "hashchange") _render = fn; };
// reload app.js now that addEventListener captures the listener
eval(readFileSync(new URL("../web/js/app.js", import.meta.url), "utf8"));
async function triggerRender() { if (_render) await _render(); }

// initial render already ran during load; ensure catalog present
ok("window.ALGO has 150 problems", window.ALGO.meta.total === 150);

const routes = ["#/", "#/tracker", "#/problems", "#/ds", "#/patterns", "#/revision", "#/about", "#/login", "#/p/two-sum", "#/p/3sum"];
for (const r of routes) {
  let threw = false;
  try { await nav(r); } catch (e) { threw = true; console.log("   error on", r, e.message); }
  ok(`route ${r} renders without throwing`, !threw);
  ok(`route ${r} populated #app`, elements.app._html.length > 100);
}

// specific content checks
await nav("#/"); ok("home shows hero", elements.app._html.includes("Crack DSA"));
await nav("#/tracker"); ok("tracker shows Day 1", elements.app._html.includes("Day 1"));
ok("tracker shows Day 30", elements.app._html.includes("Day 30"));
await nav("#/ds"); ok("DS notion renders groups", elements.app._html.includes("Notion · by Data Structure"));
await nav("#/patterns"); ok("pattern notion renders", elements.app._html.includes("Notion · by Pattern"));
await nav("#/about"); ok("about page renders", elements.app._html.includes("About Algolotl"));
await nav("#/login"); ok("login page renders", elements.app._html.includes("Welcome to Algolotl"));

// visualizer mount (two-sum has flagship frames)
await nav("#/p/two-sum");
ok("problem page has quickshot", elements.app._html.includes("Quick-shot"));
ok("problem page mounts viz container", elements.app._html.includes('id="viz-mount"'));
const vizEl = elements["viz-mount"];
ok("visualizer produced approach tabs", vizEl._html.includes("Brute Force") && vizEl._html.includes("Hash Map"));
ok("visualizer shows player", vizEl._html.includes("Play"));
ok("visualizer shows memory cards", vizEl._html.includes("Memory: what the program is holding"));
ok("visualizer shows what/why", vizEl._html.includes("What just happened") && vizEl._html.includes("Why it matters"));
ok("visualizer renders array cells", vizEl._html.includes("arrbox"));
ok("visualizer highlights a code line via Idea/steps", vizEl._html.includes("The idea in plain words"));

console.log(`\n${F === 0 ? "✅ ALL RENDER TESTS PASSED" : "❌ FAILURES"}: ${P} passed, ${F} failed`);
process.exit(F === 0 ? 0 : 1);
