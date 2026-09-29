# 0H System One Models

```{raw} html
<p class="wk-lede">A large language model answers with sentences, one token at a time. Some jobs inside software do not need a sentence at all: they need a decision, in a fixed shape, with an honest measure of how sure the model is. A newer kind of model, called a System One model, is built for exactly that. This page is pre-reading, with no session of its own.</p>
```

```{admonition} Learning objectives
:class: note
- Say what a System One model returns, and how that differs from a language model.
- Explain why a fixed output shape and a confidence score make a model easier to trust inside software.
- Name the three question types Jev offers, and say what calibrated confidence means.
- Place a System One model in an agent, and say what is vendor claim and what is undisclosed.
```

## 0H.1 Fast thinking and slow thinking

The name comes from Daniel Kahneman's *Thinking, Fast and Slow*. **System 2** is slow, deliberate reasoning; **System 1** is the quick, intuitive call, such as knowing at a glance that a face is angry. A language model that writes a long memo is doing the slow kind of work, even though it is still one token at a time (chapter 0's section 0.3).

A **System One model** is aimed at the fast kind. You do not chat with it. You give it some unstructured input, such as an email or a note, and a **form** you have defined in advance, and it fills the form in. The company that coined the term, TypeSafe AI, describes its first model, **Jev**, as a function call: unstructured state in, typed decisions out.

| | Language model | System One model |
|---|---|---|
| **Returns** | Any text, and the text may be anything | One of the options you defined, in the shape you defined |
| **Trained to** | Predict the next token, then be preferred by people (pages 0B and 0C) | Reported: make decisions whose confidence is calibrated (RLCD) |
| **Says how sure it is** | Not reliably; it sounds equally fluent when wrong (chapter 0's section 0.6) | Returns a confidence with every answer |
| **Wrong output shape** | Possible: a missing field, an invented option | Not possible, because the shape is fixed |
| **Speed and price** | Seconds, and paid per token written | Reported: tens to hundreds of milliseconds, with the output nearly free |

## 0H.2 What it hands back

TypeSafe's documentation ([docs.typesafe.ai](https://docs.typesafe.ai/)) describes three kinds of question you can put to Jev, and you can mix them in one call:

| Question type | You define | You get back |
|---|---|---|
| **Choice** | A list of options, such as `reply now`, `send to an analyst`, `ignore` | The chosen option, a probability for every option, and a confidence |
| **Score** | A scale, such as 0 to 10 for urgency | A score, a probability for each value, and a confidence |
| **Noul** | A single well-scoped question | One number between 0 and 1 |

The documentation says each question is evaluated in parallel and on its own, and that each should ask "one specific, well-scoped thing". A question that needs several steps of reasoning is a job for a language model.

Suppose the firm wants each incoming client email sorted. Dana Whitfield writes "And NVIDIA?" and the model is asked to choose among `reply now`, `send to an analyst` and `ignore`. An answer might look like this (the numbers here are made up to show the shape; they are not real Jev output):

```text
reply now          0.86
send to an analyst 0.12
ignore             0.02      confidence 0.86
```

Three things follow from a fixed shape:

1. **Nothing free-form slips through.** A language model asked the same question might answer "probably send it on, though it could wait", which a program then has to interpret. A form has no room for that.
2. **The confidence is a dial.** Above 0.80, act; below it, send the email to a person. Moving the number trades speed against mistakes, and it is set by the firm, not the model.
3. **It is cheap enough to run on everything.** A check that costs a fraction of a cent and takes a fraction of a second can sit in front of every step, not just the risky ones.

What it does not do: a System One model does not reason through a problem, explain itself or write. It is not a replacement for the agent loop in chapter 1; it is a fast decision inside one.

## 0H.3 How it is trained, and what is not said

A language model learns to predict the next token (page 0B), then is post-trained toward answers people prefer (page 0C). TypeSafe says Jev was trained differently, with a method it calls **RLCD**, Reinforcement Learning for Calibrated Decisions. The goal is not a pleasing sentence but a decision with **calibrated** confidence: "higher confidence means higher accuracy". If the model reports 0.80 on a hundred cases, about eighty should be right. A model that is right ninety-nine times has understated its confidence, and one that is right fifty times has overstated it.

That matters because the confidence becomes part of the program's control flow: at 0.95 or above, act automatically; below, hand the case to a person. A score you cannot trust is worse than none, since the program will act on it.

TypeSafe describes "a new model architecture" and a "parallel sampler" that generates all the outputs of a query at once, not one token after another. What its announcement does not say: how large the model is, what data it was trained on, whether it was built from scratch or adapted from an existing open model (page 0D), or how RLCD works in detail. Anyone who states those as fact is guessing. It is also why the speed claims below cannot yet be checked against the design.

## 0H.4 Where it sits in an agent

Chapter 1's agent uses a language model for every step, including the small ones. A System One model suggests a split: the fast model handles the many small, well-defined decisions, and the language model is called only for what needs reasoning or writing. Pick an email and move the confidence bar:

```{raw} html
:file: widgets/ch00-decision-layer.html
```

The confidence bar decides when a person is asked (chapter 0's section 0.6 is why a fluent model still needs one). Chapter 3 uses the same idea once more: section 3.2.6 puts a System One gate in front of an agent's memory.

## 0H.5 What is claimed, and what is not

The figures above come from TypeSafe AI's own announcement of Jev ([*Introducing System One models and Jev*](https://typesafe.ai/blog/introducing-system-one-models-and-jev)): 70 to 500 milliseconds end to end, input priced at $0.042 per million tokens with output free, and a "0%" hallucination rate that follows from the fixed output schema. That last one means Jev cannot return an option you did not define; it does not mean its choices are always right. This book has not tested any of it, access is early-access only, and the category is new. Treat the idea, a fast model with a closed output shape and a trustworthy confidence, as the lasting part, and the numbers as a vendor's claims until you have measured them on the firm's own examples.

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
