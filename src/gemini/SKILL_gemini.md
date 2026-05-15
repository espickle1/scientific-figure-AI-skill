# Scientific Figure Workflow — Gemini

Generate publication-quality figures from CSV/TSV/XLSX data. Iterative loop: audit data → confirm specs → generate code → render → collect feedback → repeat.

## Critical Rules

1. **Always execute code and display the figure inline.** Never show code without running it.
2. **Every script must be self-contained** — runnable from scratch with only the data file.
3. **No statistics by default.** Add stats only when the user explicitly requests them (e.g., "run stats", "add p-values", "compare groups"). See statistics_guide_gemini.md.
4. **If the user requests visual changes after stats were added, strip all statistics code.** User must re-request stats when visual design is finalized.
5. **Never hardcode p-values, significance stars, or test statistics.** All annotations must read from runtime-computed variables.
6. **Do not import** statsmodels, statannotations, scikit_posthocs, plotnine, or adjustText. These are not available.
7. **`jupytext` is the one allowed install.** The Save cell uses it to also write an `.ipynb` companion. If `jupytext` isn't pre-installed, run `!pip install jupytext -q` in a setup cell once before executing the script. No other packages may be installed.

## Workflow

### 1. INGEST
Read the uploaded data directly (no code execution needed for this step). Confirm with the user: number of rows/columns, column names, dtypes, any missing values. Propose a chart type if the user hasn't specified one.

### 2. CONTEXT
If the user provides a reference image (JPEG): describe the visual themes you observe before writing code — chart structure, error bar style, color scheme feel, axis treatment, legend placement, data point display. Do not extract exact measurements, font sizes, or hex colors. Let the user confirm or correct your interpretation.

If the user provides a previous script (pasted code): read it fully. Preserve the CONFIG dict, all data transformations, and the header comment. Edit from there — do not rewrite from scratch.

If the reference image contains multiple panels, extract style from one panel only. Do not create multi-panel layouts.

### 3. GENERATE
Write a single self-contained Python script in jupytext percent format. Cell markers (`# %%`, `# %% [markdown]`) are plain comments — the script still runs end-to-end as `python figure.py`, and percent-aware IDEs (VS Code, Cursor, JupyterLab) open it as a notebook. For Colab, the user runs `jupytext --to ipynb figure.py`.

Canonical cell layout — every code cell is preceded by a one-line `# %% [markdown]` cell:

1. **Title** (markdown only) — figure version, chart type, X/Y columns, data filename.
2. **Setup** (markdown only) — list required packages. Never put `!pip install` in a code cell; it breaks `python figure.py`.
3. **Imports** — imports + font detection.
4. **Config** — `CONFIG` dict with all tunables.
5. **Load** — read the data file; last expression `df.head()`.
6. **Transform** — all filtering, exclusions, derived columns. Nothing above here.
7. **Plot** — figure construction, ending with `plt.show()`.
8. **Save** — `fig.savefig(...)` for PNG (and SVG if requested), then export an `.ipynb` companion via the `jupytext` Python API so every iteration produces a notebook automatically.

Skeleton:

```python
# %% [markdown]
# # Figure v1 — bar chart of Response by Treatment
# Data: experiment.csv

# %% [markdown]
# ## Setup
# Required: matplotlib seaborn pandas numpy openpyxl scipy jupytext.
# Fresh Colab kernel? In a cell, run:
# `!pip install matplotlib seaborn pandas numpy openpyxl scipy jupytext`

# %% [markdown]
# ## Imports

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm

# %% [markdown]
# ## Config

# %%
CONFIG = {"data_path": "experiment.csv", "figsize": (7, 5), "dpi": 300}
available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial","Helvetica","DejaVu Sans","Liberation Sans"] if f in available), "sans-serif")
plt.rcParams["font.family"] = FONT

# %% [markdown]
# ## Load data

# %%
df = pd.read_csv(CONFIG["data_path"])
df.head()

# %% [markdown]
# ## Transform

# %%
# filtering, derived columns

# %% [markdown]
# ## Plot

# %%
fig, ax = plt.subplots(figsize=CONFIG["figsize"], dpi=CONFIG["dpi"])
# plotting
sns.despine(ax=ax)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Save

# %%
fig.savefig("figure_v1.png", dpi=300, bbox_inches="tight")

# Export .ipynb companion of this script.
try:
    import jupytext
    jupytext.write(jupytext.read("figure_v1.py"), "figure_v1.ipynb")
except (ImportError, FileNotFoundError):
    pass
```

Use only: matplotlib, seaborn, numpy, pandas, scipy, openpyxl, scikit-learn — plus `jupytext` for the `.ipynb` export. Every Plot cell ends with `plt.show()` so Gemini renders inline. The Save cell writes to the sandbox; files are ephemeral but execution succeeds and the script remains portable. The `try/except` lets the script still succeed when `jupytext` isn't installed or when cells are run interactively (no `.py` on disk); in the standard sandbox workflow `jupytext` is installed during Setup, so the `.ipynb` is produced every run.

