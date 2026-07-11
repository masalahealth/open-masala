# Open Masala — dataset expansion scope (v0.1 candidates)

_Scoped 2026-07-11. Sources cross-referenced across four internal corpora: `masala-docs/research/` threshold + genetics docs, `tools/evidence/registry.yaml` (113 cited sources), `SouthAsianScreeningPack.swift`, and `biomarker_content.yaml`. Every candidate below already has ≥1 real citation in hand — nothing here is un-sourced._

## Build status — BUILT (2026-07-11): 18 → 41 rows

Both waves are built locally, tests green, exports (CSV + FHIR) regenerated, MCP package copy synced. Version bumped `0.0.1 → 0.1.0`, status `v0.1-expansion-in-progress`. **Every added row carries a verified DOI/PMID/PMCID** — no label-only citations admitted.

- **W1 (+10):** BMI `obese_at` fix (25→27.5), TG≥175, hsCRP≥2, SA-ancestry-risk-enhancer, BMI-23 MASLD, SCORE2 SA multiplier, Enas SA LDL/non-HDL targets, SA CAC percentiles, remnant-C, APOL1 + ALDH2 do-not-apply showcases.
- **W2/W3 (+13):** B12 screening, thalassemia screening (ACOG PB-78), normal-ALT caveat, benign ethnic neutropenia, SLCO1B1 statin PGx (CPIC 2022), pediatric IAP BMI, lean-diabetes, GDM early-screening, menopause age, parity, MTHFR do-not-apply, ApoB/ApoA-I ratio, hypothyroidism emphasis.
- **Skipped (provenance discipline):** `total-cholesterol-sa-caveat` — the Goyal 2007 IJMR citation could not be verified; not minted until a correct source is found.
- **Deferred tail** (need a verified citation before minting): HOMA-IR ethnic-gap caveat (Kanaya 2014 id), homocysteine caveat, ghee→ApoB dietary effect, untreated-DBP→CAC (Moorthy 2024), the "no SA-specific ApoB target / VO₂max" absence-showcase rows, and enriching the existing vitamin-D row with the Siddiqee 2021 prevalence meta.

**Before republish:** update headline stats in `STATUS.md` / `DATASET-README.md` / `README.md` (18→41 rows, 18→35 sources), get clinician sign-off to flip the `review_status: proposed` rows to `approved`, then run the gated republish (dataset version → HF re-upload + new Zenodo DOI + PyPI data bump).

## TL;DR

The v0 dataset is **18 rows, 15 biomarkers, cardiometabolic-only**. There is enough already-cited material to roughly **double it to ~35–40 reference rows** without loosening the provenance bar, plus an optional **genetics/pharmacogenomics facet** that would be genuinely novel (nowhere else machine-readable). The headline stays *density + provenance, not volume* — every new row carries a source, a provenance tier, and an overclaim guard, same as v0.

Two decisions gate the work (see bottom): **(1)** how far to widen the editorial lens beyond cardiometabolic, and **(2)** whether to add a genetics/variant facet with its own schema.

## Guardrails this scope respects (unchanged from v0)

- Only encode **guideline-endorsed** ancestry adjustments as `guideline-endorsed`; cohort/point-estimates ship as `study-derived` with an overclaim guard; a primary study never stands alone.
- **Never invent** an adjustment. Where the SA number equals the general number (same cutoff, higher *prevalence* or tighter *interpretation*), encode it as an `interpretation_caveat` / `screening_emphasis`, not a fake cutoff.
- Keep the **"do-not-apply" showcase rows** (eGFR-style) — they are the credibility differentiator. This scope adds five more.

---

## 0. Data-quality fix to make first (not an addition)

| Row | Current | Should be | Source |
|---|---|---|---|
| `bmi-overweight-category` | `obese_at: 25` | **`obese_at: 27.5`** | WHO Expert Consultation, *Lancet* 2004 — the two Asian action points are **≥23 (increased risk)** and **≥27.5 (high risk)**. `25` looks like a v0 transcription slip. |

Confirm against `loinc.yaml`'s intent before editing; if `25` was deliberate (a different source), document why. This is the one place the current data may be *wrong*, not just incomplete.

---

## Tier A — guideline-endorsed, ready now (fastest; several already cited in `registry.yaml`)

