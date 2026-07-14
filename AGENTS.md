# AGENTS.md

## What this project is

A territory research and prospecting pipeline for an enterprise sales rep covering
San Diego and Denver. It screens companies against an ICP, enriches them from public
sources, and produces two artifacts: a prospecting packet per account, and a single-file
HTML dashboard for territory review.

The product being sold is **Factory AI** — autonomous coding agents (Droids) for
enterprise engineering organizations.

## The ICP — screen on these, not on firmographics

Revenue and headcount do NOT predict a deal. The signals that do:

1. **Developer density** — engineering headcount, not total headcount.
2. **Legacy surface area** — 20-30 year old systems, embedded/firmware, mainframe-era
   cores, acquisition-inherited stacks, active modernization programs.
3. **Constraint** — regulated, classified, or safety-critical. Governance, on-prem, and
   air-gapped requirements are where an enterprise agent platform beats an IDE plug-in.
4. **Observable pain** — job reqs for platform/DevEx/modernization roles, announced
   migrations, visible open-source footprint.

**The highest-intent signal is a company hiring a human to do the job Factory does.**
Job postings are the primary research surface. Read them first.

## Known Factory customers (use as analogues in outreach)

Nvidia (semiconductors, firmware), Morgan Stanley (regulated finserv, legacy core),
Adobe, EY, MongoDB (software co. with its own legacy), Bayer (regulated life sciences),
Palo Alto Networks.

Map each prospect to the closest analogue. Say why the match holds in one line.

## Geographic filter

Headquarters in San Diego County or Denver metro (incl. Englewood, Greenwood Village,
Centennial, Westminster, Broomfield). A large campus without HQ means selling into
someone else's budget — flag those separately rather than including them silently.

## RULES — these are not negotiable

1. **Never invent a signal.** Every claim about a company must have a source URL, or be
   explicitly labeled `INFERRED`. If you cannot find a real signal, write
   `NO SIGNAL FOUND` and move on. A fabricated detail in a cold email is instantly
   detectable by an engineering leader and burns the account permanently.
   Eight accounts with real signals beat twenty with guesses.
2. **Label every claim** `VERIFIED (url)` or `INFERRED`.
3. **Firmographics are estimates.** Always caveat them. They are for ranking, not quoting.
4. **Flag staleness.** Job postings and exec names rot. Note the date of every signal.
5. **Surface complications, don't hide them.** If a company already has an SI partner,
   an offshore capability center, or a competing internal program, say so. Those are the
   objections the rep will face; they are more valuable than another bullet point.
6. **No corporate voice.** Emails are three sentences. No greeting fluff, no value props,
   no adjectives, no "hope this finds you well."

## Output conventions

- Research output → `research/<company>.md`
- Summary table → `data/accounts_enriched.csv`
- Dashboard → `dashboard/index.html` (single file, vanilla JS, no build step, no npm)
- Markdown, not prose walls. Tables where the data is tabular.
