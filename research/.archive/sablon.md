# Research — A019 Sablon (account_id: A019)

## Selection note

The seed claims a Germany-based 280-employee Series B data-infrastructure company on `sablon.io` replacing Kafka. That entity does not resolve. The closest real co is **Sablono** (Sablono GmbH, Berlin, construction-tech PM, founded 2013, Series A €5.3M in May 2021 from Bachmaier Invest, Nemetschek SE, HTGF, and Hasso Plattner Ventures — note spelling `Sablono`, not `Sablon`). Sablono → seed gap is material (wrong vertical, name spelled differently, not data infrastructure, only ~2.8k LinkedIn vs. claimed 280 employees).

Researched by: droid, 2026-07-14. Sources cited inline.

## 1. SIGNAL

**Found, but unlikely to convert.** Three observable signals, none of them tightly aligned with Factory's fit:

- **Reference customers with sticky spend.** Sablono is *"the world leader for digital lean technology for construction enterprises"* per WISTA's coverage of the Series A (`https://www.wista.de/en/news-press/news/german-contech-champion-sablono-raise...`, dated 2021-06-03) and is listed as *"market leader in digital lean technology"* per Nemetschek (`https://www.nemetschek.com/en/news-media/nemetschek-group-strategic-start-inv...`, 2021).
- **Material strategic investment from Nemetschek SE.** Nemetschek participated in the Series A and has a long-standing relationship — Nemetschek's statement: *"the market leader in digital lean technology for construction enterprises. Nemetschek supports innovative next-generation AEC entrepreneurs in Germany"* (`https://www.nemetschek.com/en/news-media/nemetschek-group-strategic-start-inv...`, 2021-05-27). For a construction company this is the most concrete "stable but heavy" partnership signal — useful for procurement access, less useful for vendor churn.
- **Active 2025–2026 product work.** Sablono maintains an active blog (`https://www.sablono.com/en/blog/all`) and is exhibiting at Digital Construction North (`https://exhibitormanual.digitalconstructionnorth.com/meet-sablono/`) — current enough to imply ongoing engineering hiring.
- **Open Berlin engineering roles.** Sablono's jobs are listed on Berlin Startup Jobs (`https://berlinstartupjobs.com/companies/sablono/`).

**The single most defensible SIGNAL is: Sablono's largest investor (Nemetschek SE, $1B+ AEC software group) is publicly committed to its product — but engineering investment thesis ("digital lean for construction") has not changed materially since 2021.** That's a stagnation risk on engineering velocity, not a buying signal.

Job-posting signal: **NOT DEEP ENOUGH TO USE**. BerlinStartupJobs lists the company, but a specific engineering-velocity job was not surfaced in this research pass — the kind of post a Factory pitch would lean on is not in hand.

## 2. ANALOGUE

No directly analogous public Factory customer. Closest thematic match: **Bayer** (named in `https://www.idlen.io/news/factory-ai-150-million-1-5-billion-droids-coding-ag`, dated 2026-04-22) — Bayer is a major German enterprise with a slow-modernizing engineering function. Match in one line: Bayer's frame is "industrial company with custom engineering inside," Sablono is "construction-tech vendor with custom engineering inside" — same shape of buyer, vastly different industry.

## 3. PERSONA

Given Sablono's stated scale (2,804 LinkedIn followers, undated but refreshed 2023-09-26 per Lukas Olbrich's profile, ~Berlin Startup Jobs postings), the two most likely titles to own this decision are:

- **CTO / Head of Engineering** — Sablono has had ~5 co-founders listed over time and likely has a CTO-equivalent.
- **Founder-CEO Lukas Olbrich** — at this scale the CEO often still owns the build-vs-buy decision himself.

Verified currently-in-seat names:

- **Lukas Olbrich** — Co-Founder & CEO, Sablono. Verified `https://www.linkedin.com/in/lukasolbrich/` (last update 2023-09-26 visible in result), `https://www.crunchbase.com/person/lukas-olbrich`, and Sablono's own coverage (`https://www.sablono.com/en/blog/sablonos-ceo-lukas-olbrich-among-germanys-inn...`, dated 2022-02-16, naming him among *"Germany's Innovators under 35"*).

CTO / Head of Engineering: **UNKNOWN.** Sablono's leadership page (`https://www.sablono.com/en/company/team`) is referenced but my search did not surface a current CTO name.

## 4. EMAIL

```
Sablono took a strategic Series A from Nemetschek SE in May 2021 alongside Bachmaier and HTGF — the kind of partnership that locks product direction but usually leaves engineering velocity to be solved internally.
Bayer, a Factory customer, runs the same shape of buyer problem — large German enterprise, custom-developer-heavy, modernization as a slow-build — and uses Droids for the parts of the SDLC that scale without senior headcount.
Is the engineering constraint on Sablono's product roadmap the senior-vendor-coordination with Nemetschek, the rate of new feature releases, or something narrower on the data model?
```

Three sentences, no greeting, no value props, no adjectives. Question is answerable in one line.

## 5. DISCOVERY

A question only possible because of step 1's investor composition (Nemetschek + Bachmaier + HTGF):

> *"Sablono's last public funding was the €5.3M Series A in May 2021. Is the team now consolidating the platform for Nemetschek integration, or still pushing new feature surface — and which of those two trajectories is straining the senior eng bandwidth today?"*

This question maps two sources side-by-side (Nemetschek's strategic-investment framing + the 2021 funding date) and is grounded in the public material.

## 6. COMPLICATION

- **Wrong-entity risk.** Outright factual drift — `sablon.io` vs. `sablono.com`, "Kafka replacement" vs. construction PM, "280 employees" vs. ~2.8k LinkedIn. Outreach that assumes the seed framing will look unserious.
- **Wrong vertical for ICP.** AGENTS.md ICP verticals are developer tools / data infrastructure / AI/ML platforms / fintech infra. **Construction PM is none of these.** This account should be DEFER even if Sablono were perfect.
- **HTGF portfolio entry says "Successful exit 2021".** Verbatim from `https://www.htgf.de/en/portfolio/htgffamily/sablono-2/` (dated 2022-08-05). This phrasing is portfolio language meaning the fund booked a return on the position — not necessarily an acquisition. **Important:** misleading the prospect about exit status in outreach is a high-cost error; verify before any claim is made.
- **Investor-side dependency.** Nemetschek is both investor and AEC-software peer. Sablono's roadmap may be partly set by Nemetschek's M&A strategy, which is outside their decision-making.
- **Funding age.** €5.3M Series A is from 2021. Five years without a subsequent round press visible in the search results is a yellow flag for runway and execution rhythm — hard to read as "scaling" mid-2026.
- **Construction-tech tooling ecosystem is conservative.** Buyer cycles in construction software are long, and modernization tooling is rarely the first purchase.

## Verdict

`DEFER` — and recommend removing from P1/P2 entirely. Sablono is real and interesting in its own right, but the seed's framing (Kafka replacement, 280 employees, Series B) doesn't match; the ICP vertical is wrong; and the closest named investor (Nemetschek) makes deal-flow subject to a separate strategic agenda. Spend the cycle on actual ICP-vertical accounts.
