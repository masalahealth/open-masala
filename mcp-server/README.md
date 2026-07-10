# Open Masala MCP server

An **ancestry-adjusted health reference oracle** over the [Open Masala dataset](../README.md), exposed via the [Model Context Protocol](https://modelcontextprotocol.io) so any MCP client — Claude Desktop, Claude Code, an agent — can query cited, provenance-tiered reference values as tool calls.

## Design principle: it holds no user data

The server is a **stateless reference oracle**. Tools like `evaluate_value` take a value as an argument and return a computed, cited result — nothing is stored, and no personal data ever lives here. All handling of a person's actual labs happens in the *client / advisor* layer (see [`../advisor/`](../advisor/)), never in this server. That's what makes it safe to publish and run anywhere.

## Tools

| Tool | What it does |
|---|---|
| `list_measures()` | Every analyte/measure in the dataset — the coverage map. Start here. |
| `get_reference(analyte)` | Ancestry-adjusted range(s)/threshold(s) for an analyte, paired with the general-population value, provenance tier, grade, citations, and overclaim guard. Matches a LOINC code, id, or name. |
| `evaluate_value(analyte, value, sex?, age?)` | Compare a person's own value against the South-Asian-adjusted threshold; returns a flag status + cited rationale + overclaim guard. Stateless. |
| `screening_for(age, sex?)` | Which SA-specific screenings/thresholds apply to a person of this age/sex. Cited. |
| `search(query)` | Free-text search across analytes, notes, guards, and sources. |
| `list_sources()` | Every unique citation backing the dataset. |

## Resources

- `open-masala://dataset` — the full canonical JSON.
- `open-masala://guidance` — the provenance-tier + overclaim usage rules a client should follow.

## Install & run

```bash
pip install "mcp[cli]"
python3 mcp-server/server.py        # stdio transport
```

## Add to Claude Desktop

Edit `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "open-masala": {
      "command": "python3",
      "args": ["/absolute/path/to/open-masala/mcp-server/server.py"]
    }
  }
}
```

Restart Claude Desktop; the Open Masala tools appear in the tools menu. Now you can ask, e.g., *"I'm a South Asian man, 34, BMI 24 — what does Open Masala say?"* and Claude will call `evaluate_value` / `screening_for` and answer with cited, guard-respecting reference values.

## Add to Claude Code

```bash
claude mcp add open-masala -- python3 /absolute/path/to/open-masala/mcp-server/server.py
```

## Responsible-use contract

Every tool response includes `usage_rules` and a `disclaimer`. Clients (and the LLMs driving them) should:
- **Report the `provenance_tier`** — never present a `study-derived` value as guideline-backed, and tell the user *not* to apply a `contested-deprecated` adjustment.
- **Honor the `overclaim_guard`** on every row.
- **Cite the sources** attached to each row.
- **Defer diagnosis and treatment to a clinician.**

This is a reference dataset, **not a medical device**.
