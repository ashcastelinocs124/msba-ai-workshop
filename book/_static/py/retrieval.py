"""Retrieval over the firm's handbook (section 3.1): keyword, semantic, hybrid and rerank.

Every function returns a ranked list of {"id", "text", "score"}, best first. The meaning-vectors
come from embeddings.py, made once with Azure's text-embedding-3-small; a question the chapter
did not script is embedded live on the campus copy of the book, and falls back to keyword search
elsewhere.

ponytail: a Python list and cosine similarity over ~70 clauses; a vector database (pgvector,
Azure AI Search) is the upgrade when the corpus is thousands of documents.
"""
import math
import re

from handbook import CLAUSES, HANDBOOK
from embeddings import CHUNK_VECS, QUESTION_VECS

CHUNKS = CLAUSES
_BY_ID = {c["id"]: c for c in CHUNKS}
_STOP = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are", "be", "can", "i", "my", "we",
         "our", "it", "any", "after", "before", "what", "does", "do", "may", "must", "with", "at", "by", "from",
         "how", "if", "me", "you", "your", "this", "that", "about", "say", "says", "there", "them", "they"}

# Questions the chapter's cells and widgets use. Each has a stored meaning-vector, so they work
# on every copy of the book. PRESETS are the retrieval-comparison cases of section 3.1.4: which
# clause is right, which methods rank it first ("hit") and which do not ("miss").
PRESETS = [
    {"q": "Can I trade during the quiet period after we publish?", "expect": "personal-trading-2",
     "hit": ["semantic", "hybrid", "rerank"], "miss": ["keyword"],
     "why": "The handbook never says quiet period; it says blackout window. Keyword search matches trade and period in a clause about shares an employee owned before joining the firm. Meaning search sees that a quiet period after publishing is the blackout window, and hybrid and rerank keep that."},
    {"q": "Can I short NVIDIA?", "expect": "personal-trading-6",
     "hit": ["keyword", "hybrid"], "miss": ["semantic", "rerank"],
     "why": "The rule says short sales are not permitted. Keyword search finds the rare word short. Meaning search ranks the hardship-exception clause first, because it is also about selling. Hybrid rescues it; this rerank, which leans on meaning, does not."},
    {"q": "Is a $150 bottle of wine from a vendor OK?", "expect": "gifts-1",
     "hit": ["semantic", "rerank"], "miss": ["keyword", "hybrid"],
     "why": "The word vendor pulls keyword search to the data-licensing clauses. Meaning search knows a bottle of wine is a gift. Hybrid merges the two lists, and the data-licensing clauses keyword liked push gifts-1 down to fifth. The rerank reads each candidate again and puts gifts-1 first."},
    {"q": "Who approves my trade?", "expect": "pre-clearance-4",
     "hit": ["semantic", "rerank"], "miss": ["keyword", "hybrid"],
     "why": "Keyword search matches trade in a clause about shares an employee owned before joining the firm, which says nothing about who approves. Meaning search finds the clause saying only a compliance officer can approve, and the rerank restores it after hybrid lets the AI-assistants clause edge ahead."},
    {"q": "Do I need permission to buy an S&P 500 index fund?", "expect": "personal-trading-7",
     "hit": [], "miss": ["keyword", "semantic", "hybrid", "rerank"],
     "why": "Every method puts the general pre-clearance rule first, and the index-fund exemption second or lower. This is why a retrieval step hands the model the top three, not only the top one."},
]
SCRIPTED_QUESTIONS = [
    "Can Tom sell his Deere shares 6 days after we published research on Deere?",
    "Can I dump my Caterpillar shares a week after buying them?",
    "Can I offload stock I picked up last week?",
    "How long is an approval good for?",
    "Is a $150 bottle of wine from a vendor OK?",
    "What is the limit on gifts?",
    "Does my wife's brokerage account count?",
    "Do I need permission to buy an S&P 500 index fund?",
    "Can I paste FactSet estimates into ChatGPT?",
    "Can I tell a client our new rating before 7 am?",
    "Who approves my trade?",
    "What happens if I break the rules?",
    "Can the assistant approve a trade request?",
    "Can I sit on the board of a tractor company?",
    "What should I do with a suspicious email?",
    "security@champaigncapital.example",
    "Can I short NVIDIA?",
    "What does the embargo rule say?",
    "Can I trade during the quiet period after we publish?",
    "How quickly must I report a lost phone?",
    "Can the agent's notes be used as a source?",
    "Is the restricted list secret?",
    "premium economy",
    "Can I buy puts on Caterpillar?",
    "How long do we keep emails?",
    "Can I invest in my friend's start-up?",
    "Can I use WhatsApp to message a client?",
    "Who pays when I visit a company's factory?",
    "blackout window",
    "minimum holding period",
    "sell shares I bought recently",
]


def norm(q):
    """A question's lookup key: lower case, single spaces, no closing punctuation."""
    return re.sub(r"\s+", " ", q.strip().lower()).rstrip("?.! ")


def chunk(text, size, overlap=0):
    """Cut text into pieces of `size` words, each starting `size - overlap` words after the last."""
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("size must be positive and overlap smaller than size")
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, max(len(words) - overlap, 1), step)]


def _terms(text):
    words = (w.strip(".") for w in re.findall(r"[a-z0-9$@.]+", text.lower()))   # keeps security@champaigncapital.example whole
    return [w for w in words if w and w not in _STOP]


