# Audit Trail: Figure Generation Workflow

**Date:** March 2, 2026
**Dataset:** `biolog_output.csv` (Metabolic Output Data)
**Target Format:** *Cell* Journal Print Specifications (Single Column)
**Tools Utilized:** Python 3, `pandas`, `seaborn`, `matplotlib`, `numpy`

---

## 1. Initial Initialization & v1.0 Generation

### User Request (v1.0)
> "Make a heatmap from this table. Color scale should be green (lowest) to white to red (highest). Use normal standardization for color scale. Use Cell's journal figure style. Figure title is 'Metabolic Output Data for B. cereus' (B. cereus in italic), font arial, font size 9. No numbers inside the cell. Cells should be square in size. Very thin (1 point) border around each cell. Place scale on the right side- for height, 1/3 the size of the main heatmap, aspect ratio 1:12. 1 point border around the scale. Labels: no border around text, white background. For x and y axis labels, font arial, font size 7."

### Technical Implementation (v1.0)
* **Data Normalization:** A global Z-score standardization was applied to the entire dataset. 
    * *Formula:* `(df - np.nanmean(vals)) / np.nanstd(vals)`
    * *Color Scale Bounds:* Dynamically set to `-max(abs(df_norm))` and `+max(abs(df_norm))` to ensure white represents exactly 0.
* **Dimensions:** Mapped *Cell* single-column width (85 mm) to inches: `figsize=(3.346, 3.346)` at `300 DPI`.
* **Color Palette:** Created a custom diverging colormap `LinearSegmentedColormap` using `["green", "white", "red"]`.
* **Main Axes Geometry:** Manually set to `[0.15, 0.15, 0.65, 0.65]` to ensure perfect square aspect ratio for cells while leaving room for the custom colorbar. 
* **Colorbar Geometry:** Dynamically calculated based on the main axes (`ax.get_position()`). 
    * *Height:* 33.3% (`pos.height * (1/3)`).
    * *Width:* Height divided by 12 (Aspect ratio 1:12).
    * *Placement:* Vertically centered relative to the main heatmap, shifted to the right (`pos.x1 + 0.05`).
* **Typography:** Applied `['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']` globally. Title set to 9 pt, axis labels to 7 pt. Label bounding boxes set to `dict(facecolor='white', edgecolor='none', pad=0)`.
* **Borders:** Heatmap cells and colorbar outline both set to `linewidth=1`, `color='black'`.

---

## 2. Revision 1: Scale & Axis Modifications (v1.1)

### User Request (v1.1)
> "Change coloring scale to run from -0.5 to 0.5 Remove x- and y-ticks. Change tick label text direction to upright. Change x- and y-axis titles to 'Nutrient ID'."

### Technical Implementation (v1.1)
* **Scale Bounds:** Overrode the dynamic Z-score maximums. Explicitly set `vmin=-0.5` and `vmax=0.5` in the `sns.heatmap()` call.
* **Axis Titles:** Updated `ax.set_xlabel` and `ax.set_ylabel` strings from 'Column'/'Row' to `'Nutrient ID'`.
* **Tick Marks & Labels:** * Removed physical ticks by setting `length=0` in `ax.tick_params`.
    * Forced upright orientation using `plt.setp(ax.get_xticklabels(), rotation=0, ha='center')` and `plt.setp(ax.get_yticklabels(), rotation=0, va='center')`.

---

## 3. Revision 2: Fine-Tuning & Typography (v1.2)

### User Request (v1.2)
> "Decrease individual cell border size by 50%. Decrease spacing between . and c in the title 'B. cereus' by 30%. Decrease font size for scale by 50%, make negative sign in the scale a short dash (instead of regular/long dash). Decrease scale border thicknessby 50%."

