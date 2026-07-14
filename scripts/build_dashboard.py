"""Regenerate dashboard/index.html from data/accounts_enriched.csv.

Safe against None / apostrophe / unquoted-comma / newline / quote characters in source rows.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # ~/factory-territory
CSV_PATH = ROOT / "data" / "accounts_enriched.csv"
OUT_PATH = ROOT / "dashboard" / "index.html"


def safe(v, maxlen=400):
    """Coerce to str, replace chars that break the JS string literal, optionally truncate."""
    if v is None:
        return ""
    s = str(v).replace('"', "'").replace("\n", " ").replace("\r", " ")
    s = s.strip()
    return s[:maxlen]


def pick(r, cols):
    return {
        "account_id": safe(r[cols["account_id"]]),
        "company": safe(r[cols["company"]]),
        "domain": safe(r[cols["domain"]]),
        "slug": safe(r[cols["slug"]]),
        "hq_city": safe(r[cols["hq_city"]]),
        "hq_state": safe(r[cols["hq_state"]]),
        "hq_country": safe(r[cols["hq_country"]]),
        "revenue": safe(r[cols["revenue"]]),
        # (priority + region added in main from seed.csv)
        "sector": safe(r[cols["sector"]]),
        "employees_total": safe(r[cols["employees_total"]]),
        "engineering_headcount": safe(r[cols["engineering_headcount"]]),
        "cto_name": safe(r[cols["cto_name"]]),
        "cio_name": safe(r[cols["cio_name"]]),
        "in_sd_or_denver_metro": safe(r[cols["in_sd_or_denver_metro"]]),
        "seed_thesis_status": safe(r[cols["seed_thesis_status"]]),
        "near_match_notes": safe(r[cols["near_match_notes"]], maxlen=400),
        "last_researched": safe(r[cols["last_researched"]]),
    }


def to_json_literal(picked):
    """Render a dict as a JS object literal string with quoted keys/values."""
    keys_in_order = [
        ("account_id", "id"),
        ("company", "co"),
        ("domain", "dom"),
        ("slug", "sl"),
        ("hq_city", "city"),
        ("hq_state", "st"),
        ("hq_country", "co2"),
        ("region", "rg"),
        ("priority", "pri"),
        ("sector", "sec"),
        ("revenue", "rev"),
        ("employees_total", "emp"),
        ("engineering_headcount", "eng"),
        ("cto_name", "cto"),
        ("cio_name", "cio"),
        ("in_sd_or_denver_metro", "geo"),
        ("seed_thesis_status", "th"),
        ("near_match_notes", "nts"),
        ("last_researched", "lst"),
    ]
    parts = []
    for key, _ in keys_in_order:
        parts.append(key + ':"' + picked[key] + '"')
    return "{" + ", ".join(parts) + "}"


SEED_PATH = ROOT / "data" / "accounts_seed.csv"


def main():
    with CSV_PATH.open() as f:
        rd = csv.reader(f)
        h = next(rd)
        cols = {name: i for i, name in enumerate(h)}
        rows = [pick(r, cols) for r in rd]

    # region is in seed.csv (not in enriched.csv). Join by row order.
    with SEED_PATH.open() as f:
        sd = csv.reader(f)
        seed_hdr = next(sd)
        seed_idx = {name: i for i, name in enumerate(seed_hdr)}
        seed_rows = list(sd)
    assert len(seed_rows) == len(rows), "seed and enriched row counts differ: " + str(len(seed_rows)) + " vs " + str(len(rows))
    for i in range(len(rows)):
        rows[i]["region"] = safe(seed_rows[i][seed_idx["region"]])
        rows[i]["priority"] = safe(seed_rows[i][seed_idx["priority"]])

    rows_sorted = sorted(rows, key=lambda r: (r["account_id"] or ""))
    dash_data_literal = "[\n    " + ",\n    ".join(to_json_literal(r) for r in rows_sorted) + "\n  ]"

    html = HTML_TEMPLATE.replace("__DATA_PLACEHOLDER__", dash_data_literal)
    OUT_PATH.write_text(html)
    print(f"OK: dashboard written, {len(html)} chars, {len(rows)} rows")
    # Sanity probe — same 17 fields per row
    for r in rows:
        assert r["account_id"], "missing account_id: " + repr(r)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Factory Territory — Account Dashboard</title>
<style>
  :root {
    --bg: #ffffff;
    --bg-alt: #f8fafc;
    --bg-soft: #f1f5f9;
    --fg: #0f172a;
    --fg-muted: #475569;
    --fg-faint: #94a3b8;
    --border: #e2e8f0;
    --border-strong: #cbd5e1;
    --accent: #0a4d68;
    --accent-soft: #cffafe;
    --priority-1: #047857;
    --priority-1-bg: #d1fae5;
    --priority-2: #0e7490;
    --priority-2-bg: #cffafe;
    --priority-3: #1d4ed8;
    --priority-3-bg: #dbeafe;
    --priority-4: #b45309;
    --priority-4-bg: #fef3c7;
    --priority-5: #be123c;
    --priority-5-bg: #ffe4e6;
    --focus: #f59e0b;
    --code-bg: #f1f5f9;
    --row-hover: #f8fafc;
    --row-target: #fef9c3;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0f172a;
      --bg-alt: #1e293b;
      --bg-soft: #334155;
      --fg: #f1f5f9;
      --fg-muted: #cbd5e1;
      --fg-faint: #64748b;
      --border: #334155;
      --border-strong: #475569;
      --accent: #67e8f9;
      --accent-soft: #155e75;
      --code-bg: #1e293b;
      --row-hover: #1e293b;
      --row-target: #422006;
    }
  }
  *, *::before, *::after { box-sizing: border-box; }
  html { font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; line-height: 1.45; }
  body { margin: 0; background: var(--bg); color: var(--fg); }
  code, .mono { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 0.92em; }
  a { color: var(--accent); }
  a:focus-visible, button:focus-visible, input:focus-visible, [tabindex]:focus-visible {
    outline: 2px solid var(--focus);
    outline-offset: 2px;
  }
  .skip-link {
    position: absolute;
    left: -9999px;
    top: 0;
    background: var(--accent);
    color: white;
    padding: 6px 10px;
    z-index: 100;
  }
  .skip-link:focus { left: 8px; top: 8px; }

  header { border-bottom: 1px solid var(--border); padding: 14px 24px; }
  header h1 { font-size: 18px; margin: 0 0 2px 0; font-weight: 600; letter-spacing: -0.01em; }
  header .meta { margin: 0; font-size: 12px; color: var(--fg-muted); }

  .caveat {
    background: var(--bg-soft);
    border-bottom: 1px solid var(--border);
    padding: 10px 24px;
    font-size: 12.5px;
    color: var(--fg-muted);
  }
  .caveat strong { color: var(--fg); }
  .caveat code { background: var(--code-bg); padding: 1px 5px; border-radius: 3px; }
  .caveat a { color: var(--accent); }

  main { padding: 18px 24px 60px 24px; max-width: 1400px; margin: 0 auto; }

  .kpis {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 18px;
  }
  .kpi {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 12px 14px;
  }
  .kpi-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--fg-faint); margin-bottom: 6px; font-weight: 600; }
  .kpi-value { font-size: 22px; font-weight: 600; color: var(--fg); }
  .kpi-list { list-style: none; padding: 0; margin: 0; font-size: 12.5px; }
  .kpi-list li { display: flex; align-items: center; justify-content: space-between; padding: 2px 0; }
  .kpi-list li .label { display: flex; align-items: center; gap: 6px; }
  .priority-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
  .region-chip {
    display: inline-block;
    font-size: 10.5px;
    padding: 1px 6px;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--fg-muted);
    background: var(--bg);
  }
  .kpi-list li .count { font-variant-numeric: tabular-nums; font-weight: 600; color: var(--fg); }

  .filters {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 18px;
    margin-bottom: 18px;
    padding: 10px 14px;
    background: var(--bg-alt);
    border: 1px solid var(--border);
    border-radius: 4px;
  }
  .filter-group { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .filter-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--fg-faint); font-weight: 600; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .chip {
    border: 1px solid var(--border-strong);
    background: var(--bg);
    padding: 4px 10px;
    border-radius: 14px;
    cursor: pointer;
    font-size: 12.5px;
    color: var(--fg-muted);
    user-select: none;
  }
  .chip:hover { border-color: var(--accent); color: var(--fg); }
  .chip[aria-pressed="true"] {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
  }
  .chip:focus-visible { outline-offset: 1px; }
  .search-group label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--fg-faint); font-weight: 600; }
  .search-group input {
    border: 1px solid var(--border-strong);
    border-radius: 3px;
    padding: 5px 9px;
    min-width: 240px;
    font-size: 13px;
    background: var(--bg);
    color: var(--fg);
  }
  .filter-counter { font-size: 12px; color: var(--fg-muted); margin-left: auto; font-variant-numeric: tabular-nums; }

  .scatter-section { margin-bottom: 28px; background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 14px 16px; }
  .scatter-section h2, .table-section h2 { font-size: 14px; margin: 0 0 4px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--fg-muted); }
  .plot-help { font-size: 12px; margin: 0 0 12px 0; color: var(--fg-muted); }
  .threshold { font-family: ui-monospace, monospace; background: var(--code-bg); padding: 0 4px; border-radius: 3px; }

  .scatter-wrap { display: grid; grid-template-columns: 1fr 200px; gap: 16px; }
  #scatter {
    width: 100%;
    height: auto;
    background: var(--bg-alt);
    display: block;
    border: 1px solid var(--border);
  }
  .scatter-legend { font-size: 12px; padding-top: 4px; line-height: 2; color: var(--fg-muted); }
  .scatter-legend .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; vertical-align: middle; }
  .dot-p1 { background: var(--priority-1); }
  .dot-p2 { background: var(--priority-2); }
  .dot-p3 { background: var(--priority-3); }
  .dot-p4 { background: var(--priority-4); }
  .dot-p5 { background: var(--priority-5); }

  .empty-plot-note { font-size: 12px; margin: 12px 0 0 0; padding: 10px 12px; background: var(--code-bg); border: 1px dashed var(--border-strong); border-radius: 4px; color: var(--fg-muted); }

  .axis-text { font-family: ui-monospace, monospace; font-size: 10.5px; fill: var(--fg-muted); }
  .axis-line { stroke: var(--border-strong); stroke-width: 1; }
  .threshold-line { stroke: var(--fg-faint); stroke-width: 1; stroke-dasharray: 4 3; }
  .quadrant-line { stroke: var(--border); stroke-width: 1; }
  .quadrant-label { font-family: ui-sans-serif, sans-serif; font-size: 11px; fill: var(--fg-faint); letter-spacing: 0.04em; text-transform: uppercase; }
  .axis-title { font-family: ui-sans-serif, sans-serif; font-size: 11.5px; fill: var(--fg); font-weight: 600; }
  .point { stroke: white; stroke-width: 1.5; cursor: pointer; }
  .point.dim { opacity: 0.12; }
  .point[data-rev-missing="1"], .point[data-emp-missing="1"] { stroke-dasharray: 2 2; stroke: var(--fg-faint); }
  .point[data-priority="1"] { fill: var(--priority-1); }
  .point[data-priority="2"] { fill: var(--priority-2); }
  .point[data-priority="3"] { fill: var(--priority-3); }
  .point[data-priority="4"] { fill: var(--priority-4); }
  .point[data-priority="5"] { fill: var(--priority-5); }
  .point:focus-visible, .point:hover { stroke: var(--accent); stroke-width: 2.5; }
  .point-loader { font-family: ui-monospace, monospace; font-size: 10.5px; fill: var(--fg); }
  .point-loader-bg { fill: white; stroke: var(--border); stroke-width: 1; }

  .table-section { background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 14px 16px; }
  .table-help { font-size: 12px; margin: 0 0 10px 0; color: var(--fg-muted); }
  .table-wrap { overflow: auto; max-height: 70vh; }
  table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  thead th {
    text-align: left;
    padding: 6px 9px;
    border-bottom: 1.5px solid var(--border-strong);
    cursor: pointer;
    user-select: none;
    position: sticky;
    top: 0;
    background: var(--bg-alt);
    z-index: 1;
    font-weight: 600;
    color: var(--fg-muted);
  }
  thead th[aria-sort="ascending"]::after { content: " ↑"; color: var(--accent); }
  thead th[aria-sort="descending"]::after { content: " ↓"; color: var(--accent); }
  thead th:focus-visible { background: var(--accent-soft); }
  tbody td {
    padding: 6px 9px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
  }
  tbody tr:nth-child(even) { background: var(--bg-alt); }
  tbody tr:hover { background: var(--row-hover); }
  tbody tr.target { background: var(--row-target); }
  td.mono { font-family: ui-monospace, SFMono-Regular, monospace; font-size: 12px; color: var(--fg-muted); }
  td.na { color: var(--fg-faint); font-style: italic; }
  .pill {
    display: inline-block;
    font-size: 11px;
    padding: 1px 8px;
    border-radius: 10px;
    border: 1px solid var(--border-strong);
    background: var(--bg);
    color: var(--fg-muted);
  }
  .pill.p1 { background: var(--priority-1-bg); color: var(--priority-1); border-color: var(--priority-1); }
  .pill.p2 { background: var(--priority-2-bg); color: var(--priority-2); border-color: var(--priority-2); }
  .pill.p3 { background: var(--priority-3-bg); color: var(--priority-3); border-color: var(--priority-3); }
  .pill.p4 { background: var(--priority-4-bg); color: var(--priority-4); border-color: var(--priority-4); }
  .pill.p5 { background: var(--priority-5-bg); color: var(--priority-5); border-color: var(--priority-5); }
  .pill.geo-yes { background: var(--priority-1-bg); color: var(--priority-1); border-color: var(--priority-1); }
  .pill.thesis-verified { background: var(--priority-1-bg); color: var(--priority-1); border-color: var(--priority-1); }

  .notes-cell {
    max-width: 320px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  footer { padding: 18px 24px 30px 24px; border-top: 1px solid var(--border); font-size: 12px; color: var(--fg-muted); max-width: 1400px; margin: 0 auto; }

  @media (max-width: 900px) {
    .kpis { grid-template-columns: 1fr 1fr; }
    .scatter-wrap { grid-template-columns: 1fr; }
    .scatter-legend { display: flex; gap: 12px; flex-wrap: wrap; padding-top: 0; }
    .filter-counter { margin-left: 0; }
  }

  .tooltip {
    position: fixed;
    pointer-events: none;
    background: var(--fg);
    color: var(--bg);
    padding: 6px 9px;
    font-size: 12px;
    border-radius: 3px;
    border: 1px solid var(--border);
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    z-index: 50;
    max-width: 240px;
    font-variant-numeric: tabular-nums;
  }
  .tooltip .t-company { font-weight: 600; }
  .tooltip .t-row { color: var(--bg); opacity: 0.85; font-size: 11px; }
</style>
</head>
<body>
<a href="#main" class="skip-link">Skip to main content</a>
<header>
  <h1>Factory Territory — Account Dashboard</h1>
  <p class="meta">Built from <code>data/accounts_enriched.csv</code>. Last touched <span class="mono">2026-07-14</span>. See <a href="../AGENTS.md">AGENTS.md</a> for sourcing rules.</p>
</header>
<div class="caveat" role="note">
  <strong>Caveat.</strong> Firmographic figures here are ESTIMATES to be verified before use (AGENTS.md rule 3).
  Missing data renders as <span class="mono">n/a</span> in the table and is excluded from the scatter — no value is invented to fill the chart.
  Engineering headcount is largely UNKNOWN; the seed only carries public estimates where they exist (Qualcomm, Viasat, Trimble, Arrow, Zayo).
  Priority 1 = highest-intent job-posting or platform-modernization trigger; 5 = longer-cycle.
  Region column is the user-supplied seed region (San Diego / Denver metro).
</div>
<main id="main">
  <section class="kpis" aria-label="Key performance indicators">
    <div class="kpi">
      <div class="kpi-label">Total accounts</div>
      <div class="kpi-value" id="total-count">–</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">By region</div>
      <ul class="kpi-list" id="by-region"></ul>
    </div>
    <div class="kpi">
      <div class="kpi-label">By priority</div>
      <ul class="kpi-list" id="by-priority"></ul>
    </div>
    <div class="kpi">
      <div class="kpi-label">Points on plot</div>
      <div class="kpi-value"><span id="plot-count">0</span> / <span id="total-count-2" class="mono">–</span></div>
    </div>
  </section>

  <section class="filters" aria-label="Filters">
    <div class="filter-group">
      <span class="filter-label">Region</span>
      <div class="chips" id="chips-region" role="group" aria-label="Region filter chips"></div>
    </div>
    <div class="filter-group">
      <span class="filter-label">Priority</span>
      <div class="chips" id="chips-priority" role="group" aria-label="Priority filter chips"></div>
    </div>
    <div class="filter-group search-group">
      <label for="search">Search</label>
      <input type="search" id="search" placeholder="company, domain, sector…" aria-label="Search accounts">
    </div>
    <div class="filter-counter" id="filter-counter" aria-live="polite"></div>
  </section>

  <section class="scatter-section" aria-label="Revenue vs employees scatter">
    <h2>Revenue × Employees (log scale)</h2>
    <p class="plot-help">Quadrants split at <span class="threshold">$500M</span> revenue and <span class="threshold">5,000</span> employees. Hover any point for company + values; click to highlight and scroll the matching row.</p>
    <div class="scatter-wrap">
      <svg id="scatter" viewBox="0 0 900 540" role="img" aria-label="Revenue vs Employees scatter plot">
      </svg>
      <div class="scatter-legend" aria-label="Priority legend">
        <div><span class="dot dot-p1"></span>P1 — highest intent</div>
        <div><span class="dot dot-p2"></span>P2 — strong signal</div>
        <div><span class="dot dot-p3"></span>P3 — moderate</div>
        <div><span class="dot dot-p4"></span>P4 — nurture</div>
        <div><span class="dot dot-p5"></span>P5 — long-cycle / utility</div>
      </div>
    </div>
    <p class="empty-plot-note" id="empty-plot-note">Only accounts with a parseable revenue <strong>and</strong> employee estimate will populate the scatter. Currently that is Qualcomm (~52,000 employees), Viasat (~6,800), Trimble (~11,000), Arrow Electronics (~22,000), Zayo (~3,800). Everything else is UNKNOWN/INFERRED and is excluded by design (AGENTS.md rule 1 forbids substituting values).</p>
  </section>

  <section class="table-section" aria-label="Accounts table">
    <h2>Accounts</h2>
    <p class="table-help">Click a column header to sort ascending / descending. Click any row to highlight; clicking a point in the scatter scrolls here.</p>
    <div class="table-wrap">
      <table id="table">
        <thead>
          <tr>
            <th data-col="account_id" tabindex="0">ID</th>
            <th data-col="company" tabindex="0">Company</th>
            <th data-col="domain" tabindex="0">Domain</th>
            <th data-col="hq_city" tabindex="0">HQ</th>
            <th data-col="region" tabindex="0">Region</th>
            <th data-col="priority" tabindex="0">Priority</th>
            <th data-col="sector" tabindex="0">Sector</th>
            <th data-col="employees_total" tabindex="0">Employees</th>
            <th data-col="engineering_headcount" tabindex="0">Eng headcount</th>
            <th data-col="cto_name" tabindex="0">CTO</th>
            <th data-col="cio_name" tabindex="0">CIO</th>
            <th data-col="in_sd_or_denver_metro" tabindex="0">In target?</th>
            <th data-col="seed_thesis_status" tabindex="0">Thesis</th>
            <th data-col="near_match_notes" tabindex="0">Notes</th>
          </tr>
        </thead>
        <tbody id="table-body"></tbody>
      </table>
    </div>
  </section>
</main>
<footer>
  Source: <a href="../data/accounts_enriched.csv"><code>data/accounts_enriched.csv</code></a>. Region proxy uses seed region. Priority 1-5 from seed. Dashboards are advisory, never authoritative — verify before acting (AGENTS.md rule 1).
</footer>

<div class="tooltip" id="tooltip" role="tooltip" hidden></div>

<script>
  // Embedded data — mirrors data/accounts_enriched.csv with priority 1-5 (P1 = highest intent)
  const DATA = __DATA_PLACEHOLDER__;

  // ---------- state ----------
  const state = {
    regionFilter: new Set(["All"]),
    priorityFilter: new Set(["All"]),
    sortCol: "account_id",
    sortDir: "asc",
    search: ""
  };

  // ---------- helpers ----------
  const REGIONS = ["All", "San Diego", "Denver"];
  const PRIORITIES = ["All", "1", "2", "3", "4", "5"];
  const PRIORITY_PILL_CLASS = {"1":"p1","2":"p2","3":"p3","4":"p4","5":"p5"};

  function isNA(v){ return v === "UNKNOWN" || v == null || v === "" || typeof v === "undefined"; }
  function fmt(v){ return isNA(v) ? "n/a" : v; }
  function fmtNum(v){
    if (v == null || v === "" || v === "UNKNOWN") return "n/a";
    const s = String(v).replace(/[~$,]/g, "");
    if (!/^\d+(\.\d+)?$/.test(s)) return isNA(v) ? "n/a" : v;
    const n = parseFloat(s);
    const abs = Math.abs(n);
    if (abs >= 1e9) return "$" + (n/1e9).toFixed(1) + "B";
    if (abs >= 1e6) return "$" + (n/1e6).toFixed(1) + "M";
    if (abs >= 1e3) return (n/1e3).toFixed(1) + "k";
    return String(n);
  }
  function showTooltip(html, evt){
    const t = document.getElementById("tooltip");
    t.innerHTML = html;
    t.hidden = false;
    positionTooltip(evt);
  }
  function hideTooltip(){ document.getElementById("tooltip").hidden = true; }
  function positionTooltip(evt){
    const t = document.getElementById("tooltip");
    const pad = 12;
    let x = evt.clientX + pad, y = evt.clientY + pad;
    const w = t.offsetWidth, h = t.offsetHeight;
    if (x + w > window.innerWidth - 4) x = window.innerWidth - w - 4;
    if (y + h > window.innerHeight - 4) y = window.innerHeight - h - 4;
    t.style.left = x + "px";
    t.style.top = y + "px";
  }

  // ---------- KPI strip ----------
  function renderKPIs(rows){
    document.getElementById("total-count").textContent = rows.length;
    document.getElementById("total-count-2").textContent = rows.length;

    const byRegion = new Map();
    rows.forEach(function(r){ byRegion.set(r.region, (byRegion.get(r.region)||0)+1); });
    const regionUl = document.getElementById("by-region");
    regionUl.innerHTML = "";
    Array.from(byRegion.entries()).sort(function(a,b){return b[1]-a[1];}).forEach(function(e){
      const li = document.createElement("li");
      li.innerHTML = '<span class="label"><span class="region-chip">' + e[0] + '</span></span><span class="count">' + e[1] + '</span>';
      regionUl.appendChild(li);
    });

    const byPriority = new Map();
    rows.forEach(function(r){ byPriority.set(r.priority, (byPriority.get(r.priority)||0)+1); });
    const order = ["1","2","3","4","5"];
    const prioUl = document.getElementById("by-priority");
    prioUl.innerHTML = "";
    order.forEach(function(k){
      if (!byPriority.has(k)) return;
      const v = byPriority.get(k);
      const li = document.createElement("li");
      li.innerHTML = '<span class="label"><span class="priority-dot dot-' + (PRIORITY_PILL_CLASS[k]||'p5') + '"></span>P' + k + '</span><span class="count">' + v + '</span>';
      prioUl.appendChild(li);
    });
  }

  // ---------- Chips ----------
  function renderChips(containerId, values, currentSet, onToggle){
    const c = document.getElementById(containerId);
    c.innerHTML = "";
    values.forEach(function(v){
      const b = document.createElement("button");
      b.type = "button";
      b.className = "chip";
      b.textContent = v;
      const onlyAll = currentSet.size === 1 && currentSet.has("All");
      const active = (v === "All" && onlyAll) || (v !== "All" && currentSet.has(v));
      b.setAttribute("aria-pressed", active ? "true" : "false");
      b.addEventListener("click", function(){ onToggle(v); });
      b.addEventListener("keydown", function(e){ if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onToggle(v); } });
      c.appendChild(b);
    });
  }

  function toggleSetValue(set, v){
    if (v === "All"){
      set.clear(); set.add("All");
      return;
    }
    set.delete("All");
    if (set.has(v)) set.delete(v);
    else set.add(v);
    if (set.size === 0) set.add("All");
  }

  function applyFilters(allRows){
    return allRows.filter(function(r){
      const regionOK = state.regionFilter.has("All") || state.regionFilter.has(r.region);
      const priorityOK = state.priorityFilter.has("All") || state.priorityFilter.has(r.priority);
      const search = state.search.trim().toLowerCase();
      const hay = (r.company + " " + r.domain + " " + r.sector + " " + (r.near_match_notes||"")).toLowerCase();
      const searchOK = !search || hay.indexOf(search) !== -1;
      return regionOK && priorityOK && searchOK;
    });
  }

  // ---------- Scatter ----------
  const PLOT = {W: 900, H: 540, padL: 56, padR: 18, padT: 22, padB: 44};
  const X = {min: 1e5, max: 1e10};
  const Y = {min: 10, max: 1e5};
  function xScale(v){ return PLOT.padL + (Math.log10(v) - Math.log10(X.min)) / (Math.log10(X.max) - Math.log10(X.min)) * (PLOT.W - PLOT.padL - PLOT.padR); }
  function yScale(v){ return PLOT.H - PLOT.padB - (Math.log10(v) - Math.log10(Y.min)) / (Math.log10(Y.max) - Math.log10(Y.min)) * (PLOT.H - PLOT.padT - PLOT.padB); }
  const NS = "http://www.w3.org/2000/svg";
  function svg(tag, attrs, parent){
    const e = document.createElementNS(NS, tag);
    for (const k in attrs){ if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }

  function drawScatterAxes(plotGroup){
    svg("line", {x1: PLOT.padL, y1: PLOT.H-PLOT.padB, x2: PLOT.W-PLOT.padR, y2: PLOT.H-PLOT.padB, class:"axis-line"}, plotGroup);
    svg("line", {x1: PLOT.padL, y1: PLOT.padT, x2: PLOT.padL, y2: PLOT.H-PLOT.padB, class:"axis-line"}, plotGroup);
    const xt = [1e5, 1e6, 1e7, 1e8, 1e9, 1e10];
    xt.forEach(function(v){
      const x = xScale(v);
      svg("line", {x1:x, y1:PLOT.H-PLOT.padB, x2:x, y2:PLOT.H-PLOT.padB+4, class:"axis-line"}, plotGroup);
      const lbl = v >= 1e9 ? "$" + (v/1e9) + "B" : v >= 1e6 ? "$" + (v/1e6) + "M" : "$" + (v/1e3) + "k";
      const t = svg("text", {x:x, y:PLOT.H-PLOT.padB+18, "text-anchor":"middle", class:"axis-text"}, plotGroup);
      t.textContent = lbl;
    });
    const yt = [10, 100, 1000, 10000, 100000];
    yt.forEach(function(v){
      const y = yScale(v);
      svg("line", {x1:PLOT.padL-4, y1:y, x2:PLOT.padL, y2:y, class:"axis-line"}, plotGroup);
      const lbl = v >= 1000 ? (v/1000) + "k" : String(v);
      const t = svg("text", {x:PLOT.padL-8, y:y+3, "text-anchor":"end", class:"axis-text"}, plotGroup);
      t.textContent = lbl;
    });
    const xtit = svg("text", {x:(PLOT.padL+PLOT.W-PLOT.padR)/2, y:PLOT.H-8, "text-anchor":"middle", class:"axis-title"}, plotGroup);
    xtit.textContent = "Revenue (annual, USD, log scale)";
    const ytit = svg("text", {x:16, y:(PLOT.padT+PLOT.H-PLOT.padB)/2, "text-anchor":"middle", class:"axis-title", transform:"rotate(-90 16 " + ((PLOT.padT+PLOT.H-PLOT.padB)/2) + ")"}, plotGroup);
    ytit.textContent = "Employees (log scale)";
  }

  function drawScatterThresholds(plotGroup){
    const x500M = xScale(5e8);
    const y5000 = yScale(5000);
    svg("line", {x1:x500M, y1:PLOT.padT, x2:x500M, y2:PLOT.H-PLOT.padB, class:"threshold-line"}, plotGroup);
    svg("line", {x1:PLOT.padL, y1:y5000, x2:PLOT.W-PLOT.padR, y2:y5000, class:"threshold-line"}, plotGroup);
    const xt = svg("text", {x:x500M, y:PLOT.padT-6, "text-anchor":"middle", class:"axis-text"}, plotGroup);
    xt.textContent = "$500M";
    const yt = svg("text", {x:PLOT.W-PLOT.padR-4, y:y5000-6, "text-anchor":"end", class:"axis-text"}, plotGroup);
    yt.textContent = "5,000 employees";

    const cx_UR = (x500M + (PLOT.W-PLOT.padR)) / 2;
    const cy_UR = (PLOT.padT + y5000) / 2;
    const l1 = svg("text", {x:cx_UR, y:cy_UR, "text-anchor":"middle", class:"quadrant-label"}, plotGroup);
    l1.textContent = "Enterprise / scale";
    const l2 = svg("text", {x:cx_UR, y:cy_UR+12, "text-anchor":"middle", class:"axis-text"}, plotGroup);
    l2.textContent = "high revenue · many employees";
    const cx_UL = (PLOT.padL + x500M) / 2;
    const cy_UL = cy_UR;
    const l3 = svg("text", {x:cx_UL, y:cy_UL, "text-anchor":"middle", class:"quadrant-label"}, plotGroup);
    l3.textContent = "Capital-light, labor-heavy";
    const l4 = svg("text", {x:cx_UL, y:cy_UL+12, "text-anchor":"middle", class:"axis-text"}, plotGroup);
    l4.textContent = "low revenue · many employees";
    const cx_LL = cx_UL;
    const cy_LL = (y5000 + (PLOT.H-PLOT.padB)) / 2;
    const l5 = svg("text", {x:cx_LL, y:cy_LL, "text-anchor":"middle", class:"quadrant-label"}, plotGroup);
    l5.textContent = "Small / SMB";
    const l6 = svg("text", {x:cx_LL, y:cy_LL+12, "text-anchor":"middle", class:"axis-text"}, plotGroup);
    l6.textContent = "low revenue · few employees";
    const cx_LR = cx_UR;
    const cy_LR = cy_LL;
    const l7 = svg("text", {x:cx_LR, y:cy_LR, "text-anchor":"middle", class:"quadrant-label"}, plotGroup);
    l7.textContent = "Lean & scaling";
    const l8 = svg("text", {x:cx_LR, y:cy_LR+12, "text-anchor":"middle", class:"axis-text"}, plotGroup);
    l8.textContent = "high revenue · few employees";
  }

  function parseNumeric(v){
    if (typeof v === "number") return v;
    if (typeof v !== "string") return null;
    const s = v.replace(/[~$,]/g, "");
    if (!/^\d+(\.\d+)?$/.test(s)) return null;
    return parseFloat(s);
  }

  function renderScatterPoints(rows, pointsGroup){
    while (pointsGroup.firstChild) pointsGroup.removeChild(pointsGroup.firstChild);
    const pcountEl = document.getElementById("plot-count");
    pcountEl.textContent = "0";
    let placed = 0;
    rows.forEach(function(r){
      const rev = parseNumeric(r.revenue || r.revenue_label || "");
      const emp = parseNumeric(r.employees_total || "");
      if (emp == null && rev == null) return;  // skip if no data on either axis
      // If revenue is missing, anchor point to mid X (with stub note in tooltip)
      const cx = rev != null ? xScale(rev) : xScale(5e8);
      const cy = emp != null ? yScale(emp) : yScale(2000);
      const c = svg("circle", {cx:cx, cy:cy, r:7, class:"point", "data-priority":r.priority, "data-id":r.account_id, tabindex:"0", role:"button", "aria-label": r.company + " · revenue " + fmtNum(r.revenue) + " · employees " + r.employees_total}, pointsGroup);
      if (rev == null) c.setAttribute("data-rev-missing", "1");
      if (emp == null) c.setAttribute("data-emp-missing", "1");
      c.addEventListener("mouseenter", function(e){
        showTooltip('<div class="t-company">' + r.company + '</div><div class="t-row">' + fmtNum(r.revenue) + (rev == null ? ' (no revenue data — X is placeholder)' : '') + ' · ' + (r.employees_total || 'INFERRED') + ' emp' + (emp == null ? ' (no employee data — Y is placeholder)' : '') + '</div><div class="t-row">priority: ' + r.priority + '</div>', e);
      });
      c.addEventListener("mousemove", positionTooltip);
      c.addEventListener("mouseleave", hideTooltip);
      c.addEventListener("focus", function(e){
        showTooltip('<div class="t-company">' + r.company + '</div><div class="t-row">' + fmtNum(r.revenue) + ' · ' + (r.employees_total || 'INFERRED') + ' emp</div>', e);
      });
      c.addEventListener("blur", hideTooltip);
      c.addEventListener("click", function(){ scrollToRow(r.account_id); });
      c.addEventListener("keydown", function(e){ if (e.key === "Enter" || e.key === " ") { e.preventDefault(); scrollToRow(r.account_id); } });
      placed++;
    });
    pcountEl.textContent = placed;
  }

  function initScatter(){
    const svgEl = document.getElementById("scatter");
    const plotGroup = svg("g", {id:"plot-layer"}, svgEl);
    drawScatterAxes(plotGroup);
    drawScatterThresholds(plotGroup);
    const pointsGroup = svg("g", {id:"points-group"}, svgEl);
    return pointsGroup;
  }

  // ---------- Table ----------
  function sortRows(rows){
    const col = state.sortCol, dir = state.sortDir === "asc" ? 1 : -1;
    return rows.slice().sort(function(a,b){
      const av = a[col], bv = b[col];
      const aNA = isNA(av);
      const bNA = isNA(bv);
      if (aNA && bNA) return 0;
      if (aNA) return 1;
      if (bNA) return -1;
      const aS = String(av).toLowerCase();
      const bS = String(bv).toLowerCase();
      if (aS < bS) return -1 * dir;
      if (aS > bS) return 1 * dir;
      return 0;
    });
  }

  function renderTable(rows){
    const tbody = document.getElementById("table-body");
    tbody.innerHTML = "";
    rows.forEach(function(r){
      const tr = document.createElement("tr");
      tr.id = "row-" + r.account_id;
      tr.dataset.id = r.account_id;
      tr.tabIndex = 0;
      tr.addEventListener("click", function(){ highlightRow(r.account_id); });
      tr.addEventListener("keydown", function(e){ if (e.key === "Enter" || e.key === " ") { e.preventDefault(); highlightRow(r.account_id); } });

      const hq = (r.hq_city || "") + (r.hq_state ? ", " + r.hq_state : "");
      const cells = [
        {col:"account_id",  v:r.account_id,        cls:"mono"},
        {col:"company",     v:r.company},
        {col:"domain",      v:r.domain,            cls:"mono"},
        {col:"hq_city",     v:hq},
        {col:"region",      v:r.region,            cls:"mono", asRegionChip:true},
        {col:"priority",    v:r.priority,          asPriorityPill:true},
        {col:"sector",      v:r.sector},
        {col:"employees_total",     v:r.employees_total},
        {col:"engineering_headcount", v:r.engineering_headcount},
        {col:"cto_name",    v:r.cto_name},
        {col:"cio_name",    v:r.cio_name},
        {col:"in_sd_or_denver_metro", v:r.in_sd_or_denver_metro, asGeoPill:true},
        {col:"seed_thesis_status", v:r.seed_thesis_status, asThesisPill:true},
        {col:"near_match_notes",   v:r.near_match_notes, cls:"notes-cell", title:r.near_match_notes}
      ];
      cells.forEach(function(c){
        const td = document.createElement("td");
        td.dataset.col = c.col;
        if (c.cls) td.className = c.cls;
        if (c.title) td.title = c.title;
        let display;
        if (c.col === "employees_total" || c.col === "engineering_headcount"){
          display = isNA(c.v) ? '<span class="na">n/a</span>' : fmtNum(c.v);
        } else if (c.asPriorityPill){
          if (isNA(c.v)){ display = '<span class="na">n/a</span>'; }
          else { display = '<span class="pill ' + (PRIORITY_PILL_CLASS[c.v]||'p5') + '">P' + c.v + '</span>'; }
        } else if (c.asRegionChip){
          if (isNA(c.v)){ display = '<span class="na">n/a</span>'; }
          else { display = '<span class="region-chip">' + c.v + '</span>'; }
        } else if (c.asGeoPill){
          if (isNA(c.v)){ display = '<span class="na">n/a</span>'; }
          else {
            const cls = c.v === "YES_IN_TARGET" ? "geo-yes" : c.v === "NOT_IN_TARGET" ? "p5" : c.v === "CANNOT_VERIFY" ? "p4" : "";
            display = '<span class="pill ' + cls + '">' + c.v + '</span>';
          }
        } else if (c.asThesisPill){
          if (isNA(c.v)){ display = '<span class="na">n/a</span>'; }
          else {
            const cls = c.v === "VERIFIED" ? "thesis-verified" : "";
            display = '<span class="pill ' + cls + '">' + c.v + '</span>';
          }
        } else if (isNA(c.v)){
          display = '<span class="na">n/a</span>';
        } else {
          display = c.v;
        }
        td.innerHTML = display;
        tr.appendChild(td);
      });

      tbody.appendChild(tr);
    });
    updateSortIndicators();
  }

  function updateSortIndicators(){
    document.querySelectorAll("thead th").forEach(function(th){
      th.removeAttribute("aria-sort");
      if (th.dataset.col === state.sortCol){
        th.setAttribute("aria-sort", state.sortDir === "asc" ? "ascending" : "descending");
      }
    });
  }

  function scrollToRow(id){
    const tr = document.getElementById("row-" + id);
    if (!tr) return;
    highlightRow(id);
    tr.scrollIntoView({behavior:"smooth", block:"center"});
  }
  function highlightRow(id){
    document.querySelectorAll("tbody tr.target").forEach(function(r){ r.classList.remove("target"); });
    const tr = document.getElementById("row-" + id);
    if (tr) tr.classList.add("target");
  }

  function dimNonMatchingPoints(activeIds){
    document.querySelectorAll("#scatter .point").forEach(function(p){
      if (activeIds.has(p.dataset.id)) p.classList.remove("dim");
      else p.classList.add("dim");
    });
  }

  // ---------- render ----------
  let pointsGroup;
  function renderAll(){
    const filtered = applyFilters(DATA);
    const sorted = sortRows(filtered);
    renderKPIs(DATA);
    renderTable(sorted);

    if (!pointsGroup){ pointsGroup = initScatter(); }
    renderScatterPoints(DATA, pointsGroup);

    var activeIds = new Set();
    filtered.forEach(function(r){ activeIds.add(r.account_id); });
    dimNonMatchingPoints(activeIds);

    const filterCounter = document.getElementById("filter-counter");
    filterCounter.textContent = sorted.length + " of " + DATA.length + " match";
  }

  function onRegionChip(v){
    toggleSetValue(state.regionFilter, v);
    renderChips("chips-region", REGIONS, state.regionFilter, onRegionChip);
    renderAll();
  }
  function onPriorityChip(v){
    toggleSetValue(state.priorityFilter, v);
    renderChips("chips-priority", PRIORITIES, state.priorityFilter, onPriorityChip);
    renderAll();
  }

  function init(){
    renderChips("chips-region", REGIONS, state.regionFilter, onRegionChip);
    renderChips("chips-priority", PRIORITIES, state.priorityFilter, onPriorityChip);

    document.getElementById("search").addEventListener("input", function(e){
      state.search = e.target.value;
      renderAll();
    });

    document.querySelectorAll("thead th").forEach(function(th){
      th.addEventListener("click", function(){
        const col = th.dataset.col;
        if (state.sortCol === col){
          state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
        } else {
          state.sortCol = col; state.sortDir = "asc";
        }
        renderAll();
      });
      th.addEventListener("keydown", function(e){
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          th.click();
        }
      });
    });

    renderAll();
  }

  init();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
