# Screenshots — regenerated 2026-07-14

The dashboard is a single self-contained HTML file (`../index.html`). It has three tabs and a default landing (Today).

| File | What it shows |
|---|---|
| `v2-today.png` | Default landing. "Today · 2026-07-14" + stat line + sections: Overdue follow-ups, Due today, Stale signals (>30d), Accounts with no next action. Empty states when a section has zero rows. |
| `v2-accounts.png` | Accounts tab. Left: filter chips (Region / Priority / Status) + search + 20-row list with quick status badges. Right: detail panel for the selected account — pipeline, notes, next-action, contacts with confidence badges, signals with decay, references, verify-before-sending checklist, 4-touch sequence with copy / mark-sent / char-count. |
| `v2-thesis.png` | Thesis tab. Argument for the territory: revenue × employees scatter, log scale, with quadrant boundaries and the 5 publicly-verifiable employees-known accounts plotted (Qualcomm / Viasat / Trimble / Arrow / Zayo). |

All shots are taken via the Factory Desktop embedded CDP browser pane, viewport 1440×900.

## Why some accounts show "stale" without real-world age

The build script (`../../scripts/build_dashboard.py`) back-dates `last_researched` for five accounts (A009 CSG, A013 Liberty Global, A016 Arrow, A017 Maxar/Vantor, A018 Kratos) so the signal-decay feature is visually testable. In a production run those fields would be the date of the freshest source URL. The 30/60-day thresholds and the red/amber/fresh badges work the same way regardless.

## What the dashboard is NOT

- It is not a research artifact. Hypothesis-level claims stay in `research/<account>.md` (none exist yet for the SD/Denver seed — to be written when the territory gets a real rep).
- It is not a CRM. localStorage is the only storage layer. Export to CSV is the round-trip mechanism.
- It does not invent signals. Badges, lists, and the scatter plot all surface only what is in the source CSVs.

## How to regenerate

```bash
python3 ../../scripts/build_dashboard.py
```

Then open `../index.html` (or via the embedded CDP pane):

```bash
agent-browser --cdp "$AGENT_BROWSER_CDP" open "file:///Users/nashwardycomcast.net/factory-territory/dashboard/index.html"
```
