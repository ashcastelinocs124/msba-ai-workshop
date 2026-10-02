# 3.1 Retrieval and RAG

```{raw} html
<p class="wk-lede">Elena Ruiz's compliance team answers about thirty trade pre-clearance requests a week, and every answer has to cite the handbook clause it rests on. A model has never read that handbook. Find the right clause for each question, put it on the desk, and let the model answer from it. The session 3 recording is on <a href="ch03-memory-rag.html#ch03-lecture">the chapter 3 page</a>.</p>
<a class="wk-colab" href="https://colab.research.google.com/github/ashcastelinocs124/msba-ai-workshop/blob/main/notebooks/ch03-retrieval-rag.ipynb" target="_blank">▶ Open in Colab</a>
```

```{admonition} Learning objectives
:class: note
- Say what retrieval-augmented generation (RAG) is, and what it fixes that a better prompt cannot.
- Choose how to cut a document into chunks, and spot a chunk size that splits or buries a rule.
- Explain an embedding in one sentence, and why two questions with no words in common can land close together.
- Compare keyword, semantic, hybrid and reranked search, and name a question each one gets wrong.
- Let an agent decide when to search and when to search again, and check that a cited clause really says what the answer claims.
```

## 3.1.1 What RAG is

Tom Okafor, a data engineer, holds Deere shares and wants to sell. The firm published research on Deere six days ago. Can he?

A model asked this on its own answers from what it read in training: public text about markets, where employees can generally sell shares they own. It has never read Champaign Capital's handbook, so it cannot know about the firm's 14-day blackout window. It will not say "I don't know" either. It answers the general question, confidently.

**Retrieval-augmented generation**, or **RAG**, fixes this in three steps: *retrieve* the handbook passages that match the question, *augment* the desk by putting them in the system prompt, and *generate* the answer from them. The model still writes the answer. It no longer has to remember the rule, only to read it.

```{raw} html
:file: widgets/ch03-rag-before-after.html
```

The same question twice, first with nothing retrieved, then with the two best-matching passages on the desk:

```{code-block} python
:class: pyodide
from agent import agent
from retrieval import with_sources

q = "Can Tom sell his Deere shares 6 days after we published research on Deere?"

print("Without retrieval:")
answer, log = agent(q)

print("\nWhat retrieval puts on the desk:")
print(with_sources(q))

print("\nWith retrieval:")
answer, log = agent(q, system=with_sources(q))
```

Two passages came back, and only one of them is about trading after publication. That is normal: retrieval hands over a few candidates, and the model picks the one that applies. The answer names its source, so Elena can check it in ten seconds.

This is the same move as chapter 2's `build_context`, which pasted one clause onto the desk when a question mentioned vendor data. That worked because it had twelve short clauses and a list of trigger words. The rest of this section is about doing it for a real handbook, for questions nobody wrote trigger words for.

## 3.1.2 Chunking

Retrieval returns pieces of a document, not the whole thing, so the first decision is how to cut it. Each piece is a **chunk**. There are three common ways:

- **Fixed size.** Every chunk is the same number of words. Simple, and blind to where a rule starts and ends.
- **Fixed size with overlap.** Each chunk repeats the last few words of the one before, so a sentence cut at a boundary appears whole in one of them.
- **By structure.** Cut where the document itself is cut: headings, paragraphs, numbered clauses. This needs a document with structure, which a handbook has.

The size matters in both directions. A chunk too small can cut a rule in half, and neither half matches the question. A chunk too large holds the rule and twenty others, so it matches many questions weakly, and when it is retrieved it fills the desk with rules nobody asked about. Move the sliders and watch the blackout rule:

```{raw} html
:file: widgets/ch03-chunking.html
```

The same three settings in code, over the full handbook:

```{code-block} python
:class: pyodide
from handbook import HANDBOOK, CLAUSES
from retrieval import chunk

rule = "within 14 days before or after the firm publishes research on it"
for size, overlap in [(15, 0), (15, 5), (400, 0)]:
    pieces = chunk(HANDBOOK, size, overlap)
    home = [p for p in pieces if rule in p]
    status = f"whole, inside a {len(home[0].split())}-word chunk" if home else "cut in half"
    print(f"{size} words, overlap {overlap}: {len(pieces)} chunks. The blackout rule is {status}.")

print(f"\nBy structure: {len(CLAUSES)} chunks, one clause each. The blackout rule is its own chunk.")
```

