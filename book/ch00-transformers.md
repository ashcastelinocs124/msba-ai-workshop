# 0A Transformers and Mixture of Experts

```{raw} html
<p class="wk-lede">Chapter 0 showed what a model does: predict the next token, again and again. This page opens it up: the design almost every model shares, the transformer, and the trick that lets the largest ones run cheaply, mixture of experts. This page is pre-reading, with no session of its own.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

```{admonition} Learning objectives
:class: note
- Describe the three steps a transformer takes to predict the next token, and why attention makes long inputs cost more.
- Explain what a mixture-of-experts model saves, and what its "experts" are not.
```

## 0A.1 The transformer

The neural network inside an LLM has a particular design, the **transformer**. Almost every LLM in use today is one; the design was published by Google researchers in 2017.

Step through one sentence the way a transformer reads it:

```{raw} html
:file: widgets/ch00-transformer.html
```

Because every token looks at every token before it, doubling the text more than doubles the work. That is one reason the context window (chapter 0, section 0.5) has a limit.

## 0A.2 Mixture of experts

Many recent models, including DeepSeek, Mixtral and several GLM and Qwen models, split each layer into many small blocks, the **experts**, with a **router** that sends each token to only a few of them. Send tokens through and compare it with a dense model, where every token uses everything:

```{raw} html
:file: widgets/ch00-moe.html
```

The firm works the same way: a question about Deere goes to the industrials analysts, not to all 14. One difference: the experts are not neat specialists such as "finance" or "grammar". The router learns its own way of dividing the work, which is why the same token always lands in the same place but a topic can be spread across several experts.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. The router sends each token to a few experts, so only a small share of the weights does work on any one token. The model still holds all 671 billion, which is why it knows as much as a very large network."
     data-no="Think about the router: for any one token, how many of the experts actually run?">
  <p class="q">DeepSeek-V3 has 671 billion weights but uses about 37 billion for each token. What does that buy?</p>
  <label><input type="radio" name="inside-q1" value="a"> It only knows as much as a 37-billion-weight model</label>
  <label><input type="radio" name="inside-q1" value="b"> The knowledge of a very large model at roughly the running cost of a much smaller one</label>
  <label><input type="radio" name="inside-q1" value="c"> Each expert is a specialist in one topic, such as finance or law</label>
  <div class="fb"></div>
</div>
```

## Further reading

- Ashish Vaswani and others, [*Attention Is All You Need*](https://arxiv.org/abs/1706.03762) (2017) — the paper that introduced the transformer. Technical; the abstract and first figure are enough.
- Hugging Face, [*Mixture of Experts Explained*](https://huggingface.co/blog/moe) — how a router sends each token to a few experts, and what that saves.