### 4. RENDER
Execute the script. If it fails, fix and retry without asking the user. Do not install packages — use only pre-installed libraries. If execution exceeds 30 seconds, simplify: downsample data, skip KDE, reduce matrix size.

### 5. PRESENT
Display the rendered figure inline. Always show the complete Python script in a code block (user needs the copy button for restarts). Confirm that the Save cell also wrote `figure_vN.ipynb` to the sandbox and offer it as a download alongside the PNG. Give a brief one-line summary.

### 6. ITERATE
Edit the existing script — do not rewrite from scratch. Update the version number in the header comment. If the user requests a visual change and the script contains statistics, strip the stats section and note: "Statistics removed — request them again when your visual design is finalized."

## Supported Chart Types

### Bar chart
Mean height with SEM error bars. Overlay individual data points with jitter (small dots, 50% alpha). Order groups by column's natural order unless user specifies. Despine top and right axes.

### Box / violin plot
Show median, IQR, whiskers. Optionally overlay individual data points with jitter. For violin: use seaborn's `violinplot` with `inner="box"`. Size guard: if any group > 10k points, use box plot instead of violin.

### X-Y scatter
Points with moderate alpha (0.6–0.8). If regression requested, use `scipy.stats.linregress`, plot fit line as dashed black, show R² and p in text box (top-left, 7pt font, white background). Do not add regression unless asked.

### Line plot / time series
Connect points with lines, use markers at data points. If multiple series, use Wong palette colors. Auto-detect datetime columns and format with `matplotlib.dates`. Add legend outside plot if ≥3 series.

### Histogram / distribution
Use `ax.hist()` with `edgecolor="white"`. Default 20–30 bins unless user specifies. If multiple groups, use `alpha=0.6` with overlap or side-by-side. Add KDE overlay only if asked and data < 10k points.

### Heatmap
Use `seaborn.heatmap` with `annot=True` for matrices ≤ 20×20, `annot=False` for larger. Colormap: `viridis` (sequential) or `coolwarm` (diverging). Size guard: if matrix exceeds 200×200, subsample or aggregate first and warn user. Add colorbar with label.

### Grouped / stacked bar
Use seaborn or matplotlib grouped bar patterns. Match group order to data. Include legend. Despine.

## Defaults

| Parameter | Default |
|---|---|
| Library | matplotlib + seaborn |
| Figure size | 7 × 5 in (178 × 127 mm) |
| DPI | 300 |
| Output | PNG (inline display) |
| Palette | Wong colorblind-safe (below) |
| Font | Detect: Arial → Helvetica → DejaVu Sans → sans-serif |
| Style | White background, despined top+right, no grid unless useful |

### Font detection (include at top of every script)
```python
import matplotlib.font_manager as fm
available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial","Helvetica","DejaVu Sans","Liberation Sans"] if f in available), "sans-serif")
plt.rcParams["font.family"] = FONT
```

### Palettes
```python
wong = ["#E69F00","#56B4E9","#009E73","#F0E442","#0072B2","#D55E00","#CC79A7","#000000"]
tol  = ["#EE6677","#228833","#4477AA","#CCBB44","#66CCEE","#AA3377","#BBBBBB"]
# Sequential: "viridis", "magma", "plasma", "inferno", "cividis"
```
Avoid red-green only contrast. Use redundant encodings (shape + color) when ≥4 groups.

## Journal Presets

| | Single col | 1.5 col | Double col | Font | Min DPI |
|---|---|---|---|---|---|
| **Nature** | 89 mm | 120–136 mm | 183 mm | Arial/Helvetica 5–7 pt | 300 |
| **Cell Press** | 85 mm | 114 mm | 174 mm | Avenir/Arial 6–8 pt | 300 |
| **JCB** | — | — | 178 mm max | Arial 8 pt | 300 |

To apply: adjust CONFIG `figsize` to mm/25.4 inches, set `font.size` to journal range.

## Self-Review Checklist

Before displaying: readable text at print size, labeled axes with units, colorblind-safe palette, no clipped labels (`bbox_inches='tight'`), sufficient DPI, data accurately represented.

## Edge Cases

- **Missing values**: drop or impute; tell user which and why
- **Many categories (>8)**: collapse rare into "Other" or use direct labels
- **Large data (>50k rows)**: downsample scatter with alpha, aggregate bars/boxes. Critical for 30-second timeout.
- **Datetime columns**: auto-detect, format with `matplotlib.dates`

## Vector Output Note

Gemini displays figures inline as PNG only. For SVG or PDF output needed for journal submission, the user should run the generated script in Google Colab or a local Python environment. Include this note when relevant.

## Notebook Export

Every iteration also produces a `figure_vN.ipynb` notebook via the `jupytext` call in the Save cell. The user can download it directly from the sandbox or upload it to Colab via **File → Upload notebook**. No separate conversion step is needed.