_DOC_TERMS = {c["id"]: _terms(c["text"]) for c in CHUNKS}
_AVG = sum(len(t) for t in _DOC_TERMS.values()) / len(_DOC_TERMS)
_DF = {}
for _t in _DOC_TERMS.values():
    for _w in set(_t):
        _DF[_w] = _DF.get(_w, 0) + 1


def _top(scores, k):
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])[:k]
    return [{"id": i, "text": _BY_ID[i]["text"], "score": round(s, 3)} for i, s in ranked if s > 0]


def bm25(q, k=3, k1=1.5, b=0.75):
    """Keyword search: rewards chunks that share the question's rarer words."""
    n, qt, scores = len(CHUNKS), set(_terms(q)), {}
    for cid, terms in _DOC_TERMS.items():
        s = 0.0
        for w in qt:
            f = terms.count(w)
            if f:
                idf = math.log(1 + (n - _DF[w] + 0.5) / (_DF[w] + 0.5))
                s += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * len(terms) / _AVG))
        scores[cid] = s
    return _top(scores, k)


def _cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


_warned = set()


def embed(q):
    """The question's meaning-vector: stored if the chapter scripted it, live on the campus copy, else None."""
    v = QUESTION_VECS.get(norm(q))
    if v:
        return v
    try:
        from llm import azure_embed
        return azure_embed(q)
    except Exception:
        if norm(q) not in _warned:
            _warned.add(norm(q))
            print("(This question has no stored meaning-vector, and live embedding needs the campus copy of the book. Using keyword search instead.)")
        return None


def semantic(q, k=3):
    """Meaning search: ranks chunks by how close their vector is to the question's."""
    v = embed(q)
    if v is None:
        return bm25(q, k)
    return _top({cid: _cos(v, CHUNK_VECS[cid]) for cid in CHUNK_VECS}, k)


def hybrid(q, k=3, depth=10, c=60):
    """Both rankings merged by reciprocal rank fusion: a chunk high on either list rises."""
    fused = {}
    for ranking in (bm25(q, depth), semantic(q, depth)):
        for rank, r in enumerate(ranking):
            fused[r["id"]] = fused.get(r["id"], 0) + 1 / (c + rank + 1)
    return _top(fused, k)


def rerank(q, k=3):
    """Take hybrid's top 10 and score each again, more carefully: meaning, plus exact phrases and the heading.

    ponytail: a production reranker is a cross-encoder or an LLM judge reading question and chunk together."""
    v, qt = embed(q), _terms(q)
    pairs = set(zip(qt, qt[1:]))
    scores = {}
    for r in hybrid(q, 10):
        ct = _DOC_TERMS[r["id"]]
        s = _cos(v, CHUNK_VECS[r["id"]]) if v else 0
        s += 0.05 * len(pairs & set(zip(ct, ct[1:])))
        s += 0.03 * len(set(qt) & set(_terms(_BY_ID[r["id"]]["heading"])))
        scores[r["id"]] = s
    return _top(scores, k)


METHODS = {"keyword": bm25, "semantic": semantic, "hybrid": hybrid, "rerank": rerank}


def search(q, method="hybrid", k=3):
    """Top-k handbook clauses for a question, by one of: keyword, semantic, hybrid, rerank."""
    return METHODS[method](q, k)


def similarity(q, chunk_id):
    """How close a question's meaning is to one clause's, from -1 to 1 (in practice 0 to about 0.7)."""
    v = embed(q)
    return round(_cos(v, CHUNK_VECS[chunk_id]), 3) if v else None


def with_sources(q, k=2):
    """The retrieved clauses as a block for the system prompt: what RAG puts on the desk (section 3.1.1)."""
    hits = hybrid(q, k)
    return "Handbook passages you may cite:\n" + "\n".join(f"[{h['id']}] {h['text']}" for h in hits)


def show(results):
    """Print a ranking one line per clause: rank, id, score, the start of the text."""
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['id']}] ({r['score']}) {r['text'][:90]}{'…' if len(r['text']) > 90 else ''}")


if __name__ == "__main__":
    # ponytail: self-check; run `python retrieval.py` from _static/py
    for p in PRESETS:
        for m in p["hit"]:
            assert search(p["q"], m)[0]["id"] == p["expect"], (m, p["q"], search(p["q"], m))
        for m in p["miss"]:
            assert search(p["q"], m)[0]["id"] != p["expect"], (m, p["q"])
    assert PRESETS, "no presets"
    assert "sold" in _DOC_TERMS["personal-trading-3"], _DOC_TERMS["personal-trading-3"]   # a clause's last word is searchable
    assert all(norm(q) in QUESTION_VECS for q in SCRIPTED_QUESTIONS)
    assert chunk("a b c d e", 2, 1) == ["a b", "b c", "c d", "d e"]
    for bad in [(0, 0), (3, 3), (2, -1)]:
        try:
            chunk("a b c", *bad)
            raise AssertionError(bad)
        except ValueError:
            pass
    assert isinstance(semantic("an unscripted question about parking"), list)   # off campus: falls back, no crash
    assert with_sources("Can Tom sell his Deere shares 6 days after we published research on Deere?").count("[personal-trading-2]") == 1
    print("ok")
