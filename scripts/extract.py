#!/usr/bin/env python3
"""Reconcile the published Open Masala dataset against its upstream sources.

The 18 rows encode editorial judgment (which analytes, the SA-vs-general values,
provenance tiers, overclaim guards) that is NOT mechanically derivable — so this
is a *reconcile / validate* tool, not a full re-deriver. What it DOES do, and why
it matters for staleness:

  - Matches every `sources[]` entry in the canonical JSON to the upstream evidence
    registry (`tools/evidence/registry.yaml`) by DOI / PMID / PMCID / URL / label.
  - FLAGS the dangerous cases: a cited source that is retracted / superseded /
    not-yet-approved, or that is no longer in the registry at all. (Worst case the
    review found: a retracted citation silently living on in the DOI'd Zenodo
    version, HF mirror, and PyPI wheel.)
  - Refreshes the mechanically-derivable field `in_registry` to match reality
    (with --refresh).
  - Cross-checks each row's `loinc` against the upstream LOINC map (`loinc.yaml`).

Upstream lives in the separate masala-health checkout. Point at it with --upstream
or $MASALA_UPSTREAM; defaults to a sibling `../masala-health`.

Requires PyYAML:  pip install pyyaml

Usage:
    python3 scripts/extract.py                 # validation report (read-only)
    python3 scripts/extract.py --check         # exit 1 on any blocking issue (CI / monthly guard)
    python3 scripts/extract.py --refresh        # rewrite in_registry flags from upstream, then re-run build.py
"""
import argparse
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANONICAL = os.path.join(ROOT, "data", "ancestry-reference-ranges.v0.json")

# review_status values that mean "do not keep citing this without a fresh human look"
BLOCKING_STATUS = {"superseded", "retired", "retracted"}


def _norm_doi(s):
    if not s:
        return None
    s = s.strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    s = s.replace("doi:", "").strip()
    return s or None


def _ids_from_source(src):
    """Pull {doi, pmid, pmcid, url} identifiers out of a dataset source entry."""
    ref = (src.get("ref") or "")
    url = (src.get("url") or "")
    doi = None
    pmid = None
    pmcid = None
    for part in re.split(r"[;,]", ref):
        p = part.strip()
        low = p.lower()
        if low.startswith("doi:"):
            doi = _norm_doi(p[4:])
        elif low.startswith("pmid:"):
            pmid = p.split(":", 1)[1].strip()
        elif low.startswith("pmcid:"):
            pmcid = p.split(":", 1)[1].strip().upper()
    if not doi and "doi.org/" in url.lower():
        doi = _norm_doi(url)
    return {"doi": doi, "pmid": pmid, "pmcid": pmcid, "url": url.strip()}


def _index_registry(entries):
    by = {"doi": {}, "pmid": {}, "pmcid": {}, "url": {}}
    for e in entries:
        if e.get("doi"):
            by["doi"][_norm_doi(e["doi"])] = e
        if e.get("pmid"):
            by["pmid"][str(e["pmid"]).strip()] = e
        if e.get("pmcid"):
            by["pmcid"][str(e["pmcid"]).strip().upper()] = e
        if e.get("url"):
            by["url"][e["url"].strip().lower()] = e
    return by


def _match(src, idx, entries):
    ids = _ids_from_source(src)
    if ids["doi"] and ids["doi"] in idx["doi"]:
        return idx["doi"][ids["doi"]]
    if ids["pmid"] and ids["pmid"] in idx["pmid"]:
        return idx["pmid"][ids["pmid"]]
    if ids["pmcid"] and ids["pmcid"] in idx["pmcid"]:
        return idx["pmcid"][ids["pmcid"]]
    if ids["url"] and ids["url"].lower() in idx["url"]:
        return idx["url"][ids["url"].lower()]
    # last resort: fuzzy label containment
    label = (src.get("label") or "").strip().lower()
    if label:
        for e in entries:
            el = (e.get("label") or "").strip().lower()
            if el and (el in label or label in el):
                return e
    return None


