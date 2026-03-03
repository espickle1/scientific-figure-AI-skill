"""
Growth curve time series figure.
4 conditions (A1, B1, C1, D1), 3 biological replicates each.
Even-hour timepoints only. Error bars = 95% CI from t-distribution (n=3).
Nature-style formatting.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
from scipy.stats import t as t_dist

# ── CONFIG ────────────────────────────────────────────────────────────────────
CONFIG = {
    "data_path":    "/mnt/user-data/uploads/plate_growth_curve.csv",
    "out_png":      "/mnt/user-data/outputs/figure_v3.png",
    "out_svg":      "/mnt/user-data/outputs/figure_v3.svg",
    "figsize_in":   (3.5, 2.8),          # Nature single column (89 mm ≈ 3.5 in)
    "dpi":          300,
    "linewidth":    0.9,
    "marker_size":  1.75,                # 50% of 3.5
    "capsize":      2.5,
    "eb_linewidth": 0.7,
    "font_size":    5,                   # base −2
    "tick_size":    6,                   # overridden per-element below
    "label_size":   5,
    "legend_size":  4,
    "series":       ["A1", "B1", "C1", "D1"],
    "colors":       ["#0000FF", "#008000", "#EE82EE", "#FF0000"],
    "markers":      ["o", "o", "o", "o"],
    "font_axis_title": 6,                # 8 − 2
    "font_plot_title": 8,                # 10 − 2
    "font_tick":       6,                # 8 − 2
    "plot_title":   "Metabolic Output Over Time",
}

# ── FONT ──────────────────────────────────────────────────────────────────────
available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"]
             if f in available), "sans-serif")
plt.rcParams.update({
    "font.family":       FONT,
    "font.size":         CONFIG["font_size"],
    "axes.labelsize":    CONFIG["label_size"],
    "xtick.labelsize":   CONFIG["font_tick"],
    "ytick.labelsize":   CONFIG["font_tick"],
    "legend.fontsize":   CONFIG["legend_size"],
    "pdf.fonttype":      42,
    "ps.fonttype":       42,
})

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
# Header row has duplicate column names → read manually
raw = pd.read_csv(CONFIG["data_path"], header=0)
# Rename columns: Time + 3 replicates × 4 series
series = CONFIG["series"]
cols = ["Time"]
for rep in range(1, 4):
    for s in series:
        cols.append(f"{s}_r{rep}")
raw.columns = cols

# Parse time column (H:MM:SS → decimal hours)
def parse_hms(t):
    parts = str(t).split(":")
    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    return h + m / 60 + s / 3600

raw["hours"] = raw["Time"].apply(parse_hms)

# Filter to even-hour timepoints (0, 2, 4, … 24)
even_hours = list(range(0, 25, 4))
# Match rows where hours round to an even integer
raw["hours_round"] = raw["hours"].round(6)
df = raw[raw["hours_round"].apply(lambda h: any(abs(h - eh) < 1e-4 for eh in even_hours))].copy()
df = df.reset_index(drop=True)

# ── COMPUTE MEAN & 95% CI ─────────────────────────────────────────────────────
n = 3
t_crit = t_dist.ppf(0.975, df=n - 1)   # two-tailed 95% CI, df=2 → ~4.303

stats = {}
for s in series:
    rep_cols = [f"{s}_r{i}" for i in range(1, 4)]
    vals = df[rep_cols].values          # shape (timepoints, 3)
    mean = vals.mean(axis=1)
    sem  = vals.std(axis=1, ddof=1) / np.sqrt(n)
    ci95 = sem * t_crit
    stats[s] = {"mean": mean, "ci": ci95}

time_pts = df["hours_round"].values

# ── PLOT ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=CONFIG["figsize_in"])

for i, s in enumerate(series):
    m   = stats[s]["mean"]
    err = stats[s]["ci"]
    ax.errorbar(
        time_pts, m,
        yerr=err,
        fmt="o-",
        color=CONFIG["colors"][i],
        linewidth=CONFIG["linewidth"],
        markersize=CONFIG["marker_size"],
        markerfacecolor=CONFIG["colors"][i],
        markeredgecolor=CONFIG["colors"][i],
        markeredgewidth=0.7,
        capsize=CONFIG["capsize"],
        elinewidth=CONFIG["eb_linewidth"],
        label=s,
        zorder=3 + i,
    )

# Axes formatting (Nature style: despined, no grid)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.6)
ax.spines["bottom"].set_linewidth(0.6)
ax.tick_params(width=0.6, length=3, direction="out", labelsize=CONFIG["font_tick"])

ax.set_xlabel("Time (hours)", fontsize=CONFIG["font_axis_title"])
ax.set_ylabel("OD₆₀₀", fontsize=CONFIG["font_axis_title"])
ax.set_title(CONFIG["plot_title"], fontsize=CONFIG["font_plot_title"], pad=6)

# x-axis: ticks at 4, 8, ..., 24 (no tick at 0); axis starts at 0
ax.set_xticks([h for h in even_hours if h > 0])
ax.set_xlim(0, 24.5)

# y-axis: no tick at 0; start at 0
y_max = max(stats[s]["mean"].max() + stats[s]["ci"].max() for s in series) * 1.08
ax.set_ylim(0, y_max)
y_ticks = ax.get_yticks()
ax.set_yticks([t for t in y_ticks if t > 0 and t <= y_max])

# Legend: colored lines only (no markers), gray border, left edge at x=2
# Convert x=2 in data coords to axes fraction
x_legend_axes = 2.0 / 24.5   # ≈ 0.0816

from matplotlib.lines import Line2D
legend_handles = [
    Line2D([0], [0], color=CONFIG["colors"][i], linewidth=1.2, label=s)
    for i, s in enumerate(series)
]
legend = ax.legend(
    handles=legend_handles,
    frameon=True,
    framealpha=1.0,
    edgecolor="gray",
    fancybox=False,
    handlelength=1.4,
    handletextpad=0.4,
    borderpad=0.4,
    labelspacing=0.3,
    loc="upper left",
    bbox_to_anchor=(x_legend_axes, 1.0),
    bbox_transform=ax.transAxes,
    fontsize=CONFIG["legend_size"],
)

plt.tight_layout(pad=0.5)

# ── SAVE ──────────────────────────────────────────────────────────────────────
fig.savefig(CONFIG["out_png"], dpi=CONFIG["dpi"], bbox_inches="tight")
fig.savefig(CONFIG["out_svg"], format="svg",       bbox_inches="tight")
print("Saved PNG and SVG.")
print(f"Timepoints plotted: {list(time_pts)}")
print(f"Font used: {FONT}")