This chapter chunks the handbook by structure, one clause per chunk, because the handbook was written as numbered clauses and each clause is one rule. A 10-K or a transcript has no such lines, and there fixed size with overlap is the usual start.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. With no overlap, the boundary can fall mid-sentence, so neither half contains the whole rule and neither matches the question well. Overlap, or cutting at clause boundaries, keeps it whole."
     data-no="Look at where the boundary falls. What does each half of the rule contain on its own?">
  <p class="q">You cut the handbook into 15-word chunks with no overlap, and a question about the blackout window no longer finds the rule. What is the most likely reason?</p>
  <label><input type="radio" name="ch31-q1" value="a"> Fifteen words is too long for the model to read</label>
  <label><input type="radio" name="ch31-q1" value="b"> The rule was split across two chunks, and neither half matches the question</label>
  <label><input type="radio" name="ch31-q1" value="c"> Chunks without overlap cannot be searched</label>
  <div class="fb"></div>
</div>
```

## 3.1.3 Embeddings

To search by meaning, a computer needs meaning in a form it can compare. An **embedding** is a list of numbers that stands for a piece of text, made so that texts with similar meaning get similar numbers. This book uses OpenAI's `text-embedding-3-small`, run on Illinois Azure, which turns any text into 256 numbers.

Nobody chose what each number means. The embedding model learned them by reading a very large amount of text, the same way chapter 0's model learned to predict the next token, and the result is that "a quiet period after we publish" and "no employee may trade within 14 days after the firm publishes" land near each other, while "meals are reimbursed up to $60" lands far away.

Closeness is measured by **cosine similarity**: 1 means the same direction, 0 means unrelated. The map squeezes 256 numbers down to two so you can see them. Each dot is one handbook clause; click a question to drop it on the map:

```{raw} html
:file: widgets/ch03-embedding-map.html
```

The numbers themselves, and how close one question is to three clauses:

```{code-block} python
:class: pyodide
from retrieval import embed, similarity

q = "Can I trade during the quiet period after we publish?"
v = embed(q)
print(f"{len(v)} numbers. The first five: {v[:5]}")

for clause in ["personal-trading-2", "gifts-4", "expense-2"]:
    print(f"similarity to {clause}: {similarity(q, clause)}")
```

The question never says *blackout* and never says *14 days*, and it is still closest to the blackout rule. The gifts clause comes second because it also mentions the blackout window, and the travel-meals clause is nowhere near.

The handbook's 73 clauses were embedded once, when this book was built, and the vectors are stored beside it. So were the questions this chapter asks. A question you type yourself needs a new embedding: on the campus copy of this book it is made live through the site's `/api/embed` proxy (section 3.1.7); here it falls back to keyword search and says so.

## 3.1.4 Four ways to retrieve

With chunks and embeddings in hand, there are four common ways to rank the handbook for a question:

| Method | How it ranks | Good at | Misses |
|---|---|---|---|
| **Keyword** (BM25) | Counts shared words, weighting rare words more | exact terms: *short*, a ticker, an email address, a clause number | the same idea in different words |
| **Semantic** | Cosine similarity of embeddings | paraphrase: *quiet period* for blackout window | rare exact terms, which blur into their topic |
| **Hybrid** | Merges the two rankings (reciprocal rank fusion: a clause high on either list rises) | most questions, which is why most production systems start here | a question where one list is badly wrong |
| **Rerank** | Takes hybrid's top 10 and scores each again, more carefully | putting the best of a good shortlist first | anything the shortlist missed |

BM25 is the ranking formula search engines used for decades before embeddings. A production reranker is a second, slower model that reads the question and each candidate together; the one in this book is a simple stand-in that re-scores by meaning, exact phrases and the clause's heading. Pick a question:

```{raw} html
:file: widgets/ch03-retrieval-compare.html
```

Or run the four side by side on any of those questions:

```{code-block} python
:class: pyodide
from retrieval import search, show

q = "Who approves my trade?"
for method in ["keyword", "semantic", "hybrid", "rerank"]:
    print(f"\n{method}:")
    show(search(q, method))
