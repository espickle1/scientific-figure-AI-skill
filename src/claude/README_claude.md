# scientific-figure

Iterative generation of publication-quality scientific figures from tabular data (CSV, TSV, XLS/XLSX). Targets biomedical journals (Nature, Cell Press, JCB) by default but adapts to any venue.

## How to use

1. **Upload your files.** Drag and drop into the chat:
   - `SKILL_claude.md` (tells Claude how to make scientific figures)
   - `statistics_guide_claude.md` (only needed if you want statistical tests or p-values on your figure)
   - Your data file — a spreadsheet or table saved as `.csv`, `.tsv`, `.xlsx`, or `.xls`

2. **Describe the figure you want in plain English.** Be as specific or as vague as you like — Claude will fill in reasonable defaults for anything you leave out. Examples:

   > *"Make a bar chart comparing the three treatment groups in column B, with error bars."*
   >
   > *"Plot weight over time for each mouse. Color by genotype."*
   >
   > *"I need a scatter plot of age vs. blood pressure, with a trend line and R² value."*

3. **Mention any preferences.** Anything you care about, in whatever words feel natural:
   - What goes on the x-axis and y-axis (column names from your spreadsheet)
   - The type of chart (bar, scatter, line, box plot, violin, heatmap …)
   - Colors, title, axis labels, or figure size
   - Whether you want statistics shown (e.g. "add p-values", "compare groups")
   - A target journal if you have one (e.g. "format for Nature")

4. **Review and revise.** Claude will show you the figure and the code that made it. Ask for changes — move the legend, change colors, make the text bigger, add annotations — as many rounds as you need.

That's it. No coding required on your end.

## Workflow

```
INGEST → INSTRUCT → CONTEXT → GENERATE → RENDER → PRESENT → FEEDBACK → ITERATE ↺
```

| Step | What happens |
|------|-------------|
| **INGEST** | Read data; print shape, dtypes, first rows, missing values |
| **INSTRUCT** | Gather specs (plot type, columns, hue, labels, palette, stats, journal). Defaults fill anything unspecified. Ambiguous column/row selections are confirmed with the user — Claude won't guess |
| **CONTEXT** | Load prior iteration code if revising; skip otherwise. Reference images are treated as general examples only (not reverse-engineered) |
| **GENERATE** | Write a self-contained Python script with a `CONFIG` dict at the top for all tunables |
| **RENDER** | Execute the script; auto-fix code errors without asking |
| **PRESENT** | Deliver figure image(s) + script + summary |
| **FEEDBACK** | Invite revision (layout, colors, typography, data transforms, annotations, style) |
| **ITERATE** | Edit existing script (bump `figure_v1` → `figure_v2`). Statistics are stripped during visual edits and recomputed fresh as the last layer. Halt when user approves or 10 iterations reached |

## Defaults

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| Library | matplotlib + seaborn | Broadest journal compatibility |
| Figure size | 7 × 5 in (178 × 127 mm) | Fits double-column across Nature, Cell, JCB |
| DPI | 300 | Universal journal minimum |
| Output | PNG + SVG | Raster + vector pair |
| Palette | Wong colorblind-safe (primary); Tol (alternative) | No red-green conflicts; Nature compliant |
| Font | Arial → Helvetica → DejaVu Sans → Liberation Sans | Auto-detected at runtime |
| Style | White background, despined, no grid unless useful | Tufte data-ink principle |

## Journal Presets

| | Single col | 1.5 col | Double col | Font | Panel labels | Min DPI |
|---|---|---|---|---|---|---|
| **Nature** | 89 mm | 120–136 mm | 183 mm | Arial/Helvetica 5–7 pt | 8 pt bold lowercase a,b,c | 300 |
| **Cell Press** | 85 mm | 114 mm | 174 mm | Avenir/Arial 6–8 pt | Capital A,B,C | 300 (color), 1000 (line art) |
| **JCB** | — | — | 178 mm max | Arial 8 pt | — | 300 (600 mixed, 1000 line art) |

