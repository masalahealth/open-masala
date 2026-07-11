#!/usr/bin/env python3
"""Open Masala — pure reference-oracle logic (no MCP dependency).

`server.py` wraps every function here as an MCP tool. Keeping the logic in this
module means it can be unit-tested without the `mcp` SDK installed, and the
evaluation rules live in one place.

STATELESS BY DESIGN: `evaluate_value` takes a value as an argument and returns a
computed, cited result; nothing is stored. All personal-data handling lives in
the client/advisor layer, never here.
"""
import json
import os
import re
from typing import Optional


# --------------------------------------------------------------------------- #
# Dataset loading
# --------------------------------------------------------------------------- #
def _load_dataset() -> dict:
    """Load the bundled dataset. Works when installed as a package (data ships
    inside it) and when run from a source checkout."""
    # 1. Packaged resource (pip / uvx install).
    try:
        import importlib.resources as ir
        res = ir.files("open_masala_mcp").joinpath("data/ancestry-reference-ranges.v0.json")
        return json.loads(res.read_text(encoding="utf-8"))
    except (FileNotFoundError, ModuleNotFoundError, AttributeError, TypeError):
        pass
    # 2. Source-checkout fallbacks (bundled copy, then the repo's canonical data/).
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in ("data/ancestry-reference-ranges.v0.json",
                os.path.join("..", "..", "data", "ancestry-reference-ranges.v0.json")):
        cand = os.path.join(here, rel)
        if os.path.exists(cand):
            with open(cand, encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError("Open Masala dataset JSON not found (package data missing).")


DATASET = _load_dataset()
ROWS = DATASET["rows"]


# --------------------------------------------------------------------------- #
# Framing / guidance text
# --------------------------------------------------------------------------- #
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

# One-line pointer used on the token-light tools (Fix 8): the full USAGE_RULES +
# DISCLAIMER ship only from get_reference / evaluate_value (the value-bearing
# calls) and are always available via the open-masala://guidance resource.
GUIDANCE_POINTER = (
    "Usage rules + full disclaimer: read the open-masala://guidance resource "
    "(also returned in full by get_reference / evaluate_value)."
)


# --------------------------------------------------------------------------- #
# Matching / search
# --------------------------------------------------------------------------- #
# Lay/clinical synonyms so `search` works as the "I don't know the exact name"
# entry point (Fix 6). Keys are collapsed (alnum-only, lowercased); values are
# substrings to look for in a row's haystack.
SYNONYMS = {
    "cholesterol": ["hdl", "apob", "non-hdl", "ldl", "lipid", "lp(a)"],
    "lipids": ["hdl", "apob", "non-hdl", "triglyc", "lipid", "lp(a)", "atherogenic"],
    "lipid": ["hdl", "apob", "non-hdl", "triglyc", "lp(a)", "atherogenic"],
    "sugar": ["hba1c", "glucose", "diabetes", "insulin"],
    "bloodsugar": ["hba1c", "glucose", "diabetes"],
    "glucose": ["hba1c", "glucose", "diabetes"],
    "diabetes": ["diabetes", "hba1c", "glucose", "bmi"],
    "prediabetes": ["hba1c", "glucose", "diabetes"],
    "insulinresistance": ["insulin", "hba1c"],
    "kidney": ["egfr", "creatinine"],
    "renal": ["egfr"],
    "weight": ["bmi", "waist", "obesity"],
    "obesity": ["bmi", "waist"],
    "waistline": ["waist"],
    "heart": ["ascvd", "cac", "coronary", "apob", "prevent", "calcium"],
    "cardiac": ["cac", "coronary", "ascvd", "calcium"],
    "cardiovascular": ["ascvd", "cac", "apob", "prevent"],
    "vitamind": ["vitamin d", "25-oh"],
    "triglycerides": ["triglyc", "atherogenic"],
}


def _haystack(r: dict) -> str:
    return " ".join([
        r["analyte"], r["id"], r.get("loinc") or "", r.get("notes") or "",
        r.get("overclaim_guard") or "",
        " ".join(s["label"] for s in r["sources"]),
    ]).lower()


def _match_rows(analyte: str):
    """Match rows by internal code (exact), id, or analyte-name substring.

    Note: the code field holds real LOINC codes where they exist and internal
    `PRAJNA-*` placeholders otherwise (see _slim's `code_system`). Both are
    matched here; precise lookups use this, fuzzy discovery uses search()."""
    q = analyte.strip().lower()
    hits = []
    for r in ROWS:
        if (r.get("loinc") or "").lower() == q or r["id"].lower() == q \
           or q in r["analyte"].lower() or q in r["id"].lower():
            hits.append(r)
    return hits


def _code_system(loinc: Optional[str]) -> Optional[str]:
    if not loinc:
        return None
    return "internal-placeholder" if loinc.startswith("PRAJNA-") else "loinc"


def _slim(r: dict) -> dict:
    return {
        "id": r["id"], "analyte": r["analyte"],
        # `loinc` is real only when `code_system == "loinc"`; PRAJNA-* are
        # internal placeholders, not resolvable LOINC codes (Fix 5).
        "loinc": r.get("loinc"), "code_system": _code_system(r.get("loinc")),
        "unit": r["unit"], "population": r["population"], "sex": r["sex"],
        "age": r.get("age"), "measure_type": r["measure_type"],
        "south_asian_value": r.get("sa_value"),
        "general_population_value": r.get("general_value"),
        "direction_of_risk": r["direction_of_risk"],
        "provenance_tier": r["provenance_tier"], "evidence_grade": r.get("evidence_grade"),
        "sources": r["sources"], "overclaim_guard": r.get("overclaim_guard"),
        "notes": r.get("notes"),
    }


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #
def list_measures() -> dict:
    """List every analyte / measure in the dataset. Start here."""
    return {
        "dataset": DATASET["dataset"], "version": DATASET["version"], "count": len(ROWS),
        "measures": [
            {"id": r["id"], "analyte": r["analyte"], "loinc": r.get("loinc"),
             "code_system": _code_system(r.get("loinc")),
             "measure_type": r["measure_type"], "provenance_tier": r["provenance_tier"]}
            for r in ROWS
        ],
        "guidance": GUIDANCE_POINTER,
    }


def get_reference(analyte: str) -> dict:
    """Ancestry-adjusted reference(s)/threshold(s) for an analyte, each paired
    with the general-population value, provenance, citations, and overclaim guard.
    Matches a LOINC/internal code, id, or name substring."""
    hits = _match_rows(analyte)
    if not hits:
        return {"query": analyte, "matches": [],
                "hint": "Call list_measures() to see coverage, or search() if you don't know the exact name."}
    return {"query": analyte, "matches": [_slim(r) for r in hits],
            "usage_rules": USAGE_RULES, "disclaimer": DISCLAIMER}


# Measure types that are NOT a numeric flag — they carry guidance, not a cutoff.
SPECIAL_MEASURE_TYPES = {"screening_age", "interpretation_caveat", "deprecated_adjustment"}

# When several rows match, prefer the one a person asking "evaluate my value"
# most likely means (a reference range over a screening trigger, etc.).
MEASURE_TYPE_PREFERENCE = {
    "reference_range": 0, "risk_flag": 1, "screening_threshold": 2,
    "screening_age": 3, "interpretation_caveat": 4, "deprecated_adjustment": 5,
}

_COMPARATORS = {
    ">=": lambda v, t: v >= t, ">": lambda v, t: v > t,
    "<=": lambda v, t: v <= t, "<": lambda v, t: v < t, "==": lambda v, t: v == t,
}


def _numeric_target(sv):
    """Classify a `sa_value` dict into an evaluatable shape, or None."""
    if not isinstance(sv, dict):
        return None
    if "comparator" in sv and "value" in sv:
        return ("cmp", sv["comparator"], sv["value"])
    if "elevated_at" in sv:                                  # single elevated threshold → >=
        return ("cmp", ">=", sv["elevated_at"])
    if "overweight_at" in sv or "obese_at" in sv:            # ordinal category bands
        return ("bands", sv.get("overweight_at"), sv.get("obese_at"))
    if "triglycerides_mg_dl" in sv or "with_low_hdl" in sv:  # composite (needs >1 input)
        return ("composite", ["triglycerides (mg/dL)", "HDL-C (low, sex-specific)"])
    if "low" in sv or "high" in sv:
        return ("range", sv.get("low"), sv.get("high"))
    return None


def _norm_unit(u: Optional[str]) -> str:
    return "".join((u or "").split()).lower()


def _sex_matches(row_sex: str, s: str) -> bool:
    return row_sex == "any" or (bool(s) and row_sex.startswith(s[0]))


def _age_in_band(row: dict, age: Optional[int]) -> bool:
    if age is None:
        return True
    band = row.get("age") or {}
    lo, hi = band.get("min"), band.get("max")
    if lo is not None and age < lo:
        return False
    if hi is not None and age > hi:
        return False
    return True


def _guidance_text(sv) -> Optional[str]:
    if not isinstance(sv, dict):
        return None
    parts = [f"{k.replace('_', ' ')}: {sv[k]}"
             for k in ("guidance", "confirm_when", "confirm_with", "adjustment") if k in sv]
    return "; ".join(parts) or None


def _match_rank(r: dict, q: str) -> int:
    """Relevance of a row to query `q` (lower is better). Keeps a bare "HDL" from
    being answered by the *Non-HDL-C* row it merely contains as a substring."""
    if (r.get("loinc") or "").lower() == q or r["id"].lower() == q or r["analyte"].lower() == q:
        return 0
    if r["analyte"].lower().startswith(q):
        return 1
    if r["id"].lower().startswith(q):
        return 2
    return 3


def _candidate_rows(analyte: str):
    """Rows eligible for evaluation: South-Asian rows, plus special guidance rows
    (e.g. the deprecated eGFR row is population `general` but must still evaluate
    to a `do_not_apply` instruction rather than 'no reference'). Narrowed to the
    best match rank so a loose substring can't outrank the row actually named."""
    q = analyte.strip().lower()
    rows = [r for r in _match_rows(analyte)
            if r["population"] == "south_asian" or r["measure_type"] in SPECIAL_MEASURE_TYPES]
    if not rows:
        return []
    best = min(_match_rank(r, q) for r in rows)
    return [r for r in rows if _match_rank(r, q) == best]


def _evaluate_row(row: dict, value: float) -> dict:
    """Compute a status + explanation for one row. Never returns `flag` for a
    screening-age / caveat / deprecated row (Fix 4)."""
    mt = row["measure_type"]
    sv = row.get("sa_value")

    if mt == "screening_age":
        thr = sv.get("value") if isinstance(sv, dict) else None
        if thr is not None:
            applies = value >= thr
            return {"status": "screening_applies" if applies else "screening_not_yet",
                    "explanation": (f"Age {value} {'>=' if applies else '<'} South Asian screening "
                                    f"start age {thr} → {'screening applies' if applies else 'not yet at screening age'}.")}
    if mt == "interpretation_caveat":
        return {"status": "caveat",
                "explanation": _guidance_text(sv) or "Interpretation caveat — see south_asian_target and overclaim_guard."}
    if mt == "deprecated_adjustment":
        return {"status": "do_not_apply",
                "explanation": _guidance_text(sv) or "Do NOT apply an ancestry adjustment to this measure."}

    target = _numeric_target(sv)
    if target and target[0] == "cmp":
        _, comp, thresh = target
        op = _COMPARATORS.get(comp)
        if op is None:
            return {"status": "informational", "explanation": f"Unrecognized comparator '{comp}'.",
                    "south_asian_target": sv}
        flagged = op(value, thresh)
        return {"status": "flag" if flagged else "within_reference",
                "explanation": (f"{value} {comp} {thresh} → {'meets' if flagged else 'does not meet'} "
                                f"the South Asian concern threshold ({row['direction_of_risk']}-is-risk).")}
    if target and target[0] == "bands":
        ow, ob = target[1], target[2]
        if ob is not None and value >= ob:
            cat = "obese"
        elif ow is not None and value >= ow:
            cat = "overweight"
        else:
            cat = "normal"
        return {"status": "category", "category": cat,
                "explanation": (f"{value} {row['unit']} → South Asian category '{cat}' "
                                f"(overweight >= {ow}, obese >= {ob}).")}
    if target and target[0] == "range":
        lo, hi = target[1], target[2]
        flagged = (lo is not None and value < lo) or (hi is not None and value > hi)
        return {"status": "flag" if flagged else "within_reference",
                "explanation": (f"{value} vs South Asian reference "
                                f"[{lo if lo is not None else '-'}, {hi if hi is not None else '-'}] "
                                f"{row['unit']} → {'outside' if flagged else 'within'} range.")}
    if target and target[0] == "composite":
        return {"status": "composite_needs_multiple_inputs", "required_fields": target[1],
                "explanation": (f"'{row['analyte']}' is a composite pattern needing multiple inputs "
                                f"({', '.join(target[1])}); a single value cannot evaluate it. "
                                f"Provide each component and compare separately.")}
    # Fallback: surface the raw threshold so the model can still reason (Fix 1).
    return {"status": "informational",
            "explanation": (f"No simple numeric rule for this row (measure_type={mt}); "
                            f"see south_asian_target for the raw thresholds."),
            "south_asian_target": sv}


def evaluate_value(analyte: str, value: float, sex: Optional[str] = None,
                   age: Optional[int] = None, unit: Optional[str] = None) -> dict:
    """Evaluate a measured value against the South-Asian-adjusted reference for an
    analyte. STATELESS. A reference lookup, not a diagnosis."""
    cands = _candidate_rows(analyte)
    if not cands:
        return {"analyte": analyte, "value": value, "status": "no_south_asian_reference",
                "hint": "Call list_measures() / search() / get_reference() to see coverage.",
                "disclaimer": DISCLAIMER}

    # Age filter (Fix 3): drop rows whose age band excludes this person.
    if age is not None:
        aged = [r for r in cands if _age_in_band(r, age)]
        if not aged:
            return {"analyte": analyte, "value": value, "age_used": age,
                    "status": "no_reference_for_age",
                    "hint": f"Row(s) exist for '{analyte}' but none cover age {age}.",
                    "available_age_bands": [{"id": r["id"], "age": r.get("age")} for r in cands],
                    "disclaimer": DISCLAIMER}
        cands = aged

    # Sex handling (Fix 2): never silently pick a sex-specific row.
    split_sexes = sorted({r["sex"] for r in cands if r["sex"] != "any"})
    if sex:
        s = sex.strip().lower()
        sexed = [r for r in cands if _sex_matches(r["sex"], s)]
        if not sexed:
            return {"analyte": analyte, "value": value, "sex_used": sex,
                    "status": "no_reference_for_sex",
                    "hint": f"No '{analyte}' row for sex '{sex}'. Available: {split_sexes or ['any']}.",
                    "disclaimer": DISCLAIMER}
        cands = sexed
    elif len(split_sexes) > 1:
        return {"analyte": analyte, "value": value, "status": "ambiguous_needs_sex",
                "available_sexes": split_sexes,
                "hint": "This analyte is sex-split; pass sex='male' or sex='female' to evaluate.",
                "disclaimer": DISCLAIMER}

    # Pick the primary row; keep the rest visible.
    cands.sort(key=lambda r: (MEASURE_TYPE_PREFERENCE.get(r["measure_type"], 9),
                              0 if _numeric_target(r.get("sa_value")) else 1))
    row = cands[0]
    also_available = [r["id"] for r in cands[1:]]
    expected_unit = row["unit"]

    # Unit safety (Fix 7): a mmol/L-vs-mg/dL mismatch is a silent-wrong-answer
    # trap — surface it loudly and do NOT compute a possibly-wrong flag.
    if unit is not None and _norm_unit(unit) != _norm_unit(expected_unit):
        return {"analyte": row["analyte"], "expected_unit": expected_unit,
                "unit_provided": unit, "value": value, "status": "unit_mismatch",
                "warning": (f"You passed unit '{unit}' but the reference is in '{expected_unit}'. "
                            f"Convert to '{expected_unit}' and re-evaluate; not flagging to avoid a wrong answer."),
                "south_asian_target": row.get("sa_value"), "measure_type": row["measure_type"],
                "sources": row["sources"], "disclaimer": DISCLAIMER}

    evald = _evaluate_row(row, value)
    out = {
        "analyte": row["analyte"], "expected_unit": expected_unit,
        "value": value, "unit_provided": unit,
        "status": evald["status"], "explanation": evald["explanation"],
        "sex_used": sex, "age_used": age,
        "loinc": row.get("loinc"), "code_system": _code_system(row.get("loinc")),
        "measure_type": row["measure_type"],
        "south_asian_target": row.get("sa_value"),
        "general_population_target": row.get("general_value"),
        "direction_of_risk": row["direction_of_risk"],
        "provenance_tier": row["provenance_tier"], "evidence_grade": row.get("evidence_grade"),
        "sources": row["sources"], "overclaim_guard": row.get("overclaim_guard"),
        "notes": row.get("notes"),
        "usage_rules": USAGE_RULES, "disclaimer": DISCLAIMER,
    }
    # Carry any extra keys the evaluator produced (category, required_fields, …).
    for k in ("category", "required_fields"):
        if k in evald:
            out[k] = evald[k]
    if also_available:
        out["also_available"] = also_available
    return out


def screening_for(age: int, sex: Optional[str] = None) -> dict:
    """Which South-Asian-specific screenings/thresholds apply at this age (and
    optional sex). Cited. Not a care plan — a prompt to discuss with a clinician."""
    s = (sex or "").strip().lower()
    out = []
    for r in ROWS:
        if r["population"] != "south_asian":
            continue
        if r["measure_type"] not in ("screening_threshold", "screening_age", "risk_flag", "interpretation_caveat"):
            continue
        if not _age_in_band(r, age):
            continue
        if r["sex"] != "any" and s and not r["sex"].startswith(s[0]):
            continue
        out.append(_slim(r))
    return {"age": age, "sex": sex, "applicable": out, "guidance": GUIDANCE_POINTER}


def search(query: str) -> dict:
    """Free-text search across analyte names, notes, guards, and source labels,
    with a lay/clinical synonym layer (cholesterol → HDL/ApoB/…, sugar → HbA1c/…)."""
    raw = query.strip().lower()
    tokens = [t for t in re.split(r"[^a-z0-9()]+", raw) if t]
    if not tokens:
        return {"query": query, "matches": [], "count": 0, "guidance": GUIDANCE_POINTER}
    collapsed = re.sub(r"[^a-z0-9]", "", raw)
    query_syn = SYNONYMS.get(collapsed)

    def expansions(tok: str):
        exp = {tok}
        exp.update(SYNONYMS.get(tok, []))
        return exp

    hits = []
    for r in ROWS:
        hay = _haystack(r)
        if query_syn and any(term in hay for term in query_syn):
            hits.append(r)
            continue
        # AND across the user's tokens; OR across each token's synonym expansion.
        if all(any(term in hay for term in expansions(tok)) for tok in tokens):
            hits.append(r)
    return {"query": query, "matches": [_slim(r) for r in hits], "count": len(hits),
            "guidance": GUIDANCE_POINTER}


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
