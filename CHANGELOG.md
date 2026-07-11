# Changelog

All notable changes to this dataset are documented here. Versions follow a
`MAJOR.MINOR.PATCH` scheme; the dataset version is recorded in the canonical
JSON's `version` field.

## MCP server (`open-masala-mcp` on PyPI — versioned independently of the dataset)

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
