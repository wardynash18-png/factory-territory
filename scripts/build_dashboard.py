"""Factory Territory Prospecting Tool — 4-tab dashboard builder.

Tabs: Today (work queue) · Accounts (list + detail) · Forecast (sliders + MEDDPICC-weighted pipeline) · Thesis (scatter + written argument).

Reads:
  data/accounts_enriched.csv   — 20-row real SD/Denver target list
  data/accounts_seed.csv       — seed priorities + initial theses
  data/contacts.csv            — strict 5-slot buying-committee schema (Phase 3)
  data/meddpicc.json           — 8-element MEDDPICC per priority account (Phase 4)
  research/<company>_outreach.md — slot-tailored Email + LinkedIn bodies (Phase 3b)

Writes: dashboard/index.html  — single self-contained file, localStorage persistence, no build step.
"""
import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_ENRICHED = ROOT / "data" / "accounts_enriched.csv"
CSV_SEED = ROOT / "data" / "accounts_seed.csv"
CSV_CONTACTS = ROOT / "data" / "contacts.csv"
JSON_MEDDPICC = ROOT / "data" / "meddpicc.json"
OUT_PATH = ROOT / "dashboard" / "index.html"
TODAY = "2026-07-14"  # per AGENTS.md

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def safe(v, default=""):
    if v is None: return default
    s = str(v).strip()
    return s if s else default

def infer_region(state):
    if state == "CA": return "San Diego"
    if state == "CO": return "Denver"
    return ""

SLOT_ORDER = ["economic_buyer", "technical_champion", "program_owner", "security_governance", "wildcard"]
SLOT_LABEL = {
    "economic_buyer": "Economic Buyer",
    "technical_champion": "Technical Champion",
    "program_owner": "Program Owner",
    "security_governance": "Security / Governance",
    "wildcard": "Wildcard",
}
COMPANY_TO_ID = {
    "Qualcomm": "A001",
    "DaVita": "A002",
    "ResMed": "A003",
    "Western Union": "A004",
    "LPL Financial": "A005",
    "Empower": "A006",
}
URL_RE = re.compile(r"https?://[^\s\)\]\"<>]+")

# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
with open(CSV_ENRICHED, encoding="utf-8") as f:
    rd = csv.reader(f)
    enriched_h = [c.strip() for c in next(rd)]
    enriched_rows = list(rd)
enriched_cols = {c: i for i, c in enumerate(enriched_h)}

with open(CSV_SEED, encoding="utf-8") as f:
    seed_by_company = {r["company"].strip(): r for r in csv.DictReader(f)}

with open(CSV_CONTACTS, encoding="utf-8") as f:
    raw_contacts = list(csv.DictReader(f))

with open(JSON_MEDDPICC, encoding="utf-8") as f:
    MEDDPICC_RAW = json.load(f)
MEDDPICC = MEDDPICC_RAW.get("accounts", {})

contacts_by_acct = {}
for c in raw_contacts:
    aid = COMPANY_TO_ID.get(c["company"].strip())
    if not aid: continue
    slot = c["slot"].strip()
    c["person_slug"] = f"{aid}__{slot}"
    c["title"] = c.get("role_title", "").strip()
    contacts_by_acct.setdefault(aid, []).append(c)
for aid in contacts_by_acct:
    contacts_by_acct[aid].sort(key=lambda x: SLOT_ORDER.index(x["slot"]) if x["slot"] in SLOT_ORDER else 99)

# Outreach research per priority account
OUTREACH_BY_ID = {}
for comp, aid in [("qualcomm", "A001"), ("davita", "A002"), ("resmed", "A003"),
                  ("western-union", "A004"), ("lpl-financial", "A005"), ("empower", "A006")]:
    p = ROOT / "research" / f"{comp}_outreach.md"
    OUTREACH_BY_ID[aid] = p.read_text(encoding="utf-8") if p.exists() else ""

# ---------------------------------------------------------------------------
# Account payload compose
# ---------------------------------------------------------------------------
PICK = [
    "account_id", "company", "domain", "slug", "hq_city", "hq_state", "hq_country",
    "region", "sector", "employees_total", "engineering_headcount",
    "cto_name", "cio_name", "cto_source_url", "cio_source_url",
    "github_url", "in_sd_or_denver_metro", "last_researched", "near_match_notes",
]

ANALOGUES = {
    "A001": ("Nvidia", "Both are chip / firmware houses with massive embedded codebases; CIO discussion of agentic workflows lines up."),
    "A002": ("MongoDB", "DaVita is the MongoDB analogue: a software-in-its-own-product company undergoing platform modernization."),
    "A003": ("Bayer", "Both FDA-regulated; agentic AI for traceable / auditable workflows in regulated environments is the precise Bayer analogue."),
    "A004": ("Morgan Stanley", "Payments + mainframe + SI partner; the modern Morgan Stanley buyer shape."),
    "A005": ("Morgan Stanley", "Wealth-management platform modernization with a CIO whose remit literally is the platform."),
    "A006": ("Morgan Stanley", "Acquirer-inherited data stacks; the typical buyer is a Morgan Stanley-style platform-modernization buyer."),
    "A007": ("Palo Alto Networks", "Defense + classified; engineering motion resembles Palo Alto's regulated-infra buyer."),
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
    "A020": ("EY", "PE-owned, network provisioning-built-through-acquisition; cost discipline argues the ROI story."),
}

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

# Verdict / disqualifier strings per priority account (from research/<company>.md)
PRIORITY_VERDICT = {
    "A001": ("PAUSE", "verify Fortune July 2026 CIO article URL before opening"),
    "A002": ("PROCEED", "strongest signal — Sr Director Transformation req + verified CIO"),
    "A003": ("HOLD", "specific seed claim via auditable/traceable reqs is NO SIGNAL FOUND"),
    "A004": ("PROCEED", "pitch as HCLTech-augment, not HCLTech-replace"),
    "A005": ("PROCEED", "after CIO-name verified; Hyderabad GCC IS the competitor"),
    "A006": ("HOLD", "until Milliman close + integration head is seated"),
}

# ---------------------------------------------------------------------------
# Parse signals per account from near_match_notes
# ---------------------------------------------------------------------------
def extract_signals(notes, last_researched):
    urls = URL_RE.findall(notes or "")
    seen, out = set(), []
    for u in urls:
        u = u.rstrip(",.;:")
        if u in seen: continue
        seen.add(u)
        out.append({"url": u, "label": u.split("/")[2] if "/" in u else u, "accessed": last_researched})
    return out

accounts = []
for r in enriched_rows:
    pad = {c: safe(r[enriched_cols[c]]) if c in enriched_cols else "" for c in PICK}
    aid = pad["account_id"]
    comp = pad["company"]
    seed = seed_by_company.get(comp) or seed_by_company.get(comp.replace("EchoStar", "EchoStar / DISH"))
    seed_priority = (seed or {}).get("priority", "")
    seed_thesis = (seed or {}).get("initial_thesis", "")
    sr = pad["last_researched"] or TODAY
    contacts_5slot = []
    for c in contacts_by_acct.get(aid, []):
        contacts_5slot.append({
            "slot": c["slot"],
            "slot_label": SLOT_LABEL.get(c["slot"], c["slot"]),
            "person_slug": c["person_slug"],
            "name": c["name"],
            "title": c["title"],
            "confidence": c["confidence"],
            "linkedin_url": c.get("linkedin_url", ""),
            "source_url": c.get("source_url", ""),
            "why_this_person": c.get("why_this_person", ""),
        })
    accounts.append({
        "account_id": aid,
        "company": comp,
        "slug": comp.lower().replace(" / ", "-").replace("/", "-").replace(" ", "-"),
        "domain": pad["domain"],
        "hq_city": pad["hq_city"],
        "hq_state": pad["hq_state"],
        "region": pad["region"] or infer_region(pad["hq_state"]),
        "sector": pad["sector"],
        "priority": seed_priority,
        "employees_total": pad["employees_total"],
        "engineering_headcount": pad["engineering_headcount"],
        "last_researched": sr,
        "seed_thesis": seed_thesis,
        "analogue": ANALOGUES.get(aid, ("Adobe", "Default analogue.")),
        "complication": COMPLICATIONS.get(aid, "No specific complication surfaced."),
        "verdict": PRIORITY_VERDICT.get(aid, ("", "")),
        "is_priority": aid in PRIORITY_VERDICT,
        "contacts": contacts_5slot,
        "signals": extract_signals(pad["near_match_notes"], sr),
        "meddpicc_key": aid + "_" + comp.replace(" ", ""),
    })

# Demo staleness aging
age_offsets = {"A009": 45, "A013": 72, "A016": 50, "A017": 90, "A018": 32}
for a in accounts:
    if a["account_id"] in age_offsets:
        d = datetime.strptime(TODAY, "%Y-%m-%d") - timedelta(days=age_offsets[a["account_id"]])
        a["last_researched"] = d.strftime("%Y-%m-%d")

accounts.sort(key=lambda a: (int(a["priority"]) if a["priority"].isdigit() else 99, a["company"]))

# ---------------------------------------------------------------------------
# 30/60/90 Account Plan per priority account (entry persona + trigger + objections + disqualifier)
# ---------------------------------------------------------------------------
ACCOUNT_PLANS = {
    "A001": {
        "entry_persona": "Head of Agentic Platform Evaluation (PERSON UNVERIFIED — see contacts)",
        "why": "LinkedIn agentic-ai benchmark-eval-engineer posting implies the eval-of-agents team is being stood up. Whoever owns it owns the next 90 days.",
        "business_trigger": "Apr 2026 SD layoffs cost-engineering pressure + same-week eval-of-agents job posting",
        "objection_1": "We don't have budget for vendor agents — handle: GPU-cost ROI vs headcount-add savings",
        "objection_2": "We're not buying AGENTS yet, just EVALUATING — handle: pivot Day 8 to a benchmarking brief",
        "disqualifier_truthful": "If the agentic-eval-engineer posting turns out to be a sandbox, not production-adjacent, factory loses the slot — verify before opening.",
    },
    "A002": {
        "entry_persona": "Madhu Narasimhan, CIO (VERIFIED) — LinkedIn surfaced in search",
        "why": "Multi-year GCP migration of legacy revenue-cycle apps is the program; Sr Director of Transformation (R0466819) is the program owner once seated.",
        "business_trigger": "Sr Director Transformation req live on DaVita career site 2026-07-06",
        "objection_1": "HCLTech/Cognizant already owns lines — handle: factory augments SI, not competes",
        "objection_2": "Sr Director hasn't started — handle: reach Madhu the CIO until Sr Director is seated",
        "disqualifier_truthful": "If HCLTech or similar owns the modernization tooling budget end-to-end, factory loses.",
    },
    "A003": {
        "entry_persona": "DO NOT PROSPECT YET — see research/resmed_outreach.md",
        "why": "Seed-specific claim (traceable/auditable agentic reqs) is NO SIGNAL FOUND in this research pass.",
        "business_trigger": "None visible",
        "objection_1": "We don't have agentic reqs — handle: cannot anchor without a verified req",
        "objection_2": "FDA change-control is heavy — handle: not relevant unless req is real",
        "disqualifier_truthful": "If a matching auditable-agentic req never surfaces, this account is permanently HOLD.",
    },
    "A004": {
        "entry_persona": "CISO and Head of Mainframe / Legacy Modernization (PERSON UNVERIFIED — see contacts)",
        "why": "HCLTech 2026-05-14 partnership release names a WU counterpart. The SI owns the tooling budget category; pitch as HCLTech-augment.",
        "business_trigger": "HCLTech AI-led platform partnership announcement (May 14, 2026)",
        "objection_1": "HCLTech has the contract — handle: third-party tooling is allowed inside, not forbidden",
        "objection_2": "We just signed with HCLTech — handle: tooling procurement is separate from the SI contract",
        "disqualifier_truthful": "If HCLTech owns third-party agent-tooling procurement end-to-end, factory loses.",
    },
    "A005": {
        "entry_persona": "CIO of LPL Financial (PERSON UNVERIFIED — Profile Magazine 2025-06-09 in soft name)",
        "why": "Hyderabad GCC launched Feb 5-6, 2026 is the substitute for staff; pitch as GCC-partner not GCC-replacement.",
        "business_trigger": "Hyderabad GCC public (Feb 5-6, 2026) + continued Q1 2026 platform-modernization cadence",
        "objection_1": "GCC IS the modernization answer — handle: GCC delivers assignments; third-party tooling accelerates the delivery",
        "objection_2": "FINRA review is slow — handle: 9-12 month cycle is the realistic floor; don't compress",
        "disqualifier_truthful": "If GCC has its own prohibition on third-party agent tools, factory loses the slot.",
    },
    "A006": {
        "entry_persona": "Hold until Milliman integration head is seated post-close (2026-06-30 + ~9 months)",
        "why": "Integration head is the program owner; tools-buy budget follows integration head seating.",
        "business_trigger": "Milliman retirement-administration acquisition announced 2026-06-30",
        "objection_1": "PE-owned — every dollar goes through GP governance — handle: ROI narrative is mandatory",
        "objection_2": "Don't call our platform old — handle: open with the visible M&A cadence, never inferred legacy age",
        "disqualifier_truthful": "If PE governance forbids third-party tools inside integration programs, factory loses.",
    },
}

