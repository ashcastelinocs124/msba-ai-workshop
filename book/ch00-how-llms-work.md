# 0. How Large Language Models Work

```{raw} html
<p class="wk-lede">Every chapter after this one hands a question to a large language model. Before you build on one, see what it actually does: it splits text into tokens, predicts the next one, and repeats. That one idea explains why it writes fluently, why it can state a wrong figure with confidence, and why chapters 1 and 2 give it tools and context. This chapter is pre-reading, with no session of its own.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

```{admonition} Learning objectives
:class: note
- Say what a token is, and why a model's costs and limits are counted in tokens rather than words.
- Explain how a model writes by predicting the next token, and what the temperature setting changes.
- Describe at a high level how a model is trained, and why that leaves it without the firm's data or today's numbers.
```

## 0.1 What a large language model is

It is Monday at Champaign Capital Research. Priya has a client asking how Deere's revenue growth compared with Caterpillar's last quarter, and a tool on her screen that drafts the reply. The tool is built on a **large language model** (LLM), such as GPT, Claude, Gemini, Llama or GLM.

An LLM is a program that has read a very large amount of text and learned one skill from it: given some text, predict what comes next. Everything else it seems to do (answer questions, write memos, summarise filings, call tools) is that one skill, repeated.

"Large" refers to two things: the amount of text it learned from, trillions of words, and the size of the model, billions of adjustable numbers called **parameters** (section 0.4). "Language model" is the older, plainer name for any program that predicts the next word.

## 0.2 Tokens: what the model reads

A model does not read words. It reads **tokens**, pieces of text from a fixed vocabulary of about a hundred thousand. Common words are usually one token each. Rarer words, names and numbers are split into several.

Point at each word to see the pieces a toy vocabulary splits it into. Type your own sentence too:

```{raw} html
:file: widgets/ch00-tokens.html
```

The same split in Python. Change the sentence and run it again:

```{code-block} python
:class: pyodide
from llm_basics import show_tokens

show_tokens("Caterpillar's revenue grew 3.1% last quarter")
```

`·` marks a space, which is part of the token that follows it. "revenue" is one token; "Caterpillar's" is three; "3.1%" is five, counting the space in front of it. A real tokenizer splits differently, but the pattern holds.

Tokens matter to you for three reasons:

- **Cost.** Providers charge per token, for what you send and for what comes back.
- **Limits.** A model can read only so many tokens at once (section 0.5).
- **Arithmetic.** A number is several tokens, not one value, which is one reason models slip on sums. Chapter 1 hands the numbers to tools.

In English a token is roughly three-quarters of a word. Chapter 2 uses that rule, words × 1.3, to estimate what a prompt costs.

## 0.3 Writing one token at a time

To write, the model looks at everything so far and gives every token in its vocabulary a probability of coming next. One is picked and added to the text, and the model runs again on the longer text. It repeats until it produces a token that means "stop".

Try it with a toy model that has read only thirteen sentences from the firm's memos. Take the favourite a few times, then start over, raise the temperature and roll the dice:

```{raw} html
:file: widgets/ch00-next-token.html
```

The **temperature** controls how the next token is picked. At 0 the model always takes the most likely one, so the same question gets the same answer. Higher temperatures give less likely tokens a better chance, which reads as more varied and more creative, and also makes mistakes more likely.

The same toy model in Python. First, what it thinks follows "revenue", then the sentence it writes when it always takes the favourite:

```{code-block} python
:class: pyodide
from llm_basics import next_word_probs, generate

for word, p in next_word_probs("revenue")[:6]:
    print(f"{word:<8} {p:.0%}")
print()
print(generate("Deere", temperature=0))
```

Now three runs at each temperature:

```{code-block} python
:class: pyodide
from llm_basics import generate

for t in [0, 0.7, 1.5]:
    for seed in range(3):
        print(f"temperature {t}:  {generate('Deere', temperature=t, seed=seed)}")
    print()
```

At 0 all three runs agree. At 1.5 they wander, and some wander into sentences the firm never wrote.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. A client memo should come out the same way every time it is asked for, with no surprises, so the model should take the most likely token. Save higher temperatures for brainstorming, where variety is the point."
     data-no="Think about what temperature changes: how often the model picks something other than its most likely next token. Is that what you want in a memo that quotes figures to a client?">
  <p class="q">Priya's drafting tool writes client memos that quote revenue figures. Which temperature setting fits best?</p>
  <label><input type="radio" name="q0" value="a"> Low, close to 0, so the same question gets the same careful answer</label>
  <label><input type="radio" name="q0" value="b"> High, so every memo reads differently and the client does not get bored</label>
  <label><input type="radio" name="q0" value="c"> It makes no difference, because temperature only changes the length of the answer</label>
  <div class="fb"></div>
</div>
```

## 0.4 How a model learns

The toy model learned by counting which word follows which. A real LLM learns the same kind of pattern with a neural network. Training adjusts the model's **weights**, the billions of numbers that decide which token comes next, until its predictions match the text it reads. Training a large model takes months on thousands of GPUs. Using it afterwards takes a fraction of a second per token.

Those adjustable numbers are the model's **parameters**; "weights" is the usual name for nearly all of them, and the two words are often used interchangeably. A parameter is a single number, such as 0.0137, and on its own it means nothing. What the model knows is spread across all of them at once, the way a firm's judgement lives in all its people rather than in one desk.

The parameter count is how models are sized, and it is the number in many model names:

