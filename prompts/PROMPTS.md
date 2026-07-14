# PROMPTS — Prompt Library

Reusable prompts for territory work. Variables in `{{double_braces}}`. Always cite sources where the prompt asks for facts.

---

## 01 — Account deep research

```
SYSTEM: You are a B2B territory researcher. Be precise, cite sources, and never invent facts.
USER:
Produce research on {{company}}.

Required sections:
1. Snapshot — name, domain, HQ, founded year, employee count (source-linked)
2. ICP fit — match score 0–10 against our ICP: B2B SaaS, Series A–C, 50–500 employees,
   dev tools / data infra / AI-ML / fintech infra. Justify the score.
3. Buyer signals — list concrete recent signals (funding, hiring, posts, OSS activity, customer logos)
4. Likely buyers — names + titles for CTO, VP Eng, Head of Platform, Head of Data where publicly known
5. Tech stack clues — inferred from career posts, blog, talks, GitHub
6. Outreach angle — one sentence on why now + a specific pain hypothesis
7. Verdict — PURSUE | NURTURE | DEFER | DISQUALIFY with one-line rationale
8. Next action — single concrete next step (e.g., "watch Series B press", "intro to VP Eng via mutual")
```

## 02 — ICP fit check

```
USER:
Score this account against our ICP and return JSON only.

Account: {{company_json}}
ICP: B2B SaaS, Series A–C, 50–500 employees, dev tools / data infra / AI-ML / fintech infra.
Buyers: CTO, VP Eng, Head of Platform, Head of Data.

Schema:
{
  "score": 0-10,
  "fit_dimensions": {"segment":0-10,"size":0-10,"vertical":0-10,"buyer_reachability":0-10},
  "reasons": ["...", "..."],
  "disqualifiers": ["..."] | []
}
```

## 03 — Personalized first-touch email

```
USER:
Write a 90-word cold email from {{sender_name}} at {{sender_company}} to {{first_name}},
{{title}} at {{company}}.

Constraints:
- One specific observation about {{company}} (citing a public source)
- One concrete hypothesis about a pain they likely have
- One clear ask (a 20-min call next week)
- No flattery, no "I hope this finds you well"
- Subject line ≤ 50 chars
- End with a P.S. that adds value without asking
```

## 04 — Pre-call briefing

```
SYSTEM: You are briefing an AE before a first discovery call.
USER:
Generate a 1-page brief for a call with {{first_name}} ({{title}}) at {{company}}.

Include:
- 3-line company snapshot
- 3 things they likely care about right now
- 3 likely pain hypotheses (with our product angle for each)
- 3 discovery questions to ask
- 2 things to NOT bring up
- A "magic question" — a single question whose answer reveals deal sizing
```

## 05 — Account disqualification review

```
USER:
We marked {{company}} as DEFER. Re-evaluate whether it should remain DEFER, move to
NURTURE, or be DISQUALIFIED. Cite the original reason and any new signal. Recommend an
explicit re-review date.
```

---

## Changelog

- 2026-07-14 — Initial library seeded (prompts 01–05).
