// Turns every code block tagged with :class: pyodide into an editable, runnable cell.
// Python runs in the browser via Pyodide; the modules in _static/py/ are preloaded
// so cells can `from agent import agent`, `from tools import TOOLS`, etc.
(() => {
  const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";
  const PY_FILES = ["mock_model.py", "tools.py", "agent.py", "docs.py", "llm.py"];
  const BASE = document.currentScript.src.replace(/pyodide-cell\.js.*$/, "");
  let pyodidePromise = null;

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
        const src = await (await fetch(BASE + "py/" + f)).text();
        py.FS.writeFile(f, src);
      }
      return py;
    })();
    return pyodidePromise;
  }

  // A run's output is "step-shaped" when at least two lines look like "Step 1: ...". Every
  // agent-run cell in this book already prints that way (see agent.py's narrate/verbose
  // logging), so this needs no per-cell markup — it just works everywhere that format appears.
  const STEP_LINE = /^Step \d+:\s*/;

  // Each step is categorized from its own wording alone (not from any Python-side metadata),
  // so this keeps working for any future chapter's tools with zero wiring. One small icon
  // and color per category makes the sequence scannable at a glance instead of a wall of text.
  const STEP_KINDS = {
    lookup: { test: /^looked up/i, color: "#13294b", tint: "#eef1f7",
      icon: '<circle cx="10" cy="10" r="6" fill="none" stroke="currentColor" stroke-width="2"/><line x1="15" y1="15" x2="20" y2="20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>' },
    search: { test: /^searched/i, color: "#3b6fd8", tint: "#eef4ff",
      icon: '<rect x="5" y="3" width="14" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><line x1="8" y1="8" x2="16" y2="8" stroke="currentColor" stroke-width="2"/><line x1="8" y1="12" x2="16" y2="12" stroke="currentColor" stroke-width="2"/><line x1="8" y1="16" x2="13" y2="16" stroke="currentColor" stroke-width="2"/>' },
    answer: { test: /^answered/i, color: "#136c3a", tint: "#e8f7ee",
      icon: '<path d="M4 12a8 8 0 1 1 3 6.2L4 20l1.6-3.4A8 8 0 0 1 4 12z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 12l2 2 4-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' },
    other: { test: /.*/, color: "#5a6478", tint: "#f5f6f9",
      icon: '<circle cx="12" cy="12" r="3" fill="currentColor"/>' },
  };

  function stepKind(text) {
    return Object.keys(STEP_KINDS).find((k) => STEP_KINDS[k].test.test(text)) || "other";
  }

  function setGraphSteps(cell, text) {
    const lines = text.split("\n").filter((l) => STEP_LINE.test(l));
    const seg = cell.querySelector(".wk-seg"), graphBtn = seg.querySelector('[data-v="graph"]');
    graphBtn.disabled = lines.length < 2;
    graphBtn.title = graphBtn.disabled ? "This output isn't step-shaped" : "";
    cell._steps = lines.map((l) => l.replace(STEP_LINE, ""));
    renderGraph(cell);
  }

  function renderGraph(cell) {
    const track = cell.querySelector(".wk-gtrack");
    track.innerHTML = "";
    (cell._steps || []).forEach((s, i) => {
      const kind = STEP_KINDS[stepKind(s)];
      const item = document.createElement("div");
      item.className = "wk-gitem"; item.dataset.i = i;
      item.style.setProperty("--k-color", kind.color);
      item.style.setProperty("--k-tint", kind.tint);
      const last = i === (cell._steps.length - 1);
      item.innerHTML =
        `<div class="wk-grail"><div class="wk-gdot"><svg viewBox="0 0 24 24">${kind.icon}</svg></div>${last ? "" : '<div class="wk-gline"></div>'}</div>` +
        `<div class="wk-gcard"><span class="wk-glabel">Step ${i + 1}</span>${s}</div>`;
      item.addEventListener("click", () => showGraphStep(cell, i));
      track.appendChild(item);
    });
    cell._cur = -1;
    updateGraphChrome(cell);
  }

  function showGraphStep(cell, i) {
    cell._cur = i;
    cell.querySelectorAll(".wk-gitem").forEach((n, idx) => {
      n.classList.toggle("done", idx <= i);
      n.classList.toggle("cur", idx === i);
    });
    updateGraphChrome(cell);
  }

  function updateGraphChrome(cell) {
    const total = (cell._steps || []).length;
    cell.querySelector(".wk-gprogress").textContent =
      total === 0 ? "" : cell._cur < 0 ? `Ready — ${total} step${total === 1 ? "" : "s"}` : `Step ${cell._cur + 1} of ${total}`;
    cell.querySelector(".wk-gstep").disabled = cell._cur >= total - 1;
  }

  function wireGraphToggle(cell) {
    const seg = cell.querySelector(".wk-seg");
    seg.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
      if (b.disabled) return;
      seg.querySelectorAll("button").forEach((x) => x.classList.remove("on"));
      b.classList.add("on");
      const graph = b.dataset.v === "graph";
      cell.querySelector(".wk-out").style.display = graph ? "none" : "block";
      cell.querySelector(".wk-graph").style.display = graph ? "block" : "none";
    }));
    cell.querySelector(".wk-gstep").addEventListener("click", () => {
      if (cell._cur < (cell._steps || []).length - 1) showGraphStep(cell, cell._cur + 1);
    });
    cell.querySelector(".wk-greset").addEventListener("click", () => renderGraph(cell));
  }

  async function run(cell) {
    const btn = cell.querySelector(".wk-bar > .wk-bar-right > button:last-child"), ta = cell.querySelector("textarea"), out = cell.querySelector(".wk-out");
    const status = (m) => { out.className = "wk-out show"; out.textContent = m; };
    btn.disabled = true; btn.textContent = "Running…";
    // Text is the safe default on every run — a fresh run is a new sequence, and Text always
    // applies whether or not this run turns out to be step-shaped.
    const seg = cell.querySelector(".wk-seg");
    seg.querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.v === "text"));
    cell.querySelector(".wk-graph").style.display = "none";
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
      setGraphSteps(cell, buf);
    } catch (e) {
      out.className = "wk-out show err";
      out.textContent += "\n" + String(e).split("\n").filter((l) => !l.includes("pyodide")).slice(-12).join("\n");
      setGraphSteps(cell, "");
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
        + '<div class="wk-bar-right"><div class="wk-seg"><button type="button" class="on" data-v="text">Text</button><button type="button" data-v="graph" disabled>Graph</button></div>'
        + '<button type="button">▶ Run</button></div></div>'
        + '<textarea spellcheck="false"></textarea><pre class="wk-out"></pre>'
        + '<div class="wk-graph"><div class="wk-gprogress"></div><div class="wk-gtrack"></div>'
        + '<div class="wk-gctl"><button type="button" class="primary wk-gstep">Step ▶</button><button type="button" class="wk-greset">Reset</button></div></div>';
      cell.querySelector("textarea").value = code;
      cell.querySelector("textarea").rows = Math.min(30, code.split("\n").length + 1);
      cell.querySelector(".wk-bar button:not(.wk-seg button)").addEventListener("click", () => run(cell));
      wireGraphToggle(cell);
      block.replaceChildren(cell);
    });
  });
})();
