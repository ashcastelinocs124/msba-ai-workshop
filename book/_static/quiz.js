// Checkpoint quizzes. Markup:
// <div class="quiz" data-answer="b" data-ok="Correct because…" data-no="Not quite…">
//   <p class="q">Question?</p>
//   <label><input type="radio" name="q1" value="a"> …</label> …
//   <div class="fb"></div>
// </div>
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".quiz").forEach((quiz) => {
    const fb = quiz.querySelector(".fb");
    quiz.querySelectorAll("input[type=radio]").forEach((r) => {
      r.addEventListener("change", () => {
        const ok = r.value === quiz.dataset.answer;
        fb.className = "fb " + (ok ? "ok" : "no");
        fb.textContent = ok ? quiz.dataset.ok : quiz.dataset.no;
      });
    });
  });
});
