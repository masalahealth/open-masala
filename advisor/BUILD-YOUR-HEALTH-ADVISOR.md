# Build your own health advisor with Claude

A practical, best-practices guide to turning your own medical records into a **personal, ancestry-aware health advisor** — one that reads your labs, tracks trends across years, and prepares you for a sharper conversation with your doctor. It runs on your machine, your data stays local, and every ancestry-adjusted claim is backed by the cited [Open Masala](../README.md) dataset.

> ⚠️ This is a *preparation* tool, not a doctor. It surfaces patterns and gaps and translates jargon — it does **not** diagnose, and it never changes your medications. Always take findings to a clinician.

## The idea (how it works)

Three ingredients:
1. **A workspace** — a folder on your computer, one per person, where you drop your raw records.
2. **Claude** — reads everything, builds a structured health profile, and answers questions grounded in *your* history.
3. **The Open Masala MCP server** — so when Claude interprets a number, it uses South-Asian-calibrated, cited reference ranges instead of the general-population defaults your lab printed.

That's the whole system. Below is the setup, proven on a real multi-person family workspace.

---

## Step 1 — Set up a workspace

Make one folder **per person** (mixing people is the most common mistake — thresholds and history must never blend):

```
health/
  you/
    source-data/        ← raw records go here (Step 2)
    references/          ← anything you want the advisor to know (diet, goals, meds list)
    you-summary.md       ← the advisor writes/updates this (Step 4)
  mom/
    source-data/
    ...
```

Keep this on your own machine. Nothing here needs to touch a cloud account.

## Step 2 — Pull your data from Epic / MyChart

Epic powers most US hospital portals (branded "MyChart"). Menu labels vary by health system, but one of these always works. Save whatever you get into that person's `source-data/`.

**Easiest — download your record (web):**
1. Log into your MyChart on the web.
2. Open the **Menu** and look for **"Document Center"**, **"Sharing"**, or **"Share My Record."**
3. Choose **"Download My Record"** / **"Requested Records"** / **"Lucy."** This generates a **CCDA** — a machine-readable clinical-summary file (XML, sometimes a `.zip`). Download it. It typically contains multi-year labs, problems, meds, and allergies in one file — the single most useful thing to hand Claude.

**Also grab (they add detail):**
- **Test Results** → open each panel → **Download / Print to PDF.** Individual lab PDFs carry the reference ranges.
- **Visits** → **After-Visit Summaries** (PDF).

**iPhone shortcut — Apple Health Records:**
- Health app → **Sharing** (or Browse → Health Records) → **Add Account** → search your hospital → sign in. Your clinical records sync into Health. From there you can review them, and **Health → profile → Export All Health Data** produces an `export.xml` you can drop into `source-data/`.

**Beyond the portal (optional but high-value):**
- **Genetics:** your 23andMe / Ancestry raw data or reports (PDF).
- **Wearables:** Apple Health / WHOOP / Garmin / CGM exports.

> Tip: the **CCDA download is the highest-leverage single file** — get that first; add PDFs and wearables later.

## Step 3 — Point Claude at it

Use Claude Desktop (or Claude Code), and give it two things:

**a) The advisor instructions.** Paste [`ADVISOR.md`](ADVISOR.md) as your system prompt / project instructions. It makes Claude behave like a careful advisor — reports evidence strength, honors "don't-overclaim" guards, and defers to clinicians.

**b) The Open Masala MCP server**, so ancestry-adjusted thresholds are cited, not guessed. Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "open-masala": { "command": "uvx", "args": ["open-masala-mcp"] }
  }
}
```
Restart Claude. (Full setup in [`README.md`](README.md).)

## Step 4 — Build your health profile

Point Claude at the person's folder and ask it to do the review. A first prompt that works:

> *"Read everything in this folder. I'm a 34-year-old South Asian man, vegetarian, [meds/conditions]. Build my health profile: a demographics block, a time-series table of my labs by category, the trends worth noting, and a prioritized list of what to pay attention to and what to ask my doctor. Use the Open Masala tools for any South-Asian-specific thresholds, and cite them. Save it as `you-summary.md`."*

Claude will discover the files (CCDA, PDFs, exports), extract every lab value with its date and reference range, build a **time-series tracker** (direction over time matters more than any single value), apply ancestry / diet / lifestyle frameworks, and write a living `you-summary.md`. That file is the thing you keep and grow.

## Step 5 — Query it

Now you have a health advisor. Ask it things like:
- *"My ApoB is 95. What does that mean for a South Asian body, and what's the target?"* (it calls Open Masala, cites the guideline)
- *"Prep me for my cardiology appointment — what should I ask, and what tests should I request?"*
- *"My last three ferritin values — is that a trend I should worry about?"*
- *"I'm vegetarian and tired lately. What deficiencies are worth checking, and how do I raise them through food first?"*
- *"New lab just came in — add it to my tracker and tell me what changed."*

## Best practices (the distilled principles)

- **One person per folder, always.** Never let the advisor blend two people's data — thresholds and history are person-specific.
- **Keep it local.** Your records stay on your machine. The Open Masala server only ever receives the single value you ask it to check, and stores nothing.
- **Trends beat snapshots.** A ferritin of 41 *down from 90* is a different story than 41 with no history. Always give it dates.
- **Ancestry changes the numbers.** The reference range your lab printed was likely calibrated on a different population. That's the whole reason Open Masala exists — let the advisor use it.
- **Verify tier, then act.** A `guideline-endorsed` value is solid; a `study-derived` one is "worth discussing," not settled. The advisor will tell you which — believe it.
- **It prepares, it doesn't prescribe.** Never start, stop, or change a medication on its say-so. Its job is to make your next doctor visit sharper.
- **Iterate.** Each new lab, wearable export, or visit summary → drop it in, ask it to update the tracker. The profile compounds over time.
- **A good session leaves you knowing five things:** what's going well, what needs attention, what to ask your doctor, what tests to request, and which specialist (if any) to see.

## Example: what a finished profile contains

- **Patient profile** (demographics, ancestry, diet, meds, family history)
- **Key metrics** tables (cardiovascular, metabolic, nutrients — value · date · reference · status)
- **Time-series tracker** by category (lipids, metabolic/liver, CBC/iron, vitamins)
- **Trends worth noting** + **targets for the next blood draw**
- **Prioritized recommendations**, each with its *why* and whether it needs a clinician
- **Open items / labs to add**

## Disclaimer

This guide and the tools it uses are for research and personal-preparation use. They are **not a medical device**, not clinical advice, and not a substitute for a clinician's judgment. Reference ranges vary by lab and method; every decision needs individual clinical context.
