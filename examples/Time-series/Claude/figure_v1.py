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
    "out_png":      "/mnt/user-data/outputs/figure_v1.png",
    "out_svg":      "/mnt/user-data/outputs/figure_v1.svg",
    "figsize_in":   (3.5, 2.8),          # Nature single column (89 mm ≈ 3.5 in)
    "dpi":          300,
    "linewidth":    0.9,
    "marker_size":  3.5,
    "capsize":      2.5,
    "eb_linewidth": 0.7,
    "font_size":    7,
    "tick_size":    6,
    "label_size":   7,
    "legend_size":  6,
    "series":       ["A1", "B1", "C1", "D1"],
    "color":        "black",
    "markers":      ["o", "s", "^", "D"],   # distinct marker per series
}

# ── FONT ──────────────────────────────────────────────────────────────────────
available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"]
             if f in available), "sans-serif")
plt.rcParams.update({
    "font.family":       FONT,
    "font.size":         CONFIG["font_size"],
    "axes.labelsize":    CONFIG["label_size"],
    "xtick.labelsize":   CONFIG["tick_size"],
    "ytick.labelsize":   CONFIG["tick_size"],
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
even_hours = list(range(0, 25, 2))
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
        fmt=CONFIG["markers"][i] + "-",
        color=CONFIG["color"],
        linewidth=CONFIG["linewidth"],
        markersize=CONFIG["marker_size"],
        markerfacecolor="white",
        markeredgecolor=CONFIG["color"],
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
ax.tick_params(width=0.6, length=3, direction="out")

ax.set_xlabel("Time (h)")
ax.set_ylabel("OD₆₀₀")
ax.set_xticks(even_hours)
ax.set_xlim(-0.5, 24.5)

legend = ax.legend(
    frameon=False,
    handlelength=1.5,
    handletextpad=0.4,
    borderpad=0,
    labelspacing=0.3,
    loc="upper left",
)

# Caption-style note for error bars
ax.text(
    0.98, 0.02,
    "Error bars: 95% CI (n = 3)",
    transform=ax.transAxes,
    ha="right", va="bottom",
    fontsize=5.5,
    color="gray",
)

plt.tight_layout(pad=0.5)

# ── SAVE ──────────────────────────────────────────────────────────────────────
fig.savefig(CONFIG["out_png"], dpi=CONFIG["dpi"], bbox_inches="tight")
fig.savefig(CONFIG["out_svg"], format="svg",       bbox_inches="tight")
print("Saved PNG and SVG.")
print(f"Timepoints plotted: {list(time_pts)}")
print(f"Font used: {FONT}")
