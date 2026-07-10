#!/usr/bin/env python3
"""Regenerate the CSV + FHIR exports from the canonical JSON.

Stdlib only. The canonical source of truth is data/ancestry-reference-ranges.v0.json;
this script derives the flat CSV (for tabular/ML use) and the FHIR R4 Bundle (for
health systems) from it, so the three files never drift.

Run:  python3 scripts/build.py
"""
import csv
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SRC = os.path.join(DATA, "ancestry-reference-ranges.v0.json")
CSV_OUT = os.path.join(DATA, "ancestry-reference-ranges.v0.csv")
FHIR_OUT = os.path.join(DATA, "ancestry-reference-ranges.fhir.json")
# The MCP server bundles a copy of the canonical JSON so an installed package is
# self-contained; keep it in sync from the single source of truth (data/).
PKG_DATA = os.path.join(ROOT, "mcp-server", "open_masala_mcp", "data",
                        "ancestry-reference-ranges.v0.json")


def _kv(d):
    if d is None:
        return ""
    return "; ".join(f"{k}={v}" for k, v in d.items())


def build_csv(data):
    cols = [
        "id", "analyte", "loinc", "unit", "population", "sex",
        "age_min", "age_max", "measure_type",
        "sa_value", "general_value", "direction_of_risk",
        "provenance_tier", "evidence_grade",
        "source_labels", "source_urls", "source_refs", "source_kinds",
        "sources_in_registry", "overclaim_guard", "notes",
    ]
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in data["rows"]:
            srcs = r["sources"]
            w.writerow({
                "id": r["id"],
                "analyte": r["analyte"],
                "loinc": r["loinc"] or "",
                "unit": r["unit"],
                "population": r["population"],
                "sex": r["sex"],
                "age_min": (r["age"] or {}).get("min", ""),
                "age_max": (r["age"] or {}).get("max", ""),
                "measure_type": r["measure_type"],
                "sa_value": _kv(r.get("sa_value")),
                "general_value": _kv(r.get("general_value")),
                "direction_of_risk": r["direction_of_risk"],
                "provenance_tier": r["provenance_tier"],
                "evidence_grade": r.get("evidence_grade") or "",
                "source_labels": " | ".join(s["label"] for s in srcs),
                "source_urls": " | ".join(s.get("url") or "" for s in srcs),
                "source_refs": " | ".join(s.get("ref") or "" for s in srcs),
                "source_kinds": " | ".join(s.get("kind") or "" for s in srcs),
                "sources_in_registry": " | ".join(str(bool(s.get("in_registry"))).lower() for s in srcs),
                "overclaim_guard": r.get("overclaim_guard") or "",
                "notes": r.get("notes") or "",
            })
    return len(data["rows"])


def _gender(sex):
    return {"male": "male", "female": "female"}.get(sex)


def build_fhir(data):
    EXT = "https://masalahealth.co/fhir/StructureDefinition"
    entries = []
    for r in data["rows"]:
        qi = {}
        sv = r.get("sa_value") or {}
        rng = {}
        if "low" in sv:
            rng["low"] = {"value": sv["low"], "unit": r["unit"]}
        if "high" in sv:
            rng["high"] = {"value": sv["high"], "unit": r["unit"]}
        if rng:
            qi["range"] = rng
        g = _gender(r["sex"])
        if g:
            qi["gender"] = g
        age = r.get("age") or {}
        if age.get("min") is not None or age.get("max") is not None:
            arange = {}
            if age.get("min") is not None:
                arange["low"] = {"value": age["min"], "unit": "years", "system": "http://unitsofmeasure.org", "code": "a"}
            if age.get("max") is not None:
                arange["high"] = {"value": age["max"], "unit": "years", "system": "http://unitsofmeasure.org", "code": "a"}
            qi["age"] = arange
        qi["appliesTo"] = [{
            "text": ("South Asian" if r["population"] == "south_asian" else "General population")
        }]
        qi["condition"] = r["measure_type"]

        code = {"text": r["analyte"]}
        if r["loinc"] and not r["loinc"].startswith("PRAJNA-"):
            code["coding"] = [{"system": "http://loinc.org", "code": r["loinc"]}]
        elif r["loinc"]:
            code["coding"] = [{"system": "https://masalahealth.co/loinc-synthetic", "code": r["loinc"]}]

        obsdef = {
            "resourceType": "ObservationDefinition",
            "id": r["id"],
            "code": code,
            "qualifiedInterval": [qi],
            "extension": [
                {"url": f"{EXT}/provenance-tier", "valueString": r["provenance_tier"]},
                {"url": f"{EXT}/evidence-grade", "valueString": r.get("evidence_grade") or "ungraded"},
            ],
        }
        if r.get("overclaim_guard"):
            obsdef["extension"].append({"url": f"{EXT}/overclaim-guard", "valueString": r["overclaim_guard"]})
        for s in r["sources"]:
            obsdef["extension"].append({
                "url": f"{EXT}/source",
                "extension": [
                    {"url": "label", "valueString": s["label"]},
                    {"url": "url", "valueString": s.get("url") or ""},
                    {"url": "ref", "valueString": s.get("ref") or ""},
                    {"url": "kind", "valueString": s.get("kind") or ""},
                    {"url": "in-registry", "valueBoolean": bool(s.get("in_registry"))},
                ],
            })
        entries.append({"resource": obsdef})

    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "meta": {"tag": [{
            "system": "https://masalahealth.co/dataset",
            "code": "open-masala-ancestry-reference-ranges",
            "display": f"Open Masala ancestry-adjusted reference ranges {data['version']}",
        }]},
        "entry": entries,
    }
    with open(FHIR_OUT, "w") as f:
        json.dump(bundle, f, indent=2)
        f.write("\n")
    return len(entries)


def main():
    with open(SRC) as f:
        data = json.load(f)
    n_csv = build_csv(data)
    n_fhir = build_fhir(data)
    print(f"wrote data/{os.path.basename(CSV_OUT)} ({n_csv} rows)")
    print(f"wrote data/{os.path.basename(FHIR_OUT)} ({n_fhir} ObservationDefinition resources)")
    if os.path.isdir(os.path.dirname(PKG_DATA)):
        shutil.copyfile(SRC, PKG_DATA)
        print("synced mcp-server/open_masala_mcp/data/ (bundled copy)")


if __name__ == "__main__":
    main()
