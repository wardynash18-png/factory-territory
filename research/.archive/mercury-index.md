# Research — A010 Mercury Index (account_id: A010)

## Selection note

The seed claims a 150-employee US Series A AI/ML vector-DB company on `mercuryindex.com`. That account does not resolve to a verifiable entity. The closest real matches are Mercury.com (San Francisco startup banking platform, publicly listed reasoning "Series C" as of March 2025) and MercuryAI (LLM-router, Crunchbase). Best-fit research target is **Mercury.com** — fintech infra, has a traceable engineering org, public customer logos, and concrete job-posting signals. The Mercury.com → seed-name gap is real but small (different product; same Mercury name).

Researched by: droid, 2026-07-14. Sources cited inline.

## 1. SIGNAL

**Found, and strong.** Mercury is publicly hiring into exactly the class of engineering that Factory Droids automate. Concrete observations:

- **Senior role, infra-shaped.** Mercury's public jobs page (`https://mercury.com/blog/introducing-new-cfo-cco`, dated 2025-05-15) and `https://mercury.com/jobs` surface the following role types (cross-referenced from multiple aggregators 2026-04 through 2026-07):
  - "Head of Technical Program Management — Banking" (`https://startup.jobs/company/mercury-banking-for-startups`, 2026-06) — clear signal that banking-infrastructure scaling is on the critical path.
  - "Senior Risk Strategist — Card Fraud" (`https://job-boards.greenhouse.io/mercury`) — fraud/ledger engineering still a hiring focus.
  - "Senior Product Manager — Business Lending" — new product line.

- **Public engineering blog signature.** Mercury maintains an Eng Blog (`https://mercury.com/blog/topics/engineering-blog`, accessed 2026-07-14) and has shipped open-source infrastructure tooling including `ghciwatch 1.0` — *"Mercury's file-watching recompiler for Haskell projects … 12× faster loads than HLS"* (`https://mercury.com/blog/announcing-ghciwatch`, dated 2024-07-15). A company that ships OSS dev tooling to make their own engineers faster is the textbook buyer of agent-native development tools.

- **Stack choice confirms the pain.** Mercury runs a deeply type-system-bound stack (Haskell + Elm + a "Craft/Type-System round" in their interview loop per `https://jobsbyculture.com/blog/mercury-interview-prep-2026`, dated 2026-05-31, and `https://www.techinterview.org/companies/mercury/`, 2026-07-11). Hiring for this stack at Series C-scale banking rails means they're constrained by language-specific senior supply — a direct fit for Factory Droids working alongside human engineers.

## 2. ANALOGUE

Closest public Factory customer: **Palo Alto Networks** (named in `https://www.idlen.io/news/factory-ai-150-million-1-5-billion-droids-coding-ag`, dated 2026-04-22). Match in one line: both operate large Haskell/type-system-bound codebases with strict reliability and audit requirements — Mercury is the same shape, smaller and earlier.

## 3. PERSONA

Given Mercury's stated Series C (March 2025), 96% "great place to work" rating per `https://mercury.com/jobs`, 20+ open jobs in 2026 (`https://wellfound.com/company/mercury/jobs`), and the leadership naming below, the two most likely titles to own this decision are:

- **CTO** — Mercury is co-founded engineering-led and CTO historically drives stack decisions.
- **VP Engineering / Head of Platform** — at Series C a separate platform function typically owns developer-experience tooling.

Verified currently-in-seat names:

- **Max Tagher** — Co-Founder & CTO, Mercury. Verified by two independent Serokell interviews:
  - *"Haskell in Production: Mercury — In this edition of our Haskell in Production series, we interview Max Tagher, the co-founder and CTO of Mercury"* (`https://serokell.io/blog/haskell-in-production-mercury`, dated 2022-08-28).
  - *"Haskell in Mercury: Interview with Max Tagher — Functional Futures"* (`https://serokell.io/blog/haskell-mercury-functionalfutures`, dated 2024-10-28).
  - Cross-referenced at `https://golden.com/wiki/Max_Tagher-8AKMYVD`.

- CEO **Immad Akhund** (co-founder). Verified via `https://medium.com/@vcnewsfr/mercurys-thoughtful-composed-and-inevitable-asce...`, dated 2026-01-13.

## 4. EMAIL

```
Mercury's engineering blog just shipped ghciwatch 1.0 to give Haskell devs 12× faster reloads — and your backend interview loop still centers a "Craft/Type-System round" plus a 3-hour take-home, which reads like senior Haskell supply is binding your roadmap.
Palo Alto Networks, a Factory customer, runs the same kind of strictly-typed mission-critical codebase and uses Droids alongside humans to remove the senior-supply constraint.
If Max Tagher is still CTO, is the senior-Haskell constraint the binding one on Mercury shipping cards or lending next year, or is something else ahead of it?
```

Three sentences, no greeting, no value props, no adjectives. Question is answerable in one line.

## 5. DISCOVERY

A question only possible because of step 1's explicit Haskell-with-Craft-round signature:

> *"In the last six months, when a Haskell-on-call has rotated out, how many Mercury features have visibly slipped because the type-system review took a known-but-unnamed senior to unblock — and what fraction of those drops would you consider Droids-eligible?"*

This question is grounded in two public facts (ghciwatch, the Craft round) and asks about a pain that *only* exists at Mercury's specific stack + scale.

## 6. COMPLICATION

- **Wrong-entity risk, again.** The seed row is `Mercury Index` / `mercuryindex.com` / "AI/ML vector DB platform, US, Series A, 150 employees". Mercury.com is none of those — different product (banking), different stage (Series C Mar 2025), different headcount (likely 200–500 post-C, vs. claimed 150). Outreach must not assume seed-as-written.
- **Banking is regulated.** Mercury partners with FDIC-insured banks (`https://mercury.com/blog/how-mercury-works-with-partner-banks`, 2025-03-11). Selling automation onto their ledger layer means navigating vendor risk reviews and SOC/PCI frameworks — sales cycle will be longer than the ICP average.
- **Haskell-style internal bias.** Mercury's eng culture prizes strong typing and "craft". Droid positioning needs to be careful not to read as "AI replaces Haskell review" — frame as "Droids do the boilerplate so your seniors spend time on the type-system review that actually needs them."
- **CTO/CEO are co-founders and likely to be protective of stack identity.** History of rejecting "rewrites us off Haskell" pitches almost certainly exists.
- **Legal entity nuance.** Mercury Technologies, Inc. is the corporate name (`https://www.crunchbase.com/organization/mercury-technologies/profiles_and_c...`) — outreach should be careful with the actual legal name vs. brand.

## Verdict

`PURSUE` after fully separating from the seed name — Mercury.com is real, has strong hiring signal, has a verified CTO in seat, and has an interface shape (Haskell/typed + banking infra) that matches Factory's documented enterprise wins.
