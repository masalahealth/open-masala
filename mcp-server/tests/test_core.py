"""Acceptance tests for the Open Masala reference oracle.

Each test maps to a numbered item in the code review (open-masala-mcp-feedback).
Run:  cd mcp-server && PYTHONPATH=$PWD python -m pytest tests/ -q
`core` imports no MCP SDK, so these run without `mcp` installed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from open_masala_mcp import core  # noqa: E402


# --- Fix 1: evaluate the previously un-evaluable marquee analytes ----------- #
def test_bmi_returns_category_naming_sa_cutoff():
    r = core.evaluate_value("BMI", 24)
    assert r["status"] == "category"
    assert r["category"] == "overweight"          # 23 <= 24 < 25
    assert "23" in r["explanation"]               # names the SA overweight cutoff

def test_bmi_normal_and_obese_bands():
    assert core.evaluate_value("BMI", 22)["category"] == "normal"
    assert core.evaluate_value("BMI", 26)["category"] == "obese"

def test_lpa_single_elevated_threshold_flags():
    r = core.evaluate_value("Lp(a)", 50)          # elevated_at 50 → treated as >=
    assert r["status"] == "flag"

def test_atherogenic_composite_does_not_dead_end():
    r = core.evaluate_value("atherogenic dyslipidemia", 160)
    assert r["status"] == "composite_needs_multiple_inputs"
    assert "required_fields" in r and len(r["required_fields"]) >= 2


# --- Fix 2: sex-specific analytes must not silently guess a sex ------------- #
def test_hdl_without_sex_is_ambiguous():
    r = core.evaluate_value("HDL", 45)
    assert r["status"] == "ambiguous_needs_sex"
    assert set(r["available_sexes"]) == {"female", "male"}

def test_hdl_male_within_reference():
    assert core.evaluate_value("HDL", 45, sex="male")["status"] == "within_reference"

def test_hdl_female_flags():
    assert core.evaluate_value("HDL", 45, sex="female")["status"] == "flag"


# --- Fix 3: age must measurably change row selection ------------------------ #
def test_age_filters_out_of_band_row():
    # fasting insulin row is age.min 30 → no reference below the band.
    below = core.evaluate_value("fasting insulin", 8, age=25)
    assert below["status"] == "no_reference_for_age"
    within = core.evaluate_value("fasting insulin", 8, age=35)
    assert within["status"] in ("within_reference", "flag")


# --- Fix 4: screening-age / caveat rows never return `flag` ----------------- #
def test_screening_age_is_not_a_flag():
    r = core.evaluate_value("Diabetes screening start age", 40)
    assert r["status"] == "screening_applies"

def test_no_screening_age_row_ever_flags():
    for row in core.ROWS:
        if row["measure_type"] != "screening_age":
            continue
        thr = row["sa_value"]["value"]
        for v in (thr - 5, thr, thr + 5):
            assert core.evaluate_value(row["analyte"], v)["status"] != "flag"

def test_deprecated_egfr_says_do_not_apply():
    r = core.evaluate_value("eGFR", 55)
    assert r["status"] == "do_not_apply"

def test_interpretation_caveat_returns_caveat():
    r = core.evaluate_value("HbA1c", 6.0)
    assert r["status"] == "caveat"


# --- Fix 5: code_system distinguishes real LOINC from placeholders ---------- #
def test_code_system_flags_placeholders():
    ref = core.get_reference("BMI")
    bmi = next(m for m in ref["matches"] if m["id"] == "bmi-overweight-category")
    assert bmi["code_system"] == "internal-placeholder"
    hdl = core.get_reference("2085-9")["matches"][0]
    assert hdl["code_system"] == "loinc"


# --- Fix 6: synonym-aware discovery ---------------------------------------- #
def test_search_cholesterol_surfaces_lipids():
    ids = {m["id"] for m in core.search("cholesterol")["matches"]}
    assert {"hdl-low-male", "apob-preferred-marker"} & ids
    assert len(ids) >= 3

def test_search_sugar_surfaces_glycemic_rows():
    ids = {m["id"] for m in core.search("sugar")["matches"]}
    assert "hba1c-under-read-caveat" in ids

def test_search_multiword_and_semantics():
    # both terms (via synonyms) must be present in a row
    assert core.search("insulin resistance")["count"] >= 1


# --- Fix 7: unit safety ----------------------------------------------------- #
def test_unit_mismatch_does_not_flag():
    r = core.evaluate_value("HDL", 1.2, sex="male", unit="mmol/L")
    assert r["status"] == "unit_mismatch"
    assert r["expected_unit"] == "mg/dL"

def test_matching_unit_evaluates_normally():
    r = core.evaluate_value("HDL", 45, sex="male", unit="mg/dl")   # case-insensitive
    assert r["status"] == "within_reference"

def test_expected_unit_surfaced_top_level():
    r = core.evaluate_value("HDL", 45, sex="male")
    assert r["expected_unit"] == "mg/dL"


# --- Fix 8: token-light tools carry a pointer, not the full block ----------- #
def test_light_tools_use_pointer_not_full_rules():
    for payload in (core.list_measures(), core.screening_for(45), core.search("bmi")):
        assert "usage_rules" not in payload
        assert "guidance" in payload

def test_value_tools_still_carry_full_rules():
    assert "usage_rules" in core.get_reference("BMI")
    assert "usage_rules" in core.evaluate_value("BMI", 24)


# --- Regression: existing numeric paths still work -------------------------- #
def test_waist_range_and_apob_still_evaluate():
    assert core.evaluate_value("waist", 95, sex="male")["status"] == "flag"     # >= 90
    assert core.evaluate_value("ApoB", 75)["status"] == "within_reference"      # [60,90]

def test_unknown_analyte_reports_no_reference():
    assert core.evaluate_value("ferritin", 10)["status"] == "no_south_asian_reference"