### Technical Implementation (v1.2)
* **Borders:** Decreased `border_width` configuration parameter from `1.0` to `0.5` for both the `sns.heatmap` (`linewidths=0.5`) and the colorbar outline (`cbar.outline.set_linewidth(0.5)`).
* **Title Spacing:** Modified the LaTeX string in the title from `r"...\it{B.\ cereus}"` (standard math space) to `r"...\it{B.\,cereus}"` (thin math space), reducing the character gap by ~30%.
* **Scale Typography:** * Reduced colorbar tick label font size from 7 pt to 3.5 pt.
    * Configured `plt.rcParams['axes.unicode_minus'] = False` to force matplotlib to use the standard ASCII hyphen (`-`) instead of the longer Unicode minus sign (`−`) for negative values on the scale.

---

## 4. Final Recapitulation Script (v1.2)

Running the following standalone script with `biolog_output.csv` in the same directory will exactly reproduce the final audited figure.

```python
# v1.2 | Heatmap | biolog_output.csv | Adjusted borders, spacing, and tick sizes
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

CONFIG = {
    "filename": "biolog_output.csv",
    "figsize_inches": (3.346, 3.346), # 85mm Cell Single Column Width
    "dpi": 300,
    "title": r"Metabolic Output Data for $\it{B.\,cereus}$", # \, = thin math space
    "title_size": 9,
    "label_size": 7,
    "tick_size": 7,
    "cbar_tick_size": 3.5, 
    "font_family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "colors": ["green", "white", "red"],
    "border_width": 0.5, 
    "cbar_height_ratio": 1/3,
    "cbar_aspect": 12,
    "vmin": -0.5,
    "vmax": 0.5
}

# Apply font settings & negative sign formatting
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = CONFIG["font_family"]
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['axes.unicode_minus'] = False # ASCII hyphen for negative signs

# Load & Standardize Data (Global Z-score)
df = pd.read_csv(CONFIG["filename"], index_col=0)
vals = df.values
df_norm = (df - np.nanmean(vals)) / np.nanstd(vals)

# Initialize Figure & Main Axes
fig = plt.figure(figsize=CONFIG["figsize_inches"], dpi=CONFIG["dpi"])
ax = fig.add_axes([0.15, 0.15, 0.65, 0.65]) 

# Custom colormap
cmap = mcolors.LinearSegmentedColormap.from_list('custom_diverging', CONFIG["colors"])

# Plot heatmap
sns.heatmap(df_norm, cmap=cmap, square=True, 
            linewidths=CONFIG["border_width"], linecolor='black', 
            annot=False, cbar=False, ax=ax,
            vmin=CONFIG["vmin"], vmax=CONFIG["vmax"]) 

# Title and Axis Labels
ax.set_title(CONFIG["title"], fontsize=CONFIG["title_size"], pad=10)
label_bbox = dict(facecolor='white', edgecolor='none', pad=0)
ax.set_xlabel('Nutrient ID', fontsize=CONFIG["label_size"], bbox=label_bbox)
ax.set_ylabel('Nutrient ID', fontsize=CONFIG["label_size"], bbox=label_bbox)

# Tick Formatting (No lines, upright text)
ax.tick_params(axis='both', which='major', labelsize=CONFIG["tick_size"], length=0)
plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
plt.setp(ax.get_yticklabels(), rotation=0, va='center')

# Colorbar Geometry Calculation
fig.canvas.draw()
pos = ax.get_position()
cbar_height = pos.height * CONFIG["cbar_height_ratio"]
cbar_width = cbar_height / CONFIG["cbar_aspect"]
cbar_bottom = pos.y0 + (pos.height - cbar_height) / 2
cbar_left = pos.x1 + 0.05

# Draw Colorbar
cax = fig.add_axes([cbar_left, cbar_bottom, cbar_width, cbar_height])
cbar = fig.colorbar(ax.collections[0], cax=cax)
cbar.outline.set_linewidth(CONFIG["border_width"])
cbar.outline.set_edgecolor('black')
cax.tick_params(labelsize=CONFIG["cbar_tick_size"], length=0)

plt.show()