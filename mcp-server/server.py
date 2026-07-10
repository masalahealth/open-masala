#!/usr/bin/env python3
"""Open Masala MCP server — an ancestry-adjusted health reference oracle.

Exposes the Open Masala dataset (ancestry-adjusted biomarker reference ranges
and screening thresholds) as MCP tools + resources, so any MCP client (Claude
Desktop, Claude Code, an agent) can query cited, provenance-tiered reference
values instead of relying on the model's prior.

DESIGN PRINCIPLE — this server is a STATELESS REFERENCE ORACLE. It holds no user
data. `evaluate_value` takes a value as an argument and returns a computed,
cited result; nothing is stored. All the personal-data handling (reading someone's
labs) lives in the client/advisor layer, never here. That keeps the server safe
to publish and run anywhere.

Run (stdio, for Claude Desktop / Claude Code):
    pip install "mcp[cli]"
    python3 mcp/server.py

The dataset is read from ../data/ relative to this file.
"""
import json
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data", "ancestry-reference-ranges.v0.json")

with open(DATA) as f:
    DATASET = json.load(f)
ROWS = DATASET["rows"]

mcp = FastMCP("open-masala")

DISCLAIMER = (
    "Open Masala is a reference dataset for research/product development — not a "
    "medical device, not clinical advice. Reference ranges vary by lab and method; "
    "decisions require individual clinical context. v0, not yet clinician-reviewed."
)

USAGE_RULES = """How to use Open Masala data responsibly (read before answering a user):
- Every value carries a `provenance_tier`. Report it.
  * guideline-endorsed → may be stated as guideline-backed.
  * study-derived → say "some studies suggest", NEVER "guidelines recommend".
  * contested-deprecated → tell the user NOT to apply this adjustment.
- Every row carries an `overclaim_guard` — the claim you must NOT make. Honor it verbatim.
- Never invent an ancestry adjustment that isn't in the data.
- Always cite the source(s) attached to a row.
- Always defer diagnosis and treatment to a clinician.
"""


def _match_rows(analyte: str):
    """Match rows by LOINC code (exact), id, or analyte-name substring."""
    q = analyte.strip().lower()
    hits = []
    for r in ROWS:
        if (r.get("loinc") or "").lower() == q or r["id"].lower() == q \
           or q in r["analyte"].lower() or q in r["id"].lower():
            hits.append(r)
    return hits


def _slim(r: dict) -> dict:
    """A client-friendly projection of a row."""
    return {
        "id": r["id"],
        "analyte": r["analyte"],
        "loinc": r.get("loinc"),
        "unit": r["unit"],
        "population": r["population"],
        "sex": r["sex"],
        "age": r.get("age"),
        "measure_type": r["measure_type"],
        "south_asian_value": r.get("sa_value"),
        "general_population_value": r.get("general_value"),
        "direction_of_risk": r["direction_of_risk"],
        "provenance_tier": r["provenance_tier"],
        "evidence_grade": r.get("evidence_grade"),
        "sources": r["sources"],
        "overclaim_guard": r.get("overclaim_guard"),
        "notes": r.get("notes"),
    }


@mcp.tool()
def list_measures() -> dict:
    """List every analyte / measure in the dataset — what ancestry-adjusted
    coverage exists. Start here to see what can be looked up."""
    return {
        "dataset": DATASET["dataset"],
        "version": DATASET["version"],
        "count": len(ROWS),
        "measures": [
            {"id": r["id"], "analyte": r["analyte"], "loinc": r.get("loinc"),
             "measure_type": r["measure_type"], "provenance_tier": r["provenance_tier"]}
            for r in ROWS
        ],
        "disclaimer": DISCLAIMER,
    }


@mcp.tool()
def get_reference(analyte: str) -> dict:
    """Get the ancestry-adjusted reference range(s) / threshold(s) for an analyte,
    each paired with the general-population value, provenance tier, evidence grade,
    citations, and the overclaim guard. `analyte` matches a LOINC code, a row id,
    or an analyte name (e.g. "BMI", "HDL", "2085-9", "Lp(a)")."""
    hits = _match_rows(analyte)
    if not hits:
        return {"query": analyte, "matches": [],
                "hint": "Call list_measures() to see available analytes."}
    return {"query": analyte, "matches": [_slim(r) for r in hits],
            "usage_rules": USAGE_RULES, "disclaimer": DISCLAIMER}


def _row_for_eval(analyte: str, sex: Optional[str]):
    hits = [r for r in _match_rows(analyte) if r["population"] == "south_asian"]
    if not hits:
        return None
    if sex:
        s = sex.strip().lower()
        sexed = [r for r in hits if r["sex"] in ("any",) or r["sex"] == s
                 or (s.startswith("f") and r["sex"] == "female")
                 or (s.startswith("m") and r["sex"] == "male")]
        if sexed:
            # Prefer a sex-specific row over an "any" row when both exist.
            sexed.sort(key=lambda r: 0 if r["sex"] != "any" else 1)
            hits = sexed
    # Prefer rows that carry a numeric threshold/range.
    hits.sort(key=lambda r: 0 if _numeric_target(r.get("sa_value")) else 1)
    return hits[0]


