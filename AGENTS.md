# AGENTS.md — operating manual

Factory Territory is a territory research and prospecting pipeline for an
enterprise sales rep covering **San Diego County** and **the Denver metro**.
The product being sold is **Factory AI** — autonomous coding agents (Droids)
for enterprise engineering organizations.

The output of this project is four artifacts:

1. `data/accounts_enriched.csv` — one row per account, every figure labeled.
2. `research/<company>.md` — per-account prospecting packet (P1/P2 only).
3. `data/contacts.csv` — five role slots per priority account.
4. `data/meddpicc.json` — eight elements × three fields each, scored 0-3.
5. `dashboard/index.html` — single self-contained sales-ops tool.

The dashboard is the artifact the rep touches every day. The other four feed
it.

---

## The ICP — screen on these, NOT on firmographics

Revenue and total headcount do **not** predict a deal. The signals that do:

1. **Developer density** — engineering headcount, not total headcount.
2. **Legacy surface area** — 20-30 year old systems, embedded/firmware,
   mainframe-era cores, acquisition-inherited stacks, active modernization
   programs.
3. **Constraint** — regulated, classified, or safety-critical. Governance,
   on-prem, and air-gapped requirements are where an enterprise agent
   platform beats an IDE plug-in.
4. **Observable pain** — job reqs for platform/DevEx/modernization roles,
   announced migrations, visible open-source footprint.

**The highest-intent signal is a company hiring a human to do the job
Factory does.** Job postings are the primary research surface. Read them
first.

## Factory's public customers (use as analogues in outreach)

| Customer | Shape |
|---|---|
| Nvidia | Semiconductors, firmware, massive embedded codebases |
| Morgan Stanley | Regulated financial services with a legacy core |
| Adobe | Acquisition-inherited codebases needing consolidation |
| EY | Sprawling enterprise IT / engineering modernization |
| MongoDB | Software company with its own modernization mandate |
| Bayer | Regulated life sciences, FDA-auditable workflows |
| Palo Alto Networks | Defense + classified + air-gapped |

Map each prospect to the closest analogue. Say why the match holds in
**one line**.

## Geographic filter

Headquarters in San Diego County or Denver metro — incl. Englewood, Greenwood
Village, Centennial, Westminster, Broomfield. **A large campus without HQ
means selling into someone else's budget.** Flag those separately; never
include them silently.

---

## RULES — non-negotiable, apply to every phase

1. **Never invent a signal or a person.** Every claim needs a source URL or
   the label `INFERRED`. If you cannot find something, write `NO SIGNAL
   FOUND` or `UNKNOWN`. A fabricated detail in a cold email is instantly
   detectable by an engineering leader and burns the account permanently.
   **Eight accounts with real signals beat twenty with guesses.**
2. **A person may be named ONLY from a citable public source:** press release,
   exec bio page, conference talk, engineering blog byline, patent, GitHub
   profile, SEC filing. A LinkedIn URL may ONLY be included if it appeared in
   search results. **Never construct one by pattern** — `linkedin.com/in/
   firstname-lastname` is a **guess**, not a URL. If unverifiable, output the
   **role as a slot** with a LinkedIn people-search URL:
   `https://www.linkedin.com/search/results/people/?keywords=<TITLE>%20<COMPANY>`
   and set `name = "UNVERIFIED — use search link"`.
3. **Do not scrape LinkedIn.** Career pages, newsrooms, RSS, and search only.
4. **Firmographics are estimates.** Caveat them. They rank; they don't get
   quoted.
5. **Flag staleness.** Note the date of every signal.
6. **Surface complications; don't hide them.** Existing SI partner, offshore
   capability center, competing internal program — these are the objections
   the rep will face and they are worth more than another bullet point.
7. **No corporate voice.** Emails are three sentences. No greeting fluff, no
   value props, no adjectives, no "hope this finds you well." Subject lines
   are lowercase, six words max, and read like a human wrote them in a hurry.

---

## Honest-by-default UI rules (also non-negotiable)

- **Never render an unverified name as verified.** The confidence badge is
  load-bearing.
- A name with confidence `SLOT ONLY` or `INFERRED` is rendered next to a
  LinkedIn people-search link, never next to a guessed pattern URL.
- `UNKNOWN` renders as `n/a` and is excluded from charts with a note. Never
  substitute plausible values to make a chart or card look complete.

---

## MEDDPICC — the framework, not a checkbox

These accounts are **unworked**. We have not spoken to a single person. Most
MEDDPICC fields are therefore `UNKNOWN` — and a tool that lets us pretend
otherwise is worse than no tool.

Every one of the eight elements gets **three** fields, never one:

