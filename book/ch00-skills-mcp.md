# 0E Agent Skills and MCP

```{raw} html
<p class="wk-lede">An agent is only as useful as what it can reach and what it knows how to do. Two open standards now handle each: the Model Context Protocol (MCP) plugs an agent into the firm's data and tools, and Agent Skills hand it the firm's procedures, loaded only when a task needs them. This page is pre-reading, with no session of its own.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

```{admonition} Learning objectives
:class: note
- Explain the problem MCP solves, and what an MCP server offers an agent.
- Say how MCP differs from an API: who reads the instructions, and when the connection is made.
- Describe an agent skill, and why an agent loads it only when a task needs it.
- Say whether a need at the firm calls for an MCP server, a skill, or both.
```

## 0E.1 MCP: one standard plug

Page 0D showed that every data source has its own API, with its own address, key and request shape. Now connect three AI apps to four of the firm's sources: every app needs custom code for every source. Toggle MCP on, add a source, then watch one request go through:

```{raw} html
:file: widgets/ch00-mcp.html
```

The **Model Context Protocol** (MCP) is an open standard, released by Anthropic in November 2024 and now supported across the major AI apps, for connecting an AI app to data and tools. It is often compared to a USB-C port: one shape of plug, so any device fits any port.

- An **MCP server** wraps one source, such as the market-data vendor, and describes what it offers: its **tools** (actions, such as `get_financials`), and often **resources** (documents to read) and **prompts** (ready-made instructions).
- An **MCP client** lives inside the AI app. It asks each server what it offers, passes the tool descriptions to the model, and runs the calls the model chooses.

So the tools you wrote by hand in chapter 1 could be served once, as an MCP server, and every MCP-aware app at the firm could use them. The same cautions still apply: each server adds tool descriptions to the model's desk on every call, and a server can only do what its tools allow, which is why the firm's servers are read-only.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. Without a standard, each of the three apps needs its own connection to the new source. With MCP, the source is wrapped once as a server, and every app that speaks MCP can use it."
     data-no="Count the connections in the widget before and after you add a source, with MCP off and on.">
  <p class="q">The firm connects three AI apps to its data. It adds earnings-call transcripts as a new source. How many new connections does it need with MCP?</p>
  <label><input type="radio" name="mcp-q1" value="a"> Three, one for each app</label>
  <label><input type="radio" name="mcp-q1" value="b"> One: a single MCP server for the transcripts</label>
  <label><input type="radio" name="mcp-q1" value="c"> None, because the model already knows the transcripts</label>
  <div class="fb"></div>
</div>
```

## 0E.2 MCP vs API: written for developers, written for agents

If MCP servers answer requests, how is that different from the APIs on page 0D? The difference is who reads the instructions.

An **API is built for a human developer**. Its documentation is a web page: a person reads it, works out which address to call and what each field means, and writes code for that one API, weeks before anyone asks a question. The program can make only the calls someone wired up, and when the API changes, a person has to read about it and change the code.

**MCP is built for an agent**. An MCP server describes itself, in words a model reads while it is working: which tools it has, what each is for and when not to use it, and exactly which inputs each accepts. The agent asks for that list when it needs it, reads it, and decides what to call. Nobody writes code for that particular source.

Play both lanes, then change the vendor's data:

```{raw} html
:file: widgets/ch00-api-vs-mcp.html
```

| | API | MCP |
|---|---|---|
| Who reads the instructions | A developer, in documentation written for people | The model, in descriptions written for models |
| When the connection is made | In advance, in code, one API at a time | At the moment of the request, by asking the server |
| What can be called | Only what the developer wired up | Any tool the server lists |
| When the source changes | Someone updates code in every app that uses it | The server's description changes; agents read it next time |

MCP does not replace APIs. A market-data MCP server usually calls the vendor's API underneath; MCP adds a layer that an agent can read and use on its own. And because the model now decides which tool to call, the quality of those descriptions matters as much as the code, which is the lesson of chapter 1's section 1.7.

## 0E.3 Agent skills: know-how on demand

MCP gives an agent access. It does not tell the agent how the firm does things: how a note is laid out, which rules a trade request is checked against, what may never go to a client. Chapter 2 put that know-how in the system prompt, where it is read on every call whether it is needed or not.

An **agent skill** is a folder with a file called `SKILL.md`: a name, a one-line description, and step-by-step instructions, sometimes with scripts or reference files beside them. The agent keeps only each skill's name and description on its desk. When a request matches a description, it opens that skill and reads the full instructions for that task alone. Pick a request:

```{raw} html
:file: widgets/ch00-skills.html
```

This is context engineering (section 2.2) done by the agent: the firm can keep dozens of procedures ready without paying for all of them on every call. Agent Skills started at Anthropic in October 2025 and are published as an open format, so a skill written once can be used by different agents.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. Only the names and descriptions sit on the desk; a skill's full instructions load when a request matches its description. The firm can keep many procedures ready and pay for the one it uses."
     data-no="Look at the meter in the widget: what is on the desk before you pick a request, and what gets added after?">
  <p class="q">The firm has written 40 skills. What does the agent read about them on a typical call?</p>
  <label><input type="radio" name="mcp-q2" value="a"> All 40 skills in full, so it never misses one</label>
  <label><input type="radio" name="mcp-q2" value="b"> Nothing, until a person tells it which skill to use</label>
  <label><input type="radio" name="mcp-q2" value="c"> The 40 names and descriptions, plus the full text of the one or two that match the request</label>
  <div class="fb"></div>
</div>
```

## 0E.4 MCP or a skill?

| | MCP server | Agent skill |
|---|---|---|
| Gives the agent | **Access**: data it can read, actions it can take | **Know-how**: how the firm does a task |
| Made of | A program that answers the MCP protocol | A folder with `SKILL.md`, sometimes scripts |
| At Champaign Capital | Market data, SEC EDGAR, the client CRM, the handbook | Writing a research note, trade pre-clearance, replying to a client |
| On the desk | Every tool's description, on every call | One line per skill, the full text only when used |

They work together. The `earnings-comparison` skill tells the agent *how* to compare growth; the market-data MCP server is *where* the figures come from. Chapter 1 builds the loop that ties them together.

## Further reading

- Anthropic, [*Introducing the Model Context Protocol*](https://www.anthropic.com/news/model-context-protocol) (November 2024) — the announcement, and the problem it set out to solve.
- [*Model Context Protocol: introduction*](https://modelcontextprotocol.io/docs/getting-started/intro) — servers, clients, tools and resources, with diagrams.
- Anthropic, [*Introducing Agent Skills*](https://www.anthropic.com/news/skills) — what a skill is and how agents load them.
- Anthropic, [*Equipping agents for the real world with Agent Skills*](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — why skills load in stages, from the engineers who built them.
- [*Agent Skills*](https://agentskills.io) — the open format, for skills that work across agents.
