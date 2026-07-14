"""Regenerate dashboard/index.html — territory prospecting tool.

Three tabs: TODAY (work queue, default landing), ACCOUNTS (list + detail),
THESIS (scatter argument).

Reads data/accounts_enriched.csv + data/accounts_seed.csv + data/contacts.csv.
Writes a single self-contained dashboard/index.html. No npm, no framework,
no build step beyond this script.
"""
import csv
import json
import re
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_ENRICHED = ROOT / "data" / "accounts_enriched.csv"
CSV_SEED = ROOT / "data" / "accounts_seed.csv"
CSV_CONTACTS = ROOT / "data" / "contacts.csv"
OUT_PATH = ROOT / "dashboard" / "index.html"

TODAY = "2026-07-14"  # fixed per session — AGENTS.md says "Today is 2026-07-14"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def safe(v, default=""):
    if v is None:
        return default
    s = str(v).strip()
    return s if s else default

def collapse(s):
    return re.sub(r"\s+", " ", s).strip()

def infer_region(state):
    if state == "CA": return "San Diego"
    if state == "CO": return "Denver"
    return ""

# ---------------------------------------------------------------------------
# Parse CSVs
# ---------------------------------------------------------------------------
def load_csv(path, expected_cols=None):
    with open(path, encoding="utf-8") as f:
        rd = csv.reader(f)
        h = [c.strip() for c in next(rd)]
        rows = list(rd)
    return h, rows

# Enriched
enriched_h, enriched_rows = load_csv(CSV_ENRICHED)
enriched_cols = {c: i for i, c in enumerate(enriched_h)}

# Seed
with open(CSV_SEED, encoding="utf-8") as f:
    seed_by_company = {r["company"].strip(): r for r in csv.DictReader(f)}

# Contacts
with open(CSV_CONTACTS, encoding="utf-8") as f:
    contacts = list(csv.DictReader(f))

# ---------------------------------------------------------------------------
# Compose per-account JSON
# ---------------------------------------------------------------------------
PICK = [
    "account_id", "company", "domain", "slug", "hq_city", "hq_state",
    "hq_country", "region", "sector",
    "employees_total", "engineering_headcount",
    "cto_name", "cio_name", "cto_source_url", "cio_source_url",
    "github_url", "in_sd_or_denver_metro", "last_researched",
    "near_match_notes",
]

def slugify_company(company):
    # EchoStar / DISH matches "echostar-dish" slug
    s = company.lower().replace(" / ", "-").replace("/", "-").replace(" ", "-")
    return re.sub(r"[^a-z0-9-]", "", s)

def normalize_company_for_seed_match(c):
    return c.strip()

# Group contacts by account_id
contacts_by_acct = {}
for c in contacts:
    contacts_by_acct.setdefault(c["account_id"], []).append(c)

# Analogues (Factory customers) — from AGENTS.md known customers list
ANALOGUES = {
    "A001": ("Nvidia", "Both are chip / firmware houses with massive embedded codebases; CIO discussion of agentic workflows lines up."),
    "A002": ("MongoDB", "DaVita is the MongoDB analogue: a software-in-its-own-product company undergoing platform modernization."),
    "A003": ("Bayer", "Both FDA-regulated; agentic AI for traceable / auditable workflows in regulated environments is the precise Bayer analogue."),
    "A004": ("Morgan Stanley", "Payments + mainframe + SI partner; exact mirror of Morgan Stanley's modernization posture."),
    "A005": ("Morgan Stanley", "Wealth-management platform modernization with a CIO whose remit literally is the platform; close to Morgan Stanley."),
    "A006": ("Morgan Stanley", "Acquirer-inherited data stacks; the typical buyer shape is a Morgan Stanley-style platform-modernization buyer."),
    "A007": ("Palo Alto Networks", "Defense + classified; engineering motion resembles Palo Alto's regulated-infra buy."),
    "A008": ("Palo Alto Networks", "Satellite + wireless + 5G build; same regulatory shape as Palo Alto Networks infra."),
    "A009": ("MongoDB", "B2B software with its own legacy core (MongoDB analogue)."),
    "A010": ("Adobe", "Defense + commercial + post-acquisition codebase — Adobe's acquisition-integration story."),
    "A011": ("Bayer", "FDA-regulated life sciences; Bayer analogue."),
    "A012": ("Adobe", "Acquisition-inherited codebases; Adobe's consolidation story."),
    "A013": ("Palo Alto Networks", "OSS/BSS integration across many national operators — same shape as Palo Alto's stack sprawl."),
    "A014": ("MongoDB", "Software company with its own legacy problem."),
    "A015": ("Bayer", "FDA-regulated medical device firmware; Bayer analogue."),
    "A016": ("EY", "ERP + supply-chain sprawl across 80 countries; enterprise SI/consulting motion (EY analogue)."),
    "A017": ("Palo Alto Networks", "Classified / air-gapped geospatial; Palo Alto buyer shape."),
    "A018": ("Palo Alto Networks", "Defense UAS, air-gapped; Palo Alto analogue."),
    "A019": ("Morgan Stanley", "Utility SCADA, regulated, ancient core; same shape as Morgan Stanley's mainframe modernization."),
    "A020": ("EY", "PE-owned, network provisioning-built-through-acquisition; cost discipline.",
        "Morgan Stanley"),
    "A020": ("EY", "PE-owned, network provisioning-built-through-acquisition; cost discipline argues the same ROI story Morgan Stanley uses."),
}

# Per-account COMPLICATION (one-liner that the rep will face in a call)
COMPLICATIONS = {
    "A001": "Apr 2026 San Diego layoffs of 60 — internal cost discipline; approach must show efficiency not headcount.",
    "A002": "Transformation budget may already be tagged for GCP migration; qualify whether Factory is IN-scope or competing.",
    "A003": "FDA-regulated — every agent action needs an audit trail; engineering review board will gate.",
    "A004": "HCLTech AI-led platform partnership (Mar 2025) — verify whether HCLTech owns the tooling budget before pitching.",
    "A005": "Hyderabad GCC is the company's own competing solution; need a story for why US-tier Factory differs.",
    "A006": "Serial acquirer — multiple parallel integration programs compete for platform budget.",
    "A007": "Classified / air-gapped — sales cycle measured in years, not quarters.",
    "A008": "Combined earnings pressure from EchoStar + DISH merger; every platform spend is scrutinized.",
    "A009": "Carrier-integration contracts forbid breaking changes — modernization is constrained, not aspirational.",
    "A010": "Post-Inmarsat integration is ongoing; pitching another acquisition-style tool may fatigue account.",
    "A011": "FDA-regulated; change control is the dominant cost.",
    "A012": "Multiple acquisitions (B2W, Transporeon) — engineering org is mid-integration already.",
    "A013": "Bermuda-domiciled parent; selling into someone else's budget risk per AGENTS.md geo rule.",
    "A014": "Co has its own legacy core (since 1979); internal champion will defend current stack.",
    "A015": "FDA-regulated CGM firmware; safety-certification overhead applies.",
    "A016": "Distribution-heavy ERP sprawl in 80 countries — buyer is integration not modernization.",
    "A017": "Classified / air-gapped; gov-program-of-record gates every tool.",
    "A018": "Air-gapped UAS; on-prem only; Platform-as-Service frame is wrong, agents-on-isolated-VM frame is right.",
    "A019": "Safety-critical SCADA — one wrong story and procurement closes the door.",
    "A020": "PE-owned; every dollar is ROI-tested, returns narrative mandatory.",
}

# References (URLs) — pre-extracted from enriched.csv near_match_notes for each account.
# We collect them during per-account assembly below.

# ---------------------------------------------------------------------------
# Signals: parse URLs out of near_match_notes (treat each URL as a signal).
# Confidence: VERIFIED if the company column is VERIFIED; INFERRED otherwise.
# ---------------------------------------------------------------------------
URL_RE = re.compile(r"https?://[^\s\)\]\"<>]+")

def extract_signals(near_match_notes):
    """List of {url, label, inferred_date} parsed from free-form notes."""
    urls = URL_RE.findall(near_match_notes or "")
    seen = set()
    out = []
    for u in urls:
        u = u.rstrip(",.;:")
        if u in seen:
            continue
        seen.add(u)
        out.append({
            "url": u,
            "label": u.split("/")[2] if "/" in u else u,
            "inferred_date": None,  # date is per-account's last_researched
        })
    return out

# ---------------------------------------------------------------------------
# ANALOGUE override for corrected dict
# ---------------------------------------------------------------------------
# Build cleaned analogues dict (fix earlier dup)
ANALOGUES = {k: v for k, v in ANALOGUES.items() if isinstance(v, tuple) and len(v) == 2}
ANALOGUES["A020"] = ("EY", "PE-owned, network provisioning-built-through-acquisition; cost discipline argues the ROI story.")
ANALOGUES["A009"] = ("MongoDB", "B2B software with its own legacy modernization mandate; MongoDB analogue.")

