# Screenshots — last regenerated 2026-07-14, dashboard run via agent-browser (Chrome DevTools, Factory Desktop pane at port 21022)

| File | Viewport | What it captures |
|---|---|---|
| `desktop-top.png` | 1440×900 | Header, caveat banner, KPI strip, filter chips, scatter quadrant plane (top of page) |
| `desktop-full.png` | 1440-wide, full-page scroll | Entire stack: KPI strip + filters + scatter + 20-row table in one composite |
| `mobile-full.png` | 414×800 (responsive) | Responsive layout — KPI grid → 2-col, scatter collapses to 1-col, table with internal scroll (see CSS `@media (max-width: 900px)` in `index.html`) |
| `desktop-top-real2.png`, `desktop-full-real2.png`, `mobile-real.png`, `desktop-top-v2.png` | — | Stale artifacts from earlier regen iterations; safe to delete |

These are reference artifacts only; they may not match the current dashboard after future edits.

## How the dashboard is regenerated

```bash
cd ~/factory-territory
python3 scripts/build_dashboard.py
```

This reads `data/accounts_enriched.csv` and `data/accounts_seed.csv`, joins them by row order (region + priority come from seed), and writes a single self-contained `dashboard/index.html` (no build step, no npm). Open it locally or via the embedded CDP pane:

```bash
agent-browser --cdp "$AGENT_BROWSER_CDP" open "file:///Users/nashwardycomcast.net/factory-territory/dashboard/index.html"
```
