# Changelog

All notable changes to this dataset are documented here. Versions follow a
`MAJOR.MINOR.PATCH` scheme; the dataset version is recorded in the canonical
JSON's `version` field.

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