| # | Analyte / row | SA value | General | Provenance | Source (registry id / cite) |
|---|---|---|---|---|---|
| A1 | **SCORE2 risk multiplier** | ×**1.3** (Indian/Bangladeshi), ×**1.7** (Pakistani) | ×1.0 | guideline-endorsed | 2021 ESC CVD Prevention, Class IIa LOE B (*Eur Heart J* 2021;42:3227). *The only major guideline with a numeric SA correction factor — high-value companion to the PREVENT "floor" caveat.* |
| A2 | **SA ancestry = ASCVD risk-enhancer** | ancestry is a formally listed enhancer | n/a | guideline-endorsed | 2018 AHA/ACC Cholesterol Guideline (`ahaAccCholesterol2018`) |
| A3 | **SA very-high-risk lipid targets** | LDL-C **<70**, non-HDL **<100** mg/dL | LDL <100 / non-HDL <130 | study-derived → clinician-gate | Enas / LAI 2013 (`enas-south-asian-lipids-2013`). *Tightens the existing non-HDL-130 row.* |
| A4 | **Triglycerides risk-enhancer** | ≥**175** mg/dL | ≥175 | guideline-endorsed | 2018 AHA/ACC. *Same number; completes the atherogenic-pattern composite inputs.* |
| A5 | **hsCRP risk-enhancer** | >**2** mg/L | >2 | guideline-endorsed (higher SA prevalence) | 2018 AHA/ACC |
| A6 | **Vitamin B12 screening emphasis** | deficiency <200 pg/mL; screen vegetarians | same range | study-derived | Yajnik *AJCN* 2008 (`yajnik-2008`, `refsum-2001`). *Exact parallel to the vitamin-D row.* |
| A7 | **Thalassemia / hemoglobinopathy carrier screen** | offer to SA women (β-thal, HbE, HbD-Punjab) | risk-based | guideline-endorsed | ACOG Practice Bulletin 78 (`acog-practice-bulletin-78`). *Also the mechanism behind the HbA1c caveat — links two rows. Upgrades the app's deferred β-thal rule to guideline-backed.* |
| A8 | **BMI MASLD/fatty-liver screening trigger** | ≥**23** kg/m² | ≥25 | guideline-endorsed | 2023 MASLD nomenclature; Garg *JAHA* 2016 (`south-asian-masld...`) |
| A9 | **GDM early screening** | first-trimester screen for SA ancestry (same 75-g OGTT cutoffs) | screen at 24–28 wk | guideline-endorsed | ADA 2024 §15; FIGO 2015; IADPSG 2010. *New domain: women's health.* |
| A10 | **SLCO1B1 rs4149056 statin PGx** | prefer rosuvastatin/pravastatin in C-allele carriers | same | guideline-endorsed | CPIC 2022 (*Clin Pharmacol Ther* 2022;111:1007). *New domain: pharmacogenomics.* |
| A11 | **Pediatric BMI (IAP 2015)** | overweight ≥75th pct, obese ≥95th pct (= adult 23/27 equiv) | CDC 85th/95th | guideline-endorsed (national body) | Indian Academy of Pediatrics 2015 (Khadilkar). *New domain: pediatric; needs percentile representation.* |

---

## Tier B — study-derived (mostly MASALA), ready with strong overclaim guards

| # | Analyte / row | SA finding | Provenance | Source |
|---|---|---|---|---|
| B1 | **SA-specific CAC age/sex percentiles** | age→CAC>0 prevalence + 75th-pct table (e.g. age 60: ♂70% / ♀40% CAC>0; 75th pct ≈ ♂186 / ♀26) | study-derived | Tasdighi *JACC Adv* 2025, PMID 40402122 (MASALA+DILWALE, n=2,743). **First SA CAC percentiles that exist — genuinely nowhere-else data.** |
| B2 | **Total cholesterol interpretation caveat** | CHD develops at TC ~**170** mg/dL in North Indians — "normal TC ≠ low risk" | study-derived (caveat) | Goyal *IJMR* 2007 (`goyal-...-2007`) |
| B3 | **Remnant cholesterol (optional marker)** | Q4 ≥~**33** mg/dL → 2.6× incident CAC | study-derived | Manghis *J Clin Lipidol* 2025, PMID 41168049 |
| B4 | **ApoB/ApoA-I ratio** | strongest single MI predictor in SA (INTERHEART PAR ~47%) | study-derived | Paré/Yusuf INTERHEART (`interheart-south-asian-2007`). PRAJNA-APOBA1. |
| B5 | **HOMA-IR ethnic-gap caveat** | 2.23 (SA) vs 1.86 (White) — **no SA-specific reference range published**; the "67% higher" figure is a mis-cite | study-derived (caveat) | Kanaya *Diabetes Care* 2014. *Honest-limitation row.* |
| B6 | **Homocysteine caveat** | higher SA mean, driven by **B12 deficiency, not MTHFR** | study-derived (caveat) | Refsum 2001; Yajnik 2008 |
| B7 | **"Normal ALT ≠ no MASLD"** | normal ALT does not exclude fatty liver in SA | study-derived (caveat) | `normal-liver-enzymes-in-masld-meta-analysis` |
| B8 | **Lean-diabetes phenotype** | don't gate diabetes risk on BMI≥25 — T2D at BMI<25 is 2–4× commoner | study-derived | INSPIRED, PMC9076730. *Reinforces the BMI-23 screening trigger.* |
| B9 | **Benign ethnic neutropenia** | ancestry-adjusted lower WBC/ANC normal range | study-derived (caveat) | `atallah-yunes-...-benign-ethnic-neutropenia`. ⚠️ *Best-established for African ancestry; SA evidence is thinner — ship with that caveat or hold.* |

