# 0D What an API Is

```{raw} html
<p class="wk-lede">The agent in chapter 1 never reads a filing. It asks another program for the figures, and that program answers. That request and answer is an API call. See what one looks like, how the firm already depends on dozens of them, and what changes when the program answering is an AI model. This page is pre-reading, with no session of its own.</p>
```

```{raw} html
:file: widgets/goal-map.html
```

```{admonition} Learning objectives
:class: note
- Say what an API is and name the parts of one call: the address, the key, the request and the response.
- Explain how a business both buys and sells through APIs, and what it pays for.
- Describe how an AI API differs from a classic one, and why chapter 1's agent calls APIs itself.
```

## 0D.1 What an API is

When Marcus opens his spreadsheet on Monday, Deere's latest quarterly revenue is already in it. Nobody typed it in and nobody read a filing. The spreadsheet asked a market-data vendor's computer for the figure, and the vendor's computer answered in a fraction of a second.

The agreement that makes that possible is an **API**, short for application programming interface: a contract between two programs. It says, in effect, *send me a request in this shape, to this address, with this key, and I will send back an answer in that shape.* A person never has to click anything.

Every API call has the same four parts:

- **The address.** Where the request goes, written like a web address, for example `https://api.marketdata.example/v2/financials`.
- **The key.** A long secret string that says who is asking. It is how the vendor knows the firm has paid, and how it counts the calls. Treat it like a password.
- **The request.** What you want, in the fields the API expects: here, a ticker (`DE`) and a period (`Q2-2026`).
- **The response.** The answer, as structured data rather than a paragraph, usually in a format called JSON: labelled fields a program can read without guessing. It comes with a **status code** that says how the call went: `200 OK`, or a number that names the problem.

A restaurant menu is a fair picture of it. You can order only what is on the menu, in the way the menu describes, and the kitchen's workings are none of your business. You get back exactly what you ordered, or a waiter telling you why not.

Send one request to each kind of API and compare what comes back. Then send the same request again:

```{raw} html
:file: widgets/ch00-api-call.html
```

The classic API returned four labelled fields and would return the same four fields every time. The status codes are its way of complaining: `401` means the key is missing or wrong, `404` means there is no such thing (a ticker the vendor does not cover), and `429` means too many calls too quickly.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="b"
     data-ok="Correct. 401 Unauthorized means the API does not accept who is asking: a missing, mistyped or expired key. A bad ticker would come back as 404, and a server problem as a 500-something."
     data-no="Each status code names a different problem. Which part of the call says who is asking?">
  <p class="q">Priya's script asks the market-data API for Deere's revenue and gets <code>401 Unauthorized</code> back. What is most likely wrong?</p>
  <label><input type="radio" name="api-q1" value="a"> The ticker DE does not exist</label>
  <label><input type="radio" name="api-q1" value="b"> Her API key is missing, mistyped or expired</label>
  <label><input type="radio" name="api-q1" value="c"> The vendor's servers are down</label>
  <div class="fb"></div>
