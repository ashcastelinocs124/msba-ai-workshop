# AI, ML, and Financial Markets Workshop Series

An interactive textbook for the Gies MSBA workshop series. Ten chapters in five parts:

| Part | Chapters |
|---|---|
| 0 · Foundations | 0 How Large Language Models Work (tokens, next-token prediction, open vs closed models) |
| I · Agents | 1 Introduction to AI Agents (what an agent is, the loop, tool design) · 2 Prompt and Context Engineering · 3 Memory Retrieval and RAG |
| II · Machine learning | 4 ML Foundations I · 5 ML Foundations II |
| III · Systems and decisions | 6 Agent Systems · 7 When to Use ML, Agents, or Neither |
| IV · Finance | 8 Financial Markets and AI as an Investment Theme · 9 AI for Financial and Investment Research |

Every chapter is set at a fictional equity research firm, Champaign Capital Research (see `book/the-firm.md`), and has runnable Python cells that execute in the browser (Pyodide, no server), one interactive explainer widget, a checkpoint quiz, and a Colab notebook for the exercise against a real model on Lumen, the campus LLM service.

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

## Two copies, one push

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds the book once and deploys it twice:

| Copy | URL | Who | Model cells |
|---|---|---|---|
| Public | https://ashcastelinocs124.github.io/msba-ai-workshop/ | anyone | mock model only; model cells link to the campus copy |
| Campus | https://dl-msba-workshop.azurewebsites.net/ | @illinois.edu sign-in (Entra) | run against gpt-5-mini on Azure AI Foundry via `/api/chat` |

The campus copy is the same static site served by a small FastAPI app (`app/main.py`) that adds two routes: `/api/whoami` (signed-in user and today's token use) and `/api/chat`, a proxy that holds the Foundry key (an App Service setting that references Key Vault), fixes the model deployment server-side, caps `max_completion_tokens` and a per-student daily token budget, and forwards to the Foundry `/openai/v1/chat/completions` endpoint. The browser never sees a key. In-page cells reach the model with `from llm import azure_model`, a drop-in for the mock model that the chapter 1 loop accepts as `model=`.

Azure resources (resource group `DL_ResourceGroup_01`): web app `dl-msba-workshop` on the shared plan `dl-appplan-01`, Foundry account `dl-foundry-msba-workshop` (deployment `gpt-5-mini`), Key Vault `dl-kv-msba-workshop`. The Azure deploy job needs the repo secret `AZURE_PUBLISH_PROFILE` (the app's publish profile); until it exists that job fails without failing the workflow.

Run the proxy test:

```bash
uv run --with fastapi --with httpx --with pytest -q python -m pytest app/test_main.py
```

## Editing a chapter

- Runnable cell: a fenced `{code-block} python` with `:class: pyodide`. Allowed imports are the standard library, numpy, pandas, scikit-learn, and the modules in `_static/py/`.
- Widget: write `book/widgets/chNN-name.html` and embed it with a `{raw} html` block using `:file:`.
- Quiz: a `<div class="quiz" data-answer="b" data-ok="…" data-no="…">` block; see any chapter's Checkpoint.
- Notebook: `notebooks/chNN-*.ipynb`; the chapter's Colab button links to it on `main`.
