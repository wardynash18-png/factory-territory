# Factory Territory — Operating Manual

This repo is the single source of truth for our go-to-market territory. Every agent, human, or automation that touches this work reads AGENTS.md first.

## Mission

Identify, enrich, qualify, and engage 20 best-fit accounts per quarter against our Ideal Customer Profile (ICP), then hand them off to AE-led outbound with research-backed context.

## Repo layout

```
factory-territory/
├── AGENTS.md              # this file — operating manual
├── data/                  # structured account & contact data (CSV, JSON)
│   └── accounts_seed.csv  # initial 20 accounts seeded into the territory
├── prompts/               # reusable prompt library (research, outreach, qualification)
│   └── PROMPTS.md
├── research/              # per-account research notes (one file per account)
└── dashboard/             # generated artifacts (CSV summaries, JSON exports)
```

## ICP (current snapshot)

- **Segment:** B2B SaaS, Series A–C, 50–500 employees
- **Vertical focus:** developer tools, data infrastructure, AI/ML platforms, fintech infra
- **Buyer personas:** CTO, VP Engineering, Head of Platform, Head of Data
- **Trigger signals:** recent funding round, hiring surge for platform/data roles, migration away from legacy infra, public AI initiative
- **Disqualifiers:** <20 employees, pre-product, consumer-only, government-only, agency/reseller model

## Operating rules

1. **Single source of truth.** All account data lives in `data/`. Never edit CSVs by hand in chat — use scripts or PR-reviewed edits.
2. **Research is append-only.** `research/<account_slug>.md` only ever gains content; remove nothing, correct by strikethrough.
3. **Prompts are versioned.** Any change to `prompts/PROMPTS.md` gets a dated entry at the bottom.
4. **No fabricated facts.** If we don't know it, mark it `UNKNOWN`. Never invent headcount, funding, or tooling.
5. **PII handling.** Store only public business contact info. Mask emails in shared artifacts (`jane@acme.com` → `j***@acme.com`) unless explicitly approved.
6. **Every account gets a verdict.** End of research: `PURSUE | NURTURE | DEFER | DISQUALIFY` with a one-line rationale.

## Daily rhythm

- **Morning:** score new accounts against ICP, queue 3 for deep research
- **Midday:** run deep research on queued accounts using `prompts/PROMPTS.md`
- **EOD:** commit research, update `data/accounts_seed.csv` status, draft next-day queue

## Glossary

- **Account:** a target company in `data/accounts_seed.csv`
- **Contact:** a person at an account, linked by `company_slug`
- **Touchpoint:** any logged outreach, in `research/<account_slug>.md`
- **Verdict:** final disposition per account (see rule 6)
