# Schema & data dictionary

The canonical file is [`data/ancestry-reference-ranges.v0.json`](../data/ancestry-reference-ranges.v0.json). The CSV and FHIR files are derived from it by [`scripts/build.py`](../scripts/build.py) and never edited by hand.

## Top-level

```jsonc
{
  "dataset": "masala-ancestry-reference-ranges",
  "version": "0.0.1",
  "population_scope": "south_asian",
  "license_intended": "CC-BY-4.0",
  "rows": [ /* … */ ]
}
```

## Row fields

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable row key. |
| `analyte` | string | Human name (e.g. "BMI", "HDL-C"). |
| `loinc` | string \| null | LOINC code, or a synthetic `PRAJNA-*` code for computed metrics (never a real LOINC — the deliberate exception is eGFR `33914-3`). |
| `unit` | string | Unit, UCUM-preferred. |
| `population` | enum | `south_asian` \| `general`. The stratification dimension — the point of the dataset. |
| `sex` | enum | `male` \| `female` \| `any`. |
| `age` | `{min,max}` | Age band (nulls = unbounded). |
| `measure_type` | enum | `reference_range` \| `screening_threshold` \| `screening_age` \| `interpretation_caveat` \| `risk_flag` \| `deprecated_adjustment`. |
| `sa_value` | object | The South Asian value — `{comparator, value}` for a threshold, or `{low, high}` for a range. |
| `general_value` | object \| null | The default-population value, for contrast — so the *ancestry delta* is visible in one row. |
| `direction_of_risk` | enum | `high` \| `low` \| `n/a` — which way is concerning. |
| `provenance_tier` | enum | See below. **The credibility field.** |
| `evidence_grade` | enum | `A`\|`B`\|`C`\|`D`\|`X`\|`null`. |
| `sources` | array | `{label, url, ref, kind, in_registry}` per source. `ref` = PMID/DOI/PMCID. `kind` = guideline / consensus / systematicReview / primaryStudy. `in_registry` = source is backed by the curated evidence registry. |
| `overclaim_guard` | string \| null | The claim a consumer must **not** make from this row. Machine-readable honesty. |
| `notes` | string | Anything else a consumer needs. |

## Provenance tiers

The most important field. It answers "what *kind* of claim is this?" so nobody — human or LLM — over-reads a study estimate as a guideline.

- **`guideline-endorsed`** — a named guideline/consensus body recommends this exact cutoff for this population. Highest confidence.
- **`study-derived`** — a real, cited effect estimate from the literature, *not* codified into a guideline cutoff. Use with care; never present as settled practice.
- **`contested-deprecated`** — an adjustment the field is actively moving *away* from. Included precisely so we can tell consumers not to apply it. Its presence demonstrates rigor rather than undermining it.

A corollary rule the dataset follows: a `primaryStudy` never stands alone as the *reason* for a recommendation — it is paired with a guideline/consensus source.

## FHIR mapping

Each row maps to FHIR R4 `ObservationDefinition`:

| Row field | FHIR |
|---|---|
| `loinc` | `code.coding` (LOINC system; synthetic codes use a local system). |
| `sa_value.low/high` | `qualifiedInterval.range.low` / `.high` (with `unit`). |
| `population` | `qualifiedInterval.appliesTo` (text: "South Asian" / "General population"). |
| `sex` | `qualifiedInterval.gender`. |
| `age` | `qualifiedInterval.age` (UCUM `a`). |
| `measure_type` | `qualifiedInterval.condition`. |
| `provenance_tier`, `evidence_grade`, `overclaim_guard`, `sources` | `extension[*]` (R4 `ObservationDefinition` has no native citation slot). |

**Why `ObservationDefinition`, not `ValueSet`:** a `ValueSet` enumerates coded concepts; it is the wrong resource for numeric reference intervals. FHIR gives the *slot* for a population-specific range but ships **no ancestry-specific values** — which is exactly the gap this dataset fills.

## Regenerating

```bash
python3 scripts/build.py   # rewrites data/*.csv and data/*.fhir.json from the JSON
```