---

## Tier C — women's-health domain (new; well-cited but widens the lens)

| # | Row | SA finding | Source |
|---|---|---|---|
| C1 | Age at natural menopause | median **49**; ~**30% early/premature (≤45)** vs <7% other US groups | Lyu *Climacteric* 2025 |
| C2 | Parity (≥2 births) cardiometabolic effect | over 5 y: SBP +8.9, DBP +4.1 mmHg, LDL +8.9 mg/dL vs 0–1 parity | Mehta *JACC Adv* 2026 |

---

## Tier D — genetics / variant facet (highest differentiation, biggest schema change)

These do **not** fit the reference-range schema (they are variant / carrier-frequency / odds-ratio, not `low/high/comparator`). They would need a **parallel table** (`variant, gene, sa_frequency, general_frequency, effect_OR, actionability, provenance, sources`). Candidates, all cited:

- **MYBPC3 Δ25bp** — SA HCM founder allele, ~4–6% carriers, OR ~5–7× for cardiomyopathy/HF; test on HCM/DCM/SCD family history (Dhandapany *Nat Genet* 2009).
- **Familial hypercholesterolemia** (LDLR/APOB/PCSK9) — ~1:250; SA mutation spectrum differs (LDLR 92%, APOB R3527Q rare); trigger at untreated LDL ≥190 (Setia *JCL* 2020).
- **TCF7L2 rs7903146** — T2D OR **1.89** in Indians (larger than European effect; Chauhan *Diabetes* 2010).
- **MODY triggers** — young-onset (<30) + autosomal-dominant family history + low BMI → monogenic-diabetes referral; changes treatment (sulfonylurea-responsive).
- **Lp(a)/LPA** — genetic framing of the existing Lp(a) row (KIV-2 copy number; ~80–90% heritable).

---

## Do-NOT-add — new credibility-showcase rows (eGFR-style)

Encoding what *not* to apply is as valuable as what to apply. Five well-sourced "don't":

| Claim to refute | Why | Source |
|---|---|---|
| **APOL1** kidney-risk variants for SA | West-African ancestry only (<1% non-African) | PMC5495568 |
| **ALDH2\*2 / ADH1B\*2** alcohol-flush warnings for SA | Predominantly East Asian; low single-digit % in SA | PMC10594868 |
| **MTHFR C677T** as "the SA homocysteine variant" | Variant not enriched in SA — the driver is dietary B12 deficiency; treat B12, not the SNP | genetics doc |
| **SA-specific eGFR coefficient** | Already shipped as the v0 deprecated row — keep | CKD-EPI 2021 |
| **A separate SA ApoB target** | No guideline body has issued one; same target, higher LDL-ApoB discordance prior | ethnic-thresholds ref |
| **SA-specific VO₂max cutoff** | No consensus body has issued one | ethnic-thresholds ref |

---

## Sizing & sequencing

| Wave | Rows | Effort | Why this order |
|---|---|---|---|
| **W1 — the BMI fix + Tier A registry-cited** (A2, A3, A4, A5, A6, A7, A8) | ~7 + 1 fix | Low — sources already in `registry.yaml`, extraction only | Highest provenance, zero new-citation work, stays cardiometabolic |
| **W2 — Tier A new-domain + Tier B** (A1, A9, A10, A11, B1–B8) | ~12 | Medium — some need new registry entries + clinician sign-off | Adds the marquee novel data (SCORE2 multiplier, SA CAC percentiles) |
| **W3 — Tier C + do-not-add showcases** | ~7 | Low–medium | Rounds out honesty rows + women's health |
| **W4 — Tier D genetics facet** | new table | High — new schema, FHIR mapping, heavy clinician gating | Do only if we commit to the genetics differentiation |

W1+W2+W3 ≈ **18 → ~40 rows**, all in the current schema, ~2–3× coverage with provenance intact.

## ⚠️ Provenance gate discovered (2026-07-11) — read before building

Pulling the **exact** citation fields from `registry.yaml` (not reconstructing from memory) surfaced a blocker: **roughly half the candidate sources are label-only** — `url: null, doi: null, pmid: null`. These are the "43 `no_url` gaps" the provenance doc discloses. Because the dataset's core promise is *every value resolves to a named, checkable source*, a row whose only citation is a bare label would **expand** that gap, not honor it.

