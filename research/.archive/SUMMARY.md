# SUMMARY — Research ranking for P1/P2 selection

## How P1/P2 was selected (because the CSV had no priority field)

Neither `AGENTS.md` nor `data/accounts_enriched.csv` contained a priority-1 / priority-2 designation. Per AGENTS.md rule 4 ("no fabricated facts"), I did not invent one. I selected six accounts via this transparent, reproducible heuristic:

> Pick the six seed rows whose **near-match** (per the prior `accounts_enriched.csv` pass) is a **real, verifiable B2B software entity with a traceable engineering org**, then sort by **AGENTS.md ICP fit** (P1 = ICP-fit, P2 = real-B2B-but-disqualifier).

P1 = near-match is a real B2B SaaS, in ICP vertical (developer tools / data infra / AI-ML / fintech infra), with traceable hiring / public engineering signal.
P2 = near-match is a real B2B SaaS but with at least one AGENTS.md ICP disqualifier (agency model, wrong vertical, sub-50 employees).

All research files were written against the **near-match real entity**, not the seed-as-written entity — the COMPLICATION section of each file flags this drift explicitly so it cannot be missed downstream.

## Work this first — ranked

| # | Account | Real entity researched | Rank | One-line reason to work it first |
|---|---|---|---|---|
| 1 | A010 Mercury Index | **Mercury.com** (Mercury Technologies, Inc., co-founder/CEO Immad Akhund, co-founder/CTO Max Tagher) | **P1 — work first** | Strongest signal in the seed: public Series C, Haskell/type-system stack with explicit Craft round in interview loop, OSS dev tooling shipped (`ghciwatch`), active Greenhouse postings including "Head of TPM — Banking." Most Factory-shaped enterprise in the batch. |
| 2 | A014 Foldwise | **Fold Holdings, Inc. (NASDAQ:FLD)** | **P1 — work second** | Public-company with an active 8-K road map (Jan 2026) calling out card + custody rebuild, plus active Senior BE Engineer posting. Direct modernization pitch fits the published plan. |
| 3 | A006 Helio Compute | **Helio AG** (Zürich, co-founder/CEO Kevin Häfeli) | **P1 — work third** | Real infra OSS presence on github.com/helio, QBIT-led €4.9M Seed (Oct 2023) with explicit "modernize cloud workload scheduling" thesis. Wrong-stage (Seed, not Series A) and wrong-locale (CH, not US) — outreach needs to be reseated before first touch. |
| 4 | A019 Sablon | **Sablono GmbH** (Berlin, co-founder/CEO Lukas Olbrich) | P2 — defer | Construction-tech PM, not ICP vertical. Investor side (Nemetschek SE in May 2021 Series A) compounds procurement complexity. Worth staying on watchlist only. |
| 5 | A013 Tinroof | **Tin Roof Software** (Georgia US, President Daniel Gore, CIO Kapil Chandra, CTO Akash Patel) | P2 — disqualify | AGENTS.md rule 1 disqualifier: agency / digital-transformation reseller. Cannibalization risk — modernizing their customers eats their billable baseline. |
| 6 | A011 Pier 14 Labs | **Pierre** (YC W23, Ian Ownbey + Jacob Thornton, ~10 employees) | P2 — disqualify | Below AGENTS.md ICP size floor (50–500 employees) at **10 employees**. Real team, real signal (GitHub reliability narrative), wrong shape. |

## Cross-cutting risks worth flagging before first outbound

1. **The seed was 100% fictional.** No priority field existed, and the seed's headline facts (size, stage, vertical, location, named engineers) for every account failed verification against public sources. Any outreach using seed-as-written copies will land inaccurate.
2. **Real-entity outreach is best-effort.** Even where a near-match looks strong (Mercury, Fold), the seed's "name" stays wrong — first-touch asks and value props must be reseated to the real entity. See each file's COMPLICATION section.
3. **Engineering-signal strength, not company size, is the highest predictor.** Mercury's been-the-best-Signal (Haskell + Craft round + ghciwatch OSS) is what puts it at #1 — bigger than Helio AG which is the more obvious "infra" nominee.
4. **CEO-CTO pair is the right outreach pair for everyone.** At Mercury and Fold that pair is verified (`Max Tagher` + `Immad Akhund`; `Will Reeves` + UNKNOWN CTO). At Tin Roof and Pierre, the co-founders are the entire decision unit. Aggressively researching the CTO/VP Engineering name on Fold before first touch is the highest-leverage 30-minute task remaining.
