import DATASET from "./dataset.json" with { type: "json" };
import {
  DISCLAIMER,
  USAGE_RULES,
  GUIDANCE_POINTER,
  SYNONYMS,
  MEASURE_TYPE_PREFERENCE,
} from "./constants.js";
export { DATASET, DISCLAIMER, USAGE_RULES };
const ROWS = DATASET.rows;
const special = new Set([
  "screening_age",
  "interpretation_caveat",
  "deprecated_adjustment",
]);
const norm = (x) => x.trim().toLowerCase();
const codeSystem = (x) =>
  !x ? null : x.startsWith("PRAJNA-") ? "internal-placeholder" : "loinc";
const matches = (q) => {
  q = norm(q);
  return ROWS.filter(
    (r) =>
      (r.loinc || "").toLowerCase() === q ||
      r.id.toLowerCase() === q ||
      r.analyte.toLowerCase().includes(q) ||
      r.id.toLowerCase().includes(q),
  );
};
const ageOK = (r, a) =>
  a == null ||
  ((r.age?.min == null || a >= r.age.min) &&
    (r.age?.max == null || a <= r.age.max));
const sexOK = (r, s) => r.sex === "any" || (!!s && r.sex.startsWith(s[0]));
const slim = (r) => ({
  id: r.id,
  analyte: r.analyte,
  loinc: r.loinc ?? null,
  code_system: codeSystem(r.loinc),
  unit: r.unit,
  population: r.population,
  sex: r.sex,
  age: r.age ?? null,
  measure_type: r.measure_type,
  south_asian_value: r.sa_value ?? null,
  general_population_value: r.general_value ?? null,
  direction_of_risk: r.direction_of_risk,
  provenance_tier: r.provenance_tier,
  evidence_grade: r.evidence_grade ?? null,
  sources: r.sources,
  overclaim_guard: r.overclaim_guard ?? null,
  notes: r.notes ?? null,
});
export function list_measures() {
  return {
    dataset: DATASET.dataset,
    version: DATASET.version,
    count: ROWS.length,
    measures: ROWS.map((r) => ({
      id: r.id,
      analyte: r.analyte,
      loinc: r.loinc ?? null,
      code_system: codeSystem(r.loinc),
      measure_type: r.measure_type,
      provenance_tier: r.provenance_tier,
    })),
    guidance: GUIDANCE_POINTER,
  };
}
export function get_reference(analyte) {
  const hits = matches(analyte);
  return hits.length
    ? {
        query: analyte,
        matches: hits.map(slim),
        usage_rules: USAGE_RULES,
        disclaimer: DISCLAIMER,
      }
    : {
        query: analyte,
        matches: [],
        hint: "Call list_measures() to see coverage, or search() if you don't know the exact name.",
      };
}
function target(v) {
  if (!v || typeof v !== "object") return null;
  if ("comparator" in v && "value" in v) return ["cmp", v.comparator, v.value];
  if ("elevated_at" in v) return ["cmp", ">=", v.elevated_at];
  if ("overweight_at" in v || "obese_at" in v)
    return ["bands", v.overweight_at ?? null, v.obese_at ?? null];
  if ("triglycerides_mg_dl" in v || "with_low_hdl" in v)
    return [
      "composite",
      ["triglycerides (mg/dL)", "HDL-C (low, sex-specific)"],
    ];
  if ("low" in v || "high" in v)
    return ["range", v.low ?? null, v.high ?? null];
  return null;
}
const guidance = (v) =>
  !v || typeof v !== "object"
    ? null
    : ["guidance", "confirm_when", "confirm_with", "adjustment"]
        .filter((k) => k in v)
        .map((k) => `${k.replaceAll("_", " ")}: ${v[k]}`)
        .join("; ") || null;
const rank = (r, q) =>
  (r.loinc || "").toLowerCase() === q ||
  r.id.toLowerCase() === q ||
  r.analyte.toLowerCase() === q
    ? 0
    : r.analyte.toLowerCase().startsWith(q)
      ? 1
      : r.id.toLowerCase().startsWith(q)
        ? 2
        : 3;