Pass `target_journal` to apply a preset.

## Statistics

Statistics are **on-command only** — Claude adds them only when you explicitly request them (e.g. "add p-values", "compare groups"). Key policies:

- **User's test, user's responsibility**: Claude always uses the test you specify. If you don't specify one, a decision tree selects the test based on group count, pairing, and normality:

  ```
  1 group vs. reference → one-sample t / Wilcoxon signed-rank
  2 groups, paired      → paired t / Wilcoxon signed-rank
  2 groups, unpaired    → Welch's t / Mann-Whitney U
  ≥3 groups, paired     → repeated-measures ANOVA / Friedman
  ≥3 groups, unpaired   → one-way ANOVA / Kruskal-Wallis
  ```

- **Post-hoc with correction by default**: significant ANOVA is always followed by pairwise tests **with** multiple-comparison correction as a single step. Tukey HSD has built-in correction; Dunn's test uses `p_adjust="bonferroni"` or `"holm"`. Uncorrected pairwise p-values are never shown unless you explicitly request them.

- **Correction methods**: Bonferroni (conservative), Holm-Bonferroni (step-down, generally preferred), Benjamini-Hochberg FDR (common in genomics).

- **Descriptive stats**: mean ± SD (n = X) or median [IQR]. Nature requires error bar description in the figure legend.

- **Annotation**: manual `add_stat_bracket()` helper (zero dependencies) is the primary method. `statannotations` is an optional convenience library. Stars: \* p < 0.05, \*\* p < 0.01, \*\*\* p < 0.001, \*\*\*\* p < 0.0001. All annotations read from runtime-computed variables — nothing is hardcoded.

- **Iteration rule**: statistics are stripped from the script during visual edits and recomputed fresh from raw data after visual changes are finalized. Statistics are always the last layer applied.

Supported tests: one-sample/paired/unpaired t, Welch's t, Mann-Whitney U, Wilcoxon signed-rank, one-way/two-way ANOVA, Kruskal-Wallis, Friedman, Tukey HSD, Dunn's. Linear and polynomial regression via `scipy.stats.linregress` / `numpy.polyfit` / `statsmodels` OLS.

## Edge Cases

Handled automatically: missing values (drop/impute with disclosure), >8 categories (collapse or direct-label), >100k points (`rasterized=True`, alpha jitter), datetime columns (`mdates` formatting).

## Demo

The figure below is generated from synthetic dose-response data by `demo_figure.py` (included). Four panels demonstrate the core plot types the skill produces:

- **a** — Strip + box plot with pairwise significance brackets (Welch's t vs. Vehicle)
- **b** — Time-course with confidence band
- **c** — Scatter + linear regression (R², p annotated)
- **d** — Summary bar chart with SEM error bars

All panels use the Wong colorblind-safe palette, despined axes, and 300 DPI output.

![Demo figure](demo_figure.png)

## File Manifest

```
SKILL_claude.md              # Full skill spec (workflow, defaults, journal presets, checklist)
statistics_guide_claude.md   # Stat recipes: descriptive, t-test, ANOVA, non-parametric, correction, annotation
demo_figure.py               # Script that produced the figure above (self-contained, CONFIG-driven)
demo_figure.png              # Raster output (300 DPI)
demo_figure.svg              # Vector output
README.md                    # This file
```

## Dependencies

Core:
```
matplotlib seaborn pandas numpy scipy adjustText statsmodels openpyxl
```

Optional (installed on demand): `plotnine`, `statannotations`, `scikit-posthocs`, `svgutils`.

> **Note:** If `statsmodels` fails to install, Claude will notify you. It is required for Tukey HSD, two-way ANOVA, OLS regression, and `multipletests` correction. Fallback: `scipy.stats.tukey_hsd` (scipy ≥ 1.8) covers one-way post-hoc; inline Bonferroni/Holm correction is possible with numpy. Two-way ANOVA has no scipy fallback.
