# Open Masala Advisor — a health advisory engine you run yourself

This turns the Open Masala dataset into a **personal, ancestry-aware health advisor** — the kind of "review my labs and tell me what to ask my doctor" experience, calibrated for South Asian biology, running on your own machine with your data staying local.

It's two parts:
1. **The [MCP server](../mcp-server/)** — serves the cited, ancestry-adjusted reference values as tools.
2. **[`ADVISOR.md`](ADVISOR.md)** — the system instructions that make the assistant behave like a careful advisor (reports provenance tiers, honors overclaim guards, defers to clinicians).

> ⚠️ Not a medical device, not clinical advice. It prepares you for a better conversation with your physician — it does not replace one.

## Setup (Claude Desktop, ~5 minutes)

1. **Add the MCP server to Claude Desktop** — edit `~/Library/Application Support/Claude/claude_desktop_config.json` ([`uv`](https://docs.astral.sh/uv/) fetches it from PyPI, no clone):
   ```json
   {
     "mcpServers": {
       "open-masala": {
         "command": "uvx",
         "args": ["open-masala-mcp"]
       }
     }
   }
   ```
   Restart Claude Desktop.
3. **Create a project** (or a chat) and paste the contents of [`ADVISOR.md`](ADVISOR.md) as the system prompt / project instructions.
4. **Give it your data.** Put your lab PDFs, a genetic report, and a short profile (ancestry, age, sex, diet, meds, family history) in a folder, or paste them into the chat. Then ask:
   > *"Review my labs. I'm a 34-year-old South Asian man, vegetarian. What should I pay attention to and ask my doctor?"*

The advisor will call `evaluate_value`, `get_reference`, and `screening_for` against Open Masala and answer with **cited, ancestry-adjusted, guard-respecting** findings.

## Works with

- **Claude Desktop** — the setup above.
- **Claude Code** — `claude mcp add open-masala -- uvx open-masala-mcp`, then drop `ADVISOR.md` into your project.
- **Any MCP-capable client / your own agent** — point it at the server and use `ADVISOR.md` as the system prompt.

## Why it's built this way

- **Your data stays local.** The MCP server is a stateless reference oracle — it only ever receives the single value you ask it to check, and stores nothing. Your record never leaves your machine.
- **Grounded, not hallucinated.** Every ancestry-adjusted claim comes from a cited dataset row, with its evidence tier attached — the advisor can't confidently invent a South Asian threshold.
- **Honest by construction.** The overclaim guards and provenance tiers travel with every value, so the advisor tells you what a number does *and doesn't* mean.
