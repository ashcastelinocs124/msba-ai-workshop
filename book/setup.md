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

Each chapter has an **Open in Colab** button. Colab is a free hosted Jupyter notebook. The notebooks call the real Anthropic API, which the in-page cells cannot do without exposing your key.

## 3. An Anthropic API key

1. Create an account at [console.anthropic.com](https://console.anthropic.com) and add a small credit balance. Five dollars covers the whole workshop.
2. Create a key under **API Keys**.
3. In Colab, open the **Secrets** panel (the key icon in the left sidebar), add a secret named `ANTHROPIC_API_KEY`, paste the key, and enable notebook access.

Every notebook reads the key with:

```python
from google.colab import userdata
import os
os.environ["ANTHROPIC_API_KEY"] = userdata.get("ANTHROPIC_API_KEY")
```

Never paste a key into a cell. Never commit one to a repository.

## Logistics

| | |
|---|---|
| When | *To be announced* |
| Where | *To be announced* |
| Bring | A laptop, a charger, and the Colab from the previous chapter |

## Getting help

Open an issue on the [course repository](https://github.com/ashcastelinocs124/msba-ai-workshop) or ask in session.