**Citation-ready NOW** (resolvable identifier in hand, mostly sources already in v0):
- **2018 AHA/ACC Cholesterol Guideline** — `DOI:10.1161/CIR.0000000000000625` → TG≥175 (A4), hsCRP>2 (A5), SA-ancestry-risk-enhancer (A2).
- **Enas / LAI 2013** — `PMCID:PMC3868060` → SA very-high-risk LDL<70 / non-HDL<100 (A3).
- **Garg *JAHA* 2016** — `PMID:27856485` → BMI-23 MASLD trigger (A8).
- **APOL1** `PMC5495568`, **ALDH2/ADH1B** `PMC10594868` → two do-not-add showcase rows.
- **ESC 2021 CVD Prevention** — `DOI:10.1093/eurheartj/ehab484` → SCORE2 SA multiplier (A1) *(new source; resolvable)*.
- Plus the MASALA-doc rows that already carry PMIDs: **Tasdighi 2025** `PMID:40402122` (CAC percentiles, B1), **Manghis 2025** `PMID:41168049` (remnant-C, B3), **Kanaya 2014** (HOMA-IR caveat, B5).

**Needs a citation-backfill pass first** (label-only in the registry — run the registry `validate`/`discover` DOI-resolver, or backfill the PMIDs the masala-docs already list, before minting the row):
- Yajnik B12 2008, Refsum 2001 (B12 row, A6)
- ACOG Practice Bulletin 78 (thalassemia screen, A7)
- Goyal 2007 (TC~170 caveat, B2)
- Normal-liver-enzymes MASLD meta (ALT caveat, B7)
- Atallah-Yunes benign ethnic neutropenia (B9)
- MASLD-prevalence meta (supports A8)

**Revised sequencing:** insert a **W0 — citation backfill** before W1. W0 = resolve DOI/PMID for the ~7 label-only sources above (identifiers exist; they just aren't in the registry rows yet). Only then do the label-only candidates become citation-grade. The "citation-ready now" set can be authored immediately in parallel.

## Provenance cost note

Every W1 candidate is already an `approved` source in `registry.yaml` — extraction, not research. W2/W3 add ~8–10 new registry entries (Tasdighi 2025, Manghis 2025, Lyu 2025, Mehta 2026, CPIC 2022, IAP 2015, ESC 2021, ACOG PB-78), each needing the standard `discover → proposed → clinician-approved` path before its row flips from `study-derived` provisional to citable. Tier D would roughly double the citation base again.

---

## Decisions — LOCKED (2026-07-11)

1. **Editorial lens: maximal cited breadth.** Include every well-cited candidate across all domains — cardiometabolic, women's health, pediatric, hematology, pharmacogenomics — plus the softer borderline items where a real citation exists (hypothyroidism screening emphasis, ghee→ApoB dietary effect size, untreated-DBP→CAC). Anything without a citation stays out.
2. **Genetics/variant facet (Tier D): skipped for v0.x.** Keep the dataset a pure reference-range/threshold table in the current schema. Ship the ~40-row expansion first; revisit the parallel variant table later.

### Build manifest (in schema; all reference-range rows)

- **Fix:** `bmi-overweight-category` → `obese_at: 27.5`.
- **Add (guideline-endorsed):** SCORE2 SA multiplier (A1), SA-ancestry-risk-enhancer (A2), TG≥175 (A4), hsCRP>2 (A5), B12 screening (A6), thalassemia screening (A7), BMI-23 MASLD (A8), GDM early screen (A9), SLCO1B1 PGx (A10), IAP pediatric BMI (A11).
- **Add (study-derived + overclaim guards):** Enas SA LDL<70/non-HDL<100 (A3), SA CAC percentiles (B1), TC~170 caveat (B2), remnant-C (B3), ApoB/ApoA-I ratio (B4), HOMA-IR caveat (B5), homocysteine caveat (B6), normal-ALT caveat (B7), lean-diabetes (B8), benign ethnic neutropenia (B9, with the African-ancestry caveat), untreated-DBP→CAC, hypothyroidism emphasis, ghee→ApoB dietary effect.
- **Add (do-not-apply showcases):** APOL1, ALDH2/ADH1B, MTHFR-as-SNP, no-SA-ApoB-target, no-SA-VO₂max.
- **New source registry entries needed** (draft as `review_status: proposed`, clinician-gate before `approved`): Tasdighi 2025, Manghis 2025, Lyu 2025, Mehta 2026, CPIC 2022, IAP 2015, ESC 2021, ACOG PB-78, INSPIRED, Moorthy 2024, plus the East/West-ancestry "do-not-add" refs.

_Republish (new dataset version → HF re-upload + new Zenodo DOI + PyPI data bump) is a separate, explicitly-gated step — the same boundary we used for the 0.0.2 server release._
