# 0C Open-Source and Closed-Source Models

```{raw} html
<p class="wk-lede">Once a model is trained, someone holds its weights. Whether you can download them, or can only reach the model through its maker's API, decides where your data goes, what you pay, and what you can change. This page is pre-reading, with no session of its own.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

```{admonition} Learning objectives
:class: note
- Tell an open-weight model from a closed one, and name what each means for data, cost and control.
- Choose between them for a task at the firm, with a reason.
- Describe how an open model is run on campus GPUs.
```

(open-closed-models)=
## 0C.1 Who holds the weights

Training (page 0B) produces the model's **weights**, the billions of numbers that decide which token comes next. A model is two things: those weights, and the code that runs them. Who can get the weights is the difference.

| | Closed | Open-weight |
|---|---|---|
| Examples | OpenAI's GPT models, Anthropic's Claude, Google's Gemini | Meta's Llama, Alibaba's Qwen, Z.ai's GLM, Mistral |
| How you use it | Only through the company's API, on its servers | Download the weights and run it on hardware you choose |
| Your data | Sent to the provider on every call | Can stay on hardware your organization controls |
| Cost | Pay per token | Pay for the hardware, or use hardware you already have |
| Changing it | Prompting, and fine-tuning only where the provider allows it | Inspect it, fine-tune it, run it offline |
| Trade-off | Usually the strongest models, with no servers to run | You run, secure and update it; the best open models tend to trail the best closed ones |

### Open weights is not the same as open source

"Open-source model" is often used loosely for any model you can download. Strictly, those are **open-weight** models, and most of them are not open source. The two words mean different things:

- **Open weights**: the trained weights are published, so you can download the model and run it. That is usually all. The training data and the code that trained the model stay private, and a licence sets the terms: some allow almost any use, others add conditions, such as limits on commercial use or on very large companies.
- **Open source**: everything needed to study and rebuild the model, under terms that let anyone use, change and share it for any purpose. The [Open Source Initiative's definition](https://opensource.org/ai/open-source-ai-definition) asks for the weights, the code used to train and run the model, and enough detail about the training data for a skilled person to build a similar one.

So openness is a ladder, not a switch:

| | What is published | Example |
|---|---|---|
| **Closed** | Nothing; you reach the model only through its maker's API | GPT, Claude, Gemini |
| **Open code, closed weights** | The code that runs the model, but not the trained weights | Meta's first LLaMA (2023): its code was under an open-source licence (GPL v3), but the weights went only to researchers who applied, under a non-commercial licence |
| **Open weights** | The trained weights, under a licence; no training data, usually no training code | Llama, Qwen, DeepSeek, GLM, Mistral |
| **Fully open source** | Weights, training and running code, and the training data | Ai2's OLMo, EleutherAI's Pythia, LLM360's K2, Hugging Face's SmolLM3, the Swiss AI Initiative's Apertus |

Fully open models are fewer and mostly come from research groups and non-profits, because publishing the training data is costly and legally hard. The main ones:

- **[OLMo](https://allenai.org/olmo)** (Ai2, the Allen Institute for AI): weights, training code, the full training data and the training logs, at several sizes.
- **[Pythia](https://github.com/EleutherAI/pythia)** (EleutherAI): a family of models trained on a public dataset, with 154 snapshots of each saved during training, so researchers can watch a model learn.
- **[K2](https://www.llm360.ai)** (LLM360): a 65-billion-parameter model released with its data, code and intermediate checkpoints, built to be reproduced.
- **[SmolLM3](https://huggingface.co/blog/smollm3)** (Hugging Face): a small 3-billion-parameter model with its datasets and training recipe, small enough to run on a laptop.
- **[Apertus](https://www.swiss-ai.org/apertus)** (the Swiss AI Initiative, from EPFL and ETH Zurich): a national, multilingual model with its training data, code, weights and methods all documented.

Fully open models tend to trail the best open-weight models on capability, since the biggest labs keep their data private. What they offer instead is the ability to check exactly what went in, which matters for research and for anyone who has to answer where a model's knowledge came from.

Two things follow. First, a project can be open source and still not give you a model you can run: open code without the weights is a recipe without the finished dish. Training the weights yourself would take months of GPU time. Second, "open" on a model card tells you little until you read the licence. Before the firm builds on an open-weight model, someone has to check that the licence allows commercial use, since the firm sells its research.

For a firm like Champaign Capital, the data row often decides it: client data that may not leave the building can still go to a model the firm runs itself.

## 0C.2 Running an open model on campus GPUs

Open weights mean the campus can run a model itself. NCSA does this for Lumen, and you can do the same on NCSA's research GPUs, such as the [Delta cluster](https://docs.ncsa.illinois.edu/systems/delta/en/latest/) (access comes through an allocation, for example from [Illinois Computes](https://computes.illinois.edu/)). The steps, on a GPU node:

```bash
pip install vllm "huggingface_hub[cli]"
hf download Qwen/Qwen3-8B                   # pull the weights and config from Hugging Face
vllm serve Qwen/Qwen3-8B --port 8000        # serve it with an OpenAI-compatible API
```

[`hf download`](https://huggingface.co/docs/huggingface_hub/guides/cli) fetches the model files from [Hugging Face](https://huggingface.co/Qwen/Qwen3-8B), where most open models are published. vLLM loads them onto the GPU and answers requests in the OpenAI format. So the same client code works; only the address changes:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")
reply = client.chat.completions.create(model="Qwen/Qwen3-8B",
                                       messages=[{"role": "user", "content": "Say hello"}])
print(reply.choices[0].message.content)
```

