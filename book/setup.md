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

## 3. A Lumen API key

[Lumen](https://lumen.ncsa.illinois.edu/chat) is the University of Illinois campus LLM service, run by NCSA. It is free with your Illinois account, so there is nothing to pay for.

1. Sign in at [lumen.ncsa.illinois.edu/chat](https://lumen.ncsa.illinois.edu/chat) with your Illinois account.
2. Open your [profile page](https://lumen.ncsa.illinois.edu/profile), scroll down to **API key**, and create one. Copy it now; it is shown once.
3. In Colab, open the **Secrets** panel (the key icon in the left sidebar), add a secret named `LUMEN_API_KEY`, paste the key, and enable notebook access.

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
| When | *To be announced* |
| Where | *To be announced* |
| Bring | A laptop, a charger, and the Colab from the previous chapter |

## Getting help

Open an issue on the [course repository](https://github.com/ashcastelinocs124/msba-ai-workshop) or ask in session.
