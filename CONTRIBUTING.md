# Contributing to Open Masala

Thank you for helping make ancestry-adjusted health data more accurate and accessible. This is a clinical-reference dataset, so contributions are held to an evidence bar — that bar *is* the value of the dataset.

## What we welcome

- **Corrections** — a value that's wrong, out of date, or mis-cited.
- **New citations** — a better or additional source for an existing row, especially one that moves a row from `study-derived` toward `guideline-endorsed`.
- **New rows** — a South-Asian-specific (or other ancestry) reference range or screening threshold we don't cover yet.
- **Standards fixes** — a wrong LOINC/UCUM code, or a cleaner FHIR mapping.
- **Tooling** — improvements to `scripts/build.py`, exports, or validation.

## How to propose a change

1. **Edit the canonical file only** — `data/ancestry-reference-ranges.v0.json`. Do **not** hand-edit the CSV or FHIR files; they are generated.
2. **Regenerate the exports:** `python3 scripts/build.py`.
3. **Open a pull request** describing the change and, for any clinical value, **the source** — a DOI, PMID, or guideline URL. A value without a citation cannot be merged.

## The bar for clinical values

Every row is tagged with a [`provenance_tier`](docs/schema.md#provenance-tiers). New or changed clinical values follow these rules:

- **State the tier honestly.** A single primary study supports a `study-derived` row, never a `guideline-endorsed` one. `guideline-endorsed` requires a named guideline/consensus body.
- **A primary study never stands alone** as the *reason* for a recommendation — pair it with a guideline/consensus source.
- **Add an `overclaim_guard`** where a reader could over-read the row (e.g. "this is a screening trigger, not a diagnosis").
- **Don't invent adjustments.** If the evidence gives an effect estimate but no cutoff, say so; do not fabricate a threshold or a multiplier. See [`docs/governance.md`](docs/governance.md).

Clinical values undergo an evidence review before merge, and a proposed value stays flagged until it clears that review. Non-clinical contributions (tooling, docs, standards codes) move faster.

## Reporting an issue

Not sure it's a formal PR? Open an issue with the analyte, the value you're questioning, and a source. Flags of stale or retracted sources are especially valuable.

## Licensing of contributions

By contributing, you agree your contribution is licensed under the repository's [CC BY 4.0](LICENSE) license.
