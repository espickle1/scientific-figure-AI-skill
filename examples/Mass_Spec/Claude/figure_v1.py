import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# ── CONFIG ──────────────────────────────────────────────────────────────────
CONFIG = {
    "data_path": "/mnt/user-data/uploads/test_mass_spec.csv",
    "categories": ["Crosslink", "Bridgelink", "Ala", "O-acetylation", "N-deacetylation", "Lactate"],
    "figsize": (9, 5.5),
    "dpi": 300,
    "bar_color": "#1B4F72",
    "bar_alpha": 0.85,
    "dot_size": 18,
    "dot_alpha_min": 0.15,
    "dot_alpha_max": 0.95,
    "heatmap_height_frac": 0.28,   # fraction of total figure height
    "cat_colors": {                 # color per category
        "Crosslink":       "#D55E00",
        "Bridgelink":      "#CC79A7",
        "Ala":             "#009E73",
        "O-acetylation":   "#009E73",
        "N-deacetylation": "#56B4E9",
        "Lactate":         "#56B4E9",
    },
    "out_png": "/mnt/user-data/outputs/mass_spec_figure_v1.png",
    "out_svg": "/mnt/user-data/outputs/mass_spec_figure_v1.svg",
}

# ── FONT ─────────────────────────────────────────────────────────────────────
available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial","Helvetica","DejaVu Sans","Liberation Sans"] if f in available), "sans-serif")
plt.rcParams["font.family"] = FONT
plt.rcParams["font.size"] = 7

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
df = pd.read_csv(CONFIG["data_path"])
cats = CONFIG["categories"]

# ── LAYOUT ───────────────────────────────────────────────────────────────────
# Two rows: top = bar chart, bottom = dot heatmap
fig = plt.figure(figsize=CONFIG["figsize"])
hfrac = CONFIG["heatmap_height_frac"]
gs = fig.add_gridspec(
    2, 2,
    height_ratios=[1 - hfrac, hfrac],
    width_ratios=[1, 0.18],          # main + stats sidebar
    hspace=0,
    wspace=0.04,
)

ax_bar   = fig.add_subplot(gs[0, 0])
ax_dot   = fig.add_subplot(gs[1, 0], sharex=ax_bar)
ax_stats = fig.add_subplot(gs[1, 1])   # stats panel

# ── BAR CHART ─────────────────────────────────────────────────────────────────
masses = df["mass"].values
aucs   = df["AUC"].values

# Sort by mass for plotting
order = np.argsort(masses)
x_sorted = masses[order]
y_sorted = aucs[order]

# Use the actual mass values as x positions
ax_bar.bar(x_sorted, y_sorted,
           width=(x_sorted.max() - x_sorted.min()) / len(x_sorted) * 0.6,
           color=CONFIG["bar_color"], alpha=CONFIG["bar_alpha"],
           linewidth=0)

ax_bar.set_ylabel("AUC", labelpad=4, fontsize=8)
ax_bar.set_xlim(x_sorted.min() - 50, x_sorted.max() + 80)
ax_bar.set_ylim(0, y_sorted.max() * 1.12)
ax_bar.spines[["top","right","bottom"]].set_visible(False)
ax_bar.spines["left"].set_linewidth(0.8)
ax_bar.spines["bottom"].set_visible(False)
ax_bar.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
ax_bar.tick_params(axis="y", labelsize=7)
ax_bar.yaxis.set_tick_params(width=0.6)

# ── DOT HEATMAP ───────────────────────────────────────────────────────────────
# For each category, minmax-normalize its values across all rows
n_cats = len(cats)
cat_y_positions = np.arange(n_cats)  # 0 = top cat, n-1 = bottom

# We'll invert so first category is at top
cat_to_y = {c: (n_cats - 1 - i) for i, c in enumerate(cats)}

for cat in cats:
    vals = df[cat].values[order].astype(float)
    vmin, vmax = vals.min(), vals.max()
    if vmax > vmin:
        norm_vals = (vals - vmin) / (vmax - vmin)
    else:
        norm_vals = np.zeros_like(vals)

    y_pos = cat_to_y[cat]
    color = CONFIG["cat_colors"][cat]

    # Only plot dots where value > 0
    mask = vals > 0
    if mask.sum() == 0:
        mask = np.ones(len(vals), dtype=bool)

    alphas = CONFIG["dot_alpha_min"] + norm_vals * (CONFIG["dot_alpha_max"] - CONFIG["dot_alpha_min"])

    for xi, ai, active in zip(x_sorted, alphas, mask):
        if active:
            ax_dot.scatter(xi, y_pos, s=CONFIG["dot_size"],
                           color=color, alpha=float(ai),
                           linewidths=0, zorder=3)

# Category labels on y-axis
ax_dot.set_yticks(list(cat_to_y.values()))
ax_dot.set_yticklabels(list(cat_to_y.keys()), fontsize=6.5)
ax_dot.set_ylim(-0.6, n_cats - 0.4)
ax_dot.set_xlabel("mass", fontsize=8, labelpad=3)
ax_dot.spines[["top","right"]].set_visible(False)
ax_dot.spines["left"].set_linewidth(0.8)
ax_dot.spines["bottom"].set_linewidth(0.8)
ax_dot.tick_params(axis="x", labelsize=7)
ax_dot.tick_params(axis="y", length=0, pad=3)

# Align x-axis spine of bar chart to zero
ax_bar.spines["left"].set_bounds(0, y_sorted.max())

# ── STATS SIDEBAR ─────────────────────────────────────────────────────────────
ax_stats.set_xlim(0, 1)
ax_stats.set_ylim(-0.6, n_cats - 0.4)
ax_stats.axis("off")

# Header
ax_stats.text(0.05, n_cats - 0.05, "mean ± SD", fontsize=6, va="top",
              color="#444444", style="italic")

for cat in cats:
    vals = df[cat].values.astype(float)
    mean_v = vals.mean()
    std_v  = vals.std()
    y_pos  = cat_to_y[cat]
    ax_stats.text(0.05, y_pos, f"{mean_v:.2f} ± {std_v:.2f}",
                  fontsize=6, va="center", color="#222222")

# ── TIGHT LAYOUT & SAVE ───────────────────────────────────────────────────────
fig.subplots_adjust(left=0.10, right=0.98, top=0.96, bottom=0.10)

for fmt, path in [("png", CONFIG["out_png"]), ("svg", CONFIG["out_svg"])]:
    fig.savefig(path, dpi=CONFIG["dpi"], bbox_inches="tight", format=fmt)

print("Saved.")