```

No method wins every question. Keyword search gets *Can I short NVIDIA?* right and *Who approves my trade?* wrong; semantic search does the opposite. Every method puts the general pre-clearance rule above the index-fund exemption, and all four still have the exemption in their top three. That is the practical lesson: hand the model a few candidates, not one, and let it read.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="a"
     data-ok="Correct. Ticker symbols and codes are rare exact strings. Keyword search matches them directly; an embedding captures the topic and can blur a specific code into it. Hybrid search keeps the keyword hit."
     data-no="Think about what an embedding keeps: meaning. What happens to an exact code like a request number?">
  <p class="q">A compliance officer searches for <em>request 7104</em>. Which method is most likely to rank the right record first?</p>
  <label><input type="radio" name="ch31-q2" value="a"> Keyword or hybrid, because an exact code is a rare word to match</label>
  <label><input type="radio" name="ch31-q2" value="b"> Semantic, because it understands what a request is</label>
  <label><input type="radio" name="ch31-q2" value="c"> None; numbers cannot be searched</label>
  <div class="fb"></div>
</div>
```

## 3.1.5 Agentic retrieval

So far code retrieved before every call, whether or not the question needed it. In **agentic retrieval** search is a tool, and the agent decides: whether to search at all, what to search for, and whether the results are good enough or it should rewrite the query and search again. It is the chapter 1 loop with one more tool, `search_handbook`.

Marcus Bell bought Caterpillar last week and writes the way people talk:

```{code-block} python
:class: pyodide
from agent import agent

answer, log = agent("Can I dump my Caterpillar shares a week after buying them?")
```

The first search used Marcus's words, and keyword search found clauses about shares and pre-clearance, none of which says how long to hold. The agent noticed that none of them answered the question, rewrote *dump* as *sell* and *a week after buying them* as *minimum holding period*, the handbook's own words, and searched again. The second search found the rule. Press **Watch** to see the two searches in the handbook.

This is also how the agent avoids searching when it should not: a question about Deere's revenue goes to `get_financials`, and the handbook is never opened. The cost is more model calls, and one more way to go wrong, since an agent can stop after a weak first search or keep searching forever. Chapter 1's step budget still applies.

## 3.1.6 Worked example: trade pre-clearance

Everyone at Champaign Capital must ask compliance before trading a stock in a sector the firm covers. Elena's team gets about thirty requests a week by email. Each one means opening the request, checking the restricted list, checking when the firm last published on that name, checking how long the position has been held, and writing back a decision with the policy clause that supports it. The rules fit on one page. Applying them the same way at 4:55 on a Friday is the hard part.

The agent gets two read-only tools, `get_trade_request` and `search_docs`, and no `clear_trade` tool. It recommends; a compliance officer approves (handbook clause `pre-clearance-4`).

| Request | Employee | What is different | Expected recommendation |
|---|---|---|---|
| 7101 | Priya Natarajan, buy 50 DE | firm last published on Deere 41 days ago | Approve |
| 7102 | Marcus Bell, sell 200 CAT | position held 12 days | Decline, 30-day minimum holding period |
| 7103 | Jordan Lee, buy 30 NVDA | NVIDIA is on the restricted list | Decline |
| 7104 | Tom Okafor, sell 80 DE | firm published on Deere 6 days ago | Hold until the 14-day blackout ends |

```{code-block} python
:class: pyodide
from agent import agent

for request in ["7101", "7102", "7103", "7104"]:
    print(f"\n#{request}")
    answer, log = agent(f"Can compliance clear trade request #{request}?")
```

Every recommendation ends with a `[source: …]` tag naming the clause it relied on. The tag is only useful if someone checks it, so check one: does the cited clause really say what the recommendation claims?

```{code-block} python
:class: pyodide
from agent import agent
from handbook import CLAUSES

answer, log = agent("Can compliance clear trade request #7104?", verbose=False)
cited = answer.split("[source: ")[-1].rstrip("]")
clause = next(c for c in CLAUSES if c["id"] == cited)
print("The recommendation:", answer)
print(f"\nWhat {cited} says:", clause["text"])
```

