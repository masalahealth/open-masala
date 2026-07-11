#!/usr/bin/env python3
"""Open Masala MCP server — an ancestry-adjusted health reference oracle.

Exposes the Open Masala dataset (ancestry-adjusted biomarker reference ranges
and screening thresholds) as MCP tools + resources, so any MCP client can query
cited, provenance-tiered reference values instead of relying on the model's prior.

DESIGN PRINCIPLE — this server is a STATELESS REFERENCE ORACLE. It holds no user
data. `evaluate_value` takes a value as an argument and returns a computed, cited
result; nothing is stored. All personal-data handling lives in the client/advisor
layer, never here. That keeps the server safe to publish and run anywhere.

The evaluation logic lives in `core.py` (no MCP dependency, unit-tested); the
functions below are thin MCP tool/resource wrappers over it.

Run:
    uvx open-masala-mcp                 # from PyPI, no clone
    python -m open_masala_mcp.server    # from a source checkout
"""
import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from . import core

mcp = FastMCP("open-masala")


@mcp.tool()
def list_measures() -> dict:
    """List every analyte / measure in the dataset — what ancestry-adjusted
    coverage exists. Start here."""
    return core.list_measures()


@mcp.tool()
def get_reference(analyte: str) -> dict:
    """Get the ancestry-adjusted reference range(s)/threshold(s) for an analyte,
    each paired with the general-population value, provenance tier, evidence grade,
    citations, and overclaim guard. Matches a LOINC/internal code, id, or name.
    The `code_system` field says whether `loinc` is a real LOINC code or an
    internal `PRAJNA-*` placeholder."""
    return core.get_reference(analyte)


@mcp.tool()
def evaluate_value(analyte: str, value: float, sex: Optional[str] = None,
                   age: Optional[int] = None, unit: Optional[str] = None) -> dict:
    """Evaluate a person's own measured value against the SOUTH-ASIAN-adjusted
    threshold/range for an analyte, returning a status plus the cited rationale
    and overclaim guard. STATELESS: the value is used only to compute this
    response; nothing is stored. A reference lookup, not a diagnosis.

    Pass `sex` for sex-split analytes (HDL, waist) — omitting it returns
    `ambiguous_needs_sex` rather than guessing. Pass `unit` to catch a
    mg/dL-vs-mmol/L mismatch. `status` may be: flag / within_reference /
    category (BMI bands) / screening_applies / caveat / do_not_apply /
    composite_needs_multiple_inputs / ambiguous_needs_sex / unit_mismatch /
    no_south_asian_reference."""
    return core.evaluate_value(analyte, value, sex=sex, age=age, unit=unit)


@mcp.tool()
def screening_for(age: int, sex: Optional[str] = None) -> dict:
    """Which South-Asian-specific screenings/thresholds apply to a person of this
    age (and optional sex). Cited. Not a care plan — a prompt to discuss with a
    clinician."""
    return core.screening_for(age, sex=sex)


@mcp.tool()
def search(query: str) -> dict:
    """Free-text search across analyte names, notes, overclaim guards, and source
    labels, with a lay/clinical synonym layer (e.g. "cholesterol", "sugar",
    "kidney"). Use when you don't know the exact analyte name."""
    return core.search(query)


@mcp.tool()
def list_sources() -> dict:
    """List every unique citation backing the dataset (label, url, ref, kind)."""
    return core.list_sources()


@mcp.resource("open-masala://dataset")
def dataset_resource() -> str:
    """The full canonical dataset as JSON."""
    return json.dumps(core.DATASET, indent=2)


@mcp.resource("open-masala://guidance")
def guidance_resource() -> str:
    """How to use the data responsibly — provenance tiers + overclaim rules."""
    return core.USAGE_RULES + "\n\n" + core.DISCLAIMER


def main() -> None:
    """Console entry point (`open-masala-mcp`)."""
    mcp.run()


if __name__ == "__main__":
    main()
