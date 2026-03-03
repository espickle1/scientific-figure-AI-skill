# Scientific Figure Workflow — Gemini User Guide

Turn raw data into publication-quality figures using Google Gemini. No coding required.

---

## What You Need

- **Your data file**: CSV, TSV, or XLSX
- **A Gemini account** at [gemini.google.com](https://gemini.google.com)
  - Gemini Advanced (recommended): full context window, reliable code execution
  - Free tier: works, but limited to ~4–6 revision rounds per figure

You do NOT need Python installed, any programming knowledge, or any design software.

---

## Setup

### Option A: Gem (recommended, uses Agent,requires Gemini Advanced)

1. Go to [gemini.google.com](https://gemini.google.com)
2. Click **Explore Gems** → **New Gem**
3. Name it (e.g., "Scientific Figure Maker")
4. Paste the contents of `gem_instructions.txt` into the **Instructions** field
5. Click **Add files** and upload:
   - `SKILL_gemini.md`
   - `statistics_guide_gemini.md`
6. Click **Save**
7. Open your Gem, upload your data, and describe the figure you want

### Option B: Lite (paste-in prompt, works on free tier)

1. Open a new Gemini chat
2. Copy the entire contents of `SKILL_gemini_lite.md` and paste it as your first message
3. In your second message, upload or copy-paste your data and describe the figure

---

## Quick Start

**Message 1 — Upload and describe:**
> Here's my data [attach CSV]. Make a bar chart of Response grouped by Treatment. Use error bars. This is for a Nature single-column figure.

**Message 2 — Review and revise:**
> Make the bars wider, change to the tol palette, and add individual data points.

**Message 3 — Add statistics (when visual design is final):**
> Run stats — compare all treatment groups to Control.

That's it. Gemini generates the code, runs it, and displays the figure. You download the result.

---

## How to Describe Your Figure

The more specific your first message, the fewer rounds of revision you'll need. Include:

- **Chart type**: bar, scatter, box, violin, line, histogram, heatmap
- **Columns**: which columns go on x-axis, y-axis, and for grouping/coloring
- **Error bars**: SEM, SD, 95% CI, or none
- **Title and axis labels** (or let Gemini infer from column names)
- **Target journal** (optional): "Nature single-column", "Cell double-column"
- **Special requests**: log scale, specific colors, legend position

**Example prompts:**

> Box plot of Gene_Expression grouped by Cell_Type. Overlay individual data points. Color by Cell_Type using the default palette.

> Scatter plot of Age vs Blood_Pressure. Add a linear regression line with R² and p-value. No grid.

> Heatmap of the correlation matrix for all numeric columns. Use coolwarm colormap. Annotate cells with values.

> Line plot of Weight over Time, one line per Mouse_ID, colored by Genotype. Format x-axis as dates.

---

## Using Reference Images

Upload a JPEG screenshot of a figure whose style you want to match, alongside your data.

**What Gemini extracts from the image:**
- Chart structure and organization
- Error bar and significance bracket style
- Color scheme feel (warm, cool, monochrome, categorical)
- Axis treatment (despined, boxed, with/without grid)
- Legend placement and data point display

**What Gemini does NOT extract** (uses defaults instead):
- Exact hex colors → uses Wong colorblind-safe palette
- Font sizes → uses journal preset sizes
- Figure dimensions → uses CONFIG values

**Tips for reference images:**
- Crop to just the figure — exclude paper text, captions, panel labels from other panels
- JPEG format, under 1000px on the longest side (saves tokens)
- If the reference is a multi-panel figure, Gemini will match the style of one panel — not recreate the whole layout

---

## Iteration and Revisions

### Within a conversation

- **Batch your changes.** Instead of sending one change per message, collect all revisions and send them together: "Make bars wider, move legend to upper-right, change y-axis label to 'Concentration (mg/mL)'."
- **Reference CONFIG keys** for precise changes: "Change figsize to (10, 6) and DPI to 600."
- **Statistics are added last.** Finalize your visual design, then request stats. If you make visual changes after stats are added, the statistics will be removed and you'll need to re-request them.

### Continuing in a new chat (when tokens run low, or to restart)

1. Click the **copy button** on the code block in Gemini's response
2. Open a new Gemini chat
3. Paste the code as your first message
4. Upload your data file
5. Describe the changes you want

The pasted script carries your complete figure state — chart type, styling, data transformations, CONFIG values. Gemini reads it and edits from there.

**Going back to a previous version:** If the current direction isn't working, paste an earlier version of the script instead. No need to undo anything.

**Important:** If your figure involved data transformations that you described verbally (e.g., "exclude outliers above 100"), these should already be encoded in the script. If they're not, re-describe them when you paste the script into a new chat.

---

## Statistics

Statistics are never added to figures automatically. You control when they appear.

### How to request stats

> Run stats — compare all groups.

> Add p-values comparing Control vs Drug_A and Control vs Drug_B.

> Is there a significant difference between the treatment groups? Show it on the figure.

### What happens

1. Gemini checks normality (Shapiro-Wilk) for each group
2. Selects the appropriate test (parametric or non-parametric)
3. Applies multiple comparison correction if needed (Holm or Bonferroni)
4. Prints all results as text in the chat (so you can verify)
5. Annotates the figure with significance brackets and stars

### Available tests

| Scenario | Test |
|---|---|
| 2 unpaired groups | Welch's t-test or Mann-Whitney U |
| 2 paired groups | Paired t-test or Wilcoxon signed-rank |
| ≥3 unpaired groups | One-way ANOVA or Kruskal-Wallis |
| Post-hoc pairwise | Tukey HSD or pairwise Mann-Whitney + Holm |
| Correlation | Pearson or Spearman |
| Regression | Linear (scipy linregress) |

### Not available on Gemini

- Two-way ANOVA (requires statsmodels — run the script in Colab if needed)
- Repeated-measures ANOVA (Friedman test available as non-parametric alternative)

### Safety design

Statistics are always computed fresh from your data at runtime. The script never stores or caches numerical results. If you make visual changes after stats were added, the statistics code is removed to prevent accidental corruption. Re-request stats when you're ready.

---

## Output Formats

Gemini displays figures inline as PNG at 300 DPI. This is sufficient for most review and draft purposes.

**For journal submission** (SVG, PDF, TIFF, EPS), run the generated script outside Gemini:

### Google Colab (free, no setup)

1. Copy the script from Gemini (copy button on code block)
2. Go to [colab.research.google.com](https://colab.research.google.com)
3. Create a new notebook
4. Paste the script into a cell
5. Upload your data file (folder icon on left sidebar)
6. Change `plt.show()` to:
   ```python
   for fmt in ["png", "svg", "pdf"]:
       plt.savefig(f"figure.{fmt}", dpi=300, bbox_inches="tight")
   plt.show()
   ```
7. Run the cell. Download files from the file browser.

### Local Python

If you have Python installed: save the script as a `.py` file, place your data file in the same folder, edit the data path in CONFIG if needed, and run `python figure_vN.py`.

---

## Free Tier Token Management

The free tier gives you roughly 32k tokens of context. Here's how to make the most of it:

- **Be specific in your first message.** A detailed prompt often produces a usable figure in 1–2 attempts.
- **Batch all revisions into one message.** Five separate "change X" messages cost 5× the tokens of one combined message.
- **Copy your code block early.** Don't wait until you hit the limit — copy after each version you like.
- **Request stats last.** Statistical computation adds significant code and output to the conversation.
- **Skip reference images if tokens are tight.** Describe the style in words instead: "despined axes, no grid, SEM error bars with caps, muted blue palette."
- **4–6 revision rounds** is a realistic budget. Plan your changes accordingly.

---

## File Reference

| File | Purpose | Where it goes |
|---|---|---|
| `gem_instructions.txt` | Behavioral prompt | Gems → Instructions field |
| `SKILL_gemini.md` | Full workflow, chart templates, defaults | Gems → Attached file |
| `statistics_guide_gemini.md` | Stats recipes (scipy-only) | Gems → Attached file |
| `SKILL_gemini_lite.md` | Compressed prompt for free tier | Paste into chat |
| `README_gemini.md` | This user guide | For your reference |

---

## Limitations

- **No multi-panel composite figures.** Each figure is a single chart. For multi-panel layouts, use the Claude version or Colab.
- **No 3D surface plots.** Matplotlib's 3D module is slow and unreliable in the sandbox.
- **No custom library installation.** You're limited to the pre-installed set.
- **30-second execution timeout.** Large datasets or complex plots may need downsampling.
- **PNG output only in chat.** Vector formats (SVG, PDF) require running the script elsewhere.
- **Two-way ANOVA unavailable.** Requires statsmodels. Use Colab for this test.
- **Code execution is probabilistic.** If Gemini shows code without running it, reply: "Please run this code and show me the figure."

---

## Troubleshooting

**Gemini shows code but no figure:**
Reply: "Please run this code and show me the figure."

**Figure looks different from what I expected:**
Describe specifically what's wrong: "y-axis label is cut off", "bars are too narrow", "legend covers the data."

**Timeout error (no figure produced):**
Your data may be too large. Ask: "Can you downsample the data to 10k rows and try again?"

**Import error for a library:**
The library isn't available. Ask Gemini to use an alternative from matplotlib, seaborn, numpy, pandas, scipy, or scikit-learn.

**Statistics disappeared after a visual edit:**
This is by design. Finalize visual changes, then re-request statistics.

**I need SVG/PDF for my journal:**
Copy the script, run it in Google Colab with `plt.savefig("figure.svg")`.

---

*Last updated: February 2026*
