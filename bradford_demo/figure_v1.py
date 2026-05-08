# %% [markdown]
# # Figure v1 — Bradford assay standard curve
# Linear regression of OD600 vs BSA concentration (5-point standards), with
# dashed-line interpolation of an apoHb unknown. Nature single-column format.
# Data: Bradford Curves.csv. Columns: mg/mL (x), OD600 (y).

# %% [markdown]
# ## Setup
# Required packages: matplotlib pandas numpy scipy.
# Fresh Colab/Jupyter kernel? In a cell, run:
# `!pip install matplotlib pandas numpy scipy`

# %% [markdown]
# ## Imports

# %%
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
from scipy.stats import linregress

# %% [markdown]
# ## Config
# All tunables. Adjust here, not below.

# %%
CONFIG = {
    "data_path":       "Bradford Curves.csv",
    "out_png":         "figure_v1.png",
    "out_svg":         "figure_v1.svg",
    "figsize_in":      (3.5, 2.8),
    "dpi":             300,
    "marker_size":     5,
    "marker_color":    "#0072B2",
    "interp_color":    "#D55E00",
    "dash_linewidth":  0.8,
    "reg_linewidth":   1.0,
    "font_size":       7,
    "tick_size":       6,
    "label_size":      7,
    "annotation_size": 6,
}

available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"]
             if f in available), "sans-serif")
plt.rcParams.update({
    "font.family":     FONT,
    "font.size":       CONFIG["font_size"],
    "axes.labelsize":  CONFIG["label_size"],
    "xtick.labelsize": CONFIG["tick_size"],
    "ytick.labelsize": CONFIG["tick_size"],
    "pdf.fonttype":    42,
    "ps.fonttype":     42,
})

# %% [markdown]
# ## Load data

# %%
raw = pd.read_csv(CONFIG["data_path"])
raw.head()

# %% [markdown]
# ## Transform
# Coerce numeric columns, separate the apoHb unknown row from the BSA standards.

# %%
raw["mg/mL_num"] = pd.to_numeric(raw["mg/mL"], errors="coerce")
raw["OD600"]    = pd.to_numeric(raw["OD600"], errors="coerce")

standards = raw.dropna(subset=["mg/mL_num", "OD600"])
conc = standards["mg/mL_num"].values
od   = standards["OD600"].values

apoHb_row = raw[raw["mg/mL"] == "apoHb"]
apoHb_od  = float(apoHb_row["OD600"].values[0])

slope, intercept, r_value, p_value, std_err = linregress(conc, od)
r_squared  = r_value ** 2
apoHb_conc = (apoHb_od - intercept) / slope

x_fit = np.linspace(0, conc.max() * 1.05, 100)
y_fit = slope * x_fit + intercept

# %% [markdown]
# ## Plot

# %%
fig, ax = plt.subplots(figsize=CONFIG["figsize_in"], dpi=CONFIG["dpi"])

ax.scatter(conc, od, s=CONFIG["marker_size"] ** 2, color=CONFIG["marker_color"],
           zorder=5, label="BSA Standards")
ax.plot(x_fit, y_fit, color=CONFIG["marker_color"],
        linewidth=CONFIG["reg_linewidth"], zorder=3, label="Linear fit")

ax.plot([apoHb_conc, apoHb_conc], [0, apoHb_od],
        color=CONFIG["interp_color"], linestyle="--",
        linewidth=CONFIG["dash_linewidth"], zorder=4)
ax.plot([0, apoHb_conc], [apoHb_od, apoHb_od],
        color=CONFIG["interp_color"], linestyle="--",
        linewidth=CONFIG["dash_linewidth"], zorder=4)
ax.scatter([apoHb_conc], [apoHb_od], s=CONFIG["marker_size"] ** 2 * 1.5,
           color=CONFIG["interp_color"], marker="D", zorder=6)

eq_text = f"y = {slope:.4f}x + {intercept:.4f}\nR² = {r_squared:.4f}"
ax.text(0.05, 0.95, eq_text, transform=ax.transAxes,
        fontsize=CONFIG["annotation_size"], verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor="gray", linewidth=0.5))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.6)
ax.spines["bottom"].set_linewidth(0.6)
ax.tick_params(width=0.6, length=3, direction="out")

ax.set_xlabel("BSA Concentration (mg/mL)", fontsize=CONFIG["label_size"])
ax.set_ylabel(r"$\mathregular{OD_{600}}$", fontsize=CONFIG["label_size"])
ax.set_xlim(0, conc.max() * 1.1)
ax.set_ylim(0, max(od.max(), apoHb_od) * 1.15)

plt.tight_layout(pad=0.5)
plt.show()

# %% [markdown]
# ## Save

# %%
fig.savefig(CONFIG["out_png"], dpi=CONFIG["dpi"], bbox_inches="tight")
fig.savefig(CONFIG["out_svg"], format="svg", bbox_inches="tight")
print(f"Slope: {slope:.4f}, Intercept: {intercept:.4f}, R²: {r_squared:.4f}")
print(f"apoHb OD600: {apoHb_od}, Interpolated: {apoHb_conc:.4f} mg/mL")
