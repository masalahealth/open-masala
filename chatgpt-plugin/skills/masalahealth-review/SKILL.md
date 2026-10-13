---
name: masalahealth-review
description: Use Open Masala MCP tools to compare user-provided measurements with South Asian references, explain their evidence, or prepare clinician questions. Use for MasalaHealth or Open Masala requests; does not retrieve personal app records or manage treatment.
---

# MasalaHealth review

Open Masala is a stateless reference oracle. It supplies reference values, not a person's medical record. Use measurements explicitly supplied in this conversation or requested documents. Do not claim access to the Masala iOS app, lab history, sleep, or recovery data. Never infer ancestry from a name or appearance. Explain the South Asian scope when applicability is unclear; ask whether that comparison is wanted before applying it.

## Select and use the tools

Discover the connected Open Masala tools by their names and descriptions; runtime prefixes may vary. If unavailable, explain that the connection is needed and stop the reference comparison rather than inventing results.

- `list_measures`: coverage discovery, especially for a broad lab review.
- `search(query)`: find an analyte from a lay term such as cholesterol or sugar.
- `get_reference(analyte)`: retrieve full reference rows, source citations, evidence tiers, and overclaim guards. Prefer exact returned row IDs when a name matches multiple measures. `PRAJNA-*` codes are internal placeholders, not LOINC codes.
- `evaluate_value(analyte, value, sex?, age?, unit?)`: compare an actual supplied measurement. Always supply its confirmed unit. Obtain units from the document or user, never assume them. Ask for sex or age only when needed to select an applicable reference. Preserve measurement date and original lab reference interval in the answer when available.
- `screening_for(age, sex?)`: retrieve discussion prompts for the supplied age. Rows returned without sex may contain multiple sex-specific references; do not treat all as personally applicable. Use `get_reference` or the guidance resource for the complete evidence rules before explaining them.
- `list_sources`: source inventory, not a substitute for row-specific attribution.

Send only the needed analyte, number, unit, and applicable age/sex to evaluation tools. Do not send names, identifiers, complete reports, or unrelated history. Stateless server behavior does not establish the host's logging or retention policies; never promise that ChatGPT data stays on the device.

## Preserve the meaning of the result

Read `open-masala://guidance` when resources are available; otherwise use the full `usage_rules` returned by `get_reference` or `evaluate_value`.

Report each material reference's `provenance_tier` and honor its `overclaim_guard`:
- `guideline-endorsed`: may be described as guideline-backed, with the returned source.
- `study-derived`: describe as study-derived; do not call it a guideline recommendation.
- `contested-deprecated`: explicitly say the adjustment should not be applied.

Use linked row-specific sources near the supported claim. Distinguish dataset provenance from current clinical guidance: this dataset is v0 and not yet clinician-reviewed. Do not claim sources have been freshly verified unless they were actually checked.

Handle returned statuses without replacing them with a binary healthy/unhealthy judgment:
- `unit_mismatch`: resolve units before evaluating again. Do not compare or silently convert the value. Lp(a) mass and molar units need particular care and are not interchangeable through a universal factor.
- Unit spelling: the inspected server compares unit strings literally apart from whitespace and case. For confirmed equivalent typography such as BMI `kg/m²` versus returned `kg/m2`, explicitly identify the notation equivalence and resubmit the unchanged number with the reference spelling. This does not permit converting mass/molar units or assuming a missing unit.
- `ambiguous_needs_sex`: request the missing selector; do not pick a row.
- `no_reference_for_age`, `no_reference_for_sex`, or `no_south_asian_reference`: state the coverage limitation and do not invent an adjustment.
- `composite_needs_multiple_inputs`: identify missing components; do not diagnose the composite from one value.
- `caveat`, `informational`, `screening_applies`, or `screening_not_yet`: explain the guidance or applicability, not a disease flag.
- `do_not_apply`: do not apply the adjustment.
- `flag`, `within_reference`, or `category`: report the dataset comparison, with context; a reference flag is not a diagnosis, and being within a range does not establish absence of disease.

## Complete the requested workflow

For lab review, give a concise comparison of the supplied value and unit, date, original lab interval if provided, Open Masala reference, evidence tier, and source. Separate measurements from interpretation. If repeated dated results are supplied, describe changes only when units and methods are comparable. Avoid a trend claim from one result.

For evidence questions, explain the returned population, measure type, general-population comparison, evidence tier, and limitation. Avoid fabricating a reference for an uncovered analyte.

For appointment preparation, summarize relevant supplied facts, identify gaps, and draft a short prioritized list of clinician questions grounded in the retrieved references. Do not prescribe, adjust medications, order tests, or send the summary to anyone. Let the user choose which facts to share.

For recovery or sleep-history requests, explain that this MCP does not expose that history. User-provided records can be discussed, but do not claim an Open Masala recovery tool exists.
