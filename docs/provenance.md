# Provenance & methodology

## Where the numbers come from

Open Masala is a **curation and synthesis** of published clinical guidelines and peer-reviewed studies. It is *not* a primary-data release, and it does not contain any individual's health records.

Every value in the dataset traces to a named source — a guideline body (WHO, IDF, ADA, AHA/ACC, NLA, Endocrine Society, Lipid Association of India) or a peer-reviewed study (MASALA, CARRS, INTERHEART, and others). Those sources are maintained in a curated evidence registry where each entry is:

- **Link-validated** — DOIs resolved against Crossref/OpenAlex, PMIDs against PubMed, and web sources checked for reachability.
- **Kind-typed** — `guideline` / `consensus` / `systematicReview` / `primaryStudy`.
- **Evidence-graded** — an A/B/C/D/X grade where one has been assigned.
- **Review-tracked** — a state machine (`proposed → needs_physician_review → approved → superseded → retired`). A `proposed` source is visible but flagged until a clinician signs off.

The reference values in this dataset bind to those registry entries. Where a source is still `proposed`, the row that cites it is likewise provisional — surfaced honestly rather than hidden.

## How the rows were assembled

The dataset joins two things the project already maintained:

1. **General-population reference ranges** for each analyte, LOINC-coded, with units.
2. **South-Asian-specific screening thresholds** — the cutoffs and rules that differ by ancestry (BMI ≥23 diabetes screening, IDF waist 90/80, sex-specific low-HDL cuts, waist-to-height ≥0.5, earlier diabetes and coronary-calcium screening ages, the atherogenic-dyslipidemia pattern, Lp(a) test-once).

Each South Asian value is paired with the general-population value it replaces (so the *delta* is visible in a single row), tagged with a [provenance tier](schema.md#provenance-tiers), and linked to the citation that justifies it.

## What is and isn't copyrightable

Numbers and facts — a threshold value, a reference interval — are **not copyrightable** and are encoded here with citation. Guideline **prose** is copyrighted and is never copied into this dataset. Consumers should honor the same line.

## How it stays current

Freshness is handled as **surveillance**, not constant editing, because reference values change only when a guideline changes:

- **Monthly (automated, upstream):** a monthly job on the underlying evidence base detects guideline-page changes, catches retractions and dead links, and surfaces new South-Asian literature as *candidates* — never auto-merged.
- **Per-release (clinician-gated, event-driven):** when surveillance flags a change that affects a published row, a clinician reviews, values are updated, the version is bumped, and the CSV + FHIR exports are regenerated from the canonical JSON. This is the cadence external consumers actually see.
- **Out-of-band:** a retraction or a safety-relevant guideline reversal is not held for the monthly tick.

The binding constraint is clinician-review throughput, not automation frequency — which is why the dataset is transparent about review state rather than implying a completeness it doesn't have.

**Honest caveat (v0):** the upstream monthly surveillance and this published dataset are not yet automatically wired together — re-syncing a flagged upstream change into the canonical JSON is currently a manual, clinician-gated step. An automated re-extractor (upstream sources → canonical JSON) with a drift guard, plus a monthly cross-check that flags which published rows an upstream change affects, are on the near-term roadmap.

## Limitations

- **v0, not clinician-signed-off for clinical use.** Values are transcribed from published sources; a clinical review pass precedes any release positioned for care.
- **Synthesis, not primary data.** Where the literature gives an effect estimate rather than a codified cutoff, the row is tagged `study-derived`.
- **Scope is South Asian cardiometabolic + nutrition + lifestyle.** Deliberately narrow; it will never be "complete."
- **eGFR is intentionally *not* ancestry-adjusted** — see [governance](governance.md).
