# Conversation Export
**Date:** February 26, 2026
**Topic:** Bradford Assay Standard Curve — BSA Standards with apoHb Unknown

---

## Turn 1 — User

> Make a standard curve from the Bradford Curves csv. 5-point BSA standards, plot concentration vs OD600. Linear regression. Interpolate the apoHb unknown sample. Show dashed lines for the interpolation and mark the intersection point. Display R² and equation. Use Nature-style formatting.

## Turn 1 — Assistant

Read and audited `Bradford Curves.csv`:
- **Shape:** 9 rows × 2 columns (mg/mL, OD600) with empty separator row and non-numeric "apoHb" entry
- **Standards:** 5 BSA concentrations (0, 0.25, 0.5, 0.75, 1.0 mg/mL)
- **Unknown:** apoHb sample, OD600 = 0.342
- Parsed with `pd.to_numeric(errors="coerce")` to handle mixed types

Generated `figure_v1.py` producing a standard curve with:
- Scatter plot of BSA standards (Wong blue `#0072B2`)
- Linear regression via `scipy.stats.linregress`
- Horizontal + vertical dashed interpolation lines (Wong vermillion `#D55E00`)
- Diamond marker at apoHb intersection
- R² and equation in upper-left text box
- Nature single-column width (89 mm), 300 DPI, despined axes

**Delivered:** `figure_v1.png`, `figure_v1.svg`, `figure_v1.py`

---

## Turn 2 — User

> Add title "Bradford Assay Standard Curve". Increase marker size. Annotate the apoHb concentration below the x-axis drop line. Remove the equation text box border and move it to lower-right. Axis titles to 8 pt. X-ticks at 0.25 intervals. Add a legend upper-left with gray border.

## Turn 2 — Assistant

Applied all changes to produce `figure_v2.py`:
- Title added at 10 pt: "Bradford Assay Standard Curve"
- Marker size increased: 5 → 6
- apoHb concentration annotated below the vertical dashed line
- R²/equation repositioned to lower-right (0.95, 0.15), border removed
- Axis title font size set to 8 pt
- X-ticks set to [0, 0.25, 0.5, 0.75, 1.0]
- Legend added upper-left with gray border (`frameon=True`, `edgecolor="grey"`, linewidth 0.5)

**Delivered:** `figure_v2.png`, `figure_v2.svg`, `figure_v2.py`

---

## Turn 3 — User

> All fonts -1 pt. Remove zero ticks. Label the apoHb point directly with bold text instead of the concentration annotation below the axis. Regression line 25% thinner. Dashed lines to 0.6 pt. Legend border to 0.4 pt.

## Turn 3 — Assistant

Applied all changes to produce `figure_v3.py`:
- All font sizes reduced by 1 pt: base 7→6, ticks 6→5, labels 7→6, annotations 6→5, axis titles 8→7, plot title 10→9
- Zero ticks filtered from both x- and y-axes
- apoHb point labeled directly with bold "apoHb" text (offset 8, 5 points from marker)
- Regression linewidth: 1.0 → 0.75 pt (25% reduction)
- Dashed interpolation linewidth: 0.8 → 0.6 pt
- Legend border linewidth: 0.5 → 0.4 pt

**Delivered:** `figure_v3.png`, `figure_v3.svg`, `figure_v3.py`

---

## File Summary

| File | Description |
|------|-------------|
| `Bradford Curves.csv` | Raw data — 5 BSA standards + apoHb unknown |
| `figure_v1.py` | Initial standard curve script |
| `figure_v1.png` / `.svg` | Initial figure — scatter, regression, interpolation lines, R² text box |
| `figure_v2.py` | After title, marker size, annotation, legend, tick edits |
| `figure_v2.png` / `.svg` | v2 figure output |
| `figure_v3.py` | After font reduction, zero tick removal, direct label, linewidth edits |
| `figure_v3.png` / `.svg` | Final figure output |
| `conversation_export_bradford.md` | This file |

---

## Statistical Note

Linear regression performed via `scipy.stats.linregress` (OLS) on 5 BSA standard points. R² ≈ 0.99, indicating excellent linearity. The apoHb unknown sample (OD600 = 0.342) was interpolated to ≈ 0.882 mg/mL using the regression equation. The pre-calculated value in the CSV is 0.8815 mg/mL. Statistics were not modified during visual iteration turns, consistent with the scientific-figure skill guidelines.
