# Heatmap generation script (final version)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.font_manager as fm

# Load data
df = pd.read_csv('biolog_output.csv', index_col=0).apply(pd.to_numeric)

# Z-score normalization
z = (df - df.values.mean()) / df.values.std(ddof=0)

# Font setup
available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ['Arial','Helvetica','Liberation Sans','DejaVu Sans'] if f in available), 'sans-serif')
plt.rcParams['font.family'] = FONT

# Figure sizing
nrows, ncols = z.shape
cell_in = 0.28
fig_w = ncols * cell_in + 1.05
fig_h = nrows * cell_in + 0.62
fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=600)

# Colormap
cmap = LinearSegmentedColormap.from_list('gwr', ['#008000', '#FFFFFF', '#CC0000'])

# Heatmap
mesh = ax.pcolormesh(
    np.arange(ncols+1), np.arange(nrows+1), z.values,
    cmap=cmap, vmin=-0.5, vmax=0.5,
    edgecolors='black', linewidth=0.8
)

ax.set_aspect('equal')
ax.set_xlim(0, ncols)
ax.set_ylim(nrows, 0)

ax.set_xticks(np.arange(ncols)+0.5)
ax.set_yticks(np.arange(nrows)+0.5)
ax.set_xticklabels(df.columns, fontsize=7)
ax.set_yticklabels(df.index, fontsize=7)

# Tick styling
ax.tick_params(axis='both', length=1.5, width=1)

# Labels/title
ax.set_xlabel('Nutrient ID', fontsize=7)
ax.set_ylabel('Nutrient ID', fontsize=7)
ax.set_title(r'Metabolic Output Data for $\it{B.\ cereus}$', fontsize=9)

# Colorbar
cbar_h = (nrows * cell_in)/3
cbar_w = cbar_h/12
cax = inset_axes(ax, width=cbar_w, height=cbar_h,
                 loc='center left', bbox_to_anchor=(1.08,0,1,1),
                 bbox_transform=ax.transAxes)

cbar = fig.colorbar(mesh, cax=cax)
cbar.outline.set_linewidth(1)
cbar.ax.tick_params(length=1, width=0.5, labelsize=5)
cbar.set_label('Standardized output (z-score)', fontsize=5)

plt.tight_layout()
fig.savefig('heatmap_final.png', dpi=600, bbox_inches='tight')
plt.show()