function evaluateRow(r, value) {
  const v = r.sa_value,
    t = target(v),
    mt = r.measure_type;
  if (mt === "screening_age" && v?.value != null) {
    const applies = value >= v.value;
    return {
      status: applies ? "screening_applies" : "screening_not_yet",
      explanation: `Age ${value} ${applies ? ">=" : "<"} South Asian screening start age ${v.value} → ${applies ? "screening applies" : "not yet at screening age"}.`,
    };
  }
  if (mt === "interpretation_caveat")
    return {
      status: "caveat",
      explanation:
        guidance(v) ||
        "Interpretation caveat — see south_asian_target and overclaim_guard.",
    };
  if (mt === "deprecated_adjustment")
    return {
      status: "do_not_apply",
      explanation:
        guidance(v) || "Do NOT apply an ancestry adjustment to this measure.",
    };
  if (t?.[0] === "cmp") {
    const ops = {
      ">=": (a, b) => a >= b,
      ">": (a, b) => a > b,
      "<=": (a, b) => a <= b,
      "<": (a, b) => a < b,
      "==": (a, b) => a === b,
    };
    const op = ops[t[1]];
    if (!op)
      return {
        status: "informational",
        explanation: `Unrecognized comparator '${t[1]}'.`,
        south_asian_target: v,
      };
    const flag = op(value, t[2]);
    return {
      status: flag ? "flag" : "within_reference",
      explanation: `${value} ${t[1]} ${t[2]} → ${flag ? "meets" : "does not meet"} the South Asian concern threshold (${r.direction_of_risk}-is-risk).`,
    };
  }
  if (t?.[0] === "bands") {
    const category =
      t[2] != null && value >= t[2]
        ? "obese"
        : t[1] != null && value >= t[1]
          ? "overweight"
          : "normal";
    return {
      status: "category",
      category,
      explanation: `${value} ${r.unit} → South Asian category '${category}' (overweight >= ${t[1]}, obese >= ${t[2]}).`,
    };
  }
  if (t?.[0] === "range") {
    const flag =
      (t[1] != null && value < t[1]) || (t[2] != null && value > t[2]);
    return {
      status: flag ? "flag" : "within_reference",
      explanation: `${value} vs South Asian reference [${t[1] ?? "-"}, ${t[2] ?? "-"}] ${r.unit} → ${flag ? "outside" : "within"} range.`,
    };
  }
  if (t?.[0] === "composite")
    return {
      status: "composite_needs_multiple_inputs",
      required_fields: t[1],
      explanation: `'${r.analyte}' is a composite pattern needing multiple inputs (${t[1].join(", ")}); a single value cannot evaluate it. Provide each component and compare separately.`,
    };
  return {
    status: "informational",
    explanation: `No simple numeric rule for this row (measure_type=${mt}); see south_asian_target for the raw thresholds.`,
    south_asian_target: v,
  };
}
export function evaluate_value(
  analyte,
  value,
  sex = null,
  age = null,
  unit = null,
) {
  let c = matches(analyte).filter(
    (r) => r.population === "south_asian" || special.has(r.measure_type),
  );
  if (c.length) {
    const q = norm(analyte),
      best = Math.min(...c.map((r) => rank(r, q)));
    c = c.filter((r) => rank(r, q) === best);
  }
  if (!c.length)
    return {
      analyte,
      value,
      status: "no_south_asian_reference",
      hint: "Call list_measures() / search() / get_reference() to see coverage.",
      disclaimer: DISCLAIMER,
    };
  if (age != null) {
    const aged = c.filter((r) => ageOK(r, age));
    if (!aged.length)
      return {
        analyte,
        value,
        age_used: age,
        status: "no_reference_for_age",
        hint: `Row(s) exist for '${analyte}' but none cover age ${age}.`,
        available_age_bands: c.map((r) => ({ id: r.id, age: r.age ?? null })),
        disclaimer: DISCLAIMER,
      };
    c = aged;
  }
  const sexes = [
    ...new Set(c.filter((r) => r.sex !== "any").map((r) => r.sex)),
  ].sort();
  if (sex) {
    const s = norm(sex),
      sexed = c.filter((r) => sexOK(r, s));
    if (!sexed.length)
      return {
        analyte,
        value,
        sex_used: sex,
        status: "no_reference_for_sex",
        hint: `No '${analyte}' row for sex '${sex}'.`,
        disclaimer: DISCLAIMER,
      };
    c = sexed;
  } else if (sexes.length > 1)
    return {
      analyte,
      value,
      status: "ambiguous_needs_sex",
      available_sexes: sexes,
      hint: "This analyte is sex-split; pass sex='male' or sex='female' to evaluate.",
      disclaimer: DISCLAIMER,
    };
  c.sort(
    (a, b) =>
      (MEASURE_TYPE_PREFERENCE[a.measure_type] ?? 9) -
        (MEASURE_TYPE_PREFERENCE[b.measure_type] ?? 9) ||
      (target(a.sa_value) ? 0 : 1) - (target(b.sa_value) ? 0 : 1),
  );
  const r = c[0],
    expected = r.unit,
    unitNorm = (x) => (x || "").replaceAll(/\s/g, "").toLowerCase();
  if (unit != null && unitNorm(unit) !== unitNorm(expected))
    return {
      analyte: r.analyte,
      expected_unit: expected,
      unit_provided: unit,
      value,
      status: "unit_mismatch",
      warning: `You passed unit '${unit}' but the reference is in '${expected}'. Convert to '${expected}' and re-evaluate; not flagging to avoid a wrong answer.`,
      south_asian_target: r.sa_value ?? null,
      measure_type: r.measure_type,
      sources: r.sources,
      disclaimer: DISCLAIMER,
    };
  const e = evaluateRow(r, value),
    out = {
      analyte: r.analyte,
      expected_unit: expected,
      value,
      unit_provided: unit,
      status: e.status,
      explanation: e.explanation,
      sex_used: sex,
      age_used: age,
      loinc: r.loinc ?? null,
      code_system: codeSystem(r.loinc),
      measure_type: r.measure_type,
      south_asian_target: r.sa_value ?? null,
      general_population_target: r.general_value ?? null,
      direction_of_risk: r.direction_of_risk,
      provenance_tier: r.provenance_tier,
      evidence_grade: r.evidence_grade ?? null,
      sources: r.sources,
      overclaim_guard: r.overclaim_guard ?? null,
      notes: r.notes ?? null,
      usage_rules: USAGE_RULES,
      disclaimer: DISCLAIMER,
    };
  for (const k of ["category", "required_fields"]) if (k in e) out[k] = e[k];
  if (c.length > 1) out.also_available = c.slice(1).map((r) => r.id);
  return out;
}
export function screening_for(age, sex = null) {
  const s = norm(sex || "");
  return {
    age,
    sex,
    applicable: ROWS.filter(
      (r) =>
        r.population === "south_asian" &&
        [
          "screening_threshold",
          "screening_age",
          "risk_flag",
          "interpretation_caveat",
        ].includes(r.measure_type) &&
        ageOK(r, age) &&
        (!s || sexOK(r, s)),
    ).map(slim),
    guidance: GUIDANCE_POINTER,
  };
}
export function search(query) {
  const raw = norm(query),
    tokens = raw.split(/[^a-z0-9()]+/).filter(Boolean);
  if (!tokens.length)
    return { query, matches: [], count: 0, guidance: GUIDANCE_POINTER };
  const syn = SYNONYMS[raw.replaceAll(/[^a-z0-9]/g, "")];
  const hits = ROWS.filter((r) => {
    const hay = [
      r.analyte,
      r.id,
      r.loinc || "",
      r.notes || "",
      r.overclaim_guard || "",
      ...r.sources.map((s) => s.label),
    ]
      .join(" ")
      .toLowerCase();
    return (
      syn?.some((t) => hay.includes(t)) ||
      tokens.every((t) =>
        [t, ...(SYNONYMS[t] || [])].some((v) => hay.includes(v)),
      )
    );
  });
  return {
    query,
    matches: hits.map(slim),
    count: hits.length,
    guidance: GUIDANCE_POINTER,
  };
}
export function list_sources() {
  const seen = new Set(),
    sources = [];
  for (const r of ROWS)
    for (const s of r.sources) {
      const key = s.ref || s.url || s.label;
      if (!seen.has(key)) {
        seen.add(key);
        sources.push(s);
      }
    }
  return { count: sources.length, sources };
}
