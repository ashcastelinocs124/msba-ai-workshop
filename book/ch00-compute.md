# 0D Training and Inference Compute

```{raw} html
<p class="wk-lede">A model costs computing power twice: once to train it, and again every time anyone asks it something. The two are different in size, in timing and in who pays, and the difference explains model prices, why open-weight models are cheap to adopt, and much of the demand for the chips the firm's semiconductor analysts cover. This page is pre-reading, with no session of its own.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

```{admonition} Learning objectives
:class: note
- Tell training compute from inference compute: when each is spent, how much, and on what hardware.
- Estimate which one dominates for a given model and a given number of users.
- Say who pays for each, for a closed model and for an open-weight one.
```

## 0D.1 Two kinds of compute

**Training compute** is spent once per model, before anyone uses it. It is the training loop from page 0B, repeated over trillions of tokens: thousands of GPUs working together for weeks or months, wired so that they can share results many times a second. Meta reports that training Llama 3.1 405B on about 15 trillion tokens took 30.84 million GPU-hours. A rough rule for the number of calculations is 6 × parameters × training tokens.

**Inference compute** is spent every time the model answers. There is no learning, only the forward pass from page 0A: each token of the answer costs about 2 × the parameters it uses, so a model with fewer or only partly used parameters, such as a mixture of experts, is cheaper to run. One answer takes a fraction of a second on one GPU, or a few GPUs for a large model. But it is paid on every question, by every user, for as long as the model is in use.

| | Training | Inference |
|---|---|---|
| When | Once per model, before release | Every question, forever after |
| Size of one run | Enormous: months on thousands of GPUs | Tiny: under a second on one or a few GPUs |
| Grows with | Parameters × training tokens | Active parameters × tokens answered × number of questions |
| Hardware | Large clusters with very fast links between chips | Many separate servers, close to the users |
| Who pays, closed model | The lab | You, in the per-token price, which also repays the training |
| Who pays, open-weight model | Whoever trained it, already paid | You, in the hardware you run it on |

## 0D.2 Which one is bigger?

It depends on how much the model is used. Pick a model and a user, and see how long it takes for everyday questions to add up to the whole training run. Then turn on reasoning mode:

```{raw} html
:file: widgets/ch00-compute.html
```

At the firm's scale, training dwarfs everything: 5,000 questions a day would take thousands of years to match it. For a chatbot answering a billion questions a day, inference catches up within weeks, and after that it is where most of the computing goes. **Reasoning** models push the same way: they write thousands of thinking tokens before the answer (page 0B.3), which multiplies the inference cost of every question. Spending more compute at answer time instead of at training time is often called *test-time compute*.

## 0D.3 Why it matters to the firm

- **Choosing a model.** With a closed model, the firm pays only for inference, per token, and never sees the training bill. With an open-weight model, the expensive part has already been paid for by someone else; the firm pays for the servers to run it (page 0C).
- **Reading the price list.** Longer answers, longer documents in the context window (chapter 0, section 0.5) and reasoning modes all raise the bill, because each is more inference.
- **Covering the market.** Training needs giant clusters built by a few labs; inference needs chips wherever the users are, and grows with every new user. That is why investors watch both, and why the semiconductor names the firm covers, NVIDIA among them, report demand for each. Part IV comes back to this.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. At 5,000 questions a day, the firm's inference is a tiny fraction of the training run, and with an open-weight model someone else already paid for training. The firm's cost is the servers to answer its own questions."
     data-no="Try the calculator with Champaign Capital selected. Which bar is bigger, and who paid for it?">
  <p class="q">The firm runs an open-weight 70B model on its own servers for about 5,000 questions a day. Where does most of the compute behind its answers come from?</p>
  <label><input type="radio" name="cmp-q1" value="a"> The firm's own servers, answering questions</label>
  <label><input type="radio" name="cmp-q1" value="b"> The training run, which the model's maker paid for before releasing the weights</label>
  <label><input type="radio" name="cmp-q1" value="c"> Neither; open-weight models need no compute</label>
  <div class="fb"></div>
</div>
```

## Further reading

- Meta, [*Llama 3.1 405B model card*](https://huggingface.co/meta-llama/Llama-3.1-405B) — reported training tokens, GPU-hours and energy for each Llama 3.1 size.
- Epoch AI, [*Trends in AI*](https://epoch.ai/trends) — how much compute frontier models are trained with, and how fast it is growing.
