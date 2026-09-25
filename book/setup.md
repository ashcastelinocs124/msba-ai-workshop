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

The chapter 1 notebook reads the key and opens a client with:

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

Lumen speaks the OpenAI API format, which is why the `openai` package is used (the next section explains why). The chapter 2 notebooks use LangChain's `ChatOpenAI` with the same `base_url` and key. The model for this workshop is **`glm-5.3-flash`**: it is fast, handles tool calls well, and is the one every notebook is tested against. Use it unless a section says otherwise.

Never paste a key into a cell. Never commit one to a repository.

## Why the OpenAI SDK

An **SDK** (software development kit) is a package of ready-made code for talking to a service. Without one, every model call means writing the web request by hand: the address, the headers, the JSON body, and parsing the reply. With the `openai` package it is one line, `client.chat.completions.create(...)`, and the reply comes back as a Python object.

```{raw} html
:file: widgets/setup-sdk-compare.html
```

The package is from OpenAI because OpenAI's API format became the common standard. Many other providers accept the same requests: open-model servers such as [vLLM](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html), cloud platforms such as Azure, and campus services. NCSA's Lumen is one of them. So the [`openai` package](https://github.com/openai/openai-python) is not tied to OpenAI's models. Point `base_url` at Lumen and the same code calls the models NCSA serves; point it somewhere else and nothing else changes. That is why this workshop uses it, and why LangChain's `ChatOpenAI` works with Lumen too.

OpenAI also publishes the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/), a separate package built on top of `openai` for agents that call tools over many steps: the loop chapter 1 writes by hand. This workshop writes that loop itself so you can see every step, but the Agents SDK is worth knowing once you build agents for real.

What an open-source model is, how it differs from a closed one, and how to run one on NCSA's GPUs are on {ref}`page 0C <open-closed-models>`.

## Logistics

| | |
|---|---|
| When | Fridays, 1:30–3:30 pm (session 1 ran 1–3 pm) |
| Where | Business Instructional Facility (BIF); the room changes, see the [schedule](schedule.md) |
| Bring | A laptop, a charger, and the Colab from the previous chapter |

## Getting help

Open an issue on the [course repository](https://github.com/ashcastelinocs124/msba-ai-workshop) or ask in session.
