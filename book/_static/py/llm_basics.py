"""Chapter 0's toy language model: a tokenizer, and a next-word model trained on thirteen sentences of the firm's memos.

    from llm_basics import show_tokens, next_word_probs, generate, fact_check

ponytail: both are deliberately tiny. The tokenizer matches pieces from a hand-made vocabulary, where a real one
learns ~100,000 pieces from data; the model counts which word follows which (a bigram model), where a real LLM
predicts tokens with a neural network trained on trillions of them. The mechanics shown (split into pieces,
predict the next one, sample with a temperature) are the real ones. The widget ch00-next-token.html carries a
copy of CORPUS, so keep the two in step.
"""
import random
import re
from collections import Counter, defaultdict

from tools import FINANCIALS

# --- tokens -----------------------------------------------------------------------------------------------

# Common words are one piece; less common names are split into smaller pieces. A leading space is part of a piece.
VOCAB = [" revenue", " growth", " grew", " faster", " than", " the", " last", " quarter", " year", " to", " of",
         " is", " and", " a", " from", " base", " smaller", " larger", " client", " memo", " prompt",
         "Deere", " Deere", "Apple", " Apple", "NVIDIA", " NVIDIA", "Micro", " Micro", "soft",
         "Cater", " Cater", "pillar", "'s", "%", "$", "B", ".", ",", "?"]
_VOCAB = sorted(set(VOCAB), key=len, reverse=True)


def tokenize(text):
    """Split text into pieces: the longest vocabulary piece that fits, else one character."""
    pieces, i = [], 0
    while i < len(text):
        piece = next((v for v in _VOCAB if text.startswith(v, i)), text[i])
        pieces.append(piece)
        i += len(piece)
    return pieces


def show_tokens(text):
    """Print a sentence as the pieces a model reads, with · for a space."""
    pieces = tokenize(text)
    print(f"{len(text.split())} words → {len(pieces)} tokens")
    print(" ".join(f"[{p.replace(' ', '·')}]" for p in pieces))


# --- next-word prediction -------------------------------------------------------------------------------------

# Everything the toy model ever reads. A real model reads trillions of tokens; this one reads thirteen sentences.
CORPUS = [
    "Deere grew revenue faster than Caterpillar .",
    "Deere grew revenue 6.4% to $13.8B .",
    "Caterpillar grew revenue 3.1% to $16.9B .",
    "NVIDIA grew revenue faster than Apple .",
    "NVIDIA grew revenue 58.0% to $52.4B .",
    "Apple grew revenue 5.0% to $96.1B .",
    "Microsoft grew revenue 17.0% to $76.3B .",
    "Microsoft grew revenue faster than Apple .",
    "Deere grew revenue faster than Caterpillar from a smaller base .",
    "NVIDIA is growing faster than Microsoft .",
    "Deere is growing faster than Caterpillar .",
    "Caterpillar is larger than Deere by revenue .",
    "Apple is larger than NVIDIA .",
]

_FOLLOWS = defaultdict(Counter)
for _sentence in CORPUS:
    _words = _sentence.split()
    for _a, _b in zip(_words, _words[1:]):
        _FOLLOWS[_a][_b] += 1


def next_word_probs(word, temperature=1.0):
    """Every word the model has seen after `word`, with its probability, most likely first.
    Temperature reshapes the odds: below 1 the favourite gets more likely, above 1 the long shots do."""
    counts = _FOLLOWS.get(word)
    if not counts:
        return []
    if temperature <= 0:
        best = max(counts.values())
        tops = [w for w, c in counts.items() if c == best]
        return [(w, 1 / len(tops) if w in tops else 0.0) for w, _ in counts.most_common()]
    weights = {w: c ** (1 / temperature) for w, c in counts.items()}
    total = sum(weights.values())
    return sorted(((w, x / total) for w, x in weights.items()), key=lambda wp: -wp[1])


def generate(start, temperature=0.0, seed=0, max_words=12):
    """Write a sentence one word at a time, each word picked from next_word_probs. temperature=0 always takes the favourite."""
    rng, words = random.Random(seed), [start]
    while words[-1] != "." and len(words) < max_words:
        probs = next_word_probs(words[-1], temperature)
        if not probs:
            break
        if temperature <= 0:
            words.append(probs[0][0])
        else:
            words.append(rng.choices([w for w, _ in probs], weights=[p for _, p in probs])[0])
    return " ".join(words)


# --- checking what it wrote -------------------------------------------------------------------------------------

_BY_NAME = {row["name"]: row for (ticker, period), row in FINANCIALS.items() if period == "Q2-2026"}


def fact_check(sentence):
    """Compare the growth rate and revenue a sentence claims with the firm's records for that company."""
    name = sentence.split()[0]
    row = _BY_NAME.get(name)
    growth = re.search(r"(\d+\.\d)%", sentence)
    revenue = re.search(r"\$(\d+\.\d)B", sentence)
    if not row or not (growth or revenue):
        return "no figures to check"
    wrong = []
    if growth and abs(float(growth.group(1)) - row["yoy"] * 100) > 0.05:
        wrong.append(f"growth was {row['yoy'] * 100:.1f}%, not {growth.group(1)}%")
    if revenue and abs(float(revenue.group(1)) - row["revenue"] / 1e9) > 0.05:
        wrong.append(f"revenue was ${row['revenue'] / 1e9:.1f}B, not ${revenue.group(1)}B")
    return "matches the records" if not wrong else "WRONG: " + name + "'s " + " and ".join(wrong)


if __name__ == "__main__":
    assert tokenize("Caterpillar's revenue") == ["Cater", "pillar", "'s", " revenue"]
    assert "".join(tokenize("Deere grew revenue 6.4% to $13.8B.")) == "Deere grew revenue 6.4% to $13.8B."
    assert next_word_probs("revenue")[0][0] == "faster"
    assert abs(sum(p for _, p in next_word_probs("revenue", 1.7)) - 1) < 1e-9
    assert next_word_probs("revenue", 0.3)[0][1] > next_word_probs("revenue", 1.0)[0][1] > next_word_probs("revenue", 2.0)[0][1]
    assert generate("Deere") == "Deere grew revenue faster than Caterpillar ."
    assert fact_check("Deere grew revenue 6.4% to $13.8B .") == "matches the records"
    assert fact_check("Deere grew revenue 58.0% to $96.1B .").startswith("WRONG: Deere's growth was 6.4%")
    assert fact_check("Deere grew revenue faster than Caterpillar .") == "no figures to check"
    samples = [generate("Deere", temperature=1.5, seed=s) for s in range(40)]
    assert any(fact_check(s).startswith("WRONG") for s in samples), "high temperature should produce a false figure"
    print("llm_basics.py self-check passed")
