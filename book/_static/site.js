// Which copy of the book is this? The campus (Azure) copy answers /api/whoami; GitHub Pages does not.
window.WK_CAMPUS_URL = "https://dl-msba-workshop.azurewebsites.net";
document.addEventListener("DOMContentLoaded", async () => {
  const slot = document.querySelector(".article-header-buttons") || document.querySelector("article");
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