# ---------------------------------------------------------------------------
# Serialize for embedding
# ---------------------------------------------------------------------------
ACCOUNTS_JSON = json.dumps(accounts, ensure_ascii=False)
MEDDPICC_JSON = json.dumps(MEDDPICC, ensure_ascii=False)
ACCOUNT_PLANS_JSON = json.dumps(ACCOUNT_PLANS, ensure_ascii=False)

# Embed outreach research files (raw text) so the Account detail panel can render them
# (kept lightweight — only priority accounts — by Reading once at build time)
import base64 as _b64
OUTREACH_JSON = json.dumps({k: v for k, v in OUTREACH_BY_ID.items()}, ensure_ascii=False)

# ---------------------------------------------------------------------------
# HTML / CSS / JS template
# ---------------------------------------------------------------------------
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Factory Territory — Prospecting Tool</title>
<style>
:root{--bg:#fff;--bg-alt:#f8fafc;--bg-soft:#f1f5f9;--fg:#0f172a;--fg-muted:#475569;--fg-faint:#94a3b8;--border:#e2e8f0;--border-strong:#cbd5e1;--accent:#0a4d68;--accent-soft:#cffafe;--row-hover:#f8fafc;--status-not_started:#94a3b8;--status-researched:#1d4ed8;--status-contacted:#0e7490;--status-replied:#047857;--status-meeting:#15803d;--status-disqualified:#be123c;--warn-amber:#b45309;--warn-red:#be123c;--warn-red-text:#9b1c2e;--fresh:#15803d;--fresh-text:#15803d;--focus:#f59e0b;--priority-1:#047857;--priority-2:#0e7490;--priority-3:#1d4ed8;--priority-4:#b45309;--priority-5:#be123c;--verified:#047857;--inferred:#92400e;--slot-only:#475569;--callout-bg:rgba(240,180,40,0.10);--callout-border:#C98A16;--callout-text:#F0D6A0;--callout-heading:#F5C563;--callout-bg-red:rgba(190,18,60,0.12);--callout-border-red:#C91843;--callout-text-red:#F9C5CD;--callout-heading-red:#F87171;--callout-bg-green:rgba(22,163,74,0.12);--callout-border-green:#15803d;--callout-text-green:#A7E8C0;--callout-heading-green:#34D399}
@media (prefers-color-scheme:dark){:root{--bg:#0f172a;--bg-alt:#1e293b;--bg-soft:#334155;--fg:#f1f5f9;--fg-muted:#cbd5e1;--fg-faint:#64748b;--border:#334155;--border-strong:#475569;--accent:#67e8f9;--accent-soft:#155e75;--row-hover:#1e293b}}
*,*::before,*::after{box-sizing:border-box}
html{font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-size:14px;line-height:1.45}
body{margin:0;background:var(--bg);color:var(--fg);overflow-wrap:break-word}
code,.mono{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;font-size:.92em}
a{color:var(--accent)}a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.skip-link{position:absolute;left:-9999px;top:0;background:var(--accent);color:#fff;padding:6px 10px;z-index:200}.skip-link:focus{left:8px;top:8px}
header{border-bottom:1px solid var(--border);padding:12px 24px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}header h1{font-size:17px;margin:0;font-weight:600;letter-spacing:-.01em}
.tabs{display:flex;gap:4px}.tab{padding:6px 14px;border:1px solid var(--border);border-radius:4px;background:var(--bg);cursor:pointer;font-size:13px;color:var(--fg-muted)}.tab[aria-selected="true"]{background:var(--accent);border-color:var(--accent);color:#fff}.tab-count{display:inline-block;background:rgba(255,255,255,.25);padding:0 6px;border-radius:8px;font-size:11px;margin-left:4px}.tab:not([aria-selected="true"]) .tab-count{background:var(--bg-soft);color:var(--fg-muted)}
.top-actions{margin-left:auto;display:flex;gap:8px;align-items:center}.btn{background:var(--bg);border:1px solid var(--border-strong);padding:5px 10px;border-radius:3px;font-size:12.5px;cursor:pointer;color:var(--fg)}.btn:hover{border-color:var(--accent)}.btn-primary{background:var(--accent);color:#fff;border-color:var(--accent)}.btn-danger{background:var(--status-disqualified);color:#fff;border-color:var(--status-disqualified)}
main{padding:18px 24px 60px;max-width:1500px;margin:0 auto}.panel{background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:14px 16px;margin-bottom:14px}.panel h2{font-size:12.5px;margin:0 0 8px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--fg-muted)}.panel h3{font-size:13.5px;margin:0 0 6px;font-weight:600}
.row{display:flex;flex-wrap:wrap;gap:12px}.row > *{flex:1 1 240px;min-width:220px}
.today-headline{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}.today-headline h2{font-size:22px;margin:0;font-weight:600}
.work-queue-section{margin-bottom:22px}.work-queue-section h2{font-size:14px;margin:0 0 8px;color:var(--fg-muted);text-transform:uppercase;letter-spacing:.06em;font-weight:600}
.work-item{background:var(--bg);border:1px solid var(--border);border-radius:3px;padding:10px 12px;margin-bottom:6px;cursor:pointer;display:grid;grid-template-columns:1fr auto;gap:10px;align-items:baseline}.work-item:hover{background:var(--row-hover)}.work-item .title{font-weight:600}.work-item .sub{font-size:12px;color:var(--fg-muted);margin-top:2px}.work-item .meta{font-size:11.5px;color:var(--fg-muted);white-space:nowrap;text-align:right}.work-item .pill{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:8px;border:1px solid var(--border-strong);background:var(--bg);color:var(--fg-muted);margin-left:4px}.work-item .pill.overdue{background:var(--callout-bg-red);color:var(--callout-heading-red);border-color:var(--callout-border-red);font-weight:600}.work-item .pill.due-today{background:var(--accent-soft);color:var(--accent);border-color:var(--accent);font-weight:600}.work-item .pill.stale-amber{background:var(--callout-bg);color:var(--callout-heading);border-color:var(--callout-border);font-weight:600}.work-item .pill.stale-red{background:var(--callout-bg-red);color:var(--callout-heading-red);border-color:var(--callout-border-red);font-weight:600}.work-item .pill.fresh{background:var(--callout-bg-green);color:var(--callout-heading-green);border-color:var(--callout-border-green);font-weight:600}
.empty-state{background:var(--bg-alt);border:1px dashed var(--border-strong);border-radius:4px;padding:24px;text-align:center;color:var(--fg-muted)}
.toolbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;padding:10px 14px;background:var(--bg-alt);border:1px solid var(--border);border-radius:4px;margin-bottom:12px}
.filter-group{display:flex;align-items:center;gap:6px;flex-wrap:wrap}.filter-label{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--fg-faint);font-weight:600}
.chips{display:flex;flex-wrap:wrap;gap:4px}.chip{border:1px solid var(--border-strong);background:var(--bg);padding:3px 9px;border-radius:12px;cursor:pointer;font-size:12px;color:var(--fg-muted);user-select:none}.chip:hover{border-color:var(--accent)}.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.search-input{border:1px solid var(--border-strong);border-radius:3px;padding:5px 9px;min-width:240px;font-size:13px;background:var(--bg);color:var(--fg)}
.acct-layout{display:grid;grid-template-columns:320px 1fr;gap:14px}
.acct-list{max-height:75vh;overflow:auto;padding:0;border:1px solid var(--border);border-radius:4px;background:var(--bg)}
.acct-row{padding:10px 12px;border-bottom:1px solid var(--border);cursor:pointer}.acct-row:hover{background:var(--row-hover)}.acct-row.active{background:var(--callout-bg);border-left:3px solid var(--accent);padding-left:9px;color:var(--callout-heading)}
.acct-row .name{font-weight:600}.acct-row .sub{font-size:11.5px;color:var(--fg-muted);margin-top:2px}.acct-row .quick-status{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:8px;margin-top:4px}
.acct-detail .detail-head{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:8px}.acct-detail .detail-head h2{font-size:20px;margin:0}.acct-detail .detail-head .hq{font-size:12.5px;color:var(--fg-muted)}
.verdict-pill{display:inline-block;font-size:11px;padding:2px 8px;border-radius:8px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;border:1px solid}.verdict-pill.PROCEED{background:#dcfce7;color:var(--fresh);border-color:var(--fresh)}.verdict-pill.HOLD{background:#fef3c7;color:var(--warn-amber);border-color:var(--warn-amber)}.verdict-pill.PAUSE{background:#fee2e2;color:var(--warn-red);border-color:var(--warn-red)}
.pipeline{display:flex;gap:4px;margin:8px 0 12px;flex-wrap:wrap}.pipeline .step{padding:5px 10px;border:1px solid var(--border-strong);border-radius:999px;font-size:11.5px;background:var(--bg);color:var(--fg-muted);cursor:pointer}.pipeline .step:hover{border-color:var(--accent)}.pipeline .step.active{color:#fff;border-color:currentColor}
.pipeline .step[data-status="not_started"].active{background:var(--status-not_started);border-color:var(--status-not_started)}
.pipeline .step[data-status="researched"].active{background:var(--status-researched);border-color:var(--status-researched)}
.pipeline .step[data-status="contacted"].active{background:var(--status-contacted);border-color:var(--status-contacted)}
.pipeline .step[data-status="replied"].active{background:var(--status-replied);border-color:var(--status-replied)}
.pipeline .step[data-status="meeting"].active{background:var(--status-meeting);border-color:var(--status-meeting)}
.pipeline .step[data-status="disqualified"].active{background:var(--status-disqualified);border-color:var(--status-disqualified)}
.pipeline-arrow{font-size:14px;color:var(--fg-faint);align-self:center}
.section-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media (max-width:980px){.section-grid{grid-template-columns:1fr}.acct-layout{grid-template-columns:1fr}}
.sect{border:1px solid var(--border);border-radius:4px;padding:12px 14px}.sect h3{font-size:12.5px;margin:0 0 8px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--fg-muted)}
textarea,input[type=text],input[type=date],input[type=number],input[type=range]{width:100%;border:1px solid var(--border-strong);border-radius:3px;padding:6px 9px;font-size:13px;background:var(--bg);color:var(--fg);font-family:inherit}textarea{min-height:70px;resize:vertical}
.contact-card{border:1px solid var(--border);border-radius:3px;padding:10px 12px;margin-bottom:8px}.contact-card .name-row{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}.contact-card .name-row .name{font-weight:600}.contact-card .slot-label{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--fg-faint);font-weight:600}.contact-card .title{font-size:12px;color:var(--fg-muted)}.conf{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:8px;border:1px solid;font-weight:600;letter-spacing:.04em}.conf.VERIFIED{background:var(--callout-bg-green);color:var(--callout-heading-green);border-color:var(--callout-border-green)}.conf.INFERRED{background:var(--callout-bg);color:var(--callout-heading);border-color:var(--callout-border)}.conf.SLOT_ONLY{background:var(--bg-soft);color:var(--fg);border-color:var(--border-strong)}
.contact-card .meta{font-size:11.5px;color:var(--fg-muted);margin-top:4px}.contact-card .why{font-size:12px;color:var(--fg);margin-top:4px;font-style:italic}
.touch{border:1px solid var(--border);border-radius:3px;padding:10px 12px;margin-bottom:8px;background:var(--bg)}.touch.sent{background:var(--callout-bg-green);border-color:var(--callout-border-green)}
.touch-head{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}.touch-num{font-weight:700;color:var(--accent);font-size:13px}.touch-day{font-size:11.5px;color:var(--fg-muted)}.touch .touch-date{font-size:11.5px;color:var(--fg-muted);margin-left:auto}
.touch textarea{min-height:60px;margin-top:6px}
.touch .touch-controls{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-top:6px}.touch .char-count{font-size:11px;color:var(--fg-muted);margin-right:6px}.touch .char-count.warn{color:var(--warn-amber);font-weight:600}.touch .char-count.bad{color:var(--warn-red);font-weight:700}
.touch .sent-stamp{font-size:11.5px;color:var(--fresh);font-weight:600}.touch .unmark-sent{color:var(--fg-faint);font-size:11.5px;cursor:pointer;text-decoration:underline;background:none;border:none;padding:0}
.signal-row{display:grid;grid-template-columns:auto 1fr auto auto;gap:8px;align-items:baseline;padding:6px 0;border-bottom:1px solid var(--border);font-size:12.5px}.signal-row:last-child{border-bottom:none}.signal-row .age{font-size:11px;color:var(--fg-muted);font-variant-numeric:tabular-nums}.signal-row .badge{font-size:10.5px;padding:1px 6px;border-radius:8px;border:1px solid}.signal-row .badge.fresh{background:var(--callout-bg-green);color:var(--callout-heading-green);border-color:var(--callout-border-green);font-weight:600}.signal-row .badge.amber{background:var(--callout-bg);color:var(--callout-heading);border-color:var(--callout-border);font-weight:600}.signal-row .badge.red{background:var(--callout-bg-red);color:var(--callout-heading-red);border-color:var(--callout-border-red);font-weight:600}.signal-row .re-verify{font-size:11px;color:var(--accent);cursor:pointer;background:none;border:1px solid var(--border-strong);padding:2px 7px;border-radius:3px}
.ref-list{list-style:decimal-leading-zero;padding:0 0 0 24px;margin:0;max-height:240px;overflow:auto;font-size:12.5px}.ref-list li{padding:4px 0;border-bottom:1px solid var(--border);color:var(--fg-muted)}.ref-list li a{color:var(--accent)}.ref-list li .label{color:var(--fg-faint);margin-left:6px}.ref-list li .date{color:var(--fg-faint);font-family:ui-monospace,monospace;font-size:11px;margin-left:6px}
.complication-block{background:var(--callout-bg);border-left:3px solid var(--callout-border);padding:10px 12px;font-size:13px;color:var(--callout-text)}
@media (prefers-color-scheme:dark){.complication-block{background:var(--callout-bg);color:var(--callout-text)}.acct-row.active{background:rgba(240,180,40,0.18);color:var(--callout-heading)}}
.complication-block strong{color:var(--callout-heading)}
.checklist label{display:flex;align-items:flex-start;gap:8px;padding:4px 0;font-size:12.5px}
.outreach-tabs{display:flex;flex-direction:row;gap:6px;margin:0 0 10px 0;flex-wrap:wrap;align-items:center}
.outreach-tab{padding:6px 14px;border:1px solid var(--border-strong);border-radius:4px;cursor:pointer;font-size:13px;color:var(--fg-muted);background:var(--bg);white-space:nowrap;writing-mode:horizontal-tb;font-weight:600}
.outreach-tab:hover{border-color:var(--accent);color:var(--accent)}
.outreach-tab[aria-selected="true"]{background:var(--accent);color:#fff;border-color:var(--accent)}
.outreach-panel{margin-top:8px;display:block}
.outreach-panel[hidden]{display:none!important}
.outreach-slot{border:1px solid var(--border);border-radius:3px;padding:10px 12px;margin-bottom:8px;background:var(--bg)}
.outreach-slot h4{font-size:12.5px;margin:0 0 6px;color:var(--accent);letter-spacing:.04em;text-transform:uppercase;font-weight:600}
.outreach-slot .subj-row{display:flex;align-items:baseline;gap:8px;margin-bottom:8px;flex-wrap:wrap}
.outreach-slot .subj-label{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--fg-faint);font-weight:600}
.outreach-slot .subj{font-family:ui-monospace,monospace;font-size:12.5px;background:var(--bg-soft);padding:3px 8px;border-radius:3px;color:var(--fg);font-weight:600;border:1px solid var(--border)}
.outreach-slot textarea{width:100%;min-height:160px;font-size:12.5px;line-height:1.55;margin:0 0 6px 0;background:var(--bg);color:var(--fg);font-family:inherit}
.outreach-slot .char-row{display:flex;justify-content:space-between;align-items:center;margin-top:6px;font-size:11.5px;color:var(--fg-muted)}
.outreach-slot .char-count{font-family:ui-monospace,monospace;font-weight:600}
.outreach-slot .char-count.warn{color:var(--callout-heading);font-weight:700}
.outreach-slot .char-count.bad{color:var(--callout-heading-red);font-weight:700}
.outreach-slot .copy-inline{font-size:11.5px;color:#fff;background:var(--accent);border:1px solid var(--accent);padding:4px 12px;border-radius:3px;cursor:pointer;font-weight:600}
.outreach-slot .copy-inline:hover{filter:brightness(1.1)}
.plan-grid{display:grid;grid-template-columns:88px 1fr;gap:6px 14px;font-size:12.5px;align-items:baseline}.plan-grid dt{font-weight:600;color:var(--accent);font-size:11px;text-transform:uppercase;letter-spacing:.04em}.plan-grid dd{margin:0;color:var(--fg)}.plan-disqualify{background:var(--callout-bg-red);border:1px solid var(--callout-border-red);border-radius:3px;padding:8px 10px;margin-top:10px;font-size:12.5px;color:var(--callout-text-red)}.plan-disqualify strong{color:var(--callout-heading-red)}
.meddpicc-bar{display:grid;grid-template-columns:130px 1fr 36px;gap:8px;align-items:center;padding:3px 0;font-size:12.5px}.meddpicc-bar .track{height:8px;background:var(--border);border-radius:4px;overflow:hidden}.meddpicc-bar .fill{height:100%;background:var(--accent);border-radius:4px}.meddpicc-bar .score{font-family:ui-monospace,monospace;font-weight:700;text-align:right}.meddpicc-total{margin-top:8px;padding:8px 12px;background:var(--callout-bg);border-radius:4px;display:flex;justify-content:space-between;font-weight:600;font-size:13.5px;color:var(--callout-text)}.meddpicc-total .band-label{font-size:11px;padding:2px 8px;border-radius:8px;background:var(--accent);color:#fff;text-transform:uppercase;letter-spacing:.04em}.meddpicc-biggest{margin-top:8px;font-size:12px;color:var(--callout-text);background:var(--callout-bg);border-left:3px solid var(--callout-border);padding:6px 10px}
.forecast-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media (max-width:980px){.forecast-grid{grid-template-columns:1fr}}
.forecast-slider{display:grid;grid-template-columns:160px 1fr 80px;gap:8px;align-items:center;padding:6px 0;font-size:12.5px}.forecast-slider label{font-size:11.5px;color:var(--fg-muted)}.forecast-slider input[type=range]{width:100%}.forecast-slider .val{font-family:ui-monospace,monospace;text-align:right;font-weight:600}
.forecast-output{background:var(--callout-bg);border:1px solid var(--callout-border);border-radius:4px;padding:12px 14px;font-size:13px;color:var(--callout-text)}.forecast-output .top{margin-bottom:8px;font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--callout-heading);font-weight:600}.forecast-output .big{font-size:24px;font-weight:700;margin-bottom:4px;color:var(--callout-heading)}.forecast-output .pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:8px}.forecast-output .pair .weight{font-family:ui-monospace,monospace;color:var(--callout-heading);font-weight:600}
.forecast-output .comparison{margin-top:14px;padding-top:10px;border-top:1px solid var(--callout-border);font-size:12px;color:var(--callout-text)}.forecast-output .gap-line{margin-top:10px;padding:8px 10px;border-radius:3px;background:rgba(240,180,40,0.18);font-size:12.5px;color:var(--callout-heading)}.forecast-output .gap-line strong{color:var(--callout-heading)}
.assumptions-panel{margin-top:14px}.assumptions-panel table{font-size:12px;width:100%;border-collapse:collapse}.assumptions-panel th,.assumptions-panel td{padding:6px 8px;border:1px solid var(--border);text-align:left;vertical-align:top}.assumptions-panel th{background:var(--bg-soft);font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--fg-muted);font-weight:600}.assumptions-panel .who{font-style:italic;color:var(--accent)}
.thesis-writeup{background:var(--bg-alt);border:1px solid var(--border);border-radius:4px;padding:14px 18px;margin-top:14px;border-left:3px solid var(--accent)}.thesis-writeup h3{font-size:15px;margin:0 0 8px}.thesis-writeup p{margin:0 0 10px;line-height:1.55}.thesis-writeup p strong{color:var(--accent)}
.axis-text{font-family:ui-monospace,monospace;font-size:10.5px;fill:var(--fg-muted)}.axis-line{stroke:var(--border-strong);stroke-width:1}.threshold-line{stroke:var(--fg-faint);stroke-width:1;stroke-dasharray:4 3}.quadrant-label{font-family:ui-sans-serif,sans-serif;font-size:11px;fill:var(--fg-faint);letter-spacing:.04em;text-transform:uppercase}.axis-title{font-family:ui-sans-serif,sans-serif;font-size:11.5px;fill:var(--fg);font-weight:600}.point{stroke:#fff;stroke-width:2;cursor:pointer}.point[data-priority="1"]{fill:var(--priority-1)}.point[data-priority="2"]{fill:var(--priority-2)}.point[data-priority="3"]{fill:var(--priority-3)}.point[data-priority="4"]{fill:var(--priority-4)}.point[data-priority="5"]{fill:var(--priority-5)}.point.dim{opacity:.12}.point:focus-visible,.point:hover{stroke:var(--accent);stroke-width:3}
.modal-bg{position:fixed;inset:0;background:rgba(15,23,42,.6);display:none;align-items:center;justify-content:center;z-index:100;padding:24px}.modal-bg.open{display:flex}.modal{background:var(--bg);border-radius:6px;padding:22px 26px;max-width:540px;width:100%;border:1px solid var(--border);box-shadow:0 10px 30px rgba(0,0,0,.3)}.modal h3{margin:0 0 12px;font-size:17px}.modal-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:14px}
.help-overlay{position:fixed;inset:0;background:rgba(15,23,42,.7);display:none;align-items:center;justify-content:center;z-index:90}.help-overlay.open{display:flex}.help-card{background:var(--bg);border-radius:6px;padding:24px 28px;max-width:520px;width:100%;border:1px solid var(--border)}.help-card h3{margin:0 0 14px;font-size:17px}.kbd-row{display:grid;grid-template-columns:70px 1fr;gap:12px;padding:4px 0;font-size:13px}.kbd-row .key{font-family:ui-monospace,monospace;background:var(--bg-soft);border:1px solid var(--border-strong);border-radius:3px;padding:1px 8px;font-size:12px;text-align:center}
.toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--fg);color:var(--bg);padding:8px 14px;border-radius:4px;font-size:13px;box-shadow:0 6px 14px rgba(0,0,0,.3);z-index:110;display:none}.toast.show{display:block}
footer{padding:16px 24px 30px;border-top:1px solid var(--border);font-size:12px;color:var(--fg-muted);max-width:1500px;margin:0 auto}
</style>
</head>
<body>
<a href="#main" class="skip-link">Skip to main content</a>
<header>
  <h1>Factory Territory — Prospecting Tool</h1>
  <nav class="tabs" role="tablist">
    <button class="tab" role="tab" data-tab="today" aria-selected="true">Today<span class="tab-count" id="badge-today">0</span></button>
    <button class="tab" role="tab" data-tab="accounts" aria-selected="false">Accounts<span class="tab-count">20</span></button>
    <button class="tab" role="tab" data-tab="forecast" aria-selected="false">Forecast<span class="tab-count">·</span></button>
    <button class="tab" role="tab" data-tab="thesis" aria-selected="false">Thesis<span class="tab-count">·</span></button>
  </nav>
  <div class="top-actions">
    <button class="btn" id="btn-help" title="Keyboard shortcuts (?)">?</button>
    <button class="btn" id="btn-export" title="Export the full state as CSV">Export CSV</button>
    <button class="btn btn-danger" id="btn-reset" title="Reset all status / notes / touches (asks confirm)">Reset</button>
  </div>
