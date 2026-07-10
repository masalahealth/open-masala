# Governance & scientific credibility

Two questions shape what this dataset does and doesn't contain: *why don't you just use the cohort data?* and *isn't adjusting medicine by ancestry the thing the field is moving away from?* Both deserve a straight answer.

## Why we don't ship primary cohort data

The studies these numbers come from — MASALA, GenomeAsia 100K, UK Biobank, GenomeIndia and others — are access-controlled, for good reasons:

- **Re-identification risk.** You can't truly anonymize a genome — it *is* an identifier, and it implicates relatives who never consented. Public release was never on the table; the compromise is controlled access under a Data Use Agreement.
- **Consent scope.** Participants consented to specific uses, often years ago. A biobank is legally bound to that scope and cannot hand data to a commercial product.
- **The open surface is aggregate.** Allele-frequency browsers expose population-level summary statistics — safe, because you can't re-identify anyone from a frequency — while individual records stay gated. Aggregate = open, individual = gated is the whole model.
- **Data sovereignty.** South Asian data specifically is governed by national frameworks (e.g. India's DPDP Act) and a real concern about extractive "helicopter research." National cohorts are sovereign projects.

So Open Masala is deliberately **downstream** of that data: we synthesize the *published thresholds* those cohorts produced into a cited, machine-readable table. We were never going to hold raw cohort data, and we don't need it. This is a synthesis contribution, not a primary-data claim.

## The eGFR lesson: only encode guideline-endorsed adjustments

### What happened
The older CKD-EPI equation had a **race coefficient** that raised estimated kidney function for Black patients at the same creatinine — making their kidneys look *healthier* than they were. In 2021 the equation was refit to **remove race entirely**.

### Why it was retired
Two reasons: race is a **social, not biological, construct** — the coefficient was a crude proxy that didn't hold up; and it caused **measurable harm** — patients appeared less sick, delaying referral and specialist care. The retirement was an equity correction.

### The distinction that governs this dataset
The eGFR case was a **race coefficient inside a biological estimating equation** — that is what was retired. The South Asian cutoffs in this dataset (BMI ≥23, IDF waist, earlier screening) are a **different category**: *ethnicity-specific screening thresholds that are themselves guideline-endorsed*. Those aren't contested — they're recommended.

So the rule is not "never stratify by ancestry." It is:

> **Only encode ancestry adjustments that a guideline endorses. Never invent your own. Explicitly flag the contested ones.**

### How we handle it
eGFR appears in the dataset as a `contested-deprecated` row that says, in machine-readable form, *do not apply a race/ancestry adjustment here — and here's the citation for why.* Likewise, the 10-year risk score (PREVENT) is flagged as under-estimating South Asian risk **without** inventing a multiplier that doesn't exist in the evidence. Including these rows — and refusing to fabricate adjustments — is the point: it's what separates a dataset you can build on from one that hasn't read the room.
