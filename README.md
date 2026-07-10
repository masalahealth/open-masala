# Open Masala — ancestry-adjusted health reference ranges

**The open, machine-readable, cited dataset of South Asian biomarker reference ranges and screening thresholds.**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-93c19a.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/1296751900.svg)](https://zenodo.org/badge/latestdoi/1296751900)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Dataset-yellow.svg)](https://huggingface.co/datasets/masalahealthco/open-masala)
&nbsp;·&nbsp; 18 rows · every value cited · LOINC-coded · FHIR-shaped

South Asians develop cardiovascular disease and type-2 diabetes earlier, at lower BMI, through different metabolic pathways. The screening thresholds that reflect this — WHO Asian BMI cutoffs, IDF waist limits, earlier diabetes and coronary-calcium screening, Lp(a) prompts — *exist*, but they're scattered across guideline PDFs and hundreds of papers. **Nobody has ever assembled them into one structured, cited, downloadable table.** This is that table.

> ⚠️ **v0 / early release.** A curation and synthesis of *published* guidelines and studies — not a primary-data release, and not yet clinician-reviewed for clinical use. See [Provenance](docs/provenance.md) and [Disclaimer](#disclaimer).

## What this is (and isn't)

- **Is:** a synthesis of published, citable thresholds into a machine-readable table — each row LOINC-coded, evidence-graded, provenance-tiered, and linked to its source.
- **Isn't:** raw cohort data. The studies these numbers come from (MASALA, GenomeAsia, UK Biobank) are access-controlled for [good reasons](docs/governance.md); we don't re-host them. We encode the *published thresholds* they produced.

## Files

| Path | Format | For |
|---|---|---|
| [`data/ancestry-reference-ranges.v0.json`](data/ancestry-reference-ranges.v0.json) | JSON (canonical) | Everyone — source of truth, with nested sources + overclaim guards. |
| [`data/ancestry-reference-ranges.v0.csv`](data/ancestry-reference-ranges.v0.csv) | CSV (flat) | ML / data science / Hugging Face. Flattens to Parquet in one line. |
| [`data/ancestry-reference-ranges.fhir.json`](data/ancestry-reference-ranges.fhir.json) | FHIR R4 Bundle | Health-system engineers — `ObservationDefinition.qualifiedInterval` per row. |
| [`scripts/build.py`](scripts/build.py) | Python (stdlib) | Regenerates CSV + FHIR from the canonical JSON. |
| [`mcp-server/`](mcp-server/) | MCP server | Query the dataset as tool calls from any agent (Claude Desktop, Claude Code). |
| [`advisor/`](advisor/) | Prompt + guide | Run it as a personal, ancestry-aware health advisor on your own machine. |
| [`docs/schema.md`](docs/schema.md) | Markdown | Full data dictionary + FHIR/LOINC mapping. |
| [`docs/provenance.md`](docs/provenance.md) | Markdown | How it was built, and how it stays current. |
| [`docs/governance.md`](docs/governance.md) | Markdown | Why we don't ship primary data; the eGFR/race lesson. |

## Coverage (v0)

- **18 rows** across BMI, waist, HDL, triglycerides / atherogenic pattern, ApoB, Lp(a), non-HDL, HbA1c interpretation, fasting insulin, vitamin D, diabetes & CAC screening ages, eGFR, and 10-year risk.
- **Provenance tiers:** 9 guideline-endorsed · 8 study-derived · 1 contested-deprecated.
- **Citation completeness:** 100% — all 26 sources across the 18 rows are backed by a curated, link-validated citation.

## The provenance model (why you can trust a row)

Every row carries a **`provenance_tier`** — the single most important field:

| Tier | Meaning |
|---|---|
| **`guideline-endorsed`** | A named body recommends this exact cutoff for this population (WHO Asian BMI, IDF waist, ADA SA screening). Highest confidence. |
| **`study-derived`** | A real, cited effect estimate not yet codified into a guideline cutoff (e.g. the HbA1c under-read). Use with care; not settled practice. |
| **`contested-deprecated`** | An adjustment the field is moving *away* from (the eGFR race coefficient, retired 2021). Included precisely so you can tell you must **not** apply it. |

Every row also carries an **`overclaim_guard`**: the claim you must *not* make from it. Building an LLM feature? Read these — they're designed to stop confidently-wrong ancestry statements.

## Quick start

```python
import json

rows = json.load(open("data/ancestry-reference-ranges.v0.json"))["rows"]
sa_bmi = next(r for r in rows if r["id"] == "bmi-diabetes-screening-threshold")
print(sa_bmi["sa_value"], "vs general", sa_bmi["general_value"])
# {'comparator': '>=', 'value': 23} vs general {'comparator': '>=', 'value': 25}
```

```bash
# Regenerate the CSV + FHIR exports from the canonical JSON
python3 scripts/build.py

# CSV → Parquet, if you want it (needs pandas)
python3 -c "import pandas as pd; pd.read_csv('data/ancestry-reference-ranges.v0.csv').to_parquet('out.parquet')"
```

FHIR consumers: load the Bundle; each entry is an `ObservationDefinition` whose `qualifiedInterval` carries the population (`appliesTo`), `gender`, `age`, and numeric `range`. Provenance tier, evidence grade, overclaim guard, and sources ride on extensions (R4 `ObservationDefinition` has no native citation slot). See [`docs/schema.md`](docs/schema.md).

## Use it as a personal health advisor

Beyond the raw data, this repo ships an **agent-callable** layer:

- **[`mcp-server/`](mcp-server/)** — an MCP server that exposes the dataset as tools (`evaluate_value`, `get_reference`, `screening_for`, …). Add it to Claude Desktop or Claude Code and ask, *"I'm a South Asian man, 34, BMI 24 — what does this mean?"* — you get a cited, ancestry-adjusted answer instead of a guess. It's a **stateless reference oracle**: it holds no user data.
- **[`advisor/`](advisor/)** — system instructions that turn the MCP server into a careful, ancestry-aware health advisor that reviews your labs, honors the overclaim guards, and prepares you for a sharper conversation with your doctor. Your data stays on your machine.

## How to cite

See [`CITATION.cff`](CITATION.cff). A DOI-minted, versioned release (Zenodo) is on the roadmap; until then, cite the repo + version. **And cite the underlying primary sources** — each row names its guideline/study; those authors did the original work.

## Contributing

Corrections, new citations, and coverage requests are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md). Clinical values go through an evidence review before merge; a `study-derived` proposal stays flagged until it clears that bar.

## License

**[CC-BY-4.0](LICENSE)** — use freely, with attribution and the per-row citations preserved.

## Disclaimer

Open Masala is a reference dataset for research and product development. It is **not a medical device**, not clinical advice, and not a substitute for a clinician's judgment. Reference ranges vary by lab and method; screening decisions require individual clinical context.
