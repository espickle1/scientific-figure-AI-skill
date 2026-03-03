---
name: scientific-figure
description: >
  Create publication-quality scientific figures from raw data files (CSV, TSV, XLS/XLSX).
  Use this skill whenever the user wants to generate, refine, or iterate on scientific plots,
  charts, or data visualizations — especially for research papers, posters, or presentations.
  Triggers include: "make a figure", "plot this data", "create a chart from my CSV",
  "scientific visualization", "publication figure", "journal figure", requests involving
  matplotlib/seaborn/plotnine/ggplot, or any mention of plotting data from a tabular file.
  Also use when the user uploads a data file and asks to visualize it, or when they provide
  a previous figure draft and want revisions.
---

# Scientific Figure Workflow

Iterative loop: ingest data → gather specs → generate code → render → present → collect feedback → repeat.

## Workflow

1. **INGEST** — Read data from `/mnt/user-data/uploads/`. Print shape, dtypes, first 5 rows, missing values. Share summary with user before proceeding.
2. **INSTRUCT** — Gather: plot type, x/y columns, hue/facet, title, labels, figsize, palette, error bars, stat annotations, output format, target journal. Apply defaults (below) for anything unspecified. If vague, propose a plot type based on the audit but ask the user to confirm column mappings before proceeding. **Data selection is the user's responsibility**: if the prompt is ambiguous about which columns, rows, subsets, or transformations to use, ask the user — do not guess.
3. **CONTEXT** — If user provides a previous figure or references a prior iteration, load that code/image first. Otherwise skip. **Reference images are general examples only**: do not extract exact measurements, hex colors, font sizes, or layout structure from uploaded images. Do not reverse-engineer figure schemas from user descriptions, text, or numbers. The user's explicit instructions always override journal presets and reference images.
4. **GENERATE** — Write a self-contained Python script. Put tunables in a `CONFIG` dict at the top. Use relative data path in the saved-to-outputs version. Read `references/matplotlib_guide.md` or `references/plotnine_guide.md` before writing code. If stats are needed, read `references/statistics_guide.md` for test selection, annotations, and correction methods. All data transformations — filtering, exclusions, type conversions, derived columns, aggregations — must be in the script. Never apply data modifications in separate code blocks that won't be preserved.
5. **RENDER** — Execute. If the script fails due to a code error, diagnose and fix without asking the user. If a required package fails to install or a system dependency is missing, notify the user. Install packages with `pip install <pkg> --break-system-packages -q`.
6. **PRESENT** — Copy to `/mnt/user-data/outputs/` and deliver via `present_files`: **(a)** figure image(s), **(b)** the Python script (always — never skip this), **(c)** brief summary.
7. **FEEDBACK** — Invite revision. Common axes: layout, colors, typography, data transforms, annotations, style, format.
8. **ITERATE** — Edit existing script (don't rewrite from scratch). Bump filename: `figure_v1` → `figure_v2`. Return to step 4. Halt when user approves or 10 iterations reached. On final delivery, include all requested formats + script + changelog if >2 iterations. **Statistics rule**: when iterating, strip all statistics code and annotations from the script before making visual edits. If the user still wants statistics, recompute from raw data after visual changes are finalized. Statistics are always the last layer applied, always computed fresh — never carried forward from a previous iteration.

## Defaults

| Parameter | Default | Why |
|-----------|---------|-----|
| Library | matplotlib + seaborn | Most common in biomedical research |
| Figure size | 7 × 5 in (178 × 127 mm) | Fits double-column across Nature, Cell, JCB |
| DPI | 300 | Universal journal minimum |
| Output | PNG + SVG | Raster + vector pair |
| Palette | Wong colorblind-safe | Wong, B. *Nat Methods* 8:441, 2011 |
| Font | Arial/Helvetica (fallback: DejaVu Sans) | Required by Nature, Cell, JCB |
| Style | White background, despined, no grid unless useful | Tufte data-ink principle |

Font detection (run at script top — Arial is often missing in containers):
```python
import matplotlib.font_manager as fm
available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial","Helvetica","DejaVu Sans","Liberation Sans"] if f in available), "sans-serif")
plt.rcParams["font.family"] = FONT
```

## Journal Presets

Sources: `references/parameter_sources.md`

| | Single col | 1.5 col | Double col | Font | Panel labels | Min DPI |
|---|---|---|---|---|---|---|
| **Nature** | 89 mm | 120–136 mm | 183 mm | Arial/Helvetica 5–7 pt | 8 pt bold lowercase a,b,c | 300 |
| **Cell Press** | 85 mm | 114 mm | 174 mm | Avenir/Arial 6–8 pt | Capital A,B,C | 300 (color), 1000 (line art) |
| **JCB** | — | — | 178 mm max | Arial 8 pt | — | 300 (600 mixed, 1000 line art) |

## Palettes

```python
wong = ["#E69F00","#56B4E9","#009E73","#F0E442","#0072B2","#D55E00","#CC79A7","#000000"]  # categorical default
tol  = ["#EE6677","#228833","#4477AA","#CCBB44","#66CCEE","#AA3377","#BBBBBB"]            # alternative
# Sequential: cmap="viridis", "magma", "plasma", "inferno", or "cividis"
```
Avoid red-green contrast (Nature policy). Use redundant encodings (shape + color) when ≥4 groups.

## Self-Review Checklist

Before presenting, verify: readable text at print size, accurate data representation, labeled axes with units, colorblind-safe palette, no clipped labels (`bbox_inches='tight'`), sufficient DPI. If stats are shown, verify test assumptions were checked and p-values are corrected for multiple comparisons where applicable.

## Statistics

Full recipes in `references/statistics_guide.md`. Key points:

- **On-command only**: add statistics only when the user explicitly requests them. Strip stats from the script during visual iterations. Recompute fresh from raw data each time — never carry forward computed values.
- **User's test, user's responsibility**: always use the test the user specifies. Do not substitute, override, or second-guess the user's choice of statistical method. If no test is specified, use the decision tree in the guide.
- **Descriptive**: report mean ± SD (or median [IQR]) with n. Nature requires error bar description in legend.
- **Post-hoc with correction**: by default, always follow significant ANOVA with pairwise tests (Tukey HSD or Dunn's) **and** multiple comparison correction as a single step. Do not display uncorrected pairwise p-values unless the user explicitly requests them.
- **Annotation**: use manual `add_stat_bracket()` helper (zero dependencies) as the primary method. `statannotations` is an optional convenience. Stars: * p<0.05, ** p<0.01, *** p<0.001. Never hardcode p-values or significance stars — all annotations must read from runtime-computed variables.

## Edge Cases

- **Missing values**: drop or impute; tell user which and why
- **Many categories (>8)**: collapse rare into "Other" or use direct labels instead of legend
- **Large data (>100k)**: `rasterized=True` for SVG; downsample scatter with alpha
- **Datetime columns**: auto-detect, format with `mdates`

## Dependencies

```bash
pip install matplotlib seaborn pandas numpy openpyxl scipy adjustText statsmodels --break-system-packages -q
```
Install on demand: `plotnine`, `statannotations`, `scikit-posthocs`, `svgutils`.

If `statsmodels` fails to install, notify the user. It is required for Tukey HSD, two-way ANOVA, OLS regression, and `multipletests` correction. Fallback: `scipy.stats.tukey_hsd` (scipy ≥1.8) covers one-way post-hoc; inline Bonferroni/Holm correction is possible with numpy. Two-way ANOVA has no scipy fallback.
