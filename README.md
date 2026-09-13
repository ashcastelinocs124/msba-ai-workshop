# AI, ML, and Financial Markets Workshop Series

An interactive textbook for the Gies MSBA workshop series. Nine chapters in four parts:

| Part | Chapters |
|---|---|
| I · Agents | 1 Agent Loop and Tool API Design · 2 Prompt and Context Engineering · 3 Memory Retrieval and RAG |
| II · Machine learning | 4 ML Foundations I · 5 ML Foundations II |
| III · Systems and decisions | 6 Agent Systems · 7 When to Use ML, Agents, or Neither |
| IV · Finance | 8 Financial Markets and AI as an Investment Theme · 9 AI for Financial and Investment Research |

Every chapter has runnable Python cells that execute in the browser (Pyodide, no server), one interactive explainer widget, a checkpoint quiz, and a Colab notebook for the exercise against the real Anthropic API.

## Layout

```
book/               Jupyter Book source
  _config.yml       title, theme, JS/CSS hooks
  _toc.yml          parts and chapter order
  chNN-*.md         chapters (MyST markdown)
  widgets/*.html    one self-contained interactive widget per chapter
  _static/
    pyodide-cell.js turns `{code-block} python :class: pyodide` blocks into ▶ Run cells
    quiz.js         checkpoint quizzes
    custom.css      theme accents and widget/cell/quiz styles
    py/*.py         modules the in-page cells can import (agent, tools, mock_model, docs)
notebooks/          Colab notebooks, one per chapter
```

## Build locally

```bash
uv tool install --python 3.12 "jupyter-book<2"   # once
jupyter-book build book
cd book/_build/html && python3 -m http.server 8791
```

Open http://127.0.0.1:8791. Serve over HTTP rather than opening the file directly; the runnable cells fetch the Python modules from `_static/py/`.

## Deploy

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds the book and publishes it to GitHub Pages. In the repository settings, set Pages → Source to **GitHub Actions** once.

## Editing a chapter

- Runnable cell: a fenced `{code-block} python` with `:class: pyodide`. Allowed imports are the standard library, numpy, pandas, scikit-learn, and the modules in `_static/py/`.
- Widget: write `book/widgets/chNN-name.html` and embed it with a `{raw} html` block using `:file:`.
- Quiz: a `<div class="quiz" data-answer="b" data-ok="…" data-no="…">` block; see any chapter's Checkpoint.
- Notebook: `notebooks/chNN-*.ipynb`; the chapter's Colab button links to it on `main`.
