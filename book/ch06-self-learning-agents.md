# 6. Building Self-Learning AI Agents

```{raw} html
<p class="wk-lede">Build agents that get better from experience: a harness that gives them feedback, memory of past runs, learning from rewards, and ways to measure whether they really improved.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch06-self-learning-agents.ipynb" target="_blank">▶ Open in Colab</a>
```

```{raw} html
:file: widgets/goal-map.html
```

On Monday the research agent writes Deere's annual revenue memo, using the calendar-year figure. Priya sends it back: "Firm uses fiscal year. Cite the 10-K." On Tuesday the agent writes Apple's memo and makes the same mistake. The feedback existed, but nothing kept it.

Chapters 1 to 3 gave the agent a loop that calls tools, instructions it reads on every call, and memory of clients and documents. None of that changes when the work goes badly. This chapter adds the part that does: a check on each piece of work, a lesson written from the failure, and a place to keep the lesson where the next task will read it.

- **[6.1 What Self-Learning Means](ch06-what-self-learning-means.md).** What counts as a self-improving agent, and the four places an agent can change, from a note in its prompt to new model weights.
- **[6.2 The Learning Harness](ch06-learning-harness.md).** Everything around the model. Add three steps after the task (grade, reflect, save) and the week's mistake happens once. Then the three trends that decide what harnesses look like next.
- **[6.3 Memory and Experience](ch06-memory-and-experience.md).** Four ways to keep a lesson: a reflection note, a skill library, a playbook edited in small steps, and "dreaming", a cleanup that runs while the agent is idle.
- **[6.4 For Reference: Long Inputs, Rewards and Evaluation](ch06-for-reference.md).** Self-study, as in the session: recursive language models for inputs too long to read, learning from rewards, and how to prove an agent really improved.

The cells run on the mock model and need no API key. The figures are illustrative, not market data. One Colab notebook covers 6.2 to 6.4 against a real model on Lumen.

Deep learning, which the plan once placed in this session, is now a self-paced item on the [schedule](schedule.md), to do on your own time.

(ch06-lecture)=
## Watch the lecture

The session 6 recording, covering 6.1 to 6.3 in class and pointing to 6.4 for self-study. The slides are linked below the video.

```{raw} html
<figure class="wk-intro-video">
  <iframe src="https://www.youtube.com/embed/BbT-xdsY3f8" title="Session 6 · Building Self-Learning AI Agents" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
  <figcaption>Session 6 · Building Self-Learning AI Agents · <a href="https://youtu.be/BbT-xdsY3f8">Open on YouTube</a> · <a href="https://github.com/ashcastelinocs124/Workshop-Slides/blob/main/AI/education/quantitative-analyst-course/workshop-6-self-learning-agents.pdf">Slides (PDF)</a></figcaption>
</figure>
```
