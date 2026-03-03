# v1.1 | Heatmap | biolog_output.csv | Custom scale, upright labels, no ticks
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

CONFIG = {
    "filename": "biolog_output.csv",
    "figsize_inches": (3.346, 3.346), # 85mm Cell Single Column Width
    "dpi": 300,
    "title": r"Metabolic Output Data for $\it{B.\ cereus}$",
    "title_size": 9,
    "label_size": 7,
    "tick_size": 7,
    "font_family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "colors": ["green", "white", "red"],
    "border_width": 1,
    "cbar_height_ratio": 1/3,
    "cbar_aspect": 12,
    "vmin": -0.5,
    "vmax": 0.5
}

# Apply font settings
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = CONFIG["font_family"]
plt.rcParams['svg.fonttype'] = 'none'

# Load data
df = pd.read_csv(CONFIG["filename"], index_col=0)

# Apply Normal Standardization (Global Z-score)
vals = df.values
mean_val = np.nanmean(vals)
std_val = np.nanstd(vals)
df_norm = (df - mean_val) / std_val

# Create figure
fig = plt.figure(figsize=CONFIG["figsize_inches"], dpi=CONFIG["dpi"])
# Manual bounds for precise colorbar placement beside the square axes
ax = fig.add_axes([0.15, 0.15, 0.65, 0.65]) 

# Custom diverging colormap (Green -> White -> Red)
cmap = mcolors.LinearSegmentedColormap.from_list('custom_diverging', CONFIG["colors"])

# Plot heatmap
sns.heatmap(df_norm, cmap=cmap, square=True, 
            linewidths=CONFIG["border_width"], linecolor='black', 
            annot=False, cbar=False, ax=ax,
            vmin=CONFIG["vmin"], vmax=CONFIG["vmax"]) 

# Set title and labels
ax.set_title(CONFIG["title"], fontsize=CONFIG["title_size"], pad=10)
label_bbox = dict(facecolor='white', edgecolor='none', pad=0)
ax.set_xlabel('Nutrient ID', fontsize=CONFIG["label_size"], bbox=label_bbox)
ax.set_ylabel('Nutrient ID', fontsize=CONFIG["label_size"], bbox=label_bbox)

# Tick formatting
# Remove tick marks (length=0), keep labels, ensure text is upright (rotation=0)
ax.tick_params(axis='both', which='major', labelsize=CONFIG["tick_size"], length=0)

# Make sure text is upright
plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
plt.setp(ax.get_yticklabels(), rotation=0, va='center')

# Force layout update to access real axes dimensions
fig.canvas.draw()
pos = ax.get_position()

# Calculate colorbar geometry (1/3 height, 1:12 aspect)
cbar_height = pos.height * CONFIG["cbar_height_ratio"]
cbar_width = cbar_height / CONFIG["cbar_aspect"]
cbar_bottom = pos.y0 + (pos.height - cbar_height) / 2
cbar_left = pos.x1 + 0.05

# Draw colorbar
cax = fig.add_axes([cbar_left, cbar_bottom, cbar_width, cbar_height])
cbar = fig.colorbar(ax.collections[0], cax=cax)

# Colorbar styling
cbar.outline.set_linewidth(CONFIG["border_width"])
cbar.outline.set_edgecolor('black')
cax.tick_params(labelsize=CONFIG["tick_size"], length=0)

plt.show()