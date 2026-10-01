# 3. Memory Retrieval and RAG

```{raw} html
<p class="wk-lede">A model knows what it read in training, and nothing the firm wrote after that. It never read Champaign Capital's handbook, and it does not remember last week's client call. This chapter puts both on the desk: retrieval finds the right handbook clause for each question, and memory brings back what a client told us before.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

Chapter 2 made the desk: code decides what the model reads on each call. It retrieved one clause with a keyword match over twelve short passages, and it carried the last exchange by pasting it back in. Neither lasts. The real handbook has seventy-three clauses, and the words a person uses are rarely the words the handbook uses. And a client who asks a follow-up next week is in a new session, with an empty desk.

This chapter takes each problem in turn, in three parts taught in the same session:

- **[3.1 Retrieval and RAG](ch03-retrieval-rag.md).** Cut the handbook into chunks, turn each chunk into numbers that capture its meaning, and find the right one for a question four different ways. Then let the agent decide when to search, and finish with Elena's trade pre-clearance requests, each answered with a cited clause.
- **[3.2 Short-Term Memory](ch03-agent-memory.md).** Keep a conversation going when it outgrows the desk, by trimming or summarizing it, and see what each one loses.
- **[3.3 Long-Term Memory](ch03-long-term-memory.md).** Save what matters between sessions, and decide who writes the notes: the system around the agent, or the agent itself. Sort notes into episodic, semantic and procedural memory, guard against a wrong note, then see how two real frameworks, the OpenAI Agents SDK and LangGraph, do the same thing.

Section 3.1 has its own Colab notebook; 3.2 and 3.3 share one.

(ch03-lecture)=
## Watch the lecture

The session 3 recording and slides will appear here after the session on Friday, October 2.
