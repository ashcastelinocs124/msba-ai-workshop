# 0H System One Models

```{raw} html
<p class="wk-lede">A large language model answers with sentences, one token at a time. Some jobs inside software do not need a sentence at all: they need a decision, in a fixed shape, with an honest measure of how sure the model is. A newer kind of model, called a System One model, is built for exactly that. This page is pre-reading, with no session of its own.</p>
```

```{admonition} Learning objectives
:class: note
- Say what a System One model returns, and how that differs from a language model.
- Explain why a fixed output shape and a confidence score make a model easier to trust inside software.
- Name what is vendor claim and what is established, and where such a model fits at the firm.
```

## 0H.1 Fast thinking and slow thinking

The name comes from Daniel Kahneman's *Thinking, Fast and Slow*. **System 2** is slow, deliberate reasoning; **System 1** is the quick, intuitive call, such as knowing at a glance that a face is angry. A language model that writes a long memo is doing the slow kind of work, even though it is still one token at a time (chapter 0's section 0.3).

A **System One model** is aimed at the fast kind. You do not chat with it. You give it some unstructured input, such as an email or a note, and a **form** you have defined in advance, and it fills the form in. The company that coined the term, TypeSafe AI, describes its first model, **Jev**, as a function call: unstructured state in, typed decisions out.

| | Language model | System One model |
|---|---|---|
| **Returns** | Any text, and the text may be anything | One of the options you defined, in the shape you defined |
| **Built from** | Next-token prediction, then post-training (pages 0B and 0C) | Reported: reinforcement learning aimed at well-calibrated decisions |
| **Says how sure it is** | Not reliably; it sounds equally fluent when wrong (chapter 0's section 0.6) | Returns a confidence with every answer |
| **Wrong output shape** | Possible: a missing field, an invented option | Not possible, because the shape is fixed |
| **Speed and price** | Seconds, and paid per token written | Reported: tens to hundreds of milliseconds, with the output nearly free |

## 0H.2 What the fixed shape buys

Suppose the firm wants a model to look at each incoming client email and decide what to do with it. The form might allow only `reply now`, `send to an analyst` or `ignore`, plus a confidence. Three things follow:

1. **Nothing free-form slips through.** A language model asked the same question might answer "probably send it on, though it could wait", which a program then has to interpret. A form has no room for that.
2. **The confidence is a dial.** Below 0.80, send the email to a person; above it, act. Moving the number trades speed against mistakes, and it is set by the firm, not the model.
3. **It is cheap enough to run on everything.** A check that costs a fraction of a cent and takes a fraction of a second can sit in front of every step, not just the risky ones.

What it does not do: a System One model does not reason through a problem, explain itself or write. It is not a replacement for the agent loop in chapter 1; it is a fast decision inside one. And a confidence score is only useful if it is **calibrated**, meaning that answers given at 0.9 are right about nine times in ten. That is a claim to test on your own data, not to accept from a vendor.

## 0H.3 What is claimed, and what is not

The figures above come from TypeSafe AI's own announcement of Jev ([*Introducing System One models and Jev*](https://typesafe.ai/blog/introducing-system-one-models-and-jev)): 70 to 500 milliseconds end to end, input priced at $0.042 per million tokens, and calibrated confidence on every answer. This book has not tested them, and the category is new. Treat the idea, a small fast model with a closed output shape, as the lasting part, and the numbers as a vendor's marketing until you have measured them on the firm's own examples.

Chapter 3 uses the idea once: section 3.2.6 puts a System One gate in front of an agent's memory, so a note is saved only when the gate is sure of it. That cell uses a scripted stand-in, not Jev, and the gate design is this book's own.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The fixed form removes wrong shapes and invented options, and the confidence tells the program when to hand a case to a person. Neither makes the answer correct; that has to be tested."
     data-no="Compare what each kind of model is allowed to return, and what the confidence lets the program do.">
  <p class="q">What is the main advantage of a System One model over a language model, for a decision inside software?</p>
  <label><input type="radio" name="sys1-q1" value="a"> It reasons through the problem more carefully</label>
  <label><input type="radio" name="sys1-q1" value="b"> Its answers are always correct</label>
  <label><input type="radio" name="sys1-q1" value="c"> Its answer always fits the form you defined, and comes with a confidence</label>
  <div class="fb"></div>
</div>
```

## Further reading

- TypeSafe AI, [*Introducing System One models and Jev*](https://typesafe.ai/blog/introducing-system-one-models-and-jev) — the announcement; the speed, price and calibration figures on this page come from it.
- Daniel Kahneman, *Thinking, Fast and Slow* (2011) — where the System 1 and System 2 names come from.