</div>
```

## 0D.2 How companies use APIs

Almost every piece of software a company runs is talking to other companies' software through APIs. Champaign Capital Research is typical:

| API | What the firm gets | How it pays |
|---|---|---|
| Market-data vendor | Prices, estimates and reported financials for the names it covers | An annual licence per seat; the contract says the raw data may not be passed on to clients |
| SEC EDGAR | Every filing a US-listed company makes | Free, but callers must say who they are and stay under 10 requests a second |
| Email and client-relationship software | Sending notes to clients, logging who called about what | A monthly fee per user |
| Lumen, and Azure AI on the campus copy | A language model to call | Per token |
| **Its own research API** | Clients' systems pull the firm's notes and ratings directly | The firm **sells** this one, as part of the subscription |

Three things are worth noticing in that table.

**An API is a product.** For the market-data vendor, the API *is* what it sells, and the price list is written in calls, seats and data sets. Payments companies such as Stripe and messaging companies such as Twilio built whole businesses on this: other firms pay per call rather than build the thing themselves.

**The contract matters as much as the code.** The key ties every call to a paying customer, the rate limit protects the provider, and the licence says what you may do with the answer. The firm's rule against passing raw vendor data to clients is a licensing term, not a technical one, and it will come back in chapter 2 when a client asks for exactly that.

**Companies both buy and sell.** The firm buys data through four APIs and sells its own research through a fifth. When a pension-fund client's portfolio system shows the firm's latest rating on Deere, that is the client calling the firm's API.

## 0D.3 What changes in the AI era

An AI model is also reached through an API. Your Lumen key from [Setup](setup.md) is an API key, and the campus copy's in-page cells call Azure through one. The four parts are the same: an address, a key, a request, a response. But four things change, and each one shapes the chapters that follow.

1. **The request is plain English.** A classic API accepts only the fields it defines; send an unknown ticker and it refuses. An AI API accepts any text, which makes it flexible and also means nothing stops a badly worded or hostile request. Checking what goes in, and what comes out, becomes your job (chapters 2 and 6).
2. **The same request can come back different.** You saw it in the widget: the wording changed on every call, because the model picks each next token with some randomness (chapter 0, section 0.3). The market-data API is deterministic; the model is not. That is why a figure the firm publishes comes from a tool, not from the model's memory.
3. **You pay per token, not per call.** The price depends on how much you send and how much comes back, so a long document or a long answer costs more. Chapter 2 counts those tokens.
4. **The model becomes the caller.** This is the biggest change. In a classic setup a programmer decides which API to call and writes the code that calls it. In chapter 1, you give the model a list of APIs, each with a short description of what it does and what it needs, and the model decides which one to call, with which inputs, and when to stop. Those APIs are called **tools**. Because a model now reads the descriptions, they have to be written for a model as much as for a programmer, and open standards such as the Model Context Protocol (MCP) exist so that one set of tools can be offered to any model.

One risk grows with all four: **data leaves the building.** Everything you put in a request to a hosted model is sent to the provider. A client's holdings pasted into a prompt have left the firm, which is one reason open-weight models run on hardware the firm controls ([page 0C](ch00-open-closed.md)) matter.

**Checkpoint.**

```{raw} html
<div class="quiz" data-answer="c"
     data-ok="Correct. The status code only says the call worked: the request arrived, the key was good, text came back. Whether the text is true is a separate question, which is why the firm checks every figure against a tool's result."
     data-no="What does 200 OK tell you about the call, and what does it not tell you about the text that came back?">
  <p class="q">Priya asks an AI API for Tesla's revenue growth last quarter. It returns <code>200 OK</code> and a confident percentage. The firm holds no Tesla data. What does the 200 tell her?</p>
  <label><input type="radio" name="api-q2" value="a"> The figure has been checked by the provider</label>
  <label><input type="radio" name="api-q2" value="b"> The model found the figure in a filing</label>
  <label><input type="radio" name="api-q2" value="c"> Only that the call worked; the percentage may still be wrong</label>
  <div class="fb"></div>
</div>
```

## 0D.4 Where you have already met one

- **Setup.** The Lumen key you created and saved in Colab Secrets is an API key. The notebooks send it with every request, and Lumen counts your tokens against it.
- **The campus copy.** When you run a cell against the real model, the page calls the book's own small API, which adds the firm's key and passes the request on to Azure. That is why the key never reaches your browser.
- **Chapter 1.** The agent's tools, `get_financials`, `get_price` and `search_docs`, are APIs the model calls. Section 1.7 designs one, and most of what can go wrong there is a badly written contract.

## Further reading

- IBM, [*What is an API?*](https://www.ibm.com/think/topics/api) — a plain-language overview of APIs and how businesses use them.
- Postman, [*What is an API?*](https://www.postman.com/what-is-an-api/) — the parts of a request and response, with examples.
- SEC, [*EDGAR Application Programming Interfaces*](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) — a real, free API for company filings, with its rules for callers.
- Stripe, [*API reference*](https://docs.stripe.com/api) — what a company that sells its API as the product publishes for its customers.
- OpenAI, [*Function calling*](https://platform.openai.com/docs/guides/function-calling) — how a model is given APIs to call, the idea behind chapter 1's tools.
- [*Model Context Protocol: introduction*](https://modelcontextprotocol.io/docs/getting-started/intro) — the open standard for offering tools to any model.