def _numeric_target(sv):
    if not isinstance(sv, dict):
        return None
    if "value" in sv and "comparator" in sv:
        return ("cmp", sv["comparator"], sv["value"])
    if "low" in sv or "high" in sv:
        return ("range", sv.get("low"), sv.get("high"))
    return None


@mcp.tool()
def evaluate_value(analyte: str, value: float, sex: Optional[str] = None,
                   age: Optional[int] = None) -> dict:
    """Evaluate a person's own measured value against the SOUTH-ASIAN-adjusted
    threshold/range for an analyte, returning a flag status plus the cited
    rationale and the overclaim guard.

    STATELESS: the value is used only to compute this response; nothing is stored.
    This is a reference lookup, not a diagnosis — always defer to a clinician.
    `sex` is optional ("male"/"female"); `age` is informational."""
    row = _row_for_eval(analyte, sex)
    if not row:
        return {"analyte": analyte, "value": value,
                "status": "no_south_asian_reference",
                "hint": "Call list_measures() / get_reference() to see coverage."}
    target = _numeric_target(row.get("sa_value"))
    status, explanation = "informational", None
    if target and target[0] == "cmp":
        _, comparator, thresh = target
        flagged = (value >= thresh) if comparator == ">=" else \
                  (value > thresh) if comparator == ">" else \
                  (value <= thresh) if comparator == "<=" else \
                  (value < thresh) if comparator == "<" else None
        if flagged is not None:
            direction = row["direction_of_risk"]
            status = "flag" if flagged else "within_reference"
            explanation = (f"{value} {comparator} {thresh} → "
                           f"{'meets the concern threshold' if flagged else 'does not meet the concern threshold'} "
                           f"for South Asian ({direction}-is-risk).")
    elif target and target[0] == "range":
        lo, hi = target[1], target[2]
        below = lo is not None and value < lo
        above = hi is not None and value > hi
        status = "flag" if (below or above) else "within_reference"
        explanation = (f"{value} vs South Asian reference "
                       f"[{lo if lo is not None else '-'}, {hi if hi is not None else '-'}] "
                       f"{row['unit']} → {'outside' if status == 'flag' else 'within'} range.")
    else:
        explanation = ("This row is not a simple numeric threshold "
                       f"({row['measure_type']}); see the guidance below.")

    return {
        "analyte": row["analyte"],
        "loinc": row.get("loinc"),
        "value": value,
        "unit": row["unit"],
        "sex_used": sex,
        "status": status,
        "explanation": explanation,
        "south_asian_target": row.get("sa_value"),
        "general_population_target": row.get("general_value"),
        "provenance_tier": row["provenance_tier"],
        "evidence_grade": row.get("evidence_grade"),
        "sources": row["sources"],
        "overclaim_guard": row.get("overclaim_guard"),
        "notes": row.get("notes"),
        "usage_rules": USAGE_RULES,
        "disclaimer": DISCLAIMER,
    }


@mcp.tool()
def screening_for(age: int, sex: Optional[str] = None) -> dict:
    """Which South-Asian-specific screenings/thresholds apply to a person of this
    age (and optional sex): the screening_threshold, screening_age, and risk_flag
    rows whose age band the person falls into. Cited. Not a care plan — a prompt to
    discuss with a clinician."""
    s = (sex or "").strip().lower()
    out = []
    for r in ROWS:
        if r["population"] != "south_asian":
            continue
        if r["measure_type"] not in ("screening_threshold", "screening_age", "risk_flag", "interpretation_caveat"):
            continue
        band = r.get("age") or {}
        lo, hi = band.get("min"), band.get("max")
        if lo is not None and age < lo:
            continue
        if hi is not None and age > hi:
            continue
        if r["sex"] not in ("any",) and s and not r["sex"].startswith(s[0]):
            continue
        out.append(_slim(r))
    return {"age": age, "sex": sex, "applicable": out,
            "usage_rules": USAGE_RULES, "disclaimer": DISCLAIMER}


@mcp.tool()
def search(query: str) -> dict:
    """Free-text search across analyte names, notes, overclaim guards, and source
    labels. Use when you don't know the exact analyte name."""
    q = query.strip().lower()
    hits = []
    for r in ROWS:
        hay = " ".join([r["analyte"], r.get("notes") or "", r.get("overclaim_guard") or "",
                        " ".join(s["label"] for s in r["sources"])]).lower()
        if q in hay:
            hits.append(_slim(r))
    return {"query": query, "matches": hits, "count": len(hits)}


@mcp.tool()
def list_sources() -> dict:
    """List every unique citation backing the dataset (label, url, ref, kind)."""
    seen, out = set(), []
    for r in ROWS:
        for src in r["sources"]:
            key = src.get("ref") or src.get("url") or src["label"]
            if key in seen:
                continue
            seen.add(key)
            out.append(src)
    return {"count": len(out), "sources": out}


@mcp.resource("open-masala://dataset")
def dataset_resource() -> str:
    """The full canonical dataset as JSON."""
    return json.dumps(DATASET, indent=2)


@mcp.resource("open-masala://guidance")
def guidance_resource() -> str:
    """How to use the data responsibly — provenance tiers + overclaim rules."""
    return USAGE_RULES + "\n\n" + DISCLAIMER


if __name__ == "__main__":
    mcp.run()