| Model | Parameters | What that means |
|---|---|---|
| The toy model in section 0.3 | 53 counts | Enough for thirteen sentences |
| Qwen3-8B | 8 billion | Runs on one good GPU |
| Llama 3.1 405B | 405 billion | Needs a rack of GPUs |
| DeepSeek-V3 | 671 billion, 37 billion used per token | A mixture of experts ([page 0A](ch00-transformers.md)) |

More parameters can hold more knowledge and handle harder tasks, but they cost more to train and to run: every parameter is used for every token (except in a mixture of experts), and each one takes memory. At the usual precision a parameter takes 2 bytes, so an 8-billion-parameter model needs about 16 GB of GPU memory just to load. The makers of closed models such as GPT, Claude and Gemini do not publish their counts.

Two consequences shape the rest of this book:

- **It knows nothing after its training cutoff.** Last quarter's results may have come out after the model was trained. Chapter 1 gives it tools to look them up.
- **It has never seen the firm's private data.** Client preferences, the policy handbook and last week's memos were not in its training text. Chapter 2 puts them in front of it on each call.

What that network looks like inside is on [0A Transformers and Mixture of Experts](ch00-transformers.md); the three stages of training that turn it from a text predictor into an assistant are on [0B How a Model Is Trained](ch00-training.md); who can get a trained model's weights, and why that matters to the firm, is on [0C Open-Source and Closed-Source Models](ch00-open-closed.md).

## 0.5 The context window

On each call the model reads a limited number of tokens: the instructions, the conversation so far, any documents or tool results, and the question. That limit is the **context window**. Current models allow from tens of thousands to around a million tokens, and everything counts against it, including the answer being written.

The model has no memory between calls. What looks like memory in a chat app is the app sending the earlier messages again each time. Deciding what goes into the window on each call is the subject of section 2.2.

## 0.6 Why a model can be fluent and wrong

The model picks each token because it often follows the text so far, not because it checked a fact. A sentence can sound exactly like a real memo and still carry the wrong number. When a model does this it is often called **hallucination**.

The toy model shows it plainly. It has read Deere's figures and NVIDIA's figures, and at a high temperature it happily joins Deere's name to NVIDIA's growth rate. The cell checks each sentence it writes against the firm's records:

```{code-block} python
:class: pyodide
from llm_basics import generate, fact_check

for seed in range(8):
    sentence = generate("Deere", temperature=1.5, seed=seed)
    print(sentence)
    print("   ", fact_check(sentence))
```

Real models are far better than this toy, but the mechanism is the same, and it is why the firm's rule is that every figure in a memo must cite its source. The fixes come in the next chapters: tools that fetch the real figure (chapter 1), the right document on the desk (chapter 2), and retrieval with citations (chapter 3).

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The model writes the tokens that are likely to come next. A plausible growth rate is likely whether or not it is Tesla's, and the firm holds no Tesla data to check it against."
     data-no="Remember what the model is doing at each step: picking a likely next token. Does anything in that process check a fact?">
  <p class="q">Asked for Tesla's revenue growth last quarter with no tools, a model replies with a confident, specific percentage. The firm has no Tesla data. What is the best explanation?</p>
  <label><input type="radio" name="q1" value="a"> The model looked the figure up on the internet while it was answering</label>
  <label><input type="radio" name="q1" value="b"> The model is lying on purpose to please the user</label>
  <label><input type="radio" name="q1" value="c"> A specific percentage is a likely continuation of the question, so the model wrote one, whether or not it is true</label>
  <div class="fb"></div>
</div>
```

## 0.7 Run it against a real model

The toy model has read thirteen sentences. The cells below send questions to a GPT deployment on Illinois Azure through this site's `/api/chat` proxy; your browser never sees a key.

```{raw} html
<div class="wk-banner wk-pages-only">Model cells need the campus copy of this book: <a data-campus="/ch00-how-llms-work.html#run-it-against-a-real-model" href="#">open it there</a> and sign in with your @illinois.edu account. Everything else on this page works here.</div>
```

```{code-block} python
:class: pyodide
from llm import azure_model
from agent import explain_reply

reply = azure_model([{"role": "user", "content": "In two sentences, what is a token in a large language model?"}])
print(explain_reply(reply))
```

Now the question the toy model got wrong. This site's model has the firm's lookup tools available, so instead of guessing it may ask to look the figure up. That request is how chapter 1 begins:

```{code-block} python
:class: pyodide
from llm import azure_model
from agent import explain_reply

reply = azure_model([{"role": "user", "content": "What was Deere's revenue growth last quarter?"}])
print(explain_reply(reply))
```

## 0.8 Exercise

These use the cells on this page; there is no Colab notebook for this chapter.

1. In the tokens cell in 0.2, try a sentence from your own work or internship. Which words split into several tokens, and what do they have in common?
2. In the widget, start from NVIDIA and build a sentence that is true, then one that is false, by clicking the bars. How many choices did each take?
3. Change the fact-check cell in 0.6 to run 20 seeds at temperature 1.5, then at 0.5. How many false sentences did each produce?

## Further reading

- 3Blue1Brown, [*Transformers, the tech behind LLMs*](https://www.youtube.com/watch?v=wjZofJX0v4M) (video) — how a model turns text into tokens and predicts the next one, drawn step by step.
- Andrej Karpathy, [*Intro to Large Language Models*](https://www.youtube.com/watch?v=zjkBMFhNj_g) (1-hour talk) — pretraining, fine-tuning, and what models can and cannot do.
- Jay Alammar, [*The Illustrated Transformer*](https://jalammar.github.io/illustrated-transformer/) — the architecture inside the model, in pictures.
