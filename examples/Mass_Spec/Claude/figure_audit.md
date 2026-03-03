# Figure Audit — Peptidoglycan Fragment Abundance
**Date:** 2026-03-02  
**Final output:** `mass_spec_figure_v3.png` / `.svg`  
**Script:** `figure_v3.py`

---

## 1. Input Files

| File | Description |
|------|-------------|
| `test_mass_spec.csv` | Primary data — 52 rows × 8 columns |
| `mass_spec_figure_sample.png` | Hand-drawn reference sketch (template) |
| `SKILL_claude.md` | Scientific figure workflow skill |
| `statistics_guide_claude.md` | Statistics reference |

### CSV schema

| Column | Type | Description |
|--------|------|-------------|
| `mass` | float64 | Fragment mass (Daltons) — x-axis |
| `Crosslink` | int64 | Structural variant count |
| `Bridgelink` | int64 | Structural variant count |
| `Ala` | int64 | Structural variant count |
| `O-acetylation` | int64 | Structural variant count |
| `N-deacetylation` | int64 | Structural variant count |
| `Lactate` | int64 | Structural variant count |
| `AUC` | int64 | Area under curve — y-axis |

---

## 2. Figure Design

### Concept
A hybrid figure combining two vertically stacked panels sharing a common x-axis (fragment mass):

- **Top panel — bar/line chart:** AUC (signal abundance) per fragment mass, rendered as thin vertical stem lines.
- **Bottom panel — dot heatmap:** One row per structural variant category. Each dot's opacity encodes the min-max normalized value of that category at that mass position.
- **Stats sidebar:** Mean ± SD for each category displayed to the right of the dot heatmap.

### Layout
- `matplotlib.gridspec` with 2 rows × 2 columns
- Row height ratios: `[0.72, 0.28]` (bar chart : dot heatmap)
- Column width ratios: `[1, 0.18]` (main plot : stats sidebar)
- `hspace=0` (panels flush against each other), `wspace=0.04`
- `sharex=True` between bar and dot panels

---

## 3. Data Transformations

### Deduplication
- Duplicate `mass` values exist in the raw data (52 rows, fewer unique masses).
- **Rule applied:** for any mass with multiple rows, retain only the row with the **highest AUC**.
- Implemented with: `df.groupby("mass").apply(lambda g: g.loc[g["AUC"].idxmax()])`
- Deduplication is applied **before** plotting both the bar chart and the dot heatmap.

### Sorting
- All data sorted ascending by `mass` before plotting.

### Min-max normalization (dot heatmap only)
- For each category independently: `norm = (val - min) / (max - min)`
- If `max == min` (constant column), all values set to `0.0`.
- Normalization is used **only** to encode dot opacity — not to alter underlying values.
- Dots are only rendered where the raw category value is `> 0`.

### Stats sidebar
- Mean and SD computed from the **original (non-deduplicated) full dataset** (all 52 rows) for each category.

---

## 4. Visual Parameters

### Global
| Parameter | Value |
|-----------|-------|
| Figure size | 9 × 5.5 inches |
| DPI | 300 |
| Font | Arial → Helvetica → Liberation Sans → DejaVu Sans (first available) |
| Base font size | 7 pt |

> **Note on Arial:** Arial is not available in the rendering container (no network access to install `ttf-mscorefonts-installer`). **Liberation Sans** is used as a metric-compatible substitute with identical character widths. To use Arial, open the SVG in Illustrator or Inkscape and perform a global font substitution.

### Bar / Line chart (top panel)
| Parameter | Value |
|-----------|-------|
| Plot type | `vlines` (vertical stem lines from y=0) |
| Line width | 0.8 pt |
| Line color | black (`#000000`) |
| x-axis spine | Positioned at `y=0` via `set_position(("data", 0))` |
| y-axis label | "AUC", 8 pt |
| Title | "Peptidoglycan Fragment Abundance by Variations of Structure", 16 pt (2× axis labels) |
| Spines visible | left only (top, right, bottom hidden — bottom repositioned to y=0) |
| y=0 tick | Removed |

### Dot heatmap (bottom panel)
| Parameter | Value |
|-----------|-------|
| Dot size | 13.5 pt² (reduced 25% from initial 18 pt²) |
| Opacity range | 0.15 (min) → 0.95 (max), linearly mapped from normalized value |
| x-axis label | "Fragment mass (Daltons)", 8 pt |
| y-axis | Category names, 6.5 pt, no tick marks |

