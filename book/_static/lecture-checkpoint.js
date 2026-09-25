// Lecture checkpoints: <div class="wk-lcp" data-spot="…" data-label="…"></div> in a chapter.
// On the campus copy the block asks /api/checkpoints/<spot> every 10 seconds, so when the instructor
// opens or closes it in /admin, the room sees it without reloading. The Pages copy has no server,
// so the block says where to go instead.
(() => {
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const head = (title, badge, cls) => `<div class="wk-lcp-t">Lecture checkpoint${title ? " · " + esc(title) : ""} <span class="wk-lcp-st ${cls}">${badge}</span></div>`;

  function closedView(s) {
    return head(s.title, "CLOSED", "closed") +
      `<p>Your instructor opens this during the session. It will appear here without reloading the page, and your answers are saved to your account.</p>`;
  }

  function openView(s) {
    const qs = s.questions.map((q, i) => {
      const mine = s.mine[i];
      const body = q.kind === "mc"
        ? q.choices.map((c, j) => `<label><input type="radio" name="q${i}" value="${j}"${mine === String(j) ? " checked" : ""}> ${esc(c)}</label>`).join("")
        : `<textarea name="q${i}" maxlength="1000" placeholder="Your answer">${esc(mine || "")}</textarea>`;
      return `<fieldset class="wk-lcp-q"><legend>${i + 1}. ${esc(q.prompt)}</legend>${body}</fieldset>`;
    }).join("");
    const answered = Object.keys(s.mine).length;
    return head(s.title, "OPEN", "open") + `<form>${qs}
      <div class="wk-lcp-row"><button type="submit" class="wk-lcp-btn">${answered ? "Update answers" : "Submit answers"}</button>
      <span class="wk-lcp-hint">You can change your answers until the checkpoint closes.</span></div><div class="wk-lcp-fb" aria-live="polite"></div></form>`;
  }

  function revealedView(s) {
    const scored = s.questions.map((q, i) => q.kind === "mc" && s.mine[i] != null ? +(s.mine[i] === String(q.correct)) : null).filter((x) => x != null);
    const badge = Object.keys(s.mine).length ? `CLOSED · ${scored.reduce((a, b) => a + b, 0)} OF ${scored.length} CORRECT` : "CLOSED";
    const why = (q) => q.explain ? `<div class="wk-lcp-why">${esc(q.explain)}</div>` : "";
    const rows = s.questions.map((q, i) => {
      const mine = s.mine[i];
      if (q.kind === "short") {
        return `<div class="wk-lcp-r"><b>${i + 1}. ${esc(q.prompt)}</b><br>${mine ? `Your answer: “${esc(mine)}” (short answer, not scored)` : "You did not answer."}${why(q)}</div>`;
      }
      const right = q.choices[q.correct];
      if (mine == null) return `<div class="wk-lcp-r"><b>${i + 1}. ${esc(q.prompt)}</b><br>Answer: ${esc(right)}. You did not answer.${why(q)}</div>`;
      const ok = mine === String(q.correct);
      return `<div class="wk-lcp-r ${ok ? "ok" : "no"}"><b>${i + 1}. ${esc(q.prompt)}</b><br>${ok ? `✓ ${esc(right)}` : `✗ You chose: ${esc(q.choices[+mine])}. Answer: ${esc(right)}.`}${why(q)}</div>`;
    }).join("");
    return head(s.title, badge, "done") + rows;
  }

  function mount(el) {
    const spot = el.dataset.spot;
    let key = null;
    const render = (s) => {
      // Re-render only when something the student sees has changed, so a half-typed answer survives each poll.
      const k = JSON.stringify([s.status, s.revealed, s.title, s.questions]);
      if (k === key) return;
      key = k;
      el.classList.toggle("open", s.status === "open");
      el.innerHTML = s.status === "open" ? openView(s) : s.revealed ? revealedView(s) : closedView(s);
      const form = el.querySelector("form");
      if (form) form.addEventListener("submit", (e) => submit(e, s, form));
    };
    async function submit(e, s, form) {
      e.preventDefault();
      const fb = form.querySelector(".wk-lcp-fb"), btn = form.querySelector("button");
      const answers = {};
      s.questions.forEach((q, i) => {
        if (q.kind === "mc") { const c = form.querySelector(`input[name=q${i}]:checked`); if (c) answers[i] = +c.value; }
        else { const t = form.querySelector(`textarea[name=q${i}]`).value.trim(); if (t) answers[i] = t; }
      });
      if (!Object.keys(answers).length) { fb.className = "wk-lcp-fb no"; fb.textContent = "Answer at least one question before submitting."; return; }
      btn.disabled = true;
      try {
        const r = await fetch(`/api/checkpoints/${encodeURIComponent(spot)}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ answers }) });
        const body = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(body.detail || "Could not save your answers. Try again.");
        const missing = s.questions.length - Object.keys(body.mine).length;
        fb.className = "wk-lcp-fb ok";
        fb.textContent = `Saved at ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}.` +
          (missing ? ` ${missing} question${missing > 1 ? "s" : ""} still unanswered.` : "") + " Correct answers appear here when your instructor closes the checkpoint.";
        btn.textContent = "Update answers";
      } catch (err) {
        fb.className = "wk-lcp-fb no"; fb.textContent = err.message;
        if (/closed/.test(err.message)) poll();
      }
      btn.disabled = false;
    }
    async function poll() {
      if (document.hidden || key === "pages") return;
      try {
        const r = await fetch(`/api/checkpoints/${encodeURIComponent(spot)}`, { headers: { accept: "application/json" } });
        if (!r.ok) throw new Error(r.status);
        render(await r.json());
      } catch (e) {
        if (key === null) {  // never reached the server: this is the public copy (or offline)
          key = "pages";
          el.innerHTML = head("", "CAMPUS COPY", "closed") +
            `<p>Lecture checkpoints run on the campus copy of this book, where you sign in with your Illinois account. <a href="${window.WK_CAMPUS_URL || ""}${location.pathname}">Open this page there</a>.</p>`;
          clearInterval(timer);
        }
      }
    }
    const timer = setInterval(poll, 10000);
    document.addEventListener("visibilitychange", poll);
    poll();
  }

  document.addEventListener("DOMContentLoaded", () => document.querySelectorAll(".wk-lcp[data-spot]").forEach(mount));
})();
