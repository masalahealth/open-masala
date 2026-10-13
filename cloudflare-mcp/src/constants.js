export const DISCLAIMER =
  "Open Masala is a reference dataset for research/product development \u2014 not a medical device, not clinical advice. Reference ranges vary by lab and method; decisions require individual clinical context. v0, not yet clinician-reviewed.";
export const USAGE_RULES =
  'How to use Open Masala data responsibly (read before answering a user):\n- Every value carries a `provenance_tier`. Report it.\n  * guideline-endorsed \u2192 may be stated as guideline-backed.\n  * study-derived \u2192 say "some studies suggest", NEVER "guidelines recommend".\n  * contested-deprecated \u2192 tell the user NOT to apply this adjustment.\n- Every row carries an `overclaim_guard` \u2014 the claim you must NOT make. Honor it verbatim.\n- Never invent an ancestry adjustment that isn\'t in the data.\n- Always cite the source(s) attached to a row.\n- Always defer diagnosis and treatment to a clinician.\n';
export const GUIDANCE_POINTER =
  "Usage rules + full disclaimer: read the open-masala://guidance resource (also returned in full by get_reference / evaluate_value).";
export const SYNONYMS = {
  cholesterol: ["hdl", "apob", "non-hdl", "ldl", "lipid", "lp(a)"],
  lipids: [
    "hdl",
    "apob",
    "non-hdl",
    "triglyc",
    "lipid",
    "lp(a)",
    "atherogenic",
  ],
  lipid: ["hdl", "apob", "non-hdl", "triglyc", "lp(a)", "atherogenic"],
  sugar: ["hba1c", "glucose", "diabetes", "insulin"],
  bloodsugar: ["hba1c", "glucose", "diabetes"],
  glucose: ["hba1c", "glucose", "diabetes"],
  diabetes: ["diabetes", "hba1c", "glucose", "bmi"],
  prediabetes: ["hba1c", "glucose", "diabetes"],
  insulinresistance: ["insulin", "hba1c"],
  kidney: ["egfr", "creatinine"],
  renal: ["egfr"],
  weight: ["bmi", "waist", "obesity"],
  obesity: ["bmi", "waist"],
  waistline: ["waist"],
  heart: ["ascvd", "cac", "coronary", "apob", "prevent", "calcium"],
  cardiac: ["cac", "coronary", "ascvd", "calcium"],
  cardiovascular: ["ascvd", "cac", "apob", "prevent"],
  vitamind: ["vitamin d", "25-oh"],
  triglycerides: ["triglyc", "atherogenic"],
};
export const MEASURE_TYPE_PREFERENCE = {
  reference_range: 0,
  risk_flag: 1,
  screening_threshold: 2,
  screening_age: 3,
  interpretation_caveat: 4,
  deprecated_adjustment: 5,
};
