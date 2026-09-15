// Turns every code block tagged with :class: pyodide into an editable, runnable cell.
// Python runs in the browser via Pyodide; the modules in _static/py/ are preloaded
// so cells can `from agent import agent`, `from tools import TOOLS`, etc.
(() => {
  const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";
  const PY_FILES = ["mock_model.py", "tools.py", "agent.py", "docs.py", "llm.py"];
  const BASE = document.currentScript.src.replace(/pyodide-cell\.js.*$/, "");
  let pyodidePromise = null;
  // The handbook, parsed out of docs.py's source once it is fetched — the Watch view's
  // Policy Handbook window shows the same passages the agent searched, from the same file.
  let HANDBOOK = [];

  function loadPyodideOnce(status) {
    if (pyodidePromise) return pyodidePromise;
    pyodidePromise = (async () => {
      status("Loading Python runtime (first time only, ~10s)…");
      await new Promise((res, rej) => {
        const s = document.createElement("script");
        s.src = PYODIDE_URL + "pyodide.js"; s.onload = res; s.onerror = rej;
        document.head.appendChild(s);
      });
      const py = await loadPyodide({ indexURL: PYODIDE_URL });
      for (const f of PY_FILES) {
        const src = await (await fetch(BASE + "py/" + f, { cache: "no-cache" })).text(); // revalidate: a stale module after a deploy would desync from this file
        py.FS.writeFile(f, src);
        if (f === "docs.py") HANDBOOK = [...src.matchAll(/"id":\s*"([^"]+)",\s*"text":\s*"([^"]+)"/g)].map((m) => ({ id: m[1], text: m[2] }));
      }
      return py;
    })();
    return pyodidePromise;
  }

  // ---- Watch view: the run replayed as a person doing the job at their workstation ----
  // A run's output is "step-shaped" when at least two lines look like "Step 1: ...". Every
  // agent-run cell in this book prints that way (see agent.py's narrate), so no per-cell
  // markup is needed. Each step is parsed from its own wording:
  //   "looked up financials (DE, Q2-2026) → name: Deere, revenue: 13,800,000,000, …"
  //   "searched docs (blackout …) → 3 matches found (personal-trading-2, …)"
  //   "answered — Deere revenue grew 6.4% …"   /   "stopped — the step budget ran out"
  // "get_" tools read as "looked up" and open the Firm Records app; "search_" tools read as
  // "searched" and open the Policy Handbook; the answer is typed into a memo and filed.
  const STEP_LINE = /^Step \d+:\s*/;
  const APPS = {
    lookup: { name: "Firm Records", short: "R", color: "#13294b", tint: "#eef1f7" },
    search: { name: "Policy Handbook", short: "H", color: "#3b6fd8", tint: "#eef4ff" },
    answer: { name: "Memo", short: "M", color: "#136c3a", tint: "#e8f7ee" },
  };

  function parseStep(text) {
    let m;
    if ((m = text.match(/^answered\s+[—-]\s*(.*)$/s))) return { kind: "answer", text: m[1] };
    if ((m = text.match(/^stopped\s+[—-]\s*(.*)$/s))) return { kind: "answer", text: "Stopped: " + m[1], stopped: true };
    m = text.match(/^(\S+(?: up)?)\s+(.+?)(?:\s+\((.*)\))?\s+→\s+(.*)$/s);
    if (!m) return { kind: "answer", text };
    const [, verb, subject, args = "", result] = m;
    const kind = /^searched/i.test(verb) ? "search" : "lookup";
    const step = { kind, verb, subject, args, result, error: /^nothing found/.test(result) };
    if (kind === "search") {
      const ids = (result.match(/\(([^)]*)\)/) || [, ""])[1];
      step.ids = ids ? ids.split(/,\s*/) : [];
    } else {
      // "field: value, field: value" — a fragment without ": " belongs to the previous value
      // (e.g. "role: senior analyst, industrials").
      step.rows = [];
      if (!step.error) result.split(", ").forEach((frag) => {
        const i = frag.indexOf(": ");
        if (i > 0) step.rows.push([frag.slice(0, i), frag.slice(i + 2)]);
        else if (step.rows.length) step.rows[step.rows.length - 1][1] += ", " + frag;
      });
    }
    return step;
  }

  // What the agent decided, in the first person — derived from the step, never invented.
  function decision(step, i, n) {
    if (step.kind === "search") return `Check what the handbook says about: ${step.args}.`;
    if (step.kind === "lookup") return `${i === 0 ? "I can't answer this from memory. " : ""}Pull the ${step.subject}${step.args ? ` for ${step.args}` : ""}.`;
    if (step.stopped) return "I've used every step I was allowed. Stop and say so.";
    return n === 1 ? "I can answer this from what I already know." : "I have what I need. Write it up and file it.";
  }

  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const title = (s) => s.replace(/\b\w/g, (c) => c.toUpperCase());
  const sectionOf = (id) => title(id.replace(/-\d+$/, "").replace(/-/g, " "));

  function setWatchSteps(cell, text) {
    const lines = text.split("\n").filter((l) => STEP_LINE.test(l));
    const btn = cell.querySelector('.wk-seg [data-v="watch"]');
    btn.disabled = lines.length < 2;
    btn.title = btn.disabled ? "This output isn't step-shaped" : "";
    cell._steps = lines.map((l) => parseStep(l.replace(STEP_LINE, "")));
    return !btn.disabled;
  }

  function showView(cell, view) {
    cell.querySelectorAll(".wk-seg button").forEach((b) => b.classList.toggle("on", b.dataset.v === view));
    cell.querySelector(".wk-out").style.display = view === "text" ? "block" : "none";
    cell.querySelector(".wk-watch").style.display = view === "watch" ? "block" : "none";
  }

  // One player per cell. `wait` honours the speed toggle and collapses to zero while jumping.
  function makePlayer(cell) {
    const $ = (sel) => cell.querySelector(sel);
    const ws = $(".wk-ws"), cur = $(".wk-cursor");
    const p = { i: -1, playing: true, speed: 1, token: 0, instant: false };
    let timer = null;
    const wait = (ms) => p.instant ? Promise.resolve() : new Promise((r) => { timer = setTimeout(r, ms / p.speed); });
    const moveTo = (x, y) => { cur.style.transform = `translate(${x}px,${y}px)`; };
    const at = (el, dx, dy) => { const w = ws.getBoundingClientRect(), r = el.getBoundingClientRect(); return [r.left - w.left + dx, r.top - w.top + dy]; };
    const click = async () => { cur.classList.add("click"); await wait(250); cur.classList.remove("click"); };
    const typeInto = async (el, text) => {
      el.classList.add("focus");
      const per = Math.min(38, 1200 / Math.max(1, text.length));
      for (let i = 1; i <= text.length; i++) { el.innerHTML = esc(text.slice(0, i)) + '<span class="wk-caret"></span>'; await wait(per); }
      await wait(200); el.classList.remove("focus"); el.textContent = text;
    };
    const say = async (text) => { $(".wk-think span").textContent = text; $(".wk-think").classList.add("show"); await wait(1200); };
    const openApp = async (kind) => {
      const app = $(`.wk-app[data-k="${kind}"]`), win = $(`.wk-win[data-k="${kind}"]`);
      moveTo(...at(app, 20, 20)); await wait(900); app.classList.add("hint"); await click();
      app.classList.add("bounce", "open"); await wait(400);
      cell.querySelectorAll(".wk-win.show").forEach((w) => w.classList.add("back"));
      win.classList.remove("back"); win.classList.add("show"); app.classList.remove("bounce", "hint");
      $(".wk-think").classList.remove("show");
      await wait(300);
    };
    const chip = (i, step) => {
      const c = document.createElement("span");
      c.className = "wk-chip"; c.style.setProperty("--k-color", APPS[step.kind].color); c.style.setProperty("--k-tint", APPS[step.kind].tint);
      const label = step.kind === "answer" ? step.text : `${step.verb} ${step.subject}${step.args ? ` (${step.args})` : ""}`;
      c.innerHTML = `<span class="n">${i + 1}</span>${esc(label.length > 60 ? label.slice(0, 57) + "…" : label)}`;
      c.title = step.kind === "answer" ? step.text : `${label} → ${step.result}`;
      c.addEventListener("click", () => jumpTo(i));
      $(".wk-wlog").appendChild(c);
    };

    async function runLookup(step) {
      const win = $('.wk-win[data-k="lookup"]');
      win.querySelector(".wk-wt").textContent = `Firm Records — ${title(step.subject)}`;
      await openApp("lookup");
      const field = win.querySelector(".wk-field");
      moveTo(...at(field, 30, 8)); await wait(600); await click();
      await typeInto(field, step.args || step.subject);
      const go = win.querySelector(".wk-go");
      moveTo(...at(go, 18, 10)); await wait(450); go.classList.add("press"); await click(); go.classList.remove("press");
      const body = win.querySelector(".wk-wbody");
      if (step.error) { body.innerHTML = `<div class="wk-rec-err">${esc(step.result)}</div>`; await wait(600); return; }
      body.innerHTML = '<div class="wk-rec">' + step.rows.map(([k, v]) => `<div class="row">${esc(title(k))}</div><div class="row"><b>${esc(v)}</b></div>`).join("") + "</div>";
      for (const r of body.querySelectorAll(".row")) { r.classList.add("show"); await wait(70); }
      await wait(700);
    }
    async function runSearch(step) {
      const win = $('.wk-win[data-k="search"]');
      await openApp("search");
      const field = win.querySelector(".wk-field");
      moveTo(...at(field, 40, 8)); await wait(600); await click();
      await typeInto(field, step.args || step.subject);
      const go = win.querySelector(".wk-go");
      moveTo(...at(go, 18, 10)); await wait(450); go.classList.add("press"); await click(); go.classList.remove("press");
      const cnt = win.querySelector(".wk-cnt");
      cnt.style.display = ""; cnt.textContent = step.ids.length ? `${step.ids.length} match${step.ids.length === 1 ? "" : "es"}` : "no matches";
      const doc = win.querySelector(".wk-hb-doc");
      for (const id of step.ids) {
        const para = doc.querySelector(`[data-id="${id}"]`);
        if (!para) continue;
        para.innerHTML = `<mark>${esc(para.textContent)}</mark>`;
        win.querySelectorAll(".wk-hb-toc div").forEach((d) => d.classList.toggle("on", d.textContent === sectionOf(id)));
        para.scrollIntoView({ block: "nearest" });
        await wait(350);
      }
      await wait(800);
    }
    async function runAnswer(step) {
      const win = $('.wk-win[data-k="answer"]');
      win.querySelector(".wk-stamp").textContent = step.stopped ? "STOPPED" : "FILED";
      await openApp("answer");
      const body = win.querySelector(".wk-memo-body");
      moveTo(...at(body, 60, 18)); await wait(500); await click();
      const text = step.text, per = Math.min(16, 2500 / Math.max(1, text.length));
      for (let i = 1; i <= text.length; i++) { body.innerHTML = esc(text.slice(0, i)) + '<span class="wk-caret"></span>'; await wait(per); }
      body.textContent = text;
      const send = win.querySelector(".wk-send");
      moveTo(...at(send, 30, 10)); await wait(500); send.classList.add("press"); await click(); send.classList.remove("press");
      win.querySelector(".wk-stamp").classList.add("show");
      await wait(400);
    }

    function reset() {
      clearTimeout(timer); p.token++; p.i = -1;
      cell.querySelectorAll(".wk-win").forEach((w) => w.classList.remove("show", "back"));
      cell.querySelectorAll(".wk-app").forEach((a) => a.classList.remove("open", "hint", "bounce"));
      cell.querySelectorAll(".wk-field").forEach((f) => { f.textContent = ""; f.classList.remove("focus"); });
      cell.querySelectorAll(".wk-go, .wk-send").forEach((b) => b.classList.remove("press"));
      $(".wk-think").classList.remove("show"); $(".wk-stamp").classList.remove("show");
      $('.wk-win[data-k="lookup"] .wk-wbody').innerHTML = '<div class="wk-hint">No record open.</div>';
      $(".wk-cnt").style.display = "none";
      $(".wk-hb-doc").querySelectorAll("p").forEach((q) => (q.textContent = q.textContent));
      $(".wk-hb-toc").querySelectorAll("div").forEach((d) => d.classList.remove("on"));
      $(".wk-memo-body").textContent = ""; $(".wk-wlog").innerHTML = "";
      moveTo(ws.clientWidth / 2, ws.clientHeight / 2);
      progress();
    }
    function progress(note) {
      const n = (cell._steps || []).length;
      $(".wk-wprogress").textContent = p.i < 0 ? `Ready — ${n} step${n === 1 ? "" : "s"}` : note || `Step ${p.i + 1} of ${n} · ${p.playing ? "playing" : "paused"}`;
      $(".wk-pause").textContent = p.playing ? "⏸ Pause" : "▶ Play";
      $(".wk-next").disabled = p.i >= n - 1;
    }
    async function play(i) {
      const steps = cell._steps || [], my = p.token;
      if (i >= steps.length) return;
      p.i = i; progress();
      const step = steps[i];
      await say(decision(step, i, steps.length));
      if (my !== p.token) return;
      await (step.kind === "search" ? runSearch : step.kind === "lookup" ? runLookup : runAnswer)(step);
      if (my !== p.token) return;
      cell.querySelectorAll(".wk-chip").forEach((c) => c.classList.remove("cur"));
      chip(i, step); $(".wk-wlog").lastChild.classList.add("cur");
      if (i === steps.length - 1) { progress(`Done — ${steps.length} step${steps.length === 1 ? "" : "s"}`); return; }
      if (p.playing) play(i + 1); else progress();
    }
    // Jump: replay everything before step i instantly, then play step i paused.
    async function jumpTo(i) {
      reset(); p.playing = false; p.instant = true;
      for (let k = 0; k < i; k++) { p.i = k; const s = cell._steps[k]; await (s.kind === "search" ? runSearch : s.kind === "lookup" ? runLookup : runAnswer)(s); chip(k, s); }
      p.instant = false; $(".wk-think").classList.remove("show");
      play(i);
    }
    p.start = () => { reset(); p.playing = true; setTimeout(() => play(0), 200); };
    $(".wk-replay").addEventListener("click", p.start);
    $(".wk-pause").addEventListener("click", () => { p.playing = !p.playing; progress(); if (p.playing && p.i < cell._steps.length - 1 && !$(".wk-think").classList.contains("show")) play(p.i + 1); });
    $(".wk-next").addEventListener("click", () => { p.playing = false; progress(); if (p.i < cell._steps.length - 1) play(p.i + 1); });
    cell.querySelectorAll(".wk-speed").forEach((b) => b.addEventListener("click", () => {
      cell.querySelectorAll(".wk-speed").forEach((x) => x.classList.remove("on")); b.classList.add("on"); p.speed = +b.dataset.s;
    }));
    p.reset = reset;
    return p;
  }

  function fillHandbook(cell) {
    const toc = cell.querySelector(".wk-hb-toc"), doc = cell.querySelector(".wk-hb-doc");
    if (doc.children.length || !HANDBOOK.length) return;
    const sections = [...new Set(HANDBOOK.map((d) => sectionOf(d.id)))];
    toc.innerHTML = sections.map((s) => `<div>${esc(s)}</div>`).join("");
    doc.innerHTML = sections.map((s) => `<h5>${esc(s)}</h5>` + HANDBOOK.filter((d) => sectionOf(d.id) === s).map((d) => `<p data-id="${esc(d.id)}">${esc(d.text)}</p>`).join("")).join("");
  }

  const WATCH_HTML = `
    <div class="wk-wtop"><div class="wk-wprogress"></div>
      <div class="wk-wctl"><button type="button" class="primary wk-pause">⏸ Pause</button><button type="button" class="wk-next">Step ▶</button><button type="button" class="wk-replay">Replay</button><button type="button" class="wk-speed on" data-s="1">1×</button><button type="button" class="wk-speed" data-s="2">2×</button></div></div>
    <div class="wk-ws">
      <div class="wk-menubar"><span>Champaign Capital Research</span><span>File</span><span>Edit</span><span>View</span><span class="sp"></span><span class="wk-clock"></span></div>
      <div class="wk-think"><small>The agent decides</small><span></span></div>
      <div class="wk-win" data-k="lookup" style="left:4%;top:34px;width:62%">
        <div class="wk-tb"><span class="dots"><i></i><i></i><i></i></span><span class="wk-wt">Firm Records</span></div>
        <div class="wk-wbar"><span class="lbl">Look up</span><div class="wk-field"></div><button type="button" class="wk-go">Open</button></div>
        <div class="wk-wbody"><div class="wk-hint">No record open.</div></div></div>
      <div class="wk-win" data-k="search" style="left:16%;top:30px;width:70%">
        <div class="wk-tb"><span class="dots"><i></i><i></i><i></i></span><span class="wk-wt">Policy Handbook — Champaign Capital Research</span></div>
        <div class="wk-wbar"><span class="lbl">Find</span><div class="wk-field"></div><button type="button" class="wk-go">Search</button><span class="wk-cnt" style="display:none"></span></div>
        <div class="wk-hb"><div class="wk-hb-toc"></div><div class="wk-hb-doc"></div></div></div>
      <div class="wk-win" data-k="answer" style="left:28%;top:44px;width:60%">
        <div class="wk-tb"><span class="dots"><i></i><i></i><i></i></span><span class="wk-wt">Memo — new</span></div>
        <div class="wk-memo"><div class="hd"><span>To:</span><b>The person who asked</b></div><div class="hd"><span>From:</span><b>Research assistant</b></div>
          <div class="wk-memo-body"></div><div class="foot"><button type="button" class="wk-send">File it</button></div></div>
        <div class="wk-stamp">FILED</div></div>
      <div class="wk-dock">
        <div class="wk-app" data-k="lookup" style="--a:#2e4f8f;--b:#13294b">R<span class="lb">Firm Records</span></div>
        <div class="wk-app" data-k="search" style="--a:#5b8de8;--b:#2b5cc4">H<span class="lb">Policy Handbook</span></div>
        <div class="wk-app" data-k="answer" style="--a:#2fa86a;--b:#136c3a">M<span class="lb">Memo</span></div>
        <div class="wk-app" style="--a:#8d95a8;--b:#5a6478">✉<span class="lb">Mail</span></div>
        <div class="wk-app" style="--a:#e46a6a;--b:#b13a3a">${new Date().getDate()}<span class="lb">Calendar</span></div>
      </div>
      <svg class="wk-cursor" viewBox="0 0 18 18"><path d="M2 1l13 8.5-6 1.2L12 17l-2.5 1-3-6.3L2 15z" fill="#fff" stroke="#000" stroke-width="1.1" stroke-linejoin="round"/></svg>
    </div>
    <div class="wk-wlog"></div>`;

  async function run(cell) {
    const btn = cell.querySelector(".wk-run"), ta = cell.querySelector("textarea"), out = cell.querySelector(".wk-out");
    const status = (m) => { out.className = "wk-out show"; out.textContent = m; };
    btn.disabled = true; btn.textContent = "Running…";
    cell._player.reset();
    showView(cell, "text");
    try {
      const py = await loadPyodideOnce(status);
      status("");
      let buf = "";
      py.setStdout({ batched: (s) => { buf += s + "\n"; out.textContent = buf; } });
      py.setStderr({ batched: (s) => { buf += s + "\n"; out.textContent = buf; } });
      await py.loadPackagesFromImports(ta.value);
      await py.runPythonAsync(ta.value);
      if (!buf) buf = "(no output)";
      out.textContent = buf;
      if (setWatchSteps(cell, buf)) {
        // Step-shaped output: Watch is the default — a person doing the job, one step at a time.
        fillHandbook(cell);
        cell.querySelector(".wk-clock").textContent = new Date().toLocaleString(undefined, { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
        showView(cell, "watch");
        cell._player.start();
      }
    } catch (e) {
      out.className = "wk-out show err";
      out.textContent += "\n" + String(e).split("\n").filter((l) => !l.includes("pyodide")).slice(-12).join("\n");
      setWatchSteps(cell, "");
    } finally {
      btn.disabled = false; btn.textContent = "▶ Run";
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("div.pyodide").forEach((block) => {
      const pre = block.querySelector("pre");
      if (!pre) return;
      const code = pre.textContent.replace(/\n$/, "");
      const cell = document.createElement("div");
      cell.className = "wk-cell";
      cell.innerHTML = '<div class="wk-bar"><span>python · runs in your browser</span>'
        + '<div class="wk-bar-right"><div class="wk-seg"><button type="button" class="on" data-v="text">Text</button><button type="button" data-v="watch" disabled>Watch</button></div>'
        + '<button type="button" class="wk-run">▶ Run</button></div></div>'
        + '<textarea spellcheck="false"></textarea><pre class="wk-out"></pre>'
        + '<div class="wk-watch">' + WATCH_HTML + "</div>";
      cell.querySelector("textarea").value = code;
      cell.querySelector("textarea").rows = Math.min(30, code.split("\n").length + 1);
      cell.querySelector(".wk-run").addEventListener("click", () => run(cell));
      cell.querySelectorAll(".wk-seg button").forEach((b) => b.addEventListener("click", () => { if (!b.disabled) showView(cell, b.dataset.v); }));
      cell._player = makePlayer(cell);
      block.replaceChildren(cell);
    });
  });
})();
