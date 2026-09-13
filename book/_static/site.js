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
