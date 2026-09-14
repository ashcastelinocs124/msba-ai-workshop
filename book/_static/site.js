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

// Fullscreen is for reading: hide the left navigation while in it and restore it on exit
// (button or Esc), keeping a sidebar the reader had already closed closed.
(() => {
  let wasHidden = false;
  const onChange = () => {
    const sidebar = document.querySelector("#pst-primary-sidebar");
    const button = document.querySelector(".btn-fullscreen-button");
    if (!sidebar) return;
    const full = !!(document.fullscreenElement || document.webkitFullscreenElement);
    if (full) {
      wasHidden = sidebar.classList.contains("pst-sidebar-hidden");
      sidebar.classList.add("pst-sidebar-hidden");
    } else if (!wasHidden) {
      sidebar.classList.remove("pst-sidebar-hidden");
    }
    // Bootstrap moved the title attribute into data-bs-original-title when it built the tooltip.
    if (button) button.setAttribute("data-bs-original-title", full ? "Exit fullscreen" : "Fullscreen mode");
  };
  document.addEventListener("fullscreenchange", onChange);
  document.addEventListener("webkitfullscreenchange", onChange);
})();