### Category colors (Wong colorblind-safe palette)
| Category | Hex |
|----------|-----|
| Crosslink | `#D55E00` (vermillion) |
| Bridgelink | `#CC79A7` (reddish purple) |
| Ala | `#009E73` (bluish green) |
| O-acetylation | `#009E73` (bluish green) |
| N-deacetylation | `#56B4E9` (sky blue) |
| Lactate | `#56B4E9` (sky blue) |

### Stats sidebar
| Parameter | Value |
|-----------|-------|
| Format | `mean ± SD` (2 decimal places) |
| Font size | 6 pt |
| Header label | "mean ± SD" in italic, `#444444` |

---

## 5. Iteration Log

### v1 — Initial figure

**User prompt:**
> "Create a hybrid bar plot / heatmap from the uploaded data with uploaded figure sketch as the template. Note that x-axis (mass) should be attached to y-axis (AUC) at minimum values. Very small size for dots in categorical values with color transparency gradient by values (minmax normalized for each category). Provide mean and standard deviation for each category on the right of each category."

Changes implemented:
- Hybrid bar chart + dot heatmap from reference sketch
- Bars rendered with `ax.bar()` — wide colored bars
- All 52 rows plotted (duplicates included)
- x-axis label: "mass"
- No title

---

### v2 — User revision 1

**User prompt:**
> "Move up x-axis so that it's at y=0. For duplicate values, only plot the highest value. Narrow the bar on the plot so that it's a line, color black. Change the x-axis title to "Fragment mass (Daltons)"."

Changes implemented:
1. Move x-axis spine to y=0 → `spines["bottom"].set_position(("data", 0))`
2. For duplicate mass values, keep only the highest AUC row → `groupby("mass").apply(lambda g: g.loc[g["AUC"].idxmax()])`
3. Narrow bars to a line, color black → switched from `bar()` to `vlines(linewidth=0.8, color="black")`
4. Rename x-axis label to "Fragment mass (Daltons)"

---

### v3 — User revision 2

**User prompt:**
> "Decrease the size of dots in the heatmap-equivalent by 25%. Add title "Peptidoglycan Fragment Abundance by Variations of Structure", 2 times larger than axis titles. Font arial. Remove tick at y=0."

Changes implemented:
1. Decrease dot size by 25% → `dot_size: 18 → 13.5`
2. Add figure title "Peptidoglycan Fragment Abundance by Variations of Structure" at 16 pt (2× axis title size of 8 pt), font Arial
3. Remove tick mark at y=0 on AUC axis → `set_yticks([t for t in yticks if t != 0])`

---

### Audit document — User request

**User prompt:**
> "Thank you. Please give me a markdown file for audit that has every details, step-by-step so that this conversation can be recapitulated from scratch."

---

### Audit revision — User request

**User prompt:**
> "Please change the audit to include all the text inputs from the user."

---

## 6. Output Files

| File | Description |
|------|-------------|
| `mass_spec_figure_v3.png` | Final raster figure, 300 DPI |
| `mass_spec_figure_v3.svg` | Final vector figure (editable in Illustrator/Inkscape) |
| `figure_v3.py` | Self-contained Python script to reproduce the figure |

---

## 7. Reproduction Instructions

### Requirements
```bash
pip install matplotlib seaborn pandas numpy --break-system-packages
```

### Steps
1. Place `test_mass_spec.csv` at the path defined in `CONFIG["data_path"]` in the script (or update the path).
2. Update `CONFIG["out_png"]` and `CONFIG["out_svg"]` to your desired output paths.
3. Run: `python3 figure_v3.py`
4. Outputs: one PNG and one SVG file.

### To switch font to Arial (local machine)
If running on a machine with Arial installed, no changes are needed — the font detection at the top of the script will automatically select Arial first. The priority order is:
```
Arial → Helvetica → Liberation Sans → DejaVu Sans → sans-serif
```

### To change colors
Edit the `cat_colors` dict in `CONFIG` at the top of the script. All colors are hex strings.

### To re-enable all duplicate rows
Remove or comment out the deduplication block and replace `df_dedup` with `df` throughout.
