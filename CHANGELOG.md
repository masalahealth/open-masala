# Changelog

All notable changes to this dataset are documented here. Versions follow a
`MAJOR.MINOR.PATCH` scheme; the dataset version is recorded in the canonical
JSON's `version` field.

## [0.1.0] — dataset expansion (2026-07-11)

Expanded **18 → 41 rows** from the internal cited evidence base, with maximal
domain breadth. **Every added row carries a verified DOI/PMID/PMCID**; one
candidate (total-cholesterol ~170 caveat) was dropped because its citation could
not be verified. 20 new rows are `review_status: proposed` pending clinician sign-off.

- **Data fix:** BMI obese action point corrected 25 → **27.5** (WHO 2004 Asian high-risk cutoff).
- **Cardiometabolic:** TG≥175, hs-CRP≥2, SA-ancestry ASCVD risk-enhancer, SCORE2 SA
  multiplier (×1.3/×1.7), Enas SA very-high-risk LDL/non-HDL targets, remnant
  cholesterol, ApoB/ApoA-I ratio, **South-Asian CAC age/sex percentiles**, BMI-23 MASLD.
- **New domains:** women's health (GDM early screening, menopause age, parity),
  pediatric (IAP BMI cut-offs), hematology (thalassemia carrier screening, benign
  ethnic neutropenia), endocrine (hypothyroidism emphasis), nutrition (vitamin B12),
  pharmacogenomics (SLCO1B1 statins).
- **Do-not-apply showcases (contested-deprecated):** APOL1 (West-African), ALDH2/ADH1B
  (East-Asian), MTHFR-as-SA-variant — joining the deprecated eGFR row.
- Tiers now 18 guideline-endorsed / 19 study-derived / 4 contested-deprecated; 35 unique sources.

## MCP server (`open-masala-mcp` on PyPI — versioned independently of the dataset)

### [0.0.3]

Bundled dataset refreshed to **v0.1.0** (18 → 41 rows). No server-logic change; the
new `sa_value` shapes (percentile tables, PGx guidance) already fall through the
0.0.2 evaluator correctly. BMI-band test updated to the corrected 27.5 obese cutoff.

### [0.0.2]

Correctness + robustness pass on `evaluate_value` and discovery, from an external
code review. **Dataset unchanged** (no re-mint of the DOI / Hugging Face copy).

- `evaluate_value` now handles every `sa_value` shape, not just `comparator`/`range`:
  BMI category bands (returns `normal`/`overweight`/`obese`), single `elevated_at`
  thresholds (Lp(a)), and composite patterns (returns
  `composite_needs_multiple_inputs` naming the required fields instead of a dead end).
- Sex-split analytes (HDL, waist) return `ambiguous_needs_sex` when `sex` is
  omitted, rather than silently using whichever row sorted first.
- `age` is now used to filter age-banded rows (`no_reference_for_age` when none apply).
- Screening-age / interpretation-caveat / deprecated rows use a distinct status
  vocabulary (`screening_applies`, `caveat`, `do_not_apply`) — they never return `flag`.
- Match ranking so a loose substring can't answer (e.g. "HDL" no longer resolves
  to *Non-HDL-C*).
- Synonym-aware `search` (cholesterol → HDL/ApoB/…, sugar → HbA1c/…).
- Optional `unit` arg: a mg/dL-vs-mmol/L mismatch returns `unit_mismatch` instead
  of a silently wrong flag; `expected_unit` is surfaced at the top of every result.
- `code_system` field distinguishes real LOINC codes from internal `PRAJNA-*`
  placeholders.
- Full usage-rules/disclaimer block ships only from `get_reference`/`evaluate_value`;
  lighter tools carry a one-line pointer to the `open-masala://guidance` resource.
- Logic refactored into `core.py` (no MCP dependency) + a test suite covering all
  of the above.

## [0.0.1] — unreleased (v0)

Initial extraction. **Not yet clinician-reviewed for clinical use.**

- 18 rows of South-Asian-specific reference ranges and screening thresholds,
  each paired with its general-population counterpart.
- Provenance tiers: 9 `guideline-endorsed`, 8 `study-derived`, 1
  `contested-deprecated` (eGFR race adjustment — flagged do-not-apply).
- 100% of the 26 sources backed by a curated, link-validated citation. One
  source (CARRS waist-to-height, Patel 2017) is `proposed`, awaiting clinician
  sign-off.
- Exports: canonical JSON, flat CSV, FHIR R4 Bundle of `ObservationDefinition`
  resources.
- Docs: schema/data-dictionary, provenance/methodology, governance.