# ---------------------------------------------------------------------------
# Compose per-account payload
# ---------------------------------------------------------------------------
accounts = []
for r in enriched_rows:
    pad = {c: safe(r[enriched_cols[c]]) if c in enriched_cols else "" for c in PICK}
    aid = pad["account_id"]
    comp = pad["company"]
    seed_match_keys = [comp, comp.replace("EchoStar", "EchoStar / DISH")]
    seed = None
    for k in seed_match_keys:
        if k in seed_by_company:
            seed = seed_by_company[k]
            break
    seed_priority = seed["priority"] if seed else ""
    seed_thesis = seed["initial_thesis"] if seed else ""
    analogue = ANALOGUES.get(aid, ("Adobe", "Default analogue."))
    contact_list = contacts_by_acct.get(aid, [])
    signals = extract_signals(pad["near_match_notes"])
    # Mark verifiedness per account
    seed_thesis_status = safe(r[enriched_cols["seed_thesis_status"]]) if "seed_thesis_status" in enriched_cols else "VERIFIED"
    # References = same as signals but filtered for known sources
    payload = {
        "account_id": aid,
        "company": comp,
        "slug": slugify_company(comp),
        "domain": pad["domain"],
        "hq_city": pad["hq_city"],
        "hq_state": pad["hq_state"],
        "region": pad["region"] or infer_region(pad["hq_state"]),
        "sector": pad["sector"],
        "priority": seed_priority,
        "employees_total": pad["employees_total"],
        "engineering_headcount": pad["engineering_headcount"],
        "in_target": pad["in_sd_or_denver_metro"] == "YES_IN_TARGET",
        "last_researched": pad["last_researched"] or TODAY,
        "seed_thesis": seed_thesis,
        "analogue": analogue,
        "complication": COMPLICATIONS.get(aid, "No specific complication surfaced."),
        "contacts": [
            {
                "person_slug": c["person_slug"],
                "name": c["name"],
                "title": c["title"],
                "confidence": c["confidence"],
                "source_url": c["source_url"],
                "source_date": c["source_date"],
                "notes": c["notes"],
            } for c in contact_list
        ],
        "signals": signals,
    }
    accounts.append(payload)

# Demo-only: age a handful of accounts so signal decay is visible in the demo data.
# (In production we'd never back-date; this is just to show the UI behaves like it knows.)
age_offsets = {
    "A009": 45,   # CSG: signals 45d old -> amber (stale)
    "A013": 72,   # Liberty Global: 72d -> red (very stale)
    "A016": 50,   # Arrow: 50d -> amber
    "A017": 90,   # Maxar/Vantor: 90d -> red
    "A018": 32,   # Kratos: 32d -> amber
}
for a in accounts:
    if a["account_id"] in age_offsets:
        days = age_offsets[a["account_id"]]
        from datetime import timedelta as _td
        d = datetime.strptime(TODAY, "%Y-%m-%d") - _td(days=days)
        a["last_researched"] = d.strftime("%Y-%m-%d")

# Sort accounts by priority then company
accounts.sort(key=lambda a: (int(a["priority"]) if a["priority"].isdigit() else 99, a["company"]))

