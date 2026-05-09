# scientific-figure for Microsoft Copilot

Iterative generation of publication-quality scientific figures from tabular data (CSV, TSV, XLS/XLSX). Targets biomedical journals (Nature, Cell Press, JCB) by default but adapts to any venue.

Same output format as the Claude and Gemini variants — the generated script runs locally or in Google Colab; Copilot does not execute it.

---

## Setup

### Option A — Custom Instructions (recommended, persistent)

Set it once and it applies to every Copilot conversation automatically.

1. Go to [copilot.microsoft.com](https://copilot.microsoft.com)
2. Click your profile icon → **Settings** → **Personalization** → **Custom Instructions**
3. Paste the full contents of `SKILL_copilot.md` into the custom instructions box
4. Save

From that point on, any Copilot chat will behave as the scientific figure skill without needing to paste anything.

### Option B — Paste as first message (per-session, no setup)

1. Open a new conversation at [copilot.microsoft.com](https://copilot.microsoft.com)
2. Copy the full contents of `SKILL_copilot.md`
3. Paste it as your **first message** and send
4. Copilot will confirm it understood; then proceed with your data

---

## Model selection

In the Copilot interface, open the model picker and select **GPT-5.2** (or the latest available GPT model). The skill works with any GPT model but produces best results with the most capable one available.

---

## Uploading data

Click the **paperclip / attachment icon** in the message bar and attach your data file:

- `.csv` — comma-separated values
- `.tsv` — tab-separated values
- `.xlsx` / `.xls` — Excel workbooks

Copilot reads the file directly. No preprocessing needed.

---

## Basic usage

1. (If using Option B) Paste `SKILL_copilot.md` as message 1
2. Upload your data file
3. Describe the figure you want in plain English:

   > *"Bar chart comparing the three treatment groups, with error bars for SEM."*
   >
   > *"Plot weight over time for each mouse, colored by genotype."*
   >
   > *"Scatter plot of age vs. blood pressure with a trend line and R² annotation."*

4. Copilot returns a summary and the complete Python script in a code block
5. Copy the code block and run it locally (VS Code, JupyterLab) or in [Google Colab](https://colab.research.google.com)
6. Ask for revisions — colors, layout, fonts, axis ranges — as many rounds as needed

---

## Running the generated script

The script is a self-contained `.py` file in jupytext percent format. Three ways to run it:

| Environment | How |
|---|---|
| **Local terminal** | `python figure_v1.py` |
| **VS Code / JupyterLab** | Open the file — cell markers (`# %%`) are recognized as notebook cells with the jupytext extension |
| **Google Colab** | `pip install jupytext && jupytext --to ipynb figure_v1.py`, then open the `.ipynb` |

The script saves PNG (300 DPI) and SVG outputs alongside itself.

---

## Adding statistics

For stat-heavy work, paste `statistics_guide_copilot.md` as a second message before requesting statistics. This gives Copilot the full recipe library (t-tests, ANOVA, non-parametric tests, multiple-comparison correction, bracket annotations).

**Statistics are on-command only** — Copilot will not add p-values or test annotations unless you explicitly ask (e.g. "add p-values comparing groups", "run a t-test"). Finalize your visual design first, then request statistics.

---

## Workflow summary

```
INGEST → INSTRUCT → CONTEXT → GENERATE → PRESENT → FEEDBACK → ITERATE ↺
```

| Step | What happens |
|---|---|
| **INGEST** | Read uploaded file; print shape, dtypes, first rows, missing values |
| **INSTRUCT** | Gather specs (chart type, columns, hue, labels, palette, stats, journal). Ambiguous column/row selections are confirmed — not guessed |
| **CONTEXT** | Load prior iteration code if revising; skip otherwise |
| **GENERATE** | Write a self-contained jupytext `.py` script with a `CONFIG` dict for all tunables |
| **PRESENT** | Output summary + complete script in a code block (always) |
| **FEEDBACK** | Invite revision: layout, colors, typography, data transforms, annotations |
| **ITERATE** | Edit existing script, bump `figure_v1` → `figure_v2`. Statistics stripped during visual edits, recomputed fresh as the final layer |

---

## Defaults

| Parameter | Default |
|---|---|
| Figure size | 7 × 5 in (178 × 127 mm) |
| DPI | 300 |
| Output | PNG + SVG |
| Palette | Wong colorblind-safe |
| Font | Arial → Helvetica → DejaVu Sans (auto-detected) |
| Style | White background, despined axes |

---

## File manifest

```
SKILL_copilot.md              # Full skill spec — paste into Custom Instructions or as message 1
statistics_guide_copilot.md   # Stat recipes — paste as a second message for stats-heavy work
README_copilot.md             # This file
```
