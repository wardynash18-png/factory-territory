# Screenshots — last regenerated 2026-07-14

All shots are taken via the Factory Desktop embedded CDP pane (Chrome DevTools) at the dashboard URL `file:///Users/nashwardycomcast.net/factory-territory/dashboard/index.html` with viewport 1440×900.

| File | What it captures |
|---|---|
| `desktop-top.png` | Header, caveat banner, KPI strip (20 accounts, 10 SD / 10 Denver, P1–P5 mix, 5 points on plot), filter chips (region + priority 1–5 + search), scatter quadrant plane with the 5 publicly-verifiable companies (Qualcomm, Viasat, Trimble, Arrow, Zayo), priority legend |
| `desktop-full.png` | Same view as `desktop-top.png` plus the full sortable 20-row table and the footer |

## How the dashboard is regenerated

```bash
cd ~/factory-territory
python3 scripts/build_dashboard.py
```

If the build script does not exist yet, the embedded JSON is rebuilt by reading `data/accounts_enriched.csv` and joining `data/accounts_seed.csv` for the priority column. The `dashboard/index.html` file is the source of truth — it is a single self-contained file (no build step, no npm).

Open it locally or via the embedded CDP pane:

```bash
agent-browser --cdp "$AGENT_BROWSER_CDP" open "file:///Users/nashwardycomcast.net/factory-territory/dashboard/index.html"
```

## Notes on the scatter plot

Revenue values are deliberately absent for most rows because `data/accounts_enriched.csv` does not carry revenue estimates for the seed companies (the seed focuses on hiring signals and tech-debt signals, not financials — per AGENTS.md rule 3). As a result the scatter populates only the 5 rows that have public employee estimates: Qualcomm, Viasat, Trimble, Arrow Electronics, Zayo Group. All 5 are vertically anchored to the $500M revenue place-holder x, marked `data-rev-missing="1"` in the SVG.

This is intentional. We never invent values to fill a chart.

## Stale screenshots to delete

Any PNG whose name does not match one of the two above (`desktop-top.png`, `desktop-full.png`) is a stale artifact from earlier regen iterations and is safe to remove.