On a shared cluster you would usually run this as a batch job on an allocated GPU node rather than on the login node; the Delta documentation explains how. You do not need any of this for the workshop. Lumen already does it for you.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. Client holdings may not leave the firm, so the model has to run where the firm controls the data. Open weights make that possible."
     data-no="Look at the Your data row of the table. Where does the text go when you call a closed model?">
  <p class="q">Champaign Capital wants a model to summarise each client's private holdings file. The files may not leave the firm's systems. Which fits?</p>
  <label><input type="radio" name="oc-q1" value="a"> A closed model through its public API, because it is usually the strongest</label>
  <label><input type="radio" name="oc-q1" value="b"> An open-weight model the firm runs on its own servers, or on campus GPUs for a class project</label>
  <label><input type="radio" name="oc-q1" value="c"> Either one, because models do not keep what they read</label>
  <div class="fb"></div>
</div>
```

## 0C.3 Exercise

For each task, choose an open-weight or a closed model, with one reason: a memo that quotes a client's private holdings; a summary of public news about Deere; a first draft of a Python script for the data team.

## 0C.4 How they compare today

How capable are the models on each side? [Artificial Analysis](https://artificialanalysis.ai/models) runs the same ten tests on hundreds of models and combines them into one score, its Intelligence Index. Here are the top 25, captured on 25 September 2026:

```{figure} _static/media/aa-intelligence-index-2026-09.png
:alt: Bar chart of the Artificial Analysis Intelligence Index for 25 models, from Claude Opus 5.5 at 58 down to Mistral Medium 3.5 at 14.
:width: 100%

Artificial Analysis Intelligence Index, top 25 of 673 models. Source: [artificialanalysis.ai/models](https://artificialanalysis.ai/models), 25 September 2026.
```

The same chart, coloured by who can get the weights. Black bars are closed (proprietary); blue bars are open-weight, and dark blue marks open weights whose licence restricts commercial use:

```{figure} _static/media/aa-open-vs-proprietary-2026-09.png
:alt: The same 25 models coloured as proprietary (black) or open weights (blue). The top six are proprietary; the best open-weight model, MiMo-V2.6-Pro, scores 46 against a top score of 58.
:width: 100%

Intelligence Index by open weights and proprietary. Source: [artificialanalysis.ai/models](https://artificialanalysis.ai/models), 25 September 2026.
```

Three things to read off it:

- **The top is closed.** The six highest scores are all proprietary models.
- **Open is close behind.** The best open-weight model, MiMo-V2.6-Pro, scores 46 against the leader's 58, level with closed models only a step down, and GLM, Kimi and DeepSeek models score between 39 and 45. GLM-5.3-Flash, the open model Lumen serves in your Colab notebooks, scores 42. That is the trade-off in the table in 0C.1: a little capability given up for control over where the data goes.
- **Check the licence colour.** Some open models (dark blue) may not be used commercially, which matters for a firm that sells its research.

These rankings change every few weeks. Open the live page for the current order before choosing a model.

## Further reading

- Hugging Face, [*LLM Course*](https://huggingface.co/learn/llm-course/chapter1/1) — free, hands-on, and the place most open models are published.
- Artificial Analysis, [*Comparison of Models*](https://artificialanalysis.ai/models) — live rankings of intelligence, speed and price, including open weights against proprietary.