def load_upstream(upstream):
    reg_path = os.path.join(upstream, "tools", "evidence", "registry.yaml")
    loinc_path = os.path.join(upstream, "ios", "MasalaHealth", "Resources", "loinc.yaml")
    if not os.path.exists(reg_path):
        sys.exit(f"registry.yaml not found at {reg_path}\n"
                 f"Point --upstream at your masala-health checkout (or set $MASALA_UPSTREAM).")
    entries = yaml.safe_load(open(reg_path))
    loinc_codes = {}
    if os.path.exists(loinc_path):
        for lab in (yaml.safe_load(open(loinc_path)) or {}).get("labs", []):
            loinc_codes[lab["code"]] = lab
    return entries, loinc_codes


def reconcile(upstream):
    entries, loinc_codes = load_upstream(upstream)
    idx = _index_registry(entries)
    data = json.load(open(CANONICAL))
    rows = data["rows"]

    report = []          # (row_id, level, message)
    changed = False      # would --refresh change in_registry?
    blocking = 0

    for r in rows:
        rid = r["id"]
        loinc = r.get("loinc")
        if loinc and not loinc.startswith("PRAJNA-") and loinc_codes and loinc not in loinc_codes:
            report.append((rid, "BLOCK", f"loinc {loinc} not found in upstream loinc.yaml"))
            blocking += 1
        for src in r["sources"]:
            e = _match(src, idx, entries)
            in_reg_now = e is not None
            if bool(src.get("in_registry")) != in_reg_now:
                report.append((rid, "REFRESH",
                               f"in_registry {src.get('in_registry')} → {in_reg_now} for “{src['label'][:44]}”"))
                changed = True
                src["in_registry"] = in_reg_now
            if e is None:
                report.append((rid, "BLOCK", f"source not in registry: “{src['label'][:50]}”"))
                blocking += 1
                continue
            status = (e.get("review_status") or "").lower()
            if status in BLOCKING_STATUS or e.get("superseded_by"):
                report.append((rid, "BLOCK",
                               f"cited source “{e['id']}” is {status or 'superseded'}"
                               + (f" (→ {e['superseded_by']})" if e.get("superseded_by") else "")))
                blocking += 1
            elif status == "proposed":
                report.append((rid, "WARN", f"cited source “{e['id']}” is still `proposed` (unreviewed)"))
    return data, report, changed, blocking


def main():
    ap = argparse.ArgumentParser(description="Reconcile Open Masala against upstream registry + LOINC.")
    ap.add_argument("--upstream", default=os.environ.get("MASALA_UPSTREAM",
                    os.path.join(os.path.dirname(ROOT), "masala-health")),
                    help="path to the masala-health checkout (default: ../masala-health or $MASALA_UPSTREAM)")
    ap.add_argument("--check", action="store_true", help="exit 1 on any blocking issue or drift")
    ap.add_argument("--refresh", action="store_true", help="write refreshed in_registry flags back to the canonical JSON")
    args = ap.parse_args()

    data, report, changed, blocking = reconcile(args.upstream)

    warns = sum(1 for _, lvl, _ in report if lvl == "WARN")
    refreshes = sum(1 for _, lvl, _ in report if lvl == "REFRESH")
    for rid, lvl, msg in report:
        print(f"  [{lvl:7}] {rid}: {msg}")
    print(f"\n{len(data['rows'])} rows · {blocking} blocking · {warns} warnings · "
          f"{refreshes} in_registry drift")

    if args.refresh and changed:
        json.dump(data, open(CANONICAL, "w"), indent=2, ensure_ascii=False)
        open(CANONICAL, "a").write("\n") if not open(CANONICAL).read().endswith("\n") else None
        print("wrote refreshed in_registry flags → data/ancestry-reference-ranges.v0.json "
              "(now re-run scripts/build.py)")

    if args.check and (blocking or changed):
        print("\nFAIL: publish-blocking issues or unrefreshed drift. "
              "Resolve upstream (clinician-gated for value/status changes) before re-publishing.")
        sys.exit(1)
    print("\nOK." if not blocking else "\nReview the blocking items above.")


if __name__ == "__main__":
    main()
