"""Champaign Capital Research's compliance handbook, in full (chapter 3).

docs.py holds twelve of these clauses, word for word, for chapters 1 and 2. Chapter 3 retrieves
over the whole handbook: section 3.1 chunks it, embeds it and searches it, and section 3.2's
agent notes are governed by its last section. Each clause is one dict on one line with its id
first and its text second; the Watch view reads that pattern to highlight a cited clause.
"""
SECTIONS = [
    {"heading": "1. Purpose and scope", "clauses": [
        {"id": "scope-1", "text": "This handbook sets out the rules every employee of Champaign Capital Research follows when trading for their own account, publishing research, handling client and vendor data, and using firm systems."},
        {"id": "scope-2", "text": "It applies to all 38 employees in the Champaign and Chicago offices, to contractors with access to research systems, and to interns from their first day. Nobody is exempt because of seniority or role."},
        {"id": "scope-3", "text": "Compliance, led by Elena Ruiz, owns this handbook, answers questions about it, and reviews it every January. Where a rule is unclear, ask compliance before you act rather than after."},
        {"id": "scope-4", "text": "Breaking a rule in this handbook can lead to a written warning, the reversal of a trade at the employee's own cost, loss of a bonus, or dismissal. Serious breaches are reported to regulators."},
    ]},
    {"heading": "2. Personal trading", "clauses": [
        {"id": "personal-trading-1", "text": "Employees must obtain compliance pre-clearance before trading any security in a sector the firm covers."},
        {"id": "personal-trading-2", "text": "Blackout window: no employee may trade a security within 14 days before or after the firm publishes research on it."},
        {"id": "personal-trading-3", "text": "Minimum holding period: positions in covered securities must be held at least 30 days before they are sold."},
        {"id": "personal-trading-4", "text": "The covered sectors are industrials, agricultural equipment and semiconductors. Compliance publishes the full list of covered companies on the intranet, and a company stays covered for 90 days after the firm drops coverage."},
        {"id": "personal-trading-5", "text": "These rules apply to every account an employee can influence: their own, a spouse's or partner's, a dependent child's, and any trust or investment club in which they make or suggest decisions."},
        {"id": "personal-trading-6", "text": "Options, warrants, convertible bonds and single-stock futures on a covered company count as trades in that company. Short sales of covered securities are not permitted at all."},
        {"id": "personal-trading-7", "text": "Broad index funds, exchange-traded funds that track a whole market, money-market funds and government bonds are exempt from pre-clearance, the blackout window and the minimum holding period."},
        {"id": "personal-trading-8", "text": "If a price falls sharply and an employee needs to sell a covered position before the minimum holding period ends, they may ask compliance for a hardship exception. Exceptions are rare, recorded, and never granted inside the blackout window."},
        {"id": "personal-trading-9", "text": "Employees must give compliance duplicate statements for every brokerage account within 10 days of joining and every quarter after that. Compliance compares them with pre-clearance records."},
    ]},
    {"heading": "3. Pre-clearance procedure", "clauses": [
        {"id": "pre-clearance-1", "text": "To request pre-clearance, email compliance with the ticker, whether you want to buy or sell, the number of shares, and the account. Each request receives a four-digit request number."},
        {"id": "pre-clearance-2", "text": "Compliance checks each request against the restricted list, the date the firm last published research on the company, and, for a sale, how long the position has been held."},
        {"id": "pre-clearance-3", "text": "An approval is valid until the end of the next business day. An order not filled by then needs a new request, and a partly filled order needs a new request for the rest."},
        {"id": "pre-clearance-4", "text": "Only a compliance officer can approve a request. A recommendation from a colleague, a manager, or a software assistant is advice to compliance, not an approval, and trading on it is a breach."},
        {"id": "pre-clearance-5", "text": "Compliance aims to answer every request within four business hours. A request received after 3 pm is answered the next business morning."},
        {"id": "pre-clearance-6", "text": "A declined request can be submitted again once the reason has passed, for example after the blackout window ends or the holding period is complete. Compliance does not keep a queue of declined requests."},
    ]},
    {"heading": "4. Restricted list", "clauses": [
        {"id": "restricted-list-1", "text": "Securities on the restricted list may not be traded by any employee; compliance maintains the list and reviews it weekly."},
        {"id": "restricted-list-2", "text": "A company is added to the restricted list when the firm is preparing a new report on it, when an employee holds material non-public information about it, or when a client relationship creates a conflict."},
        {"id": "restricted-list-3", "text": "The restricted list is confidential. Do not tell anyone outside the firm which companies are on it, because the list itself can reveal research the firm has not yet published."},
        {"id": "restricted-list-4", "text": "If you learn something about a company that may not be public, tell compliance at once and do not trade or discuss it. Compliance decides whether the company goes on the restricted list."},
    ]},
    {"heading": "5. Research process", "clauses": [
        {"id": "research-process-1", "text": "Every figure in a published note must cite its source document or data vendor field; uncited figures block publication."},
        {"id": "research-process-2", "text": "Financial models are re-run on the latest filings before a note is published, and the run is logged with a timestamp."},
        {"id": "research-process-3", "text": "A second analyst reviews every note before publication and checks each figure against its cited source. The reviewer signs the review log; a note without a signed review cannot be published."},
        {"id": "research-process-4", "text": "Analysts may use software assistants to draft text, look up figures and summarize filings. The analyst remains responsible for every word and figure, and must check each figure the assistant produced against its source."},
        {"id": "research-process-5", "text": "Corrections to a published note are issued as a dated correction notice sent to every client who received the note. The original note is never silently edited."},
    ]},
    {"heading": "6. Publication and embargo", "clauses": [
        {"id": "publication-1", "text": "Research is published to all subscribing clients at the same time, at 7 am Central, through the client portal. No client may receive a note, a rating or a price target before the others."},
        {"id": "publication-2", "text": "A note is under embargo from the moment its draft is approved until it is published. During the embargo its conclusions may not be discussed with clients, the press or anyone outside the research team."},
        {"id": "publication-3", "text": "Changes of rating or price target are published only as part of a full note. They are never announced first by email, phone, chat or social media."},
        {"id": "publication-4", "text": "When the firm starts or stops covering a company, compliance records the date. That date starts the blackout window and the 90-day covered period for personal trading."},
    ]},
    {"heading": "7. Data licensing", "clauses": [
        {"id": "data-licensing-1", "text": "Raw vendor data (prices, fundamentals, estimates) may not be redistributed to clients; only derived figures may appear in notes."},
        {"id": "data-licensing-2", "text": "A derived figure is one the firm calculated, such as a growth rate, a margin or a ratio. Copying a vendor's number into a note unchanged counts as redistribution, even with a citation."},
        {"id": "data-licensing-3", "text": "Vendor data may not be pasted into an outside website, chatbot or AI service that is not on the firm's approved-tools list, because the vendor's licence does not allow it to leave firm systems."},
        {"id": "data-licensing-4", "text": "Company filings, press releases and other public documents are not vendor data and may be quoted with a citation."},
    ]},
    {"heading": "8. Client service", "clauses": [
        {"id": "client-service-1", "text": "Client data requests are answered within one business day; investment recommendations are given only in published notes."},
        {"id": "client-service-2", "text": "Every client has a named contact at the firm. Requests go through that contact, who records each one in the client log with the date, the question and the reply."},
        {"id": "client-service-3", "text": "Client preferences, such as a preferred format or a sector of interest, are recorded on the client's card so every colleague answers in the same way. The card never holds personal data beyond a contact name and role."},
        {"id": "client-service-4", "text": "Replies to clients restate figures from published notes or filings with their source. An analyst may explain a published view but may not offer a new one in a private reply."},
    ]},
    {"heading": "9. Communications and social media", "clauses": [
        {"id": "communications-1", "text": "Business communication with clients happens only on firm email, the client portal and the firm's recorded phone lines. Personal messaging apps may not be used for firm business."},
        {"id": "communications-2", "text": "All business communications are archived for seven years and may be reviewed by compliance at any time."},
        {"id": "communications-3", "text": "Employees may not comment publicly on companies the firm covers, including on social media, podcasts or conference panels, without approval from compliance and the head of research."},
        {"id": "communications-4", "text": "Press enquiries go to the managing partner. Do not answer a journalist's question about a covered company, even informally or off the record."},
    ]},
    {"heading": "10. Gifts and entertainment", "clauses": [
        {"id": "gifts-1", "text": "Employees may accept gifts from clients, vendors or companies the firm covers worth up to $100 per giver per year. Anything more valuable is declined or handed to compliance."},
        {"id": "gifts-2", "text": "Meals and events with a client or vendor are allowed when the host attends and the purpose is business. Travel or hotel costs paid by a covered company are never accepted."},
        {"id": "gifts-3", "text": "Every gift or entertainment above $25 is recorded in the gifts log within five business days, with the giver, the date and an estimated value."},
        {"id": "gifts-4", "text": "Analysts may not accept any gift or hospitality from a company they cover during the blackout window around their own research on it."},
    ]},
    {"heading": "11. Expenses and travel", "clauses": [
        {"id": "expense-1", "text": "Expense reports must be submitted within 30 days with itemized receipts for any item over $25."},
        {"id": "expense-2", "text": "Meals while traveling are reimbursed up to $60 per day; alcohol is not reimbursable."},
        {"id": "expense-3", "text": "Air travel is booked in economy through the firm's travel agent. Flights over six hours may be booked in premium economy with the managing partner's approval."},
        {"id": "expense-4", "text": "Site visits to covered companies are paid for by the firm, never by the company being visited, so the research stays independent."},
    ]},
    {"heading": "12. Information security", "clauses": [
        {"id": "security-1", "text": "Laptops must use full-disk encryption and auto-lock after 10 minutes of inactivity."},
        {"id": "security-2", "text": "Report a suspected phishing email to security@champaigncapital.example within one hour of receipt."},
        {"id": "security-3", "text": "Passwords are at least 14 characters and unique to each system, and every firm account uses two-factor sign-in. Never share a password or a sign-in code, even with a colleague."},
        {"id": "security-4", "text": "Only software on the firm's approved-tools list may be installed on a firm laptop or connected to firm data. Ask the data team to review a new tool before you use it."},
        {"id": "security-5", "text": "A lost or stolen laptop or phone must be reported to the data team at once, day or night, so it can be locked and wiped remotely."},
    ]},
    {"heading": "13. Conflicts of interest", "clauses": [
        {"id": "conflicts-1", "text": "A conflict of interest is any situation in which an employee's own interest, or a family member's, could influence or appear to influence their work. Every employee declares conflicts to compliance when they join and whenever something changes."},
        {"id": "conflicts-2", "text": "An analyst may not write research on a company in which they, their spouse or partner, or a dependent child holds shares, options or a job. Coverage passes to a colleague until the holding is sold or the job ends."},
        {"id": "conflicts-3", "text": "An analyst who owns shares in a covered company from before they joined the firm may keep them, but must declare them, and any sale follows the pre-clearance, blackout and holding-period rules like any other trade."},
        {"id": "conflicts-4", "text": "The firm does not do investment banking, underwriting or paid consulting for companies it covers, and does not accept payment from a company in return for research on it."},
        {"id": "conflicts-5", "text": "A client's request to see a note before it is published, to change a rating, or to add or drop coverage of a company is declined and reported to compliance, whoever the client is."},
        {"id": "conflicts-6", "text": "Each published note states whether the author or the firm holds any position in the companies it discusses, and whether any other conflict applies. A note with no disclosure statement cannot be published."},
    ]},
    {"heading": "14. Outside activities", "clauses": [
        {"id": "outside-1", "text": "Employees must ask compliance before taking a second job, a paid speaking role, a board seat or an advisory position with any company, whether or not the firm covers it."},
        {"id": "outside-2", "text": "Board seats and advisory roles at companies in a covered sector are not approved. Unpaid roles with charities, schools and community groups are usually approved, but still need to be declared."},
        {"id": "outside-3", "text": "Teaching, writing and speaking about markets in general are encouraged. Discussing a covered company in a class, article or talk needs the same approval as a public comment."},
        {"id": "outside-4", "text": "Personal investments in private companies, such as a friend's start-up, are declared to compliance before the money is committed, so compliance can check them against the firm's coverage."},
        {"id": "outside-5", "text": "Political donations and campaign work in an employee's own name and time are private matters, but may not use the firm's name, email, premises or client lists."},
    ]},
    {"heading": "15. Records and AI assistants", "clauses": [
        {"id": "records-1", "text": "Firm records are the documents the firm relies on: published notes, models, the client log, pre-clearance decisions and the gifts log. They are kept for seven years and changed only by the people responsible for them."},
        {"id": "records-2", "text": "AI assistants approved by the firm may read firm records through read-only tools. No assistant may change a firm record, approve a trade, or send anything to a client without a person."},
        {"id": "records-3", "text": "An assistant may keep working notes, such as a client's preferred format or figures it looked up, so it can pick up where it left off. These notes are not firm records and are never the source for a figure in a note."},
        {"id": "records-4", "text": "Every note an assistant keeps must show where it came from and when it was written. Any employee may read the notes kept about their clients and delete one that is wrong."},
        {"id": "records-5", "text": "Before an assistant repeats a figure from its notes to a client, the figure must be checked again against the firm's data. A note is a reminder of where to look, not evidence."},
    ]},
]

CLAUSES = [{**c, "heading": s["heading"]} for s in SECTIONS for c in s["clauses"]]
HANDBOOK = "\n\n".join(f"## {s['heading']}\n\n" + "\n\n".join(c["text"] for c in s["clauses"]) for s in SECTIONS)

if __name__ == "__main__":
    # ponytail: self-check; run `python handbook.py` from _static/py
    from docs import DOCS
    ids = [c["id"] for c in CLAUSES]
    assert len(ids) == len(set(ids)), "duplicate clause id"
    for d in DOCS:
        assert any(c["id"] == d["id"] and c["text"] == d["text"] for c in CLAUSES), d["id"]
    words = len(HANDBOOK.split())
    assert 2000 <= words <= 3600, words
    print("ok", len(CLAUSES), "clauses,", words, "words")
