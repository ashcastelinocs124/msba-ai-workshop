# Setup: Python, keys, Colab

You need three things. None of them require installing anything on your laptop.

## 1. A browser that can run the in-page cells

Every chapter has cells marked **▶ Run**. They execute Python in your browser using [Pyodide](https://pyodide.org). The first run downloads the runtime (about ten seconds); after that cells run instantly. Chrome, Edge, Firefox, and Safari all work.

Try it now:

```{code-block} python
:class: pyodide
import sys
print("Python", sys.version.split()[0], "is running in your browser.")
print(sum(range(1, 101)))
```

## 2. A Google account for Colab

Each chapter has an **Open in Colab** button. Colab is a free hosted Jupyter notebook. The notebooks call a real model through Lumen, which the in-page cells cannot do without exposing your key.

This walkthrough opens the chapter 1 notebook and adds your Lumen key to Colab's **Secrets** panel (step 4 below):

```{raw} html
<figure class="wk-intro-video">
  <video controls preload="metadata" poster="_static/media/setup-colab-secret-poster.jpg">
    <source src="_static/media/setup-colab-secret.mp4" type="video/mp4">
    <track kind="captions" src="_static/media/setup-colab-secret.vtt" srclang="en" label="English" default>
    Your browser cannot play this video. <a href="_static/media/setup-colab-secret.mp4">Download it</a> instead.
  </video>
  <figcaption>Setting up the Colab notebook · 44 s · captions on · <a href="_static/media/setup-colab-secret.mp4">Download the video</a></figcaption>
</figure>
```

## 3. A Lumen API key

[Lumen](https://lumen.ncsa.illinois.edu/chat) is the University of Illinois campus LLM service, run by NCSA. It is free with your Illinois account, so there is nothing to pay for.

Watch it once, then follow the steps. The key in the video is hidden on purpose; yours will be a long string starting with `sk_`.

```{raw} html
<figure class="wk-intro-video">
  <video controls preload="metadata" poster="_static/media/setup-lumen-key-poster.jpg">
    <source src="_static/media/setup-lumen-key.mp4" type="video/mp4">
    <track kind="captions" src="_static/media/setup-lumen-key.vtt" srclang="en" label="English" default>
    Your browser cannot play this video. <a href="_static/media/setup-lumen-key.mp4">Download it</a> instead.
  </video>
  <figcaption>Creating a Lumen API key and consenting to glm-5.3-flash · 54 s · captions on · <a href="_static/media/setup-lumen-key.mp4">Download the video</a></figcaption>
</figure>
```

1. Sign in at [lumen.ncsa.illinois.edu/chat](https://lumen.ncsa.illinois.edu/chat) with your Illinois account.
2. Open your [profile page](https://lumen.ncsa.illinois.edu/profile), scroll down to **API key**, and create one. Copy it now; it is shown once.
3. On Lumen's **Models** page, open **glm-5.3-flash**. If it asks you to consent to the model's use, accept; the key will not work with it until you do.
4. In Colab, open the **Secrets** panel (the key icon in the left sidebar), add a secret named `LUMEN_API_KEY`, paste the key, and enable notebook access.

Every notebook reads the key and opens a client with:

```python
import os
from google.colab import userdata
from openai import OpenAI

os.environ["LUMEN_API_KEY"] = userdata.get("LUMEN_API_KEY")
client = OpenAI(
    base_url="https://lumen.ncsa.illinois.edu/v1",
    api_key=os.environ["LUMEN_API_KEY"],
)
```

Lumen speaks the OpenAI API format, which is why the `openai` package is used. The model for this workshop is **`glm-5.3-flash`**: it is fast, handles tool calls well, and is the one every notebook is tested against. Use it unless a section says otherwise.

Never paste a key into a cell. Never commit one to a repository.

## Logistics

| | |
|---|---|
| When | Fridays, 1:30–3:30 pm (session 1 ran 1–3 pm) |
| Where | Business Instructional Facility (BIF); the room changes, see the schedule |
| Bring | A laptop, a charger, and the Colab from the previous chapter |

### Schedule

| Session | Date | Time | Room | Part | Chapters |
|---|---|---|---|---|---|
| 1 | Fri, Sep 18, 2026 | 1:00–3:00 pm | 3039 BIF | I · Agents | [1. Introduction to AI Agents](ch01-agent-loop.md) |
| 2 | Fri, Sep 25, 2026 | 1:30–3:30 pm | 3007 BIF | I · Agents | [2. Prompt Engineering](ch02-prompt-engineering.md) and [3. Context Engineering](ch03-context-engineering.md) |
| 3 | Fri, Oct 2, 2026 | 1:30–3:30 pm | 2043 BIF | I · Agents | [4. Memory Retrieval and RAG](ch04-memory-rag.md) |
| 4 | Fri, Oct 16, 2026 | 1:30–3:30 pm | 3007 BIF | II · Machine learning | [5. ML Foundations I](ch05-ml-foundations-1.md) |
| 5 | Fri, Oct 23, 2026 | 1:30–3:30 pm | 3007 BIF | II · Machine learning | [6. ML Foundations II](ch06-ml-foundations-2.md) |
| 6 | Fri, Oct 30, 2026 | 1:30–3:30 pm | 3007 BIF | III · Systems and decisions | [7. Agent Systems](ch07-agent-systems.md) |
| 7 | Fri, Nov 6, 2026 | 1:30–3:30 pm | 3007 BIF | III · Systems and decisions | [8. When to Use ML, Agents, or Neither](ch08-ml-agents-or-neither.md) |
| 8 | Fri, Nov 13, 2026 | 1:30–3:30 pm | 3007 BIF | IV · Finance | [9. Financial Markets and AI as an Investment Theme](ch09-markets-and-ai.md) |
| 9 | Fri, Dec 4, 2026 | 1:30–3:30 pm | 3007 BIF | IV · Finance | [10. AI for Financial and Investment Research](ch10-ai-investment-research.md) |

No sessions on Oct 9, Nov 20, or Nov 27. Most sessions are in 3007 BIF; sessions 1 and 3 are not.

## Getting help

Open an issue on the [course repository](https://github.com/ashcastelinocs124/msba-ai-workshop) or ask in session.