- **KNOWN** — what we can evidence, with a source URL. Usually very little.
- **ASSUMPTION** — our hypothesis, explicitly labeled a guess.
- **HOW I TEST** — the specific question, and WHO answers it.

**Never promote an ASSUMPTION into KNOWN** to make an account look healthier.
That is exactly how forecasts start lying.

Score each 0-3:

- 0 = Unknown
- 1 = Assumed
- 2 = Validated (one person inside)
- 3 = Multi-threaded (two+, one with authority)

Bands:

- 0–6  Unqualified  (research target, not a deal)
- 7–12 Early
- 13–18 Qualified
- 19–24 Forecastable

**Expect 2–6/24** on these accounts. That is CORRECT. Frame low scores as
honesty, not failure. The dashboard displays verbatim:

> Nothing here is forecastable until someone inside the account has told me
> it's true.

Per-account supplement:

- **M** Metrics — what number moves if they buy (eng hours in legacy,
  migration timeline, on-call load, contractor/offshore spend, time-to-release).
- **E** Economic Buyer — name only if verified.
- **D** Decision Criteria — what they evaluate on (governance/on-prem, model
  routing + cost, codebase comprehension at scale, security review). Note
  which we WIN on AND which we LOSE on — an account with no losing criterion
  hasn't been thought about honestly.
- **D** Decision Process — architecture review board? security review?
  procurement? In regulated/defense accounts this is the long pole, **not**
  the pitch.
- **P** Paper Process — legal, InfoSec questionnaire, MSA. For defense: is
  FedRAMP/IL-level a hard gate? If yes, that may DISQUALIFY the account —
  say so.
- **I** Identify Pain — the verified SIGNAL from Phase 2, cited.
- **C** Champion — who feels the pain daily. Usually the **technical**
  champion, NOT the economic buyer. A champion who can't describe the pain in
  their own words isn't a champion.
- **C** Competition — rarely another agent vendor. Usually (a) Copilot/Cursor
  already deployed and "good enough"; (b) a systems integrator holding the
  budget (Western Union → HCLTech); (c) an offshore capability center
  (LPL → Hyderabad GCC); (d) do nothing / hire more engineers. **Name which
  applies HERE.**

---

## Output conventions

- Research output → `research/<company>.md`
- Per-account outreach → `research/<company>_outreach.md`
- Per-account priority file → `research/<priority>.md` is forbidden; use the
  per-account path.
- Sequence files → None. Sequences live in the dashboard and are generated
  from the seed + analogue. Don't write them to disk separately.
- Summary table → `data/accounts_enriched.csv`
- Contacts → `data/contacts.csv` (5 slots × N priority accounts)
- MEDDPICC → `data/meddpicc.json`
- Dashboard → `dashboard/index.html` (single file, vanilla JS, no build step,
  no npm)

Per-company research file skeleton (research/<company>.md):

```
# <Company> (account_id: A0xx)

## 1. SIGNAL
<one specific verifiable observation, dating the source; or NO SIGNAL FOUND>

## 2. ANALOGUE
<closest Factory customer + one-line "why this matches">

## 3. PERSONA
<the two titles most likely to own this decision at THIS company>

## 4. EMAIL
Subject: <max 6 words, lowercase>
Observation. Analogue-link. Discovery question.

## 5. DISCOVERY
<one question I could ONLY ask because of the signal>

## 6. COMPLICATION
<what makes this harder. Honest. Never padded.>
```

Per-company outreach file (research/<company>_outreach.md) layout:

```
# Outreach — <Company>

## Slot 1 — Economic Buyer (CTO/CIO/EVP Eng)
- name | confidence | linkedin | source
- why_this_person

### First Email
<subject, body — 3 sentences, slot-tailored>

### First LinkedIn
<≤300 chars. One observation + one curious question. Different from the email.>

## Slot 2 — Technical Champion (VP/Sr Dir Platform)
... etc.

## Slot 5 — Wildcard
... etc.
```

If an account's SIGNAL is `NO SIGNAL FOUND`, write **"DO NOT PROSPECT
YET"** at the top of the outreach file and stop. Never backfill with
generic industry language.

---

## Build lifecycle

```
data/accounts_seed.csv  →  built once, hand-maintained
                        ↓
scripts/build_dashboard.py
                        ↓
data/accounts_enriched.csv
research/*.md
data/contacts.csv
data/meddpicc.json
                        ↓
dashboard/index.html
```

The build script reads the four data files and the markdown, embeds them as
JSON constants into the HTML, and writes a single self-contained HTML file. No
fetch, no build pipeline beyond that. The script is the only piece of "build"
infrastructure.