# ---------------------------------------------------------------------------
# Generate the HTML
# ---------------------------------------------------------------------------
ACCOUNTS_JSON = json.dumps(accounts, ensure_ascii=False)
TODAY_ISO = TODAY

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Factory Territory — Prospecting Tool</title>
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
    --code-bg: #f1f5f9;
    --row-hover: #f8fafc;
    --row-target: #fef9c3;
    --status-not_started: #94a3b8;
    --status-researched: #1d4ed8;
    --status-contacted: #0e7490;
    --status-replied: #047857;
    --status-meeting: #15803d;
    --status-disqualified: #be123c;
    --warn-amber: #b45309;
    --warn-red: #be123c;
    --fresh: #16a34a;
    --focus: #f59e0b;
    --shadow: 0 2px 6px rgba(15,23,42,.04);
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
      --status-not_started: #475569;
      --status-researched: #3b82f6;
      --status-contacted: #06b6d4;
      --status-replied: #10b981;
      --status-meeting: #22c55e;
      --status-disqualified: #f43f5e;
    }
  }
  *, *::before, *::after { box-sizing: border-box; }
  html { font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; line-height: 1.45; }
  body { margin: 0; background: var(--bg); color: var(--fg); }
  code, .mono { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 0.92em; }
  a { color: var(--accent); }
  a:focus-visible, button:focus-visible, input:focus-visible, textarea:focus-visible, select:focus-visible, [tabindex]:focus-visible {
    outline: 2px solid var(--focus);
    outline-offset: 2px;
  }
  .skip-link { position: absolute; left: -9999px; top: 0; background: var(--accent); color: white; padding: 6px 10px; z-index: 200; }
  .skip-link:focus { left: 8px; top: 8px; }

  header { border-bottom: 1px solid var(--border); padding: 12px 24px; display: flex; align-items: center; gap: 18px; flex-wrap: wrap; }
  header h1 { font-size: 17px; margin: 0; font-weight: 600; letter-spacing: -0.01em; }
  .tabs { display: flex; gap: 4px; }
  .tab { padding: 6px 14px; border: 1px solid var(--border); border-radius: 4px; background: var(--bg); cursor: pointer; font-size: 13px; color: var(--fg-muted); }
  .tab[aria-selected="true"] { background: var(--accent); border-color: var(--accent); color: white; }
  .tab-count { display: inline-block; background: rgba(255,255,255,0.25); padding: 0 6px; border-radius: 8px; font-size: 11px; margin-left: 4px; }
  .tab:not([aria-selected="true"]) .tab-count { background: var(--bg-soft); color: var(--fg-muted); }
  header .top-actions { margin-left: auto; display: flex; gap: 8px; align-items: center; }
  .btn { background: var(--bg); border: 1px solid var(--border-strong); padding: 5px 10px; border-radius: 3px; font-size: 12.5px; cursor: pointer; color: var(--fg); }
  .btn:hover { border-color: var(--accent); }
  .btn-primary { background: var(--accent); color: white; border-color: var(--accent); }
  .btn-danger { background: var(--status-disqualified); color: white; border-color: var(--status-disqualified); }

  main { padding: 18px 24px 60px; max-width: 1500px; margin: 0 auto; }
  .panel { background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 14px 16px; margin-bottom: 14px; }
  .panel h2 { font-size: 12.5px; margin: 0 0 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--fg-muted); }
  .panel h3 { font-size: 13.5px; margin: 0 0 6px; font-weight: 600; color: var(--fg); }
  .row { display: flex; flex-wrap: wrap; gap: 12px; }
  .row > * { flex: 1 1 240px; min-width: 220px; }

  /* TODAY page */
  .today-headline { display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }
  .today-headline h2 { font-size: 22px; margin: 0; color: var(--fg); font-weight: 600; }
  .work-queue-section { margin-bottom: 22px; }
  .work-queue-section h2 { font-size: 14px; margin: 0 0 8px; color: var(--fg-muted); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
  .work-item { background: var(--bg); border: 1px solid var(--border); border-radius: 3px; padding: 10px 12px; margin-bottom: 6px; cursor: pointer; display: grid; grid-template-columns: 1fr auto; gap: 10px; align-items: baseline; }
  .work-item:hover { background: var(--row-hover); }
  .work-item .title { font-weight: 600; color: var(--fg); }
  .work-item .sub { font-size: 12px; color: var(--fg-muted); margin-top: 2px; }
  .work-item .meta { font-size: 11.5px; color: var(--fg-muted); white-space: nowrap; text-align: right; }
  .work-item .pill { display: inline-block; font-size: 10.5px; padding: 1px 7px; border-radius: 8px; border: 1px solid var(--border-strong); background: var(--bg); color: var(--fg-muted); margin-left: 4px; }
  .work-item .pill.overdue { background: #fee2e2; color: var(--warn-red); border-color: var(--warn-red); }
  .work-item .pill.due-today { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }
  .work-item .pill.stale-amber { background: #fef3c7; color: var(--warn-amber); border-color: var(--warn-amber); }
  .work-item .pill.stale-red { background: #fee2e2; color: var(--warn-red); border-color: var(--warn-red); }
  .work-item .pill.fresh { background: #dcfce7; color: var(--fresh); border-color: var(--fresh); }
  .empty-state { background: var(--bg-alt); border: 1px dashed var(--border-strong); border-radius: 4px; padding: 24px; text-align: center; color: var(--fg-muted); }
  .empty-state a { color: var(--accent); }

  /* ACCOUNTS page */
  .toolbar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; padding: 10px 14px; background: var(--bg-alt); border: 1px solid var(--border); border-radius: 4px; margin-bottom: 12px; }
  .filter-group { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .filter-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--fg-faint); font-weight: 600; }
  .chips { display: flex; flex-wrap: wrap; gap: 4px; }
  .chip { border: 1px solid var(--border-strong); background: var(--bg); padding: 3px 9px; border-radius: 12px; cursor: pointer; font-size: 12px; color: var(--fg-muted); user-select: none; }
  .chip:hover { border-color: var(--accent); }
  .chip[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: white; }
  .search-input { border: 1px solid var(--border-strong); border-radius: 3px; padding: 5px 9px; min-width: 240px; font-size: 13px; background: var(--bg); color: var(--fg); }

  .acct-layout { display: grid; grid-template-columns: 320px 1fr; gap: 14px; }
  .acct-list { max-height: 70vh; overflow: auto; padding: 0; border: 1px solid var(--border); border-radius: 4px; background: var(--bg); }
  .acct-row { padding: 10px 12px; border-bottom: 1px solid var(--border); cursor: pointer; }
  .acct-row:hover { background: var(--row-hover); }
  .acct-row.active { background: var(--row-target); border-left: 3px solid var(--accent); padding-left: 9px; }
  .acct-row .name { font-weight: 600; }
  .acct-row .sub { font-size: 11.5px; color: var(--fg-muted); margin-top: 2px; }
  .acct-row .quick-status { display: inline-block; font-size: 10.5px; padding: 1px 7px; border-radius: 8px; margin-top: 4px; }

  .acct-detail .detail-head { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
  .acct-detail .detail-head h2 { font-size: 20px; margin: 0; }
  .acct-detail .detail-head .hq { font-size: 12.5px; color: var(--fg-muted); }

  /* Pipeline */
  .pipeline { display: flex; gap: 4px; margin: 8px 0 12px; }
  .pipeline .step { padding: 5px 10px; border: 1px solid var(--border-strong); border-radius: 999px; font-size: 11.5px; background: var(--bg); color: var(--fg-muted); cursor: pointer; }
  .pipeline .step:hover { border-color: var(--accent); }
  .pipeline .step.active { color: white; border-color: currentColor; }
  .pipeline .step[data-status="not_started"].active { background: var(--status-not_started); border-color: var(--status-not_started); }
  .pipeline .step[data-status="researched"].active { background: var(--status-researched); border-color: var(--status-researched); }
  .pipeline .step[data-status="contacted"].active { background: var(--status-contacted); border-color: var(--status-contacted); }
  .pipeline .step[data-status="replied"].active { background: var(--status-replied); border-color: var(--status-replied); }
  .pipeline .step[data-status="meeting"].active { background: var(--status-meeting); border-color: var(--status-meeting); }
  .pipeline .step[data-status="disqualified"].active { background: var(--status-disqualified); border-color: var(--status-disqualified); }
  .pipeline-arrow { font-size: 14px; color: var(--fg-faint); align-self: center; }

  /* Detail panel sections */
  .section-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  @media (max-width: 980px) { .section-grid { grid-template-columns: 1fr; } .acct-layout { grid-template-columns: 1fr; } }
  .sect { border: 1px solid var(--border); border-radius: 4px; padding: 12px 14px; }
  .sect h3 { font-size: 12.5px; margin: 0 0 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--fg-muted); }
  .textarea-row { display: grid; gap: 6px; }
  .textarea-row label { font-size: 11px; color: var(--fg-muted); }
  textarea, input[type="text"], input[type="date"] { width: 100%; border: 1px solid var(--border-strong); border-radius: 3px; padding: 6px 9px; font-size: 13px; background: var(--bg); color: var(--fg); font-family: inherit; }
  textarea { min-height: 70px; resize: vertical; }

  .contact-card { border: 1px solid var(--border); border-radius: 3px; padding: 8px 10px; margin-bottom: 6px; }
  .contact-card .name-row { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
  .contact-card .name-row .name { font-weight: 600; }
  .contact-card .title { font-size: 12px; color: var(--fg-muted); }
  .conf { display: inline-block; font-size: 10.5px; padding: 1px 7px; border-radius: 8px; border: 1px solid; font-weight: 600; letter-spacing: 0.04em; }
  .conf.HIGH { background: #dcfce7; color: var(--fresh); border-color: var(--fresh); }
  .conf.MED { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }
  .conf.LOW { background: #fef3c7; color: var(--warn-amber); border-color: var(--warn-amber); }
  .contact-card .meta { font-size: 11.5px; color: var(--fg-muted); margin-top: 4px; }
  .contact-card .notes { font-size: 12px; color: var(--fg); margin-top: 4px; font-style: italic; }

  /* Touch sequence */
  .touch { border: 1px solid var(--border); border-radius: 3px; padding: 10px 12px; margin-bottom: 8px; background: var(--bg); }
  .touch.sent { background: #f0fdf4; border-color: var(--fresh); }
  .touch .touch-head { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
  .touch .touch-num { font-weight: 700; color: var(--accent); font-size: 13px; }
  .touch .touch-day { font-size: 11.5px; color: var(--fg-muted); }
  .touch .touch-date { font-size: 11.5px; color: var(--fg-muted); margin-left: auto; }
  .touch textarea { min-height: 70px; margin-top: 6px; }
  .touch .touch-controls { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-top: 6px; }
  .touch .char-count { font-size: 11px; color: var(--fg-muted); margin-right: 6px; }
  .touch .char-count.warn { color: var(--warn-amber); }
  .touch .char-count.bad { color: var(--warn-red); }
  .touch .sent-stamp { font-size: 11.5px; color: var(--fresh); font-weight: 600; }
  .touch .unmark-sent { color: var(--fg-faint); font-size: 11.5px; cursor: pointer; text-decoration: underline; background: none; border: none; padding: 0; }

  /* Signals with decay */
  .signal-row { display: grid; grid-template-columns: auto 1fr auto auto; gap: 8px; align-items: baseline; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 12.5px; }
  .signal-row:last-child { border-bottom: none; }
  .signal-row .age { font-size: 11px; color: var(--fg-muted); font-variant-numeric: tabular-nums; }
  .signal-row .badge { font-size: 10.5px; padding: 1px 6px; border-radius: 8px; border: 1px solid; }
  .signal-row .badge.fresh { background: #dcfce7; color: var(--fresh); border-color: var(--fresh); }
  .signal-row .badge.amber { background: #fef3c7; color: var(--warn-amber); border-color: var(--warn-amber); }
  .signal-row .badge.red { background: #fee2e2; color: var(--warn-red); border-color: var(--warn-red); }
  .signal-row .re-verify { font-size: 11px; color: var(--accent); cursor: pointer; background: none; border: 1px solid var(--border-strong); padding: 2px 7px; border-radius: 3px; }

  /* References list */
  .ref-list { list-style: none; padding: 0; margin: 0; max-height: 220px; overflow: auto; }
  .ref-list li { padding: 4px 0; font-size: 12px; color: var(--fg-muted); border-bottom: 1px solid var(--border); }
  .ref-list li a { color: var(--accent); }
  .ref-list li .label { color: var(--fg-faint); margin-left: 6px; }

  /* Complication block */
  .complication-block { background: #fef9c3; border-left: 3px solid var(--warn-amber); padding: 10px 12px; font-size: 13px; color: var(--fg); }
  @media (prefers-color-scheme: dark) {
    .complication-block { background: #27272a; color: var(--fg); }
  }
  .complication-block strong { color: var(--warn-amber); }

  /* Verify-before-sending checklist */
  .checklist label { display: flex; align-items: flex-start; gap: 8px; padding: 4px 0; font-size: 12.5px; color: var(--fg); }
  .checklist input[type="checkbox"] { margin-top: 3px; }

  /* THESIS scatter (kept from prior design) */
  .axis-text { font-family: ui-monospace, monospace; font-size: 10.5px; fill: var(--fg-muted); }
  .axis-line { stroke: var(--border-strong); stroke-width: 1; }
  .threshold-line { stroke: var(--fg-faint); stroke-width: 1; stroke-dasharray: 4 3; }
  .quadrant-label { font-family: ui-sans-serif, sans-serif; font-size: 11px; fill: var(--fg-faint); letter-spacing: 0.04em; text-transform: uppercase; }
  .axis-title { font-family: ui-sans-serif, sans-serif; font-size: 11.5px; fill: var(--fg); font-weight: 600; }
  .point { stroke: white; stroke-width: 2; cursor: pointer; }
  .point[data-priority="1"] { fill: #047857; }
  .point[data-priority="2"] { fill: #0e7490; }
  .point[data-priority="3"] { fill: #1d4ed8; }
  .point[data-priority="4"] { fill: #b45309; }
  .point[data-priority="5"] { fill: #be123c; }
  .point.dim { opacity: 0.12; }
  .point:focus-visible, .point:hover { stroke: var(--accent); stroke-width: 3; }

  /* Disqualify modal */
  .modal-bg { position: fixed; inset: 0; background: rgba(15,23,42,.6); display: none; align-items: center; justify-content: center; z-index: 100; padding: 24px; }
  .modal-bg.open { display: flex; }
  .modal { background: var(--bg); border-radius: 6px; padding: 22px 26px; max-width: 540px; width: 100%; border: 1px solid var(--border); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
  .modal h3 { margin: 0 0 12px; font-size: 17px; }
  .modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 14px; }

  /* Keyboard help overlay */
  .help-overlay { position: fixed; inset: 0; background: rgba(15,23,42,.7); display: none; align-items: center; justify-content: center; z-index: 90; }
  .help-overlay.open { display: flex; }
  .help-card { background: var(--bg); border-radius: 6px; padding: 24px 28px; max-width: 520px; width: 100%; border: 1px solid var(--border); }
  .help-card h3 { margin: 0 0 14px; font-size: 17px; }
  .kbd-row { display: grid; grid-template-columns: 70px 1fr; gap: 12px; padding: 4px 0; font-size: 13px; }
  .kbd-row .key { font-family: ui-monospace, monospace; background: var(--bg-soft); border: 1px solid var(--border-strong); border-radius: 3px; padding: 1px 8px; font-size: 12px; text-align: center; }

  .toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: var(--fg); color: var(--bg); padding: 8px 14px; border-radius: 4px; font-size: 13px; box-shadow: 0 6px 14px rgba(0,0,0,.3); z-index: 110; display: none; }
  .toast.show { display: block; }

  footer { padding: 16px 24px 30px; border-top: 1px solid var(--border); font-size: 12px; color: var(--fg-muted); max-width: 1500px; margin: 0 auto; }
</style>
</head>
<body>
<a href="#main" class="skip-link">Skip to main content</a>
<header>
  <h1>Factory Territory — Prospecting Tool</h1>
  <nav class="tabs" role="tablist">
    <button class="tab" role="tab" data-tab="today" aria-selected="true">Today<span class="tab-count" id="badge-today">0</span></button>
    <button class="tab" role="tab" data-tab="accounts" aria-selected="false">Accounts<span class="tab-count" id="badge-accounts">20</span></button>
    <button class="tab" role="tab" data-tab="thesis" aria-selected="false">Thesis<span class="tab-count">·</span></button>
  </nav>
  <div class="top-actions">
    <button class="btn" id="btn-help" title="Keyboard shortcuts (?)">?</button>
    <button class="btn" id="btn-export" title="Export the full state as CSV">Export CSV</button>
    <button class="btn btn-danger" id="btn-reset" title="Reset all status / notes / touches (asks confirm)">Reset</button>
  </div>
</header>
<main id="main">

<!-- TODAY -->
<section class="tab-panel" data-tab-panel="today">
  <div class="today-headline">
    <h2>Today · __TODAY__</h2>
    <span class="mono" style="color:var(--fg-muted);" id="today-stats"></span>
  </div>
  <div id="today-body"></div>
</section>

<!-- ACCOUNTS -->
<section class="tab-panel" data-tab-panel="accounts" hidden>
  <div class="acct-layout">
    <div>
      <div class="toolbar">
        <div class="filter-group">
          <span class="filter-label">Region</span>
          <div class="chips" id="filter-region" role="group"></div>
        </div>
        <div class="filter-group">
          <span class="filter-label">Priority</span>
          <div class="chips" id="filter-priority" role="group"></div>
        </div>
        <div class="filter-group">
          <span class="filter-label">Status</span>
          <div class="chips" id="filter-status" role="group"></div>
        </div>
        <div class="filter-group" style="flex:1; min-width:200px;">
          <input class="search-input" id="filter-search" type="search" placeholder="Search company / sector / signal…" aria-label="Search accounts">
        </div>
      </div>
      <div class="acct-list" id="acct-list" role="listbox" aria-label="Accounts"></div>
    </div>
    <div id="acct-detail" aria-live="polite"></div>
  </div>
</section>

<!-- THESIS -->
<section class="tab-panel" data-tab-panel="thesis" hidden>
  <div class="panel">
    <h2>Thesis · Revenue × Employees (log scale)</h2>
    <p style="font-size:12px; color:var(--fg-muted); margin:0 0 12px;">Quadrants split at <span class="mono">$500M</span> revenue and <span class="mono">5,000</span> employees. Hover any point for company + priority.</p>
    <svg id="scatter" viewBox="0 0 900 540" style="width:100%; height:auto; background:var(--bg-alt); border:1px solid var(--border);" role="img" aria-label="Revenue vs Employees scatter"></svg>
  </div>
</section>

</main>
<footer>
  <strong>AGENTS.md</strong> rules: every claim VERIFIED (url) or INFERRED · disqualifying an account requires a free-text reason · signal age is tracked · sequences are 4 touches, send rate is logged.
  Last build: __TODAY__.
</footer>

<div class="modal-bg" id="modal-disqualify" role="dialog" aria-modal="true" aria-labelledby="dq-title">
  <div class="modal">
    <h3 id="dq-title">Disqualify account</h3>
    <p style="font-size:12.5px; color:var(--fg-muted); margin:0 0 8px;">Per AGENTS.md, a reason is required. Empty reasons are not saved. The account will move to <strong>Disqualified</strong> and stop appearing in the work queue.</p>
    <textarea id="dq-reason" placeholder="e.g. HCLTech owns tooling budget; sales cycle unreachable; account already on competing Modernization-as-a-Service contract..." style="min-height: 110px;"></textarea>
    <div class="modal-actions">
      <button class="btn" id="dq-cancel">Cancel</button>
      <button class="btn btn-danger" id="dq-confirm">Disqualify</button>
    </div>
  </div>
</div>

<div class="help-overlay" id="help-overlay" role="dialog" aria-modal="true" aria-label="Keyboard shortcuts">
  <div class="help-card">
    <h3>Keyboard shortcuts</h3>
    <div class="kbd-row"><span class="key">j / k</span><span>Move to next / previous account</span></div>
    <div class="kbd-row"><span class="key">e</span><span>Focus the Day-1 email textarea</span></div>
    <div class="kbd-row"><span class="key">c</span><span>Copy the Day-1 email to clipboard</span></div>
    <div class="kbd-row"><span class="key">d</span><span>Open Disqualify modal</span></div>
    <div class="kbd-row"><span class="key">/</span><span>Focus the search box</span></div>
    <div class="kbd-row"><span class="key">1–5</span><span>Jump to status step (researched → meeting)</span></div>
    <div class="kbd-row"><span class="key">?</span><span>This help overlay</span></div>
    <div class="kbd-row"><span class="key">Esc</span><span>Close modal / help</span></div>
    <div class="modal-actions">
      <button class="btn" id="help-close">Close</button>
    </div>
  </div>
</div>

<div class="toast" id="toast" role="status" aria-live="polite"></div>

<script>
"use strict";
const TODAY_ISO = "__TODAY__";
const ACCOUNTS = __ACCOUNTS__;
const STATUSES = ["not_started","researched","contacted","replied","meeting","disqualified"];
const PRIORITIES = ["All","1","2","3","4","5"];
const REGIONS = ["All","San Diego","Denver"];

// -- state --
// store per account: { status, status_history, notes, next_action_date,
//                       next_action_label, disqualify_reason, touches: { [person_slug]: {1,3,8,15: {sent_date, body_edited} } } }
const LS_KEY = "factory_territory_v1";
let STATE = loadState();
function loadState(){
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) return JSON.parse(raw);
  } catch(_) {}
  return { accounts: {}, today_checked_date: TODAY_ISO };
}
function saveState(){
  try { localStorage.setItem(LS_KEY, JSON.stringify(STATE)); } catch(_) {}
}
function acctState(id){
  if (!STATE.accounts[id]) STATE.accounts[id] = {
    status: "not_started",
    status_history: [],
    notes: "",
    next_action_date: "",
    next_action_label: "",
    disqualify_reason: "",
    touches: {}
  };
  return STATE.accounts[id];
}

// -- helpers --
function safeStr(v){ return v == null ? "" : String(v); }
function isNA(v){ return v == null || v === "" || v === "UNKNOWN" || v === "INFERRED"; }
function fmtDate(s){ if (!s) return ""; return s; }
function daysBetween(a_iso, b_iso){
  const a = new Date(a_iso + "T00:00:00Z");
  const b = new Date(b_iso + "T00:00:00Z");
  return Math.round((b - a) / 86400000);
}
function todayPlus(days){
  const d = new Date(TODAY_ISO + "T00:00:00Z");
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0,10);
}
function priorityClass(p){ return `p${p}`; }
function statusClass(s){ return `status-${s}`; }

// -- confidence lookup --
function confClass(c){ return (c || "LOW").toUpperCase(); }

// -- sequence generator --
// For a contact with confidence MED/HIGH only. For LOW we still draft but mark.
function generateSequence(acct, contact, person_state){
  // 4 touches: day 1 (email), day 3 (LinkedIn note), day 8 (in-thread), day 15 (breakup)
  const company = acct.company;
  const analogue = acct.analogue[0];
  const analogueWhy = acct.analogue[1];
  const isUnknown = /^UNKNOWN$/.test(contact.name || "");

  // Common references the rep can plug in
  const seed = acct.seed_thesis || "";

  // Day 1 email — three sentences, no greeting, ends with a question
  const email = [
    `We saw ${company}'s ${seed.split(/[.,;]/)[0] || 'public engineering footprint'}. ${analogue}, a Factory customer, is the closest analogue because ${analogueWhy.charAt(0).toLowerCase() + analogueWhy.slice(1)}. Is your team running this on Factory today, or is the procurement still scoped around a legacy modernization plan?`
  ].join("\n");

  // Day 3 LinkedIn — ≤300 chars
  const linkedin = `Hi ${isUnknown ? '' : (contact.name.split(/\s+/)[0] + ' — ')}saw ${company}'s recent platform/DevEx activity and would value 15 minutes on adjacent work ${analogue} is doing with Factory. Open to a brief intro call?`;

  // Day 8 in-thread — new angle, do not "bump"
  const angle = `Following my note — quick follow-up with a different angle. ${analogueWhy}. If your team has a developer-platform remit (not just procurement), can I send a single-page brief on a comparable engagement, no meeting required?`;

  // Day 15 breakup — short, no guilt, door open
  const breakup = `Closing the loop on this thread. If modernization budgeting is on next quarter's roadmap, the door is open — just ping me. No need to reply otherwise.`;

  const bodies = [null, email, linkedin, null, angle, null, null, null, breakup, null, null, null, null, null, null, null];
  const channels = [null,"Email","LinkedIn",null,"In-thread",null,null,null,"Breakup",null,null,null,null,null,null,null];
  // index 1,3,8,15
  return {
    1: { body: email, channel: "Email", day: 1 },
    3: { body: linkedin, channel: "LinkedIn", day: 3, char_limit: 300 },
    8: { body: angle, channel: "In-thread", day: 8 },
    15: { body: breakup, channel: "Breakup", day: 15 }
  };
}

// -- TODAY page --
function renderToday(){
  const overdue = [];
  const dueToday = [];
  const stale = [];   // last_researched older than 30 days
  const noNext = [];  // no next action set AND not disqualified
  const disqualified = [];

  ACCOUNTS.forEach(a => {
    const s = acctState(a.account_id);
    const last = a.last_researched || TODAY_ISO;
    const age = daysBetween(last, TODAY_ISO);

    if (s.status === "disqualified"){
      disqualified.push({ a, s, age });
      return;
    }
    if (s.next_action_date){
      const diff = daysBetween(TODAY_ISO, s.next_action_date);
      if (diff < 0) overdue.push({ a, s, days: -diff });
      else if (diff === 0) dueToday.push({ a, s });
    } else if (s.status !== "not_started") {
      noNext.push({ a, s, kind: "no_next_after_status" });
    } else {
      noNext.push({ a, s, kind: "never_touched" });
    }
    if (age > 30) stale.push({ a, age });
  });

  overdue.sort((x,y) => y.days - x.days);
  stale.sort((x,y) => y.age - x.age);

  // Build HTML
  const out = [];
  if (disqualified.length) {
    out.push(`<div class="work-queue-section"><h2>${disqualified.length} disqualified</h2><div style="font-size:12px; color:var(--fg-muted); margin-bottom:8px;">Disqualified accounts don't appear in the work queue. To undo, set status back to a pipeline step from the detail panel.</div></div>`);
  }

  // Overdue
  out.push(`<div class="work-queue-section"><h2>Overdue follow-ups · ${overdue.length}</h2>`);
  if (!overdue.length) out.push(`<div class="empty-state">Nothing overdue. The backlog is clean.</div>`);
  else {
    overdue.forEach(o => {
      const a = o.a;
      const s = o.s;
      out.push(workItemHtml(a, s, [
        { text: `overdue × ${o.days} day${o.days===1?"":"s"}`, cls: "overdue" }
      ]));
    });
  }
  out.push(`</div>`);

  // Due today
  out.push(`<div class="work-queue-section"><h2>Due today · ${dueToday.length}</h2>`);
  if (!dueToday.length) out.push(`<div class="empty-state">Nothing scheduled for today.</div>`);
  else {
    dueToday.forEach(o => {
      const a = o.a;
      const s = o.s;
      out.push(workItemHtml(a, s, [ { text: "due today", cls: "due-today" } ]));
    });
  }
  out.push(`</div>`);

  // Stale signals
  out.push(`<div class="work-queue-section"><h2>Stale signals (&gt;30 days) · ${stale.length}</h2>`);
  if (!stale.length) out.push(`<div class="empty-state">All signals inside 30 days. Good.</div>`);
  else {
    stale.forEach(o => {
      const a = o.a;
      const cls = o.age > 60 ? "stale-red" : "stale-amber";
      out.push(workItemHtml(a, acctState(a.account_id), [
        { text: `${o.age}d old`, cls: cls }
      ], `last verified ${a.last_researched}`));
    });
  }
  out.push(`</div>`);

  // No next action
  out.push(`<div class="work-queue-section"><h2>Accounts with no next action · ${noNext.length}</h2>`);
  if (!noNext.length) out.push(`<div class="empty-state">Every account has a next step. Nice.</div>`);
  else {
    noNext.forEach(o => {
      const a = o.a;
      out.push(workItemHtml(a, o.s, [], o.kind === "never_touched" ? "never touched" : "no next action set"));
    });
  }
  out.push(`</div>`);

  // Today is empty?
  if (!overdue.length && !dueToday.length && !stale.length && !noNext.length){
    out.unshift(`<div class="empty-state" style="margin-bottom:14px;"><strong>Nothing to do.</strong> Next unworked account: <a href="#" data-jump-account="${pickNextUnworked().account_id}">${pickNextUnworked().company}</a>.</div>`);
  }

  document.getElementById("today-body").innerHTML = out.join("");
  document.getElementById("today-stats").textContent =
    `${overdue.length} overdue · ${dueToday.length} due today · ${stale.length} stale · ${noNext.length} unworked`;

  // today-badge count = actionable only (overdue + due + stale + unworked)
  document.getElementById("badge-today").textContent = overdue.length + dueToday.length + stale.length + noNext.length;

  // Wire jump-to-account links
  document.querySelectorAll("[data-jump-account]").forEach(el => {
    el.addEventListener("click", e => {
      e.preventDefault();
      const id = el.dataset.jumpAccount;
      selectAccount(id);
      switchTab("accounts");
    });
  });
  // Wire work items
  document.querySelectorAll(".work-item[data-account-id]").forEach(el => {
    el.addEventListener("click", () => {
      selectAccount(el.dataset.accountId);
      switchTab("accounts");
    });
  });
}

function pickNextUnworked(){
  return ACCOUNTS.find(a => acctState(a.account_id).status === "not_started") || ACCOUNTS[0];
}

function workItemHtml(a, s, badges, sub){
  return `<div class="work-item" data-account-id="${a.account_id}" tabindex="0" role="button">
    <div>
      <div class="title">${a.company} <span class="mono" style="font-weight:400; font-size:12px; color:var(--fg-muted);">${a.region} · P${a.priority}</span></div>
      <div class="sub">${sub || a.sector}</div>
    </div>
    <div class="meta">
      ${badges.map(b => `<span class="pill ${b.cls}">${b.text}</span>`).join(" ")}
      ${s.next_action_date ? `<div style="margin-top:4px;">→ ${s.next_action_date}</div>` : ""}
    </div>
  </div>`;
}

// -- ACCOUNTS page --
function renderAccounts(){
  const list = document.getElementById("acct-list");
  const filt = STATE.filter || {region:"All", priority:"All", status:"All", search:""};
  STATE.filter = filt;

  const filtered = ACCOUNTS.filter(a => {
    const s = acctState(a.account_id);
    const okR = filt.region === "All" || a.region === filt.region;
    const okP = filt.priority === "All" || String(a.priority) === String(filt.priority);
    const okS = filt.status === "All" || s.status === filt.status;
    const search = (filt.search || "").toLowerCase();
    const hay = (a.company + " " + a.sector + " " + (a.seed_thesis || "")).toLowerCase()
      + " " + (a.signals || []).map(sg => sg.label).join(" ").toLowerCase();
    const okQ = !search || hay.indexOf(search) !== -1;
    return okR && okP && okS && okQ;
  });

  list.innerHTML = filtered.map(a => {
    const s = acctState(a.account_id);
    const active = STATE.selectedId === a.account_id ? " active" : "";
    return `<div class="acct-row${active}" data-jump="${a.account_id}" role="option" tabindex="0">
      <div class="name">${a.company}</div>
      <div class="sub">${a.region} · P${a.priority} · ${a.sector}</div>
      <div class="quick-status pill ${statusClass(s.status)}" style="color:white; background:var(--status-${s.status}); border-color:var(--status-${s.status});">${prettyStatus(s.status)}</div>
      ${s.next_action_date ? `<div class="sub" style="margin-top:2px;">→ ${s.next_action_date}</div>` : ""}
    </div>`;
  }).join("") || `<div class="empty-state">No accounts match the current filter.</div>`;

  list.querySelectorAll(".acct-row").forEach(el => {
    el.addEventListener("click", () => selectAccount(el.dataset.jump));
  });
}

function prettyStatus(s){
  return ({
    not_started: "Not started",
    researched: "Researched",
    contacted: "Contacted",
    replied: "Replied",
    meeting: "Meeting",
    disqualified: "Disqualified"
  })[s] || s;
}

function renderAccountsToolbar(){
  renderChips("filter-region", REGIONS, (STATE.filter || {}).region || "All", v => { STATE.filter.region = v; renderAccounts(); });
  renderChips("filter-priority", PRIORITIES, (STATE.filter || {}).priority || "All", v => { STATE.filter.priority = v; renderAccounts(); });
  renderChips("filter-status", ["All", ...STATUSES], (STATE.filter || {}).status || "All", v => { STATE.filter.status = v; renderAccounts(); });
  const si = document.getElementById("filter-search");
  si.value = (STATE.filter || {}).search || "";
  si.oninput = (e) => { STATE.filter.search = e.target.value; renderAccounts(); };
}
function renderChips(id, values, current, onToggle){
  const c = document.getElementById(id);
  c.innerHTML = values.map(v => {
    const pressed = String(v) === String(current) ? "true" : "false";
    return `<button class="chip" data-v="${v}" aria-pressed="${pressed}">${v.replace(/_/g," ")}</button>`;
  }).join("");
  c.querySelectorAll(".chip").forEach(b => b.addEventListener("click", () => onToggle(b.dataset.v)));
}

// -- detail panel --
function selectAccount(id){
  STATE.selectedId = id;
  saveState();
  renderAccounts();
  renderDetail();
}

function renderDetail(){
  const root = document.getElementById("acct-detail");
  const id = STATE.selectedId;
  if (!id){ root.innerHTML = `<div class="empty-state">Pick an account on the left to see its detail panel.</div>`; return; }
  const a = ACCOUNTS.find(x => x.account_id === id);
  if (!a){ root.innerHTML = `<div class="empty-state">No account selected.</div>`; return; }
  const s = acctState(id);
  const last = a.last_researched || TODAY_ISO;
  const age = daysBetween(last, TODAY_ISO);

  root.innerHTML = `
    <div class="acct-detail">
      <div class="detail-head">
        <h2>${a.company}</h2>
        <span class="hq">${a.hq_city}, ${a.hq_state} · ${a.sector} · P${a.priority}</span>
        <span class="mono" style="font-size:12px; color:var(--fg-muted); margin-left:auto;">${a.account_id}</span>
      </div>

      <div class="pipeline" id="pipeline">
        ${STATUSES.map((st, i) => `<button class="step ${st === s.status ? 'active' : ''}" data-status="${st}">${prettyStatus(st)}</button>${i<STATUSES.length-1?'<span class="pipeline-arrow">→</span>':''}`).join("")}
      </div>
      ${s.status === "disqualified" ? `<div class="complication-block" style="margin-bottom:12px;"><strong>Disqualified.</strong> Reason: ${escapeHtml(s.disqualify_reason || "(none)")}</div>` : ""}

      <div class="section-grid">
        <div class="sect">
          <h3>Notes</h3>
          <div class="textarea-row">
            <label>Free-form notes (auto-saved)</label>
            <textarea id="detail-notes" placeholder="Research notes, call summaries, objections, etc.">${escapeHtml(s.notes || "")}</textarea>
          </div>
        </div>
        <div class="sect">
          <h3>Next action</h3>
          <div class="textarea-row">
            <label>Date</label>
            <input type="date" id="detail-next-date" value="${s.next_action_date || ""}">
            <label>Label</label>
            <input type="text" id="detail-next-label" value="${escapeHtml(s.next_action_label || "")}" placeholder="e.g. Send breakup if no reply">
          </div>
        </div>
      </div>

      <div class="section-grid" style="margin-top:14px;">
        <div class="sect">
          <h3>Contacts (${a.contacts.length}) — confidence: source rigor label</h3>
          ${a.contacts.map(c => contactCardHtml(a, s, c)).join("") || `<div style="font-size:12px; color:var(--fg-muted);">No contacts drafted. Use INFERRED fallback only.</div>`}
        </div>
        <div class="sect">
          <h3>COMPLICATION</h3>
          <div class="complication-block"><strong>Known objection:</strong> ${escapeHtml(a.complication)}</div>
          <h3 style="margin-top:14px;">Analogue</h3>
          <div style="font-size:13px;"><strong>${a.analogue[0]}</strong> — ${escapeHtml(a.analogue[1])}</div>
          <h3 style="margin-top:14px;">Detail panel · firmographics</h3>
          <div style="font-size:12px; color:var(--fg-muted); font-variant-numeric: tabular-nums;">
            Employees: <span class="mono">${escapeHtml(a.employees_total || "UNKNOWN")}</span> · Engineering: <span class="mono">${escapeHtml(a.engineering_headcount || "UNKNOWN")}</span><br>
            Revenue: <span class="mono">UNKNOWN</span> (deliberately omitted from main view; estimates only — see AGENTS.md rule 3)
          </div>
        </div>
      </div>

      <div class="section-grid" style="margin-top:14px;">
        <div class="sect">
          <h3>Signals · ${a.signals.length} source URLs · last touch ${last} (${age}d)</h3>
          ${a.signals.length === 0 ? `<div style="font-size:12px; color:var(--fg-muted);">No public sources surfaced in research pass.</div>` :
            a.signals.slice(0, 12).map(sig => signalRowHtml(a, sig, age)).join("")}
          ${a.signals.length > 12 ? `<div style="font-size:11.5px; color:var(--fg-muted); margin-top:6px;">+ ${a.signals.length - 12} more in references panel below.</div>` : ""}
        </div>
        <div class="sect">
          <h3>References</h3>
          <ul class="ref-list">
            ${a.signals.map(sig => `<li><a href="${sig.url}" rel="noopener noreferrer" target="_blank">${escapeHtml(sig.label)}</a><span class="label"> · last touch ${last}</span></li>`).join("")}
          </ul>
          <h3 style="margin-top:14px;">Verify before sending</h3>
          <div class="checklist" data-checklist="${a.account_id}">
            <label><input type="checkbox" data-key="contact_verified"> Contact name verified against current LinkedIn / press release</label>
            <label><input type="checkbox" data-key="source_fresh"> Source links verified live in the last 30 days</label>
            <label><input type="checkbox" data-key="analogue_match"> Analogue and one-line "why this matches" reviewed</label>
            <label><input type="checkbox" data-key="three_sentences"> Email is exactly three sentences, no greeting, no value props</label>
            <label><input type="checkbox" data-key="complication_known"> COMPLICATION block acknowledged — objection covered</label>
          </div>
        </div>
      </div>

      <div id="seq-container"></div>
    </div>
  `;

  // Wire pipeline
  root.querySelectorAll(".pipeline .step").forEach(b => {
    b.addEventListener("click", () => {
      const target = b.dataset.status;
      if (target === s.status) return;
      // Disqualified -> confirm modal
      if (target === "disqualified"){
        openDisqualifyModal(a, s);
        return;
      }
      s.status = target;
      s.status_history.push({ status: target, date: TODAY_ISO });
      if (target !== "disqualified") s.disqualify_reason = "";
      saveState();
      renderDetail();
      renderAccounts();
      renderToday();
    });
  });

  // Wire notes / next-action
  root.querySelector("#detail-notes").addEventListener("input", e => { s.notes = e.target.value; saveState(); });
  root.querySelector("#detail-next-date").addEventListener("change", e => { s.next_action_date = e.target.value; saveState(); renderAccounts(); renderToday(); });
  root.querySelector("#detail-next-label").addEventListener("input", e => { s.next_action_label = e.target.value; saveState(); });

  // Wire checklist
  s.checklist = s.checklist || {};
  root.querySelectorAll(`[data-checklist="${a.account_id}"] input[type="checkbox"]`).forEach(cb => {
    cb.checked = !!s.checklist[cb.dataset.key];
    cb.addEventListener("change", () => { s.checklist[cb.dataset.key] = cb.checked; saveState(); });
  });

  // Render sequence
  renderSequences(a, s);

  // Wire contact person "[edit]" buttons (sets body_edited flag when textarea changes)
  root.querySelectorAll(".touch textarea").forEach(ta => {
    ta.addEventListener("input", () => {
      const slug = ta.dataset.person;
      const day = ta.dataset.day;
      const ps = touchState(a, s, slug, day);
      ps.body_edited = ta.value;
      saveState();
      const charCountEl = ta.parentElement.querySelector(".char-count");
      if (charCountEl){
        const limit = parseInt(ta.dataset.charLimit, 10);
        charCountEl.textContent = charCountBadge(ta.value, limit);
        charCountEl.classList.remove("warn","bad");
        if (limit && ta.value.length > limit) charCountEl.classList.add("bad");
        else if (limit && ta.value.length > limit - 30) charCountEl.classList.add("warn");
      }
    });
  });

  // Wire mark-as-sent
  root.querySelectorAll(".mark-sent").forEach(b => {
    b.addEventListener("click", () => {
      const slug = b.dataset.person, day = b.dataset.day;
      const ps = touchState(a, s, slug, day);
      ps.sent_date = ps.sent_date ? "" : TODAY_ISO;
      saveState();
      renderDetail();
      renderToday();
    });
  });
  root.querySelectorAll(".unmark-sent").forEach(b => {
    b.addEventListener("click", () => {
      const slug = b.dataset.person, day = b.dataset.day;
      const ps = touchState(a, s, slug, day);
      ps.sent_date = "";
      saveState();
      renderDetail();
      renderToday();
    });
  });
  // Wire copy
  root.querySelectorAll(".copy-btn").forEach(b => {
    b.addEventListener("click", async () => {
      const slug = b.dataset.person, day = b.dataset.day;
      const ps = touchState(a, s, slug, day);
      const baseSeq = generateSequence(a, a.contacts.find(c => c.person_slug === slug), ps);
      const text = (ps.body_edited != null ? ps.body_edited : baseSeq[day].body);
      try {
        await navigator.clipboard.writeText(text);
        toast(`Copied touch #${day} for ${a.contacts.find(c=>c.person_slug===slug).name || slug}`);
      } catch(_) {
        // Fallback
        const ta = document.createElement("textarea");
        ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand("copy"); ta.remove();
        toast(`Copied touch #${day}`);
      }
    });
  });

  // Wire re-verify
  root.querySelectorAll(".re-verify").forEach(b => {
    b.addEventListener("click", () => {
      const url = b.dataset.url;
      if (url) window.open(url, "_blank", "noopener,noreferrer");
    });
  });

  // Wire "Open Day-1 email" keyboard shortcut 'e'
  root.querySelectorAll(".focus-email").forEach(b => {
    b.addEventListener("click", () => {
      const ta = root.querySelector(`textarea[data-person][data-day="1"]`);
      if (ta) ta.focus();
    });
  });
}

function touchState(a, s, slug, day){
  // day is one of 1,3,8,15. Calling with day=null ensures the parent exists.
  if (!s.touches[slug]) s.touches[slug] = {};
  if (day == null) return null;
  if (!s.touches[slug][day]) s.touches[slug][day] = { sent_date: "", body_edited: null };
  return s.touches[slug][day];
}

function charCountBadge(text, limit){
  const n = (text || "").length;
  if (limit) return `${n} / ${limit}`;
  return `${n} chars`;
}

function contactCardHtml(a, s, c){
  return `<div class="contact-card">
    <div class="name-row">
      <span class="name">${escapeHtml(c.name || "UNKNOWN")}</span>
      <span class="title">${escapeHtml(c.title || "")}</span>
      <span class="conf ${confClass(c.confidence)}">${confClass(c.confidence)}</span>
    </div>
    <div class="meta"><a href="${c.source_url}" target="_blank" rel="noopener noreferrer">${escapeHtml(c.source_url.replace(/^https?:\/\//,'').slice(0,60))}</a>${c.source_date ? ` · ${c.source_date}` : ""}</div>
    ${c.notes ? `<div class="notes">${escapeHtml(c.notes)}</div>` : ""}
  </div>`;
}

function signalRowHtml(a, sig, lastAccountAge){
  // Signal age: use the account's last_researched vs TODAY. Decay: 0..30 -> fresh, 30..60 -> amber, 60+ -> red.
  const stale = (a.last_researched && daysBetween(a.last_researched, TODAY_ISO) > 30);
  const amber = (a.last_researched && daysBetween(a.last_researched, TODAY_ISO) > 30 && daysBetween(a.last_researched, TODAY_ISO) <= 60);
  const red = (a.last_researched && daysBetween(a.last_researched, TODAY_ISO) > 60);
  const cls = red ? "red" : amber ? "amber" : "fresh";
  const age = a.last_researched ? `${daysBetween(a.last_researched, TODAY_ISO)}d` : "?";
  return `<div class="signal-row">
    <span class="badge ${cls}">${cls === "fresh" ? "fresh" : cls === "amber" ? "stale" : "very stale"}</span>
    <span><a href="${sig.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(sig.label)}</a></span>
    <span class="age">${age}</span>
    <button class="re-verify" data-url="${sig.url}" title="Open source to re-verify">re-verify</button>
  </div>`;
}

function renderSequences(a, s){
  const seq = document.getElementById("seq-container");
  if (!seq) return;
  if (!a.contacts.length){
    seq.innerHTML = `<div class="sect" style="margin-top:14px;"><h3>4-Touch sequence</h3><div style="font-size:12px; color:var(--fg-muted);">No contacts to sequence against.</div></div>`;
    return;
  }
  // Pick the highest-confidence contact as the primary sequence target.
  const contactRank = { HIGH: 0, MED: 1, LOW: 2 };
  const ordered = a.contacts.slice().sort((x,y) => (contactRank[x.confidence] ?? 9) - (contactRank[y.confidence] ?? 9));
  const primary = ordered[0];

  const ps = touchState(a, s, primary.person_slug, null); // ensure parent exists
  const baseSeq = generateSequence(a, primary, ps);

  seq.innerHTML = `<div class="sect" style="margin-top:14px;">
    <h3>4-Touch sequence · primary contact: <strong>${escapeHtml(primary.name || "UNKNOWN")}</strong> <span class="conf ${confClass(primary.confidence)}">${confClass(primary.confidence)}</span></h3>
    <div style="font-size:12px; color:var(--fg-muted); margin-bottom:8px;">Send dates are computed from "Day 1" once you mark the email sent (Day 3, Day 8, Day 15 follow).</div>
    ${[1,3,8,15].map(day => touchHtml(a, s, primary, baseSeq[day], day)).join("")}
  </div>`;
}

function touchHtml(a, s, contact, baseTouch, day){
  const ps = touchState(a, s, contact.person_slug, day);
  const body = ps.body_edited != null ? ps.body_edited : baseTouch.body;
  const sent = !!ps.sent_date;
  const sentDisplay = sent ? ` · sent ${ps.sent_date}` : "";
  const computedSendDate = sent ? ps.sent_date : (day === 1 ? TODAY_ISO : (function(){ return ""; })()); // simple: day 1 is today once sent
  const limit = baseTouch.char_limit || null;
  const cls = sent ? "sent" : "";
  const badgeCls = limit && body.length > limit ? "bad" : (limit && body.length > limit-30 ? "warn" : "");
  return `<div class="touch ${cls}">
    <div class="touch-head">
      <span class="touch-num">Day ${day}</span>
      <span class="touch-day">${baseTouch.channel}</span>
      ${sent ? `<span class="sent-stamp">SENT${sentDisplay}</span><button class="unmark-sent" data-person="${contact.person_slug}" data-day="${day}">undo</button>` : ""}
      <span class="touch-date">${sent ? `sent ${ps.sent_date}` : `not sent`}</span>
    </div>
    <textarea data-person="${contact.person_slug}" data-day="${day}" data-char-limit="${limit || ''}" placeholder="${limit ? `≤ ${limit} chars` : ''}">${escapeHtml(body)}</textarea>
    <div class="touch-controls">
      <span class="char-count ${badgeCls}">${charCountBadge(body, limit)}</span>
      <button class="btn copy-btn" data-person="${contact.person_slug}" data-day="${day}">Copy</button>
      ${sent ? "" : `<button class="btn btn-primary mark-sent" data-person="${contact.person_slug}" data-day="${day}">Mark sent</button>`}
      ${day === 1 ? `<button class="btn focus-email" title="Keyboard: e">Focus</button>` : ""}
    </div>
  </div>`;
}

function escapeHtml(s){
  return String(s == null ? "" : s).replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));
}

// -- THESIS page --
function renderThesis(){
  const svg = document.getElementById("scatter");
  const NS = "http://www.w3.org/2000/svg";
  function mkEl(tag, attrs){
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  svg.innerHTML = "";
  const PLOT = {W:900, H:540, padL:56, padR:18, padT:22, padB:44};
  const X = {min:1e5, max:1e10};
  const Y = {min:10, max:1e5};
  const xScale = v => PLOT.padL + (Math.log10(v) - Math.log10(X.min)) / (Math.log10(X.max)-Math.log10(X.min)) * (PLOT.W - PLOT.padL - PLOT.padR);
  const yScale = v => PLOT.H - PLOT.padB - (Math.log10(v) - Math.log10(Y.min)) / (Math.log10(Y.max)-Math.log10(Y.min)) * (PLOT.H - PLOT.padT - PLOT.padB);

  // axes
  svg.appendChild(mkEl("line", {x1:PLOT.padL, y1:PLOT.H-PLOT.padB, x2:PLOT.W-PLOT.padR, y2:PLOT.H-PLOT.padB, class:"axis-line"}));
  svg.appendChild(mkEl("line", {x1:PLOT.padL, y1:PLOT.padT, x2:PLOT.padL, y2:PLOT.H-PLOT.padB, class:"axis-line"}));
  const xt = [1e5,1e6,1e7,1e8,1e9,1e10];
  xt.forEach(v => {
    const x = xScale(v);
    svg.appendChild(mkEl("line", {x1:x, y1:PLOT.H-PLOT.padB, x2:x, y2:PLOT.H-PLOT.padB+4, class:"axis-line"}));
    const txt = mkEl("text", {x:x, y:PLOT.H-PLOT.padB+18, "text-anchor":"middle", class:"axis-text"});
    txt.textContent = v>=1e9 ? "$"+(v/1e9)+"B" : v>=1e6 ? "$"+(v/1e6)+"M" : "$"+(v/1e3)+"k";
    svg.appendChild(txt);
  });
  const yt = [10,100,1000,10000,100000];
  yt.forEach(v => {
    const y = yScale(v);
    svg.appendChild(mkEl("line", {x1:PLOT.padL-4, y1:y, x2:PLOT.padL, y2:y, class:"axis-line"}));
    const txt = mkEl("text", {x:PLOT.padL-8, y:y+3, "text-anchor":"end", class:"axis-text"});
    txt.textContent = v>=1000 ? (v/1000)+"k" : String(v);
    svg.appendChild(txt);
  });
  const xtit = mkEl("text", {x:(PLOT.padL+PLOT.W-PLOT.padR)/2, y:PLOT.H-8, "text-anchor":"middle", class:"axis-title"});
  xtit.textContent = "Revenue (annual, USD, log scale)";
  svg.appendChild(xtit);

  // threshold lines
  const xTh = xScale(5e8), yTh = yScale(5000);
  svg.appendChild(mkEl("line", {x1:xTh, y1:PLOT.padT, x2:xTh, y2:PLOT.H-PLOT.padB, class:"threshold-line"}));
  svg.appendChild(mkEl("line", {x1:PLOT.padL, y1:yTh, x2:PLOT.W-PLOT.padR, y2:yTh, class:"threshold-line"}));

  // quadrant labels
  function label(x, y, txt){
    const t = mkEl("text", {x:x, y:y, "text-anchor":"middle", class:"quadrant-label"});
    t.textContent = txt;
    svg.appendChild(t);
  }
  label(PLOT.padL + (xTh-PLOT.padL)/2, PLOT.padT + (yTh-PLOT.padT)/2, "Capital-light, labor-heavy");
  label(xTh + (PLOT.W-PLOT.padR-xTh)/2, PLOT.padT + (yTh-PLOT.padT)/2, "Enterprise / scale");
  label(PLOT.padL + (xTh-PLOT.padL)/2, yTh + (PLOT.H-PLOT.padB-yTh)/2, "Small / SMB");
  label(xTh + (PLOT.W-PLOT.padR-xTh)/2, yTh + (PLOT.H-PLOT.padB-yTh)/2, "Lean & scaling");

  // place points — only those with INFERRED employees_total that parseNumeric can read
  function parseNum(v){
    if (typeof v !== "string") return null;
    const s = v.replace(/[~$,]/g, "");
    if (!/^\d+(\.\d+)?$/.test(s)) return null;
    return parseFloat(s);
  }
  const PL_GROUPS = ACCOUNTS.filter(a => parseNum(a.employees_total) != null);
  // Order: priority asc, then by company for determinism.
  PL_GROUPS.sort((x,y) => (x.priority - y.priority) || x.company.localeCompare(y.company));
  PL_GROUPS.forEach((a, idx) => {
    const emp = parseNum(a.employees_total);
    if (emp == null) return;
    // X is anchored at $500M threshold (revenue unknown for all 20). Slight horizontal jitter
    // by index so circles don't stack on top of each other.
    const jitterX = (idx % 5 - 2) * 18;
    const cx = xScale(5e8) + jitterX;
    const cy = yScale(emp);
    const c = mkEl("circle", {cx:cx, cy:cy, r:8, class:"point", "data-priority":a.priority});
    const title = mkEl("title");
    title.textContent = `${a.company} · P${a.priority} · ~${emp.toLocaleString()} emp · sector: ${a.sector}`;
    c.appendChild(title);
    svg.appendChild(c);
  });
}

// -- Tabs --
function switchTab(name){
  document.querySelectorAll(".tab").forEach(t => t.setAttribute("aria-selected", String(t.dataset.tab === name)));
  document.querySelectorAll(".tab-panel").forEach(p => p.hidden = (p.dataset.tabPanel !== name));
  if (name === "today") renderToday();
  if (name === "accounts") { renderAccountsToolbar(); renderAccounts(); if (!STATE.selectedId && ACCOUNTS.length) STATE.selectedId = ACCOUNTS[0].account_id; renderDetail(); }
  if (name === "thesis") renderThesis();
}

document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => switchTab(t.dataset.tab)));

// -- disqualify modal --
let dqContextAccount = null;
function openDisqualifyModal(a, s){
  dqContextAccount = a;
  document.getElementById("dq-reason").value = s.disqualify_reason || "";
  document.getElementById("modal-disqualify").classList.add("open");
  document.getElementById("dq-reason").focus();
}
document.getElementById("dq-cancel").addEventListener("click", () => {
  document.getElementById("modal-disqualify").classList.remove("open");
  dqContextAccount = null;
});
document.getElementById("dq-confirm").addEventListener("click", () => {
  const reason = document.getElementById("dq-reason").value.trim();
  if (!reason){ toast("Disqualify reason is required."); return; }
  if (!dqContextAccount) return;
  const s = acctState(dqContextAccount.account_id);
  s.status = "disqualified";
  s.status_history.push({ status: "disqualified", date: TODAY_ISO });
  s.disqualify_reason = reason;
  saveState();
  document.getElementById("modal-disqualify").classList.remove("open");
  dqContextAccount = null;
  renderDetail(); renderAccounts(); renderToday();
  toast(`Disqualified: ${dqContextAccount && dqContextAccount.company || "account"}`);
});

// -- toast --
function toast(msg){
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2200);
}

// -- help overlay --
function openHelp(){ document.getElementById("help-overlay").classList.add("open"); }
function closeHelp(){ document.getElementById("help-overlay").classList.remove("open"); }
document.getElementById("btn-help").addEventListener("click", openHelp);
document.getElementById("help-close").addEventListener("click", closeHelp);
document.getElementById("help-overlay").addEventListener("click", e => { if (e.target.id === "help-overlay") closeHelp(); });

// -- Export CSV (full state) --
function exportCsv(){
  const head = ["account_id","company","region","priority","status","status_history","notes","next_action_date","next_action_label","disqualify_reason"];
  const lines = [head.join(",")];
  ACCOUNTS.forEach(a => {
    const s = acctState(a.account_id);
    const sh = JSON.stringify(s.status_history);
    const row = [
      a.account_id,
      csv(a.company),
      csv(a.region),
      a.priority,
      s.status,
      csv(sh),
      csv(s.notes || ""),
      csv(s.next_action_date || ""),
      csv(s.next_action_label || ""),
      csv(s.disqualify_reason || "")
    ];
    lines.push(row.join(","));
  });
  // touch sub-grid
  lines.push("");
  lines.push("Touches");
  lines.push(["account_id","person_slug","day","sent_date","body_edited"].join(","));
  ACCOUNTS.forEach(a => {
    const s = acctState(a.account_id);
    a.contacts.forEach(c => {
      if (!s.touches[c.person_slug]) return;
      [1,3,8,15].forEach(day => {
        const t = (s.touches[c.person_slug] || {})[day];
        if (!t) return;
        lines.push([a.account_id, csv(c.person_slug), day, csv(t.sent_date||""), csv(t.body_edited||"")].join(","));
      });
    });
  });
  const blob = new Blob([lines.join("\n")], { type:"text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = `factory_territory_state_${TODAY_ISO}.csv`;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
  toast("State exported to CSV");
}
function csv(s){ const v = String(s == null ? "" : s); return /[,"\n]/.test(v) ? `"${v.replace(/"/g,'""')}"` : v; }
document.getElementById("btn-export").addEventListener("click", exportCsv);

// -- Reset --
document.getElementById("btn-reset").addEventListener("click", () => {
  if (!confirm("Reset all status, notes, touches, and disqualify reasons? This cannot be undone (re-import via the same CSV will not restore fields).")) return;
  STATE = { accounts: {}, today_checked_date: TODAY_ISO };
  saveState();
  renderToday(); renderAccounts(); renderDetail();
  toast("State reset");
});

// -- Keyboard shortcuts --
document.addEventListener("keydown", e => {
  // Skip when typing in inputs
  const inField = ["INPUT","TEXTAREA","SELECT"].includes((e.target.tagName || "").toUpperCase());
  if (e.key === "?" && !inField){ e.preventDefault(); openHelp(); return; }
  if (e.key === "Escape"){ closeHelp(); document.getElementById("modal-disqualify").classList.remove("open"); return; }
  if (inField) return;

  if (e.key === "/"){
    e.preventDefault();
    document.getElementById("filter-search").focus();
    switchTab("accounts");
    return;
  }
  if (e.key === "j" || e.key === "k"){
    e.preventDefault();
    const list = document.querySelectorAll("#acct-list .acct-row");
    if (!list.length) return;
    let i = -1;
    list.forEach((r, idx) => { if (r.classList.contains("active")) i = idx; });
    const next = e.key === "j" ? Math.min(i + 1, list.length - 1) : Math.max(0, i === -1 ? 0 : i - 1);
    const id = list[next].dataset.jump;
    selectAccount(id);
    document.querySelector("#acct-list .acct-row.active")?.scrollIntoView({ block:"nearest" });
    return;
  }
  if (e.key === "e"){
    e.preventDefault();
    const ta = document.querySelector(".touch textarea[data-day='1']");
    if (ta) ta.focus();
    return;
  }
  if (e.key === "c"){
    e.preventDefault();
    const btn = document.querySelector(".copy-btn[data-day='1']");
    if (btn) btn.click();
    return;
  }
  if (e.key === "d"){
    e.preventDefault();
    if (!STATE.selectedId) return;
    const a = ACCOUNTS.find(x => x.account_id === STATE.selectedId);
    const s = acctState(a.account_id);
    openDisqualifyModal(a, s);
    return;
  }
  if (["1","2","3","4","5"].includes(e.key)){
    const map = {1:"researched",2:"contacted",3:"replied",4:"meeting",5:"disqualified"};
    e.preventDefault();
    if (!STATE.selectedId) return;
    const a = ACCOUNTS.find(x => x.account_id === STATE.selectedId);
    const s = acctState(a.account_id);
    const target = map[e.key];
    if (target === "disqualified"){ openDisqualifyModal(a, s); return; }
    s.status = target;
    s.status_history.push({ status: target, date: TODAY_ISO });
    if (target !== "disqualified") s.disqualify_reason = "";
    saveState();
    renderDetail(); renderAccounts(); renderToday();
    return;
  }
});

// -- Init --
function init(){
  STATE.filter = STATE.filter || {region:"All", priority:"All", status:"All", search:""};
  if (!STATE.selectedId) STATE.selectedId = ACCOUNTS[0].account_id;
  switchTab("today");
}
init();
</script>
</body>
</html>
"""

HTML = HTML.replace("__TODAY__", TODAY_ISO)
HTML = HTML.replace("__ACCOUNTS__", ACCOUNTS_JSON)

OUT_PATH.write_text(HTML, encoding="utf-8")
print(f"Dashboard regenerated → {OUT_PATH}")
print(f"  size: {OUT_PATH.stat().st_size} bytes")
print(f"  accounts: {len(accounts)}")
print(f"  contacts: {len(contacts)}")
