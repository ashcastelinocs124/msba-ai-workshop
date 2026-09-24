# The firm: Champaign Capital Research

```{raw} html
<p class="wk-lede">Every chapter of this book is set at one company. Read this page first: the people, the product, and the plan are the same from chapter 1 to chapter 9.</p>
```

## The business

Champaign Capital Research is an independent equity research firm in Champaign, Illinois, with a second office in Chicago. It employs 38 people: 14 analysts, 6 associates, 2 compliance officers, a data team of 3, sales, and operations. About 120 institutional clients, mostly pension funds, endowments, and mid-sized asset managers, pay an annual subscription for its research on three sectors: industrials, agricultural equipment, and semiconductors.

The product is the written note. A note takes an analyst between two days and two weeks: pulling filings and vendor data, re-running a model, writing the view, getting compliance sign-off, and publishing. Clients then call with follow-up questions, and answering those is where a surprising share of the week goes.

```{raw} html
:file: widgets/firm-glance.html
```

## The problem

Three things eat the firm's time, and none of them is the hard part of the job.

1. **Lookups.** A client asks for Deere's revenue growth last quarter and how it compares with Caterpillar. The answer is in a filing the analyst has already read. Finding it, checking it, and writing it back takes forty minutes, thirty times a week across the firm.
2. **Handbook checks.** Can an analyst quote a vendor's raw estimates in a note? Is a trip's hotel within policy? The handbook is twelve pages. People ask a colleague instead of reading it, and get different answers.
3. **Pre-clearance.** Every employee must ask compliance before trading a stock in a covered sector. Elena Ruiz's team handles about thirty requests a week by email, checking each against the restricted list, the blackout window, and the holding-period rule. It is careful work, and it is the same work every time.

Each of these is a lookup followed by a short judgment. The firm's plan for the year is to hand the lookups to software and keep the judgments with people.

## How a note gets made

```{raw} html
:file: widgets/firm-pipeline.html
```

## The plan for the year

The firm is adopting agents and machine learning one careful step at a time, and this book follows that roadmap. Each chapter is one task that lands on the data team's desk.

```{raw} html
:file: widgets/firm-roadmap.html
```

## The people

```{raw} html
:file: widgets/firm-people.html
```

None of them are real. The problems are: the fixture data behind every cell in this book (filings figures, the policy handbook, the pre-clearance requests) is modeled on what a firm like this actually keeps.

## Your first Monday

You have just joined the data team. Your inbox has three items in it:

1. A portfolio manager at a pension fund client wants Deere's revenue growth last quarter, compared with Caterpillar, by noon.
2. Elena has forwarded four trade pre-clearance requests from staff.
3. Priya asks whether the handbook lets her quote a data vendor's raw estimates in a client note.

Chapter 1 starts with the first item. By the end of it, you will have built the thing that answers all three.
