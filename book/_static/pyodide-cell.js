// Turns every code block tagged with :class: pyodide into an editable, runnable cell.
// Python runs in the browser via Pyodide; the modules in _static/py/ are preloaded
// so cells can `from agent import agent`, `from tools import TOOLS`, etc.
(() => {
  const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";
  const PY_FILES = ["mock_model.py", "tools.py", "agent.py", "docs.py"];
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

  async function run(cell) {
    const btn = cell.querySelector("button"), ta = cell.querySelector("textarea"), out = cell.querySelector(".wk-out");
    const status = (m) => { out.className = "wk-out show"; out.textContent = m; };
    btn.disabled = true; btn.textContent = "Running…";
    try {
      const py = await loadPyodideOnce(status);
      status("");
      let buf = "";
      py.setStdout({ batched: (s) => { buf += s + "\n"; out.textContent = buf; } });
      py.setStderr({ batched: (s) => { buf += s + "\n"; out.textContent = buf; } });
      await py.loadPackagesFromImports(ta.value);
      await py.runPythonAsync(ta.value);
      if (!buf) out.textContent = "(no output)";
    } catch (e) {
      out.className = "wk-out show err";
      out.textContent += "\n" + String(e).split("\n").filter((l) => !l.includes("pyodide")).slice(-12).join("\n");
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
      cell.innerHTML = '<div class="wk-bar"><span>python · runs in your browser</span><button type="button">▶ Run</button></div><textarea spellcheck="false"></textarea><pre class="wk-out"></pre>';
      cell.querySelector("textarea").value = code;
      cell.querySelector("textarea").rows = Math.min(30, code.split("\n").length + 1);
      cell.querySelector("button").addEventListener("click", () => run(cell));
      block.replaceChildren(cell);
    });
  });
})();
