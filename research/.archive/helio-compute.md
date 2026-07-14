# Research — A006 Helio Compute (account_id: A006)

## Selection note

This account resolves to a real but different company than the seed described. The seed claims a 75-employee US B2B SaaS Series A AI/ML platform on `helio-compute.dev`. There is no such entity. The closest verifiable match is **Helio AG** (Zurich, Switzerland, ~2,134 LinkedIn followers, Seed €4.9M Oct 2023, carbon-aware distributed compute). All research below is on Helio AG. The Helio AG → Factory-fit gap is: it's Seed, not Series A; it's Swiss, not US; it's carbon-aware cloud rendering, not AI/ML platform. Quality of the lead is "real-entity, wrong-shape" — flag before outreach.

Researched by: droid, 2026-07-14. Sources cited inline.

## 1. SIGNAL

**Found.** On Helio AG's open-source presence, the company maintains a GitHub organization (`https://github.com/helio`) described as *"Carbon Aware Cloud Computing — we democratize compute, empowering anyone who is using technology to solve the world's most complex challenges"* (`https://github.com/helio`, accessed 2026-07-14). The same tagline appears verbatim on the company's LinkedIn page (`https://ch.linkedin.com/company/helioag`), which gives the engineering org a public commit trail — a buying signal that the engineering team is willing to ship their scheduler publicly.

Stronger signal — funding and stated mission: Helio AG raised €4.9M Seed in October 2023 led by QBIT Capital (per `https://www.eu-startups.com/2023/10/zurich-based-helio-raises-e4-9-million-to-lead-the-sustainable-`, `https://techfundingnews.com/zurich-based-helio-raises-e4-9m-to-reduce-co2-emi`, both dated 2023-10-05). The mission framing in those write-ups — *"revolutionize cloud computing by addressing its environmental and efficiency pitfalls"* — is a documented modernization / workload-scheduling problem statement, which is exactly the class of work Factory Droids automate.

Secondary signal — engineering blog: Helio publishes carbon-aware scheduling posts (`https://blog.helio.exchange/posts/carbon-aware-cloud`), confirming there is an engineering org writing externally.

Job-postings signal: **none surfaced.** Helio AG has a careers URL at `https://helio.cloud/careers` (2026-07-14) but the search did not return open requisitions in this category. Climate Draft's job board lists a "Software Engineer, Business Automation @ Helio Home" posting dated 2026-04-03 (`https://jobs.climatedraft.org/companies/helio-home-2/jobs/73207259-software-e...`) — Helio **Home** is a separate residential retrofit startup, **not** Helio AG, so I am not counting it.

## 2. ANALOGUE

Closest public Factory customer: **Adyen** (named in idlen.io's April 22, 2026 coverage of the $150M Series C, alongside Nvidia, Adobe, Bayer, MongoDB, Palo Alto Networks — `https://www.idlen.io/news/factory-ai-150-million-1-5-billion-droids-coding-ag`, dated 2026-04-22). Match in one line: Adyen runs distributed batch workloads across heterogeneous clouds with tight cost/latency controls; Helio AG's carbon-aware scheduler is the same shape of problem at smaller scale.

## 3. PERSONA

Given Helio AG's size (~2.1k LinkedIn followers, undocumented engineering org size, Seed-stage), the two most likely titles to own this decision are:

- **CTO / Head of Engineering** — at this scale the technical co-founder is usually the buyer.
- **Founding Engineer / Platform Lead** — secondarily, because seeding-stage infra is led by whoever is shipping the scheduler day-to-day.

Verified currently-in-seat names:
- **Kevin Häfeli** — Co-Founder & CEO, Helio AG. Verified `https://www.linkedin.com/in/kevinhaefeli/` (last update 2020-01-17 visible in result; still listed "Experience: Helio AG") and `https://theorg.com/org/helio/org-chart/kevin-hafeli`. Address Sihlquai 131, 8005 Zürich per `https://www.swissmadesoftware.org/en/companies/helio-ag/home.html`.

CTO / second technical co-founder: **UNKNOWN.** No public name surfaced in this research pass.

## 4. EMAIL

```
We saw Helio AG open-sources its carbon-aware scheduler on github.com/helio while the company is still early — including EU-Startups' coverage tied to the QBIT-led €4.9M Seed in October 2023.
Adyen, a Factory customer, runs distributed batch workloads across heterogeneous clouds with tight cost and carbon controls — close to the class of problem Helio's scheduler solves, just at much larger scale.
Are you running a single off-the-shelf orchestrator inside Helio AG right now, or rolling your own scheduler per workload type?
```

Three sentences. No greeting, no value props, no adjectives. Question is answerable in one line.

## 5. DISCOVERY

A question only possible because of step 1's open-source trail:

> *"On github.com/helio, which repos are personal experiments versus the production scheduler your customers actually run today — and how is production parity tested against those repos?"*

I can't ask that without having seen the org's commit cadence and repo list — which is why it belongs here.

## 6. COMPLICATION

- **Wrong-entity risk.** The seed entry's *stated* company (75-employee US Series A AI/ML platform on helio-compute.dev) **does not appear to exist**. Outreach addressed to a fabricated entity is wasted and reputational damage if it lands.
- **Shape mismatch.** Helio AG is Swiss Seed, not US Series A. If the AE brief assumed US timezone + larger org, expect a process mismatch.
- **No tech vendor gap visible.** Their product *is* an infra scheduler — they may feel less need for an external modernization agent than a fintech that has a bank partner. Harder "why now."
- **Founder-led buying motion.** At Seed-stage the CTO-equivalent often IS the founder, which means a single-person decision and slower procurement — outreach to Kevin Häfeli directly is the highest-leverage move.

## Verdict

`DEFER` — real entity, real engineering org, but not what the seed described. Pause outbound until the seed is replanted or until the team confirms we have a story for the Seed-stage, Switzerland, ~25-person version of Helio AG.