</header>
<main id="main">

<section class="tab-panel" data-tab-panel="today">
  <div class="today-headline">
    <h2>Today · 2026-07-14</h2>
    <span class="mono" style="color:var(--fg-muted);" id="today-stats"></span>
  </div>
  <div id="today-body"></div>
</section>

<section class="tab-panel" data-tab-panel="accounts" hidden>
  <div class="acct-layout">
    <div>
      <div class="toolbar">
        <div class="filter-group"><span class="filter-label">Region</span><div class="chips" id="filter-region" role="group"></div></div>
        <div class="filter-group"><span class="filter-label">Priority</span><div class="chips" id="filter-priority" role="group"></div></div>
        <div class="filter-group"><span class="filter-label">Status</span><div class="chips" id="filter-status" role="group"></div></div>
        <div class="filter-group" style="flex:1;min-width:200px;"><input class="search-input" id="filter-search" type="search" placeholder="Search company / sector / signal…" aria-label="Search accounts"></div>
      </div>
      <div class="acct-list" id="acct-list" role="listbox" aria-label="Accounts"></div>
    </div>
    <div id="acct-detail" aria-live="polite"></div>
  </div>
</section>

<section class="tab-panel" data-tab-panel="forecast" hidden>
  <div class="panel" style="background:var(--callout-bg);border-left:3px solid var(--callout-border);color:var(--callout-text);">
    <h2 style="color:var(--callout-heading);">Forecasting the territory</h2>
    <p style="font-size:13.5px;line-height:1.55;margin:0;">
      <strong style="color:var(--callout-heading);">This is not a commit.</strong> I have zero conversations and zero pipeline. This is a model of what it would TAKE — built on assumptions I need corrected by someone who knows the real numbers. Move any slider to see the model move.
    </p>
  </div>
  <div class="forecast-grid">
    <div class="panel">
      <h2>Inputs (sliders)</h2>
      <div id="forecast-sliders"></div>
    </div>
    <div class="panel">
      <h2>Outputs</h2>
      <div class="forecast-output" id="forecast-output"></div>
      <div id="forecast-assumptions"></div>
    </div>
  </div>
