// Which copy of the book is this? The campus (Azure) copy answers /api/whoami; GitHub Pages does not.
window.WK_CAMPUS_URL = "https://dl-msba-workshop.azurewebsites.net";
window.WK_REPO = "https://github.com/ashcastelinocs124/msba-ai-workshop";

// Report button: a Bug / Feature-request dialog that opens a prefilled new-issue page on the
// repo in a new tab. The repo is public and the book has no server-side logging, so the reader
// reviews and submits the issue themselves; nothing is sent by the page.
function reportButton(slot) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "btn btn-sm pst-navbar-icon wk-report";
  btn.title = "Report a bug or suggest a feature";
  btn.innerHTML = '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M4.72.22a.75.75 0 0 1 1.06 0l1 .999a3.5 3.5 0 0 1 2.44 0l1-1a.75.75 0 1 1 1.06 1.061l-.83.828A3.49 3.49 0 0 1 11.5 4v.5h1.75a.75.75 0 0 1 0 1.5H11.5v1.02c.62.11 1.2.36 1.7.72l1.03-1.03a.75.75 0 1 1 1.06 1.06l-1.17 1.17c.19.48.31 1 .34 1.56h1.79a.75.75 0 0 1 0 1.5h-1.86a5 5 0 0 1-9.78 0H2.75a.75.75 0 0 1 0-1.5h1.79c.03-.56.15-1.08.34-1.56L3.71 8.27a.75.75 0 0 1 1.06-1.06L5.8 8.24c.5-.36 1.08-.61 1.7-.72V6H5.75a.75.75 0 0 1 0-1.5H7.5V4c0-.6.15-1.16.42-1.65L4.72 1.28a.75.75 0 0 1 0-1.06Z"/></svg><span>Report</span>';

  const dlg = document.createElement("dialog");
  dlg.className = "wk-report-dlg";
  dlg.innerHTML = `
    <form method="dialog">
      <div class="wk-title">/// Report</div>
      <h3>Something broken, or something you wish the book did?</h3>
      <div class="wk-seg">
        <label><input type="radio" name="kind" value="bug" checked> Bug</label>
        <label><input type="radio" name="kind" value="feature"> Feature request</label>
      </div>
      <textarea name="desc" rows="4" required minlength="10"></textarea>
      <p class="wk-meta">We'll attach the page you're on and your browser. Nothing about your account.</p>
      <div class="wk-row">
        <span class="wk-hint">Opens a prefilled issue on GitHub in a new tab. You review it there before submitting.</span>
        <button type="button" data-cancel>Cancel</button>
        <button type="submit" class="primary" disabled>Continue on GitHub</button>
      </div>
    </form>`;
  const form = dlg.querySelector("form"), desc = form.desc, submit = form.querySelector("[type=submit]");
  const placeholders = { bug: "What happened, and what did you expect?", feature: "What should the book do, and why would it help?" };
  const sync = () => { desc.placeholder = placeholders[form.kind.value]; submit.disabled = desc.value.trim().length < 10; };
  form.addEventListener("input", sync);
  dlg.querySelector("[data-cancel]").onclick = () => dlg.close();
  btn.onclick = () => { sync(); dlg.showModal(); desc.focus(); };

  form.onsubmit = () => {
    const bug = form.kind.value === "bug";
    const text = desc.value.trim();
    const m = navigator.userAgent.match(/(Edg|Firefox|Chrome|Safari)\/(\d+)/);
    const browser = `${m ? `${m[1] === "Edg" ? "Edge" : m[1]} ${m[2]}` : "unknown browser"} · ${navigator.platform}`;
    const body = [
      `**Type:** ${bug ? "Bug" : "Feature request"}`,
      `**Page:** ${location.href}`,
      `**Browser:** ${browser}`,
      "", "### What the reader reported", "",
      text.split("\n").map((l) => `> ${l}`).join("\n"),
      "", "<!-- Filed from the book's Report button. Add screenshots or steps below. -->",
    ].join("\n");
    const q = new URLSearchParams({ labels: `user-report,${bug ? "bug" : "enhancement"}`,
                                    title: `${bug ? "[Bug]" : "[Feature]"} ${text.replace(/\s+/g, " ").slice(0, 70)}`, body });
    window.open(`${window.WK_REPO}/issues/new?${q}`, "_blank", "noopener");
    form.reset();
  };

  slot.prepend(btn);
  document.body.append(dlg);
}

document.addEventListener("DOMContentLoaded", async () => {
  const slot = document.querySelector(".article-header-buttons") || document.querySelector("article");
  if (slot) reportButton(slot);
  let who = null;
  try {
    const r = await fetch("/api/whoami", { headers: { accept: "application/json" } });
    if (r.ok) who = await r.json();
  } catch (e) { /* offline or no proxy */ }
  if (who && slot) {
    const pill = document.createElement("span");
    pill.className = "wk-who";
    pill.innerHTML = `Signed in as <b>${who.name}</b> · ${who.used.toLocaleString()} / ${who.cap.toLocaleString()} tokens today · <a href="/.auth/logout">Sign out</a>`;
    slot.prepend(pill);
  }
  document.querySelectorAll(".wk-pages-only").forEach((el) => { el.hidden = !!who; });
  document.querySelectorAll(".wk-campus-only").forEach((el) => { el.hidden = !who; });
  document.querySelectorAll("a[data-campus]").forEach((a) => { a.href = window.WK_CAMPUS_URL + a.dataset.campus; });
});

// sphinx-book-theme binds its desktop sidebar toggle to the first .primary-toggle, which is
// the hidden mobile one, so the visible ☰ in the article header does nothing. Bind it here.
document.addEventListener("DOMContentLoaded", () => {
  const button = document.querySelector(".bd-header-article .primary-toggle, .header-article .primary-toggle");
  const sidebar = document.querySelector("#pst-primary-sidebar");
  if (!button || !sidebar) return;
  button.addEventListener("click", (e) => {
    if (!window.matchMedia("(min-width: 992px)").matches) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    sidebar.classList.toggle("pst-sidebar-hidden");
  }, true);
});