A citation that points to a real clause, which really says what the answer claims, is what lets a person approve thirty of these in the time one used to take. A citation that points nowhere, or to a clause that says something else, is worse than none: it looks checked. Section 3.3.4 comes back to this.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. A source tag is a claim, not a proof. Open the clause and read it: if it does not say what the answer says, the answer is unsupported, however confident it sounds."
     data-no="The tag names a clause. What would you do with that name before trusting the answer?">
  <p class="q">The agent recommends DECLINE for a request and cites <code>personal-trading-3</code>. What should the compliance officer do before approving the decline?</p>
  <label><input type="radio" name="ch31-q3" value="a"> Nothing; a cited answer has already been checked</label>
  <label><input type="radio" name="ch31-q3" value="b"> Ask the agent whether it is sure</label>
  <label><input type="radio" name="ch31-q3" value="c"> Read personal-trading-3 and check it says what the decline claims, for this request</label>
  <div class="fb"></div>
</div>
```

```{raw} html
<div class="wk-lcp" data-spot="ch03-retrieval" data-label="3.1 Retrieval and RAG · after §3.1.6 trade pre-clearance"></div>
```

## 3.1.7 Run it against a real model

The mock follows the retrieved clause because it was written to. A real model usually does, and it can also ignore a clause, blend two, or answer from training anyway. On the campus copy, the cells below use the GPT deployment on Illinois Azure through `/api/chat`, and embed any question you type through `/api/embed`; your browser never sees a key.

```{raw} html
<div class="wk-banner wk-pages-only">Model cells need the campus copy of this book: <a data-campus="/ch03-retrieval-rag.html#run-it-against-a-real-model" href="#">open it there</a> and sign in with your @illinois.edu account. Everything else on this page works here.</div>
```

First, retrieval on its own. Type your own question about the handbook and compare the four methods:

```{code-block} python
:class: pyodide
from retrieval import search, show

q = "Can I accept concert tickets from a company we cover?"
for method in ["keyword", "semantic", "hybrid", "rerank"]:
    print(f"\n{method}:")
    show(search(q, method))
```

Then the whole RAG step with a real model. Does it follow the retrieved clause, and does it cite it?

```{code-block} python
:class: pyodide
from agent import agent
from llm import azure_model
from retrieval import with_sources

q = "Can I accept concert tickets from a company we cover?"
system = "You answer employees' questions about the firm's handbook. Use only the passages below, and cite the id you relied on as [source: id].\n" + with_sources(q, k=3)
answer, log = agent(q, model=azure_model, system=system)
```

Change `k=3` to `k=1` and ask again. With one passage, did it still find the rule, or answer without it?

## 3.1.8 Exercise

Open the Colab notebook. It loads this handbook, chunks it, embeds it, and builds keyword, semantic and hybrid search and a reranker that asks `glm-5.3-flash` on Lumen to score each candidate (see [Setup](setup.md) for the key).

1. Find a question of your own where hybrid search ranks the right clause first and semantic search does not. Then find one where the reranker changes the top answer. Write down why, in a sentence each.
2. Re-chunk the handbook with fixed 40-word chunks and a 10-word overlap, and run the five questions from section 3.1.4 again. Which ones got worse, and why?
3. The retrieval-augmented agent in the notebook cites a clause id. Add a check in code, after the model answers, that the cited id exists and that the clause shares at least one key term with the answer. What does the check catch, and what can it not catch?

## Further reading

- Patrick Lewis and others, [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401) (2020) — the paper that named RAG.
- Anthropic, [*Introducing Contextual Retrieval*](https://www.anthropic.com/news/contextual-retrieval) (2024) — why chunks lose their context, and how adding a sentence of context to each chunk plus hybrid search and reranking cut retrieval failures.
- OpenAI, [*Vector embeddings*](https://platform.openai.com/docs/guides/embeddings) — the embedding model this chapter uses, and what the numbers are for.
- Pinecone, [*Chunking Strategies for LLM Applications*](https://www.pinecone.io/learn/chunking-strategies/) — fixed size, overlap and structure-aware chunking, with the trade-offs.
- Stephen Robertson and Hugo Zaragoza, [*The Probabilistic Relevance Framework: BM25 and Beyond*](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf) (2009) — where keyword ranking's formula comes from.
- Gordon Cormack, Charles Clarke and Stefan Büttcher, [*Reciprocal Rank Fusion outperforms Condorcet and individual rank learning methods*](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) (2009) — the one-line formula hybrid search uses to merge two rankings.