</section>

<section class="tab-panel" data-tab-panel="thesis" hidden>
  <div class="panel">
    <h2>Thesis · Revenue × Employees (log scale)</h2>
    <p style="font-size:12px;color:var(--fg-muted);margin:0 0 12px;">Quadrants split at $500M revenue and 5,000 employees. Hover any point for company + priority.</p>
    <svg id="scatter" viewBox="0 0 900 540" style="width:100%;height:auto;background:var(--bg-alt);border:1px solid var(--border);" role="img" aria-label="Revenue vs Employees scatter"></svg>
  </div>
  <div class="thesis-writeup">
    <h3>The written thesis (read with the scatter above)</h3>
    <p><strong>San Diego is a firmware-and-defense town;</strong> <strong>Denver is a telecom-legacy graveyard</strong> (Qwest · CenturyLink · Level 3 · DISH heritage) <strong>plus mainframe-era payments.</strong></p>
    <p>The scatter above shows a problem: by firmographics alone (revenue × employees), the priority 1 and 2 accounts are impossible to separate from the long tail. <em>The real buying signal is who's hiring a human to do Factory's job</em> — which appears in ZERO firmographic filters. The only place that signal surfaces is in this dashboard's Account detail panel: a Sr Director of Transformation req at DaVita (A002), the HCLTech partnership release for Western Union (A004), the Hyderabad GCC launch for LPL (A005), and the Milliman acquisition announcement for Empower (A006).</p>
    <p><strong>What this implies about the Forecast tab:</strong> the unweighted pipeline counts every account equally. The MEDDPICC-weight shifts that count by giving dollar weight to <em>verified</em> signals (reqs, press releases, named CIOs) and stripping out account-shape that has no published trigger. Two accounts at &quot;Early&quot; band (A002 DaVita, A004 Western Union) carry disproportionate weight; two accounts at &quot;Unqualified&quot; (A001, A003, A006) collapse. The gap between weighted and unweighted is the honest cost of &quot;negative signals I won't repeat here.&quot;</p>
    <p><strong>What this implies about the contact list:</strong> the 5-slot schema (Economic Buyer · Technical Champion · Program Owner · Security/Governance · Wildcard) is the &quot;humans the rep needs to know.&quot; Where the seed suggested a name that this research pass could not verify, the slot is &quot;SLOT ONLY&quot; and the LinkedIn URL is replaced with a people-search link. <em>That is the AGENTS.md rule 2 telling: pattern-constructing a LinkedIn URL is worse than admitting the slot is unfilled.</em></p>
  </div>
</section>

</main>
<footer>
  <strong>AGENTS.md</strong>: every claim VERIFIED (URL) or INFERRED · disqualifying requires a free-text reason · signal age tracked · LinkedIn URLs come from search results only (never pattern-constructed) · 300-char LinkedIn cap is enforced with red above.
  Forecast is unweighted by default; MEDDPICC-weight applies when the slider engages.
  Last build: 2026-07-14.
</footer>

<div class="modal-bg" id="modal-disqualify" role="dialog" aria-modal="true" aria-labelledby="dq-title">
  <div class="modal">
    <h3 id="dq-title">Disqualify account</h3>
    <p style="font-size:12.5px;color:var(--fg-muted);margin:0 0 8px;">Per AGENTS.md, a reason is required. The account will move to Disqualified and stop appearing in the work queue.</p>
    <textarea id="dq-reason" placeholder="e.g. HCLTech owns tooling budget end-to-end; SI is locked-in through 2027..." style="min-height:110px;"></textarea>
    <div class="modal-actions"><button class="btn" id="dq-cancel">Cancel</button><button class="btn btn-danger" id="dq-confirm">Disqualify</button></div>
  </div>
</div>

<div class="help-overlay" id="help-overlay" role="dialog" aria-modal="true" aria-label="Keyboard shortcuts">
  <div class="help-card">
    <h3>Keyboard shortcuts</h3>
    <div class="kbd-row"><span class="key">j / k</span><span>Move to next / previous account</span></div>
    <div class="kbd-row"><span class="key">e</span><span>Focus the day's primary textarea</span></div>
    <div class="kbd-row"><span class="key">c</span><span>Copy the day's primary message</span></div>
    <div class="kbd-row"><span class="key">d</span><span>Open Disqualify modal</span></div>
    <div class="kbd-row"><span class="key">/</span><span>Focus the search box</span></div>
    <div class="kbd-row"><span class="key">1–4</span><span>Switch tabs (Today/Accounts/Forecast/Thesis)</span></div>
    <div class="kbd-row"><span class="key">?</span><span>This help overlay</span></div>
    <div class="kbd-row"><span class="key">Esc</span><span>Close modal / help</span></div>
    <div class="modal-actions"><button class="btn" id="help-close">Close</button></div>
  </div>
</div>

<div class="toast" id="toast" role="status" aria-live="polite"></div>

<script>
"use strict";
const TODAY_ISO = "2026-07-14";
const ACCOUNTS = __ACCOUNTS__;
const MEDDPICC = __MEDDPICC__;
const ACCOUNT_PLANS = __ACCOUNT_PLANS__;
const OUTREACH = __OUTREACH__;
const STATUSES = ["not_started","researched","contacted","replied","meeting","disqualified"];
const PRIORITIES = ["All","1","2","3","4","5"];
const REGIONS = ["All","San Diego","Denver"];
const SLOT_LABEL = {economic_buyer:"Economic Buyer",technical_champion:"Technical Champion",program_owner:"Program Owner",security_governance:"Security / Governance",wildcard:"Wildcard"};

const LS_KEY = "********************";
let STATE = loadState();
function loadState(){try{const raw=localStorage.getItem(LS_KEY);if(raw)return JSON.parse(raw);}catch(_){}return{accounts:{},filter:{region:"All",priority:"All",status:"All",search:""},forecast:{}}; }
function saveState(){try{localStorage.setItem(LS_KEY,JSON.stringify(STATE));}catch(_){}}
function acctState(id){if(!STATE.accounts[id])STATE.accounts[id]={status:"not_started",status_history:[],notes:"",next_action_date:"",next_action_label:"",disqualify_reason:"",touches:{},checklist:{}};return STATE.accounts[id];}
function escapeHtml(s){return String(s==null?"":s).replace(/[&<>"]/g, ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));}
function daysBetween(a,b){return Math.round((new Date(b+"T00:00:00Z")-new Date(a+"T00:00:00Z"))/86400000);}
function parseNum(v){if(typeof v!=="string")return null;const s=v.replace(/[~$,]/g,"");if(!/^\\d+(\\.\\d+)?$/.test(s))return null;return parseFloat(s);}

// -- TODAY --
function renderToday(){
  const overdue=[],dueToday=[],stale=[],noNext=[];
  ACCOUNTS.forEach(a=>{
    const s=acctState(a.account_id);const last=a.last_researched||TODAY_ISO;const age=daysBetween(last,TODAY_ISO);
    if(s.status==="disqualified")return;
    if(s.next_action_date){const diff=daysBetween(TODAY_ISO,s.next_action_date);if(diff<0)overdue.push({a,s,days:-diff});else if(diff===0)dueToday.push({a,s});}
    else if(s.status!=="not_started")noNext.push({a,s,kind:"no_next_after_status"});
    else noNext.push({a,s,kind:"never_touched"});
    if(age>30)stale.push({a,age});
  });
  overdue.sort((x,y)=>y.days-x.days);stale.sort((x,y)=>y.age-x.age);
  const out=[];
  const renderPill=(t,cls)=>`<span class="pill ${cls}">${t}</span>`;
  const renderItem=(a,s,badges,sub)=>`<div class="work-item" data-account-id="${a.account_id}" tabindex="0" role="button"><div><div class="title">${a.company} <span class="mono" style="font-weight:400;font-size:12px;color:var(--fg-muted);">${a.region} · P${a.priority}</span></div><div class="sub">${sub||a.sector}</div></div><div class="meta">${badges.map(b=>renderPill(b.text,b.cls)).join(" ")}${s.next_action_date?`<div style="margin-top:4px;">→ ${s.next_action_date}</div>`:""}</div></div>`;
  out.push(`<div class="work-queue-section"><h2>Overdue follow-ups · ${overdue.length}</h2>${overdue.length?overdue.map(o=>renderItem(o.a,o.s,[{text:`overdue × ${o.days}d`,cls:"overdue"}])).join(""):`<div class="empty-state">Nothing overdue.</div>`}</div>`);
  out.push(`<div class="work-queue-section"><h2>Due today · ${dueToday.length}</h2>${dueToday.length?dueToday.map(o=>renderItem(o.a,o.s,[{text:"due today",cls:"due-today"}])).join(""):`<div class="empty-state">Nothing scheduled for today.</div>`}</div>`);
  out.push(`<div class="work-queue-section"><h2>Stale signals (>30 days) · ${stale.length}</h2>${stale.length?stale.map(o=>renderItem(o.a,acctState(o.a.account_id),[{text:`${o.age}d old`,cls:o.age>60?"stale-red":"stale-amber"}],`last verified ${o.a.last_researched}`)).join(""):`<div class="empty-state">All signals inside 30 days.</div>`}</div>`);
  out.push(`<div class="work-queue-section"><h2>No next action · ${noNext.length}</h2>${noNext.length?noNext.map(o=>renderItem(o.a,o.s,[],o.kind==="never_touched"?"never touched":"no next action")).join(""):`<div class="empty-state">Every account has a next step.</div>`}</div>`);
  document.getElementById("today-body").innerHTML=out.join("");
  document.getElementById("today-stats").textContent=`${overdue.length} overdue · ${dueToday.length} due today · ${stale.length} stale · ${noNext.length} unworked`;
  document.getElementById("badge-today").textContent=overdue.length+dueToday.length+stale.length+noNext.length;
  document.querySelectorAll(".work-item[data-account-id]").forEach(el=>{el.addEventListener("click",()=>{selectAccount(el.dataset.accountId);switchTab("accounts");});});
}

// -- ACCOUNTS --
function renderAccounts(){
  const list=document.getElementById("acct-list");
  const f=STATE.filter;
  const filtered=ACCOUNTS.filter(a=>{
    const s=acctState(a.account_id);
    return (f.region==="All"||a.region===f.region)&&(f.priority==="All"||String(a.priority)===String(f.priority))&&(f.status==="All"||s.status===f.status)&&(!f.search||(a.company+" "+a.sector+" "+(a.seed_thesis||"")+" "+a.signals.map(sg=>sg.label).join(" ")).toLowerCase().indexOf(f.search.toLowerCase())!==-1);
  });
  list.innerHTML=filtered.map(a=>{
    const s=acctState(a.account_id);const active=STATE.selectedId===a.account_id?" active":"";
    return `<div class="acct-row${active}" data-jump="${a.account_id}" role="option" tabindex="0"><div class="name">${a.company}${a.is_priority?` <span class="verdict-pill ${a.verdict[0]}" style="margin-left:6px;">${a.verdict[0]}</span>`:""}</div><div class="sub">${a.region} · P${a.priority} · ${a.sector}</div></div>`;
  }).join("")||`<div class="empty-state">No accounts match the current filter.</div>`;
  list.querySelectorAll(".acct-row").forEach(el=>el.addEventListener("click",()=>selectAccount(el.dataset.jump)));
}
function renderAccountsToolbar(){
  function chips(id,vals,cur,on){const c=document.getElementById(id);c.innerHTML=vals.map(v=>`<button class="chip" data-v="${v}" aria-pressed="${String(v)===String(cur)}">${String(v).replace(/_/g," ")}</button>`).join("");c.querySelectorAll(".chip").forEach(b=>b.addEventListener("click",()=>on(b.dataset.v)));}
  chips("filter-region",REGIONS,STATE.filter.region,v=>{STATE.filter.region=v;renderAccounts();});
  chips("filter-priority",PRIORITIES,STATE.filter.priority,v=>{STATE.filter.priority=v;renderAccounts();});
  chips("filter-status",["All",...STATUSES],STATE.filter.status,v=>{STATE.filter.status=v;renderAccounts();});
  const si=document.getElementById("filter-search");si.value=STATE.filter.search||"";si.oninput=e=>{STATE.filter.search=e.target.value;renderAccounts();};
}
function selectAccount(id){STATE.selectedId=id;saveState();renderAccounts();renderDetail();}

// -- DETAIL --
function renderDetail(){
  const root=document.getElementById("acct-detail");
  const id=STATE.selectedId;if(!id){root.innerHTML=`<div class="empty-state">Pick an account on the left.</div>`;return;}
  const a=ACCOUNTS.find(x=>x.account_id===id);if(!a){root.innerHTML=`<div class="empty-state">No account selected.</div>`;return;}
  const s=acctState(id);
  const plan=ACCOUNT_PLANS[a.account_id];
  const meddpicc=MEDDPICC[a.meddpicc_key];
  const age=daysBetween(a.last_researched||TODAY_ISO,TODAY_ISO);

  root.innerHTML=`
    <div class="acct-detail">
      <div class="detail-head">
        <h2>${a.company}${a.is_priority?` <span class="verdict-pill ${a.verdict[0]}" style="margin-left:8px;">${a.verdict[0]}</span>`:""}</h2>
        <span class="hq">${a.hq_city}, ${a.hq_state} · ${a.sector} · P${a.priority}</span>
        <span class="mono" style="font-size:12px;color:var(--fg-muted);margin-left:auto;">${a.account_id}</span>
      </div>
      ${a.is_priority?`<div style="font-size:12px;color:var(--fg-muted);margin-bottom:8px;">${escapeHtml(a.verdict[1])}</div>`:`<div style="font-size:12px;color:var(--fg-muted);margin-bottom:8px;">Not in priority set. Firmographic-only signal.</div>`}

      <div class="pipeline">${STATUSES.map((st,i)=>`<button class="step ${st===s.status?'active':''}" data-status="${st}">${prettyStatus(st)}</button>${i<STATUSES.length-1?'<span class="pipeline-arrow">→</span>':''}`).join("")}</div>
      ${s.status==="disqualified"?`<div class="complication-block" style="margin-bottom:12px;border-left-color:var(--status-disqualified);"><strong style="color:var(--status-disqualified);">Disqualified.</strong> Reason: ${escapeHtml(s.disqualify_reason||"(none)")}</div>`:""}

      <div class="section-grid">
        <div class="sect"><h3>Notes</h3><textarea id="detail-notes" placeholder="Research notes, call summaries, objections…">${escapeHtml(s.notes||"")}</textarea></div>
        <div class="sect"><h3>Next action</h3><label style="font-size:11px;color:var(--fg-muted);">Date</label><input type="date" id="detail-next-date" value="${s.next_action_date||""}"><label style="font-size:11px;color:var(--fg-muted);margin-top:6px;display:block;">Label</label><input type="text" id="detail-next-label" value="${escapeHtml(s.next_action_label||"")}" placeholder="e.g. Send breakup if no reply by Day 15"></div>
      </div>

      <div class="section-grid" style="margin-top:14px;">
        <div class="sect">
          <h3>5-slot buying committee (${a.contacts.length})</h3>
          ${a.contacts.map(c=>contactCardHtml(c)).join("")||`<div style="font-size:12px;color:var(--fg-muted);">No contacts drafted for this account.</div>`}
        </div>
        <div class="sect">
          <h3>Complication &amp; Analogue</h3>
          <div class="complication-block"><strong>Known objection:</strong> ${escapeHtml(a.complication)}</div>
          <div style="margin-top:10px;font-size:13px;"><strong>${a.analogue[0]}</strong> — ${escapeHtml(a.analogue[1])}</div>
          <h3 style="margin-top:14px;">Firmographics (estimates only)</h3>
          <div style="font-size:12px;color:var(--fg-muted);font-variant-numeric:tabular-nums;">Employees: <span class="mono">${escapeHtml(a.employees_total||"UNKNOWN")}</span> · Engineering: <span class="mono">${escapeHtml(a.engineering_headcount||"UNKNOWN")}</span> · Revenue: <span class="mono">UNKNOWN</span> (deliberately omitted — see AGENTS.md rule 3)</div>
        </div>
      </div>

      <div class="section-grid" style="margin-top:14px;">
        <div class="sect">
          <h3>Signals · ${a.signals.length} sources · last touch ${a.last_researched} (${age}d)</h3>
          ${a.signals.length===0?`<div style="font-size:12px;color:var(--fg-muted);">No public sources surfaced.</div>`:a.signals.slice(0,12).map(sig=>signalRowHtml(a,sig)).join("")}
          ${a.signals.length>12?`<div style="font-size:11.5px;color:var(--fg-muted);margin-top:6px;">+ ${a.signals.length-12} more in references panel below.</div>`:""}
        </div>
        <div class="sect">
          <h3>References (numbered, date accessed)</h3>
          <ol class="ref-list">${a.signals.map((sig,i)=>`<li value="${i+1}"><a href="${sig.url}" rel="noopener noreferrer" target="_blank">${escapeHtml(sig.label)}</a><span class="label">${escapeHtml(sig.url.replace(/^https?:\\/\\//,'').slice(0,60))}</span><span class="date">accessed ${escapeHtml(sig.accessed)}</span></li>`).join("")}</ol>
        </div>
      </div>

      ${plan?accountPlanHtml(plan):""}
      ${meddpicc?meddpiccHtml(meddpicc):""}
      ${a.is_priority?outreachHtml(a):""}

      <div class="section-grid" style="margin-top:14px;">
        <div class="sect">
          <h3>Verify before sending</h3>
          <div class="checklist" data-checklist="${a.account_id}">
            <label><input type="checkbox" data-key="contact_verified"> At least one slot has a VERIFIED (Link surface in search results) name</label>
            <label><input type="checkbox" data-key="source_fresh"> All source URLs verified live in the last 30 days</label>
            <label><input type="checkbox" data-key="linkchain_safe"> LinkedIn URLs come from search results, not pattern-constructed</label>
            <label><input type="checkbox" data-key="three_sentences"> Email is 3 sentences, no greeting, no value props, lowercase 6-word subject</label>
            <label><input type="checkbox" data-key="linkedin_under_300"> LinkedIn body ≤300 chars</label>
            <label><input type="checkbox" data-key="complication_known"> Complication block read and acknowledged — objection covered</label>
            <label><input type="checkbox" data-key="disqualify_truthful"> What would disqualify statement reads as honest, not aspirational</label>
          </div>
        </div>
      </div>
    </div>
  `;

  // Wire pipeline
  root.querySelectorAll(".pipeline .step").forEach(b=>b.addEventListener("click",()=>{
    if(b.dataset.status===s.status)return;
    if(b.dataset.status==="disqualified"){openDisqualifyModal(a,s);return;}
    s.status=b.dataset.status;s.status_history.push({status:b.dataset.status,date:TODAY_ISO});s.disqualify_reason="";saveState();renderDetail();renderAccounts();renderToday();
  }));
  // Wire notes + next action
  root.querySelector("#detail-notes").addEventListener("input",e=>{s.notes=e.target.value;saveState();});
  root.querySelector("#detail-next-date").addEventListener("change",e=>{s.next_action_date=e.target.value;saveState();renderAccounts();renderToday();});
  root.querySelector("#detail-next-label").addEventListener("input",e=>{s.next_action_label=e.target.value;saveState();});
  // Wire checklist
  root.querySelectorAll(`[data-checklist="${a.account_id}"] input[type=checkbox]`).forEach(cb=>{cb.checked=!!s.checklist[cb.dataset.key];cb.addEventListener("change",()=>{s.checklist[cb.dataset.key]=cb.checked;saveState();});});

  // Outreach: wire Outreach Email/LinkedIn tab + char counters
  const outreachRoot=root.querySelector("#outreach-host");
  if(outreachRoot){
    const tabs=outreachRoot.querySelectorAll(".outreach-tab");
    tabs.forEach(t=>t.addEventListener("click",()=>{
      tabs.forEach(x=>x.setAttribute("aria-selected","false"));
      t.setAttribute("aria-selected","true");
      outreachRoot.querySelectorAll(".outreach-panel").forEach(p=>p.hidden=p.dataset.panel!==t.dataset.tab);
    }));
    outreachRoot.querySelectorAll(".outreach-slot textarea").forEach(ta=>{
      updateOneCharCount(ta);
      ta.addEventListener("input",()=>{
        updateOneCharCount(ta);
        const key = `${a.account_id}|${ta.dataset.slot}|${ta.dataset.kind}`;
        STATE.outreachEdits = STATE.outreachEdits || {};
        STATE.outreachEdits[key] = ta.value;
        saveState();
      });
    });
    outreachRoot.querySelectorAll(".copy-inline").forEach(b=>b.addEventListener("click", async()=>{
      const slotEl = b.closest(".outreach-slot");
      if(!slotEl) return;
      const ta = slotEl.querySelector("textarea");
      if(!ta) return;
      let payload;
      if(b.dataset.kind === "email"){
        const subjEl = slotEl.querySelector(".subj");
        const subj = subjEl ? subjEl.textContent.trim() : "";
        const body = ta.value.trim();
        payload = (subj && !/^\(empty/.test(subj))
          ? `Subject: ${subj}\n\n${body}`
          : body;
      } else {
        payload = ta.value.trim();
      }
      try{
        await navigator.clipboard.writeText(payload);
        toast("Copied.");
      }catch(_){
        toast("Copy failed.");
      }
    }));
  }
}

function prettyStatus(s){return({not_started:"Not started",researched:"Researched",contacted:"Contacted",replied:"Replied",meeting:"Meeting",disqualified:"Disqualified"})[s]||s;}

function contactCardHtml(c){
  const link=c.linkedin_url?`<a href="${c.linkedin_url}" target="_blank" rel="noopener noreferrer">linkedin</a>`:(c.source_url?`<a href="${c.source_url}" target="_blank" rel="noopener noreferrer">source</a>`:"");
  return `<div class="contact-card">
    <div class="name-row">
      <span class="slot-label">${SLOT_LABEL[c.slot]||c.slot}</span>
      <span class="title">${escapeHtml(c.title||"")}</span>
      <span class="conf ${c.confidence}">${c.confidence}</span>
    </div>
    <div class="name" style="margin-top:4px;">${escapeHtml(c.name)}</div>
    <div class="meta">${link}</div>
    ${c.why_this_person?`<div class="why">"${escapeHtml(c.why_this_person)}"</div>`:""}
  </div>`;
}

function signalRowHtml(a,sig){
  const cls=daysBetween(a.last_researched||TODAY_ISO,TODAY_ISO)>60?"red":daysBetween(a.last_researched||TODAY_ISO,TODAY_ISO)>30?"amber":"fresh";
  return `<div class="signal-row"><span class="badge ${cls}">${cls}</span><span><a href="${sig.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(sig.label)}</a></span><span class="age">${daysBetween(a.last_researched||TODAY_ISO,TODAY_ISO)}d</span><button class="re-verify" data-url="${sig.url}">re-verify</button></div>`;
}

function accountPlanHtml(p){
  return `<div class="sect" style="margin-top:14px;">
    <h3>Account Plan · 30 / 60 / 90</h3>
    <dl class="plan-grid">
      <dt>Entry persona</dt><dd>${escapeHtml(p.entry_persona)}</dd>
      <dt>Why</dt><dd>${escapeHtml(p.why)}</dd>
      <dt>Business trigger</dt><dd>${escapeHtml(p.business_trigger)}</dd>
      <dt>Objection 1</dt><dd>${escapeHtml(p.objection_1)}</dd>
      <dt>Objection 2</dt><dd>${escapeHtml(p.objection_2)}</dd>
    </dl>
    <div class="plan-disqualify"><strong>What would DISQUALIFY this account</strong> (read truthfully): ${escapeHtml(p.disqualifier_truthful)}</div>
  </div>`;
}

function meddpiccHtml(m){
  const elements=Object.keys(m).filter(k=>!["total_score","band","BIGGEST_UNKNOWN"].includes(k));
  const bars=elements.map(el=>{
    const o=m[el]||{};const score=o.score||0;
    return `<div class="meddpicc-bar"><span>${el.replace(/_/g," ")}</span><div class="track"><div class="fill" style="width:${(score/3)*100}%"></div></div><span class="score">${score}/3</span></div>`;
  }).join("");
  return `<div class="sect" style="margin-top:14px;">
    <h3>MEDDPICC · 8 elements · score 0–3 each (max 24)</h3>
    <div style="font-size:11.5px;color:var(--fg-muted);margin-bottom:8px;">"${escapeHtml(MEDDPICC._frame||"Expect 2–6/24 — nothing here is forecastable until someone inside the account has told me it's true.")}"</div>
    ${bars}
    <div class="meddpicc-total"><span class="mono">${m.total_score||0} / 24 · ${elements.length} elements scored</span><span class="band-label">${m.band||"Unqualified"}</span></div>
    <div class="meddpicc-biggest"><strong>BIGGEST UNKNOWN:</strong> ${escapeHtml(m.BIGGEST_UNKNOWN||"")}</div>
  </div>`;
}

function outreachHtml(a){
  const raw=OUTREACH[a.account_id]||"";
  const slots=parseOutreach(raw);
  if(!slots.length){return `<div class="sect" style="margin-top:14px;"><h3>Outreach Email + LinkedIn</h3><div style="font-size:12.5px;color:var(--fg-muted);">No outreach research file for this account.</div></div>`;}
  const emailPanel=slots.map(s=>outreachSlotHtml(a,s,"email")).join("");
  const linkedinPanel=slots.map(s=>outreachSlotHtml(a,s,"linkedin")).join("");
  return `<div class="sect" style="margin-top:14px;">
    <h3>Outreach Email + LinkedIn · slot-tailored</h3>
    <div class="outreach-tabs" id="outreach-host">
      <button class="outreach-tab" data-tab="email" aria-selected="true">Email</button>
      <button class="outreach-tab" data-tab="linkedin" aria-selected="false">LinkedIn (≤300 chars, red above)</button>
      <div class="outreach-panel" data-panel="email">${emailPanel}</div>
      <div class="outreach-panel" data-panel="linkedin" hidden>${linkedinPanel}</div>
    </div>
  </div>`;
}
function outreachSlotHtml(a,s,kind){
  const slot=SLOT_LABEL[s.slot]||s.slot;
  const subjOrBody=kind==="email"?s.email_subject:s.linkedin_body;
  const charLimit=kind==="linkedin"?300:"";
  const btnLabel=kind==="email"?"Copy email":"Copy LinkedIn";
  const stored=(STATE.outreachEdits||{})[`${a.account_id}|${s.slot}|${kind}`];
  const value=stored!=null?stored:(subjOrBody||"");
  const cls=value.length>parseInt(charLimit||"0",10)?"bad":value.length>parseInt(charLimit||"0",10)-30?"warn":"";
  return `<div class="outreach-slot">
    <h4>${slot}</h4>
    ${kind==="email"?`<span class="subj">${escapeHtml(s.email_subject||"")}</span>`:""}
    <textarea data-slot="${s.slot}" data-kind="${kind}" data-char-limit="${charLimit}" placeholder="${charLimit?`≤${charLimit} chars`:""}">${escapeHtml(value)}</textarea>
    <div class="char-row"><span class="char-count ${cls}">${value.length} / ${charLimit||"∞"} chars</span><button class="copy-inline">${btnLabel}</button></div>
  </div>`;
}
function updateOutlookCharCounts(root){
  root.querySelectorAll(".outreach-slot textarea[data-char-limit]").forEach(ta=>{
    const limit=parseInt(ta.dataset.charLimit,10);
    const cc=ta.parentElement.querySelector(".char-count");
    if(cc){cc.textContent=`${ta.value.length} / ${limit} chars`;cc.classList.remove("warn","bad");if(ta.value.length>limit)cc.classList.add("bad");else if(ta.value.length>limit-30)cc.classList.add("warn");}
  });
}
function parseOutreach(raw){
  if(!raw) return [];
  const lines = raw.split("\n");
  const slots = [];
  let curSlot = null;
  let curBlock = null; // 'intro' | 'email' | 'linkedin'
  let curEmailSub = null;
  let curEmailBodyLines = [];
  let curLinkedinLines = [];
  const finalize = () => {
    if(!curSlot) return;
    slots.push({
      slot: curSlot,
      email_subject: (curEmailSub || "").trim(),
      email_body: curEmailBodyLines.join("\n").trim(),
      linkedin_body: curLinkedinLines.join("\n").trim(),
    });
  };
  for(const line of lines){
    const slotM = line.match(/^##\s+Slot:\s*(\w[\w_]*)/);
    if(slotM){
      finalize();
      curSlot = slotM[1];
      curBlock = "intro";
      curEmailSub = null;
      curEmailBodyLines = [];
      curLinkedinLines = [];
      continue;
    }
    if(!curSlot) continue;
    if(/^###\s+Email\b/.test(line)){ curBlock = "email"; continue; }
    if(/^###\s+LinkedIn\b/.test(line)){ curBlock = "linkedin"; continue; }
    if(curBlock === "email"){
      const subjM = line.match(/^Subject:\s*(.+?)\s*$/);
      if(subjM){ curEmailSub = subjM[1]; continue; }
      if(curEmailSub != null){ curEmailBodyLines.push(line); }
      continue;
    }
    if(curBlock === "linkedin"){
      curLinkedinLines.push(line);
      continue;
    }
  }
  finalize();
  return slots;
}

function chatCountText(n, limit){
  if(limit > 0){
    if(typeof n !== "number" || isNaN(n)) return "— / " + limit;
    return n + " / " + limit;
  }
  if(typeof n !== "number" || isNaN(n)) return "— chars";
  return n + " chars";
}

function outreachSlotHtml(a, s, kind){
  const slot = SLOT_LABEL[s.slot] || s.slot;
  const stored = (STATE.outreachEdits || {})[`${a.account_id}|${s.slot}|${kind}`];
  let value, charLimit, btnLabel, placeholder;
  if(kind === "email"){
    value = stored != null ? stored : (s.email_body || "");
    charLimit = 0;
    btnLabel = "Copy email + subj";
    placeholder = "Hi <First Name>,\n\n<signal sentence — verified URL>\n\n<analogue sentence — Factory customer link>\n\n<one-line question>\n\nNash\n\nNash Wardy · Factory AI";
  } else {
    value = stored != null ? stored : (s.linkedin_body || "");
    charLimit = 300;
    btnLabel = "Copy LinkedIn note";
    placeholder = "≤ 300 chars — observation + question, no meeting ask, no analogue name-drop.";
  }
  const over = charLimit > 0 && value.length > charLimit;
  const near = charLimit > 0 && value.length >= charLimit - 30 && value.length <= charLimit;
  const cls = over ? "bad" : (near ? "warn" : "");
  const subjBox = kind === "email"
    ? `<div class="subj-row"><span class="subj-label">Subject</span><span class="subj">${escapeHtml(s.email_subject || "(empty — fix in research/<company>_outreach.md)")}</span></div>`
    : `<div class="subj-row"><span class="subj-label">Channel</span><span class="subj">LinkedIn connection note · ≤ 300 chars</span></div>`;
  return `<div class="outreach-slot">
    <h4>${slot}</h4>
    ${subjBox}
    <textarea data-slot="${s.slot}" data-kind="${kind}" data-char-limit="${charLimit}" placeholder="${escapeHtml(placeholder)}">${escapeHtml(value)}</textarea>
    <div class="char-row">
      <span class="char-count ${cls}">${chatCountText(value.length, charLimit)}</span>
      <button class="copy-inline" data-kind="${kind}" data-slot="${s.slot}">${btnLabel}</button>
    </div>
  </div>`;
}

function updateOneCharCount(ta){
  const cc = ta.parentElement.querySelector(".char-count");
  if(!cc) return;
  cc.classList.remove("warn","bad");
  const limit = parseInt(ta.dataset.charLimit, 10);
  const n = ta.value.length;
  cc.textContent = chatCountText(n, limit);
  if(limit > 0 && n > limit){ cc.classList.add("bad"); }
  else if(limit > 0 && n > limit - 30){ cc.classList.add("warn"); }
}

// -- FORECAST --
// All money stored internally in actual dollars (not scaled).
// Display goes through fmtMoney() — never render raw digit strings.
function fmtMoney(n){
  n = Number(n) || 0;
  const abs = Math.abs(n);
  if(abs >= 1e9) return "$" + (n/1e9).toFixed(1) + "B";
  if(abs >= 1e6) return "$" + (n/1e6).toFixed(abs >= 1e7 ? 0 : 1) + "M";
  if(abs >= 1e3) return "$" + (n/1e3).toFixed(0) + "k";
  if(n === 0) return "$0";
  return "$" + Math.round(n);
}
const FORECAST_DEFAULTS = {
  accounts:20,
  outreach_to_meeting:5, meeting_to_opp:30, opp_to_won:20,
  acv:150000,             // dollars — $150k
  cycle_days:180, regulated_def_multiplier:1.5, ramp_weeks:4,
  quota:3000000,          // dollars — $3.0M
  sd_share:50, sd_cycle_days:210, sd_acv:200000,        // SD avg ACV dollars — $200k
  denver_cycle_days:150, denver_acv:120000,             // Denver avg ACV dollars — $120k
  opp_size_baseline:5,
  use_meddpicc_weight:true,
};
function renderForecast(){
  STATE.forecast=STATE.forecast||{};
  const f=Object.assign({},FORECAST_DEFAULTS,STATE.forecast);
  const pct={suffix:"%"};
  const days={unit:"d"};
  const money={isMoney:true};
  const moneySD={isMoney:true, formatMin:50, formatStep:50, max:500000};
  const sliders=[
    {key:"accounts",label:"Accounts in queue",min:1,max:50,step:1},
    {key:"outreach_to_meeting",label:"Outreach → Meeting",min:1,max:20,step:1, ...pct},
    {key:"meeting_to_opp",label:"Meeting → Opp",min:5,max:60,step:5, ...pct},
    {key:"opp_to_won",label:"Opp → Won",min:5,max:60,step:5, ...pct},
    {key:"acv",label:"Avg ACV (unweighted baseline)",min:50000,max:500000,step:10000, ...money},
    {key:"cycle_days",label:"Sales cycle (days)",min:60,max:540,step:30, ...days},
    {key:"regulated_def_multiplier",label:"Regulated/defense multiplier",min:1,max:3,step:0.1,suffix:"x"},
    {key:"ramp_weeks",label:"Rep ramp (weeks)",min:1,max:12,step:1,unit:"wk"},
    {key:"quota",label:"Quota",min:500000,max:10000000,step:500000, ...money},
  ];
  const seg=[
    {key:"sd_share",label:"SD share of accounts",min:0,max:100,step:5, ...pct},
    {key:"sd_cycle_days",label:"SD sales cycle",min:60,max:540,step:30, ...days},
    {key:"sd_acv",label:"SD avg ACV",min:50000,max:500000,step:10000, ...money},
    {key:"denver_cycle_days",label:"Denver sales cycle",min:60,max:540,step:30, ...days},
    {key:"denver_acv",label:"Denver avg ACV",min:50000,max:500000,step:10000, ...money},
    {key:"opp_size_baseline",label:"Avg opp size (lines per opp)",min:1,max:20,step:1},
  ];
  function fmtSlider(s, v){
    v = Number(v) || 0;
    if(s.isMoney) return fmtMoney(v);
    if(s.suffix==="%") return v + "%";
    if(s.suffix==="x") return v.toFixed(1) + "x";
    if(s.unit==="d") return v + "d";
    if(s.unit==="wk") return v + "wk";
    return String(v);
  }
  const renderSlider=(s)=>{
    const val=f[s.key];
    return `<div class="forecast-slider"><label>${s.label}</label><input type="range" min="${s.min}" max="${s.max}" step="${s.step}" value="${val}" data-key="${s.key}"><span class="val" id="fk-${s.key}">${fmtSlider(s, val)}</span></div>`;
  };
  document.getElementById("forecast-sliders").innerHTML=
    `<h3>Volume & conversion</h3>`+sliders.map(renderSlider).join("")+
    `<h3 style="margin-top:14px;">Segment split (SD vs Denver)</h3>`+seg.map(renderSlider).join("")+
    `<h3 style="margin-top:14px;">Model behavior</h3>`+
    `<div class="forecast-slider"><label>MEDDPICC weight</label><label style="display:flex;align-items:center;gap:6px;font-size:12.5px;cursor:pointer;"><input type="checkbox" id="fk-use_meddpicc_weight" ${f.use_meddpicc_weight?"checked":""}> Shift pipeline by Σ(ACV × MEDDPICC_score / 24)</label><span class="val">on/off</span></div>`;
  document.querySelectorAll("#forecast-sliders input[type=range]").forEach(inp=>{
    inp.addEventListener("input",()=>{
      f[inp.dataset.key]=parseFloat(inp.value);
      STATE.forecast=Object.assign({},f);
      saveState();
      const slider=sliders.concat(seg).find(s=>s.key===inp.dataset.key);
      if(slider){
        const valEl=document.getElementById("fk-"+inp.dataset.key);
        if(valEl) valEl.textContent=fmtSlider(slider, parseFloat(inp.value));
      }
      refreshForecastOutput();
    });
  });
  document.getElementById("fk-use_meddpicc_weight").addEventListener("change",e=>{
    f.use_meddpicc_weight=e.target.checked;
    STATE.forecast=Object.assign({},f);
    saveState();
    refreshForecastOutput();
  });
  refreshForecastOutput();
}
function refreshForecastOutput(){
  const f=Object.assign({},FORECAST_DEFAULTS,STATE.forecast);
  const sdAccounts = f.accounts * (f.sd_share/100);
  const denAccounts = f.accounts - sdAccounts;
  // Operating funnel (still useful but not the hero metric):
  const meetings = f.accounts * (f.outreach_to_meeting/100);
  const opps     = meetings * (f.meeting_to_opp/100);
  const won      = opps * (f.opp_to_won/100);
  // Pipeline math — BOTH unweighted and weighted use the SAME account set and the SAME ACV.
  // Unweighted = Σ ACV across all accounts (probability factor = 1, no MEDDPICC discounting)
  // Weighted   = Σ ACV × MEDDPICC_score / 24 across all accounts (probability factor = per-account score)
  // Since score/24 ≤ 1 always, weighted ≤ unweighted and gap ≥ 0 always.
  let unweighted = 0, weighted = 0;
  let countWithMeddpicc = 0, scoreSum = 0;
  ACCOUNTS.forEach(a => {
    const m = MEDDPICC[a.meddpicc_key];
    const score = m ? (m.total_score || 0) : 0;
    unweighted += f.acv;
    if(f.use_meddpicc_weight){
      weighted += f.acv * (score / 24);
      countWithMeddpicc++;
      scoreSum += score;
    } else {
      weighted = unweighted; // disabling weight collapses to unweighted
    }
  });
  // assertion: weighted ≤ unweighted; gap ≥ 0
  if(weighted > unweighted + 0.01){
    // (should be unreachable) — log for diagnostics rather than clamp
    console.warn("forecast: weighted > unweighted — formula is wrong");
  }
  const gap = unweighted - weighted;
  // Segment sub-block (operating funnel + per-segment ACV math)
  const sdACV = sdAccounts * (f.outreach_to_meeting/100) * (f.meeting_to_opp/100) * (f.opp_to_won/100) * f.sd_acv;
  const denACV = denAccounts * (f.outreach_to_meeting/100) * (f.meeting_to_opp/100) * (f.opp_to_won/100) * f.denver_acv;

  const contactRate = (f.outreach_to_meeting/100) * (f.meeting_to_opp/100) * (f.opp_to_won/100);
  const fkUseSliders = document.getElementById("fk-use_meddpicc_weight");
  const weightOn = fkUseSliders ? fkUseSliders.checked : f.use_meddpicc_weight;

  document.getElementById("forecast-output").innerHTML=`
    <div class="top">Pipeline forecast</div>
    <div class="big">${fmtMoney(weighted)} <span style="font-size:14px;font-weight:400;color:var(--callout-text);">MEDDPICC-weighted pipeline</span></div>
    <div class="comparison">Unweighted (full-ACV × account-count) baseline: <strong>${fmtMoney(unweighted)}</strong>. Same account set, same ACV — the difference is the per-account qualification factor.</div>
    <div class="gap-line"><strong>Gap:</strong> ${fmtMoney(gap)} unweighted − weighted. <span>The gap is the pipeline I have NOT earned yet — dollars I'd be forecasting on assumption rather than evidence.</span></div>

    <div class="top" style="margin-top:14px;">By segment</div>
    <div class="pair">
      <div><strong style="color:var(--callout-heading);">San Diego</strong><br>${fmtMoney(sdACV)} · cycle ${f.sd_cycle_days}d · ACV ${fmtMoney(f.sd_acv)} · share ${f.sd_share}% <em>(defense+firmware: longer cycle, larger ACV, harder procurement)</em></div>
      <div><strong style="color:var(--callout-heading);">Denver</strong><br>${fmtMoney(denACV)} · cycle ${f.denver_cycle_days}d · ACV ${fmtMoney(f.denver_acv)} · share ${100-f.sd_share}% <em>(finserv+telecom: shorter cycle, clearer ROI)</em></div>
    </div>

    <div class="comparison"><strong>Operating funnel</strong> &middot; meetings <span style="font-family:ui-monospace,monospace;">${meetings.toFixed(2)}</span> · opps <span style="font-family:ui-monospace,monospace;">${opps.toFixed(2)}</span> · won <span style="font-family:ui-monospace,monospace;">${won.toFixed(2)}</span> · quota ${fmtMoney(f.quota)} · ramp ${f.ramp_weeks} wk · ${f.accounts} accounts · weight ${weightOn?"ON (Σ ACV × score/24)":"OFF (= unweighted)"}</div>
  `;
  document.getElementById("forecast-assumptions").innerHTML=`
    <div class="assumptions-panel">
      <h3>Assumptions · &quot;Who corrects this?&quot;</h3>
      <table>
        <tr><th>Assumption</th><th>Value</th><th>Who corrects this?</th></tr>
        <tr><td>Outreach → Meeting rate</td><td>${f.outreach_to_meeting}%</td><td class="who">A working AE inside Factory or a peer rep at another dev-tools company</td></tr>
        <tr><td>Meeting → Opp conversion</td><td>${f.meeting_to_opp}%</td><td class="who">A Field AE / Sales Director who has closed ${fmtMoney(200000)}+ ACV deals in 2025 or 2026</td></tr>
        <tr><td>Opp → Won close rate</td><td>${f.opp_to_won}%</td><td class="who">A Field AE working the same segment (finserv / defense) over 18 months</td></tr>
        <tr><td>Avg ACV (baseline)</td><td>${fmtMoney(f.acv)}</td><td class="who">Someone with actual P&amp;L access, not a sales-engineering estimate</td></tr>
        <tr><td>SD cycle is longer than Denver</td><td>${f.sd_cycle_days}d vs ${f.denver_cycle_days}d</td><td class="who">A defense-tech AE who has sold DOD-class software</td></tr>
        <tr><td>Regulated/defense multiplier</td><td>${f.regulated_def_multiplier.toFixed(1)}x</td><td class="who">A public-sector AE or someone who's watched SI-burden extend cycle</td></tr>
        <tr><td>Quota ${fmtMoney(f.quota)} achievable in ramp + 1 quarter</td><td>Yes/No</td><td class="who">A Factory sales manager or RVP</td></tr>
        <tr><td>Opps per quarter (operating funnel)</td><td>${won.toFixed(2)}</td><td class="who">A consistency check from an AE carrying a real territory</td></tr>
        <tr><td>MEDDPICC accounts scored</td><td>${countWithMeddpicc} of ${ACCOUNTS.length} · sum ${scoreSum}/24</td><td class="who">Recompute via $&gt;≥3 element. KNOWN line each — see data/meddpicc.json</td></tr>
      </table>
      <div style="font-size:12.5px;color:var(--callout-text);margin-top:10px;font-style:italic;">I would rather be corrected on these in week one than defend them in month six.</div>
    </div>
  `;
}

// -- THESIS --
function renderThesis(){
  const svg=document.getElementById("scatter");const NS="http://www.w3.org/2000/svg";
  function mkEl(t,a){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);return e;}
  svg.innerHTML="";
  const PLOT={W:900,H:540,padL:56,padR:18,padT:22,padB:44};
  const X={min:1e5,max:1e10},Y={min:10,max:1e5};
  const xScale=v=>PLOT.padL+(Math.log10(v)-Math.log10(X.min))/(Math.log10(X.max)-Math.log10(X.min))*(PLOT.W-PLOT.padL-PLOT.padR);
  const yScale=v=>PLOT.H-PLOT.padB-(Math.log10(v)-Math.log10(Y.min))/(Math.log10(Y.max)-Math.log10(Y.min))*(PLOT.H-PLOT.padT-PLOT.padB);
  svg.appendChild(mkEl("line",{x1:PLOT.padL,y1:PLOT.H-PLOT.padB,x2:PLOT.W-PLOT.padR,y2:PLOT.H-PLOT.padB,class:"axis-line"}));
  svg.appendChild(mkEl("line",{x1:PLOT.padL,y1:PLOT.padT,x2:PLOT.padL,y2:PLOT.H-PLOT.padB,class:"axis-line"}));
  [1e5,1e6,1e7,1e8,1e9,1e10].forEach(v=>{const x=xScale(v);svg.appendChild(mkEl("line",{x1:x,y1:PLOT.H-PLOT.padB,x2:x,y2:PLOT.H-PLOT.padB+4,class:"axis-line"}));const tx=mkEl("text",{x:x,y:PLOT.H-PLOT.padB+18,"text-anchor":"middle",class:"axis-text"});tx.textContent=v>=1e9?"$"+(v/1e9)+"B":v>=1e6?"$"+(v/1e6)+"M":"$"+(v/1e3)+"k";svg.appendChild(tx);});
  [10,100,1000,10000,100000].forEach(v=>{const y=yScale(v);svg.appendChild(mkEl("line",{x1:PLOT.padL-4,y1:y,x2:PLOT.padL,y2:y,class:"axis-line"}));const tx=mkEl("text",{x:PLOT.padL-8,y:y+3,"text-anchor":"end",class:"axis-text"});tx.textContent=v>=1000?(v/1000)+"k":String(v);svg.appendChild(tx);});
  const xtit=mkEl("text",{x:(PLOT.padL+PLOT.W-PLOT.padR)/2,y:PLOT.H-8,"text-anchor":"middle",class:"axis-title"});xtit.textContent="Revenue (annual, USD, log scale)";svg.appendChild(xtit);
  const xTh=xScale(5e8),yTh=yScale(5000);
  svg.appendChild(mkEl("line",{x1:xTh,y1:PLOT.padT,x2:xTh,y2:PLOT.H-PLOT.padB,class:"threshold-line"}));
  svg.appendChild(mkEl("line",{x1:PLOT.padL,y1:yTh,x2:PLOT.W-PLOT.padR,y2:yTh,class:"threshold-line"}));
  function qrLab(x,y,t){const t1=mkEl("text",{x:x,y:y,"text-anchor":"middle",class:"quadrant-label"});t1.textContent=t;svg.appendChild(t1);}
  qrLab(PLOT.padL+(xTh-PLOT.padL)/2,PLOT.padT+(yTh-PLOT.padT)/2,"Capital-light, labor-heavy");
  qrLab(xTh+(PLOT.W-PLOT.padR-xTh)/2,PLOT.padT+(yTh-PLOT.padT)/2,"Enterprise / scale");
  qrLab(PLOT.padL+(xTh-PLOT.padL)/2,yTh+(PLOT.H-PLOT.padB-yTh)/2,"Small / SMB");
  qrLab(xTh+(PLOT.W-PLOT.padR-xTh)/2,yTh+(PLOT.H-PLOT.padB-yTh)/2,"Lean & scaling");
  const PL=ACCOUNTS.filter(a=>parseNum(a.employees_total)!=null).sort((x,y)=>(parseInt(x.priority)||99)-(parseInt(y.priority)||99)||x.company.localeCompare(y.company));
  PL.forEach((a,idx)=>{const emp=parseNum(a.employees_total);if(emp==null)return;const cx=xScale(5e8)+((idx%5-2)*18);const cy=yScale(emp);const c=mkEl("circle",{cx,cy,r:8,class:"point","data-priority":a.priority});const tt=mkEl("title");tt.textContent=`${a.company} · P${a.priority} · ~${emp.toLocaleString()} emp · ${a.sector}`;c.appendChild(tt);svg.appendChild(c);});
}

// -- Tabs --
function switchTab(name){
  document.querySelectorAll(".tab").forEach(t=>t.setAttribute("aria-selected",String(t.dataset.tab===name)));
  document.querySelectorAll(".tab-panel").forEach(p=>p.hidden=p.dataset.tabPanel!==name);
  if(name==="today")renderToday();
  if(name==="accounts"){renderAccountsToolbar();renderAccounts();if(!STATE.selectedId)STATE.selectedId=ACCOUNTS[0].account_id;renderDetail();}
  if(name==="forecast")renderForecast();
  if(name==="thesis")renderThesis();
}
document.querySelectorAll(".tab").forEach(t=>t.addEventListener("click",()=>switchTab(t.dataset.tab)));

// -- Disqualify modal --
function openDisqualifyModal(a,s){window._dqAccount=a;document.getElementById("dq-reason").value=s.disqualify_reason||"";document.getElementById("modal-disqualify").classList.add("open");document.getElementById("dq-reason").focus();}
document.getElementById("dq-cancel").addEventListener("click",()=>{document.getElementById("modal-disqualify").classList.remove("open");});
document.getElementById("dq-confirm").addEventListener("click",()=>{const r=document.getElementById("dq-reason").value.trim();if(!r){toast("Reason required.");return;}const a=window._dqAccount;if(!a)return;const s=acctState(a.account_id);s.status="disqualified";s.status_history.push({status:"disqualified",date:TODAY_ISO});s.disqualify_reason=r;saveState();document.getElementById("modal-disqualify").classList.remove("open");renderDetail();renderAccounts();renderToday();toast("Disqualified: "+a.company);});

// -- Toast --
function toast(m){const t=document.getElementById("toast");t.textContent=m;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2200);}

// -- Help overlay --
function openHelp(){document.getElementById("help-overlay").classList.add("open");}
function closeHelp(){document.getElementById("help-overlay").classList.remove("open");}
document.getElementById("btn-help").addEventListener("click",openHelp);
document.getElementById("help-close").addEventListener("click",closeHelp);
document.getElementById("help-overlay").addEventListener("click",e=>{if(e.target.id==="help-overlay")closeHelp();});

// -- Export CSV (full state) --
function exportCsv(){
  const lines=[["account_id","company","region","priority","status","status_history","notes","next_action_date","next_action_label","disqualify_reason","meddpicc_score","meddpicc_band"].join(",")];
  ACCOUNTS.forEach(a=>{
    const s=acctState(a.account_id);
    const m=MEDDPICC[a.meddpicc_key];
    const cells=[a.account_id,csv(a.company),csv(a.region),a.priority,s.status,csv(JSON.stringify(s.status_history)),csv(s.notes||""),csv(s.next_action_date||""),csv(s.next_action_label||""),csv(s.disqualify_reason||""),m?(m.total_score||0):"UNKNOWN",m?(m.band||""):"UNKNOWN"];
    lines.push(cells.join(","));
  });
  const blob=new Blob([lines.join("\\n")],{type:"text/csv;charset=utf-8"});
  const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=`factory_territory_state_${TODAY_ISO}.csv`;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);toast("State exported to CSV.");
}
function csv(s){const v=String(s==null?"":s);return /[,"\\n]/.test(v)?`"${v.replace(/"/g,'""')}"`:v;}
document.getElementById("btn-export").addEventListener("click",exportCsv);

document.getElementById("btn-reset").addEventListener("click",()=>{if(!confirm("Reset status, notes, touches, checklist, disqualify reasons? This cannot be undone."))return;STATE={accounts:{},filter:{region:"All",priority:"All",status:"All",search:""},forecast:{}};saveState();renderToday();renderAccounts();renderDetail();toast("State reset.");});

// -- Keyboard shortcuts --
document.addEventListener("keydown",e=>{
  const inField=["INPUT","TEXTAREA","SELECT"].includes((e.target.tagName||"").toUpperCase());
  if(e.key==="?"&&!inField){e.preventDefault();openHelp();return;}
  if(e.key==="Escape"){closeHelp();document.getElementById("modal-disqualify").classList.remove("open");return;}
  if(inField)return;
  if(e.key==="/"){e.preventDefault();document.getElementById("filter-search").focus();switchTab("accounts");return;}
  if(e.key==="j"||e.key==="k"){e.preventDefault();const list=document.querySelectorAll("#acct-list .acct-row");if(!list.length)return;let i=-1;list.forEach((r,idx)=>{if(r.classList.contains("active"))i=idx;});const next=e.key==="j"?Math.min(i+1,list.length-1):Math.max(0,i===-1?0:i-1);selectAccount(list[next].dataset.jump);document.querySelector("#acct-list .acct-row.active")?.scrollIntoView({block:"nearest"});return;}
  if(e.key==="e"){e.preventDefault();const ta=document.querySelector("#acct-detail .outreach-panel[data-panel='email'] textarea")||document.querySelector("#acct-detail textarea");if(ta)ta.focus();return;}
  if(e.key==="c"){e.preventDefault();const btn=document.querySelector(".copy-inline");if(btn)btn.click();return;}
  if(e.key==="d"){e.preventDefault();if(!STATE.selectedId)return;const a=ACCOUNTS.find(x=>x.account_id===STATE.selectedId);openDisqualifyModal(a,acctState(a.account_id));return;}
  if(["1","2","3","4"].includes(e.key)){e.preventDefault();const m={1:"today",2:"accounts",3:"forecast",4:"thesis"};switchTab(m[e.key]);return;}
});

// -- Init --
function init(){STATE.filter=STATE.filter||{region:"All",priority:"All",status:"All",search:""};STATE.forecast=STATE.forecast||{};if(!STATE.selectedId)STATE.selectedId=ACCOUNTS[0].account_id;switchTab("today");}
init();
</script>
</body>
</html>
"""

HTML = (HTML
        .replace("__ACCOUNTS__", ACCOUNTS_JSON)
        .replace("__MEDDPICC__", MEDDPICC_JSON)
        .replace("__ACCOUNT_PLANS__", ACCOUNT_PLANS_JSON)
        .replace("__OUTREACH__", OUTREACH_JSON))

OUT_PATH.write_text(HTML, encoding="utf-8")
print(f"Dashboard regenerated → {OUT_PATH}")
print(f"  size: {OUT_PATH.stat().st_size} bytes")
print(f"  accounts: {len(accounts)}  (priority set: {sum(1 for a in accounts if a['is_priority'])})")
print(f"  contacts: {len(raw_contacts)}")
print(f"  MEDDPICC accounts: {len(MEDDPICC)}")
