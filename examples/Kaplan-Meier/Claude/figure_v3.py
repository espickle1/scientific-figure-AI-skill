"""
Kaplan-Meier survival plot — Joseph Mice
Groups: GST vs. Vac
Event: 1 = death, 0 = censored (survived to end)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

# ── CONFIG ─────────────────────────────────────────────────────────────────
CONFIG = {
    "data_path":    "/mnt/user-data/uploads/Joseph_Mice.csv",
    "time_col":     "Time",
    "event_col":    "Event",
    "group_col":    "Treatment",
    "groups":       ["GST", "Vac"],
    "colors":       ["#0000FF", "#FF0000"],   # blue GST, red Vac
    "markers":      ["o", "s"],               # censored tick shapes
    "x_min":        0,
    "x_max":        18,
    "fig_w_mm":     89,                       # Nature single-column
    "fig_h_mm":     75,
    "dpi":          300,
    "out_png":      "/mnt/user-data/outputs/figure_v3.png",
    "out_svg":      "/mnt/user-data/outputs/figure_v3.svg",
}

# ── FONT ───────────────────────────────────────────────────────────────────
available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"]
             if f in available), "sans-serif")
plt.rcParams.update({
    "font.family":      FONT,
    "font.size":        7,
    "axes.linewidth":   0.75,
    "xtick.major.width": 0.75,
    "ytick.major.width": 0.75,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.direction":  "out",
    "ytick.direction":  "out",
    "pdf.fonttype":     42,
    "svg.fonttype":     "none",
})

# ── LOAD DATA ──────────────────────────────────────────────────────────────
df = pd.read_csv(CONFIG["data_path"])
print(f"Shape: {df.shape}")
print(df.head())
print(df.groupby("Treatment").size())

# ── KAPLAN-MEIER FIT ───────────────────────────────────────────────────────
kmf = {}
n_start = {}
for grp in CONFIG["groups"]:
    sub = df[df[CONFIG["group_col"]] == grp]
    kf = KaplanMeierFitter()
    kf.fit(sub[CONFIG["time_col"]], event_observed=(sub[CONFIG["event_col"]] == 1),
           label=grp)
    kmf[grp] = kf
    n_start[grp] = len(sub)

# Log-rank test
g1 = df[df[CONFIG["group_col"]] == CONFIG["groups"][0]]
g2 = df[df[CONFIG["group_col"]] == CONFIG["groups"][1]]
lr = logrank_test(
    g1[CONFIG["time_col"]], g2[CONFIG["time_col"]],
    event_observed_A=(g1[CONFIG["event_col"]] == 1),
    event_observed_B=(g2[CONFIG["event_col"]] == 1),
)
p_val = lr.p_value
print(f"\nLog-rank p = {p_val:.4f}")

# ── PLOT ───────────────────────────────────────────────────────────────────
fig_w = CONFIG["fig_w_mm"] / 25.4
fig_h = CONFIG["fig_h_mm"] / 25.4
fig, ax = plt.subplots(figsize=(fig_w, fig_h))

for grp, color in zip(CONFIG["groups"], CONFIG["colors"]):
    kf = kmf[grp]
    n  = n_start[grp]
    t  = kf.timeline
    sf = kf.survival_function_[grp].values  # proportion (0–1)

    # Scale to number of mice remaining
    n_alive = sf * n

    # Step plot
    ax.step(t, n_alive, where="post", color=color, linewidth=1.125,
            label=f"{grp} (n={n})")

    # Censored tick marks — where event == 0
    sub = df[df[CONFIG["group_col"]] == grp]
    censored_times = sub.loc[sub[CONFIG["event_col"]] == 0, CONFIG["time_col"]].values
    for ct in censored_times:
        # Evaluate survival at censored time
        idx = np.searchsorted(t, ct, side="right") - 1
        idx = max(idx, 0)
        y_c = sf[idx] * n
        ax.plot(ct, y_c, "+", color=color, markersize=5, markeredgewidth=1.0)

# p-value annotation
def p_to_label(p):
    if p < 0.0001: return "****"
    if p < 0.001:  return "***"
    if p < 0.01:   return "**"
    if p < 0.05:   return "*"
    return "ns"

stars = p_to_label(p_val)
p_text = f"Log-rank {stars}\np = {p_val:.3f}"
ax.text(0.97, 0.97, p_text, transform=ax.transAxes,
        ha="right", va="top", fontsize=6)

# ── AXES FORMATTING ────────────────────────────────────────────────────────
ax.set_xlim(CONFIG["x_min"], CONFIG["x_max"])

# y-axis: maximum is the larger of the two starting n
y_max = max(n_start.values())
ax.set_ylim(0, y_max + 0.5)

ax.set_xlabel("Days post-vaccination", fontsize=8, labelpad=4)
ax.set_ylabel("Mice surviving", fontsize=8, labelpad=4)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Legend: lower-left corner anchored to data point (1 day, 1 mouse)
leg = ax.legend(frameon=True, fontsize=6, loc="lower left",
                bbox_to_anchor=(1, 1),          # data coordinates
                bbox_transform=ax.transData,
                handlelength=1.5, handletextpad=0.4,
                edgecolor="grey")
leg.get_frame().set_linewidth(0.5)

# Tick font size 5; suppress tick labels at 0 on both axes
ax.tick_params(labelsize=5)
ax.set_yticks([t for t in range(0, y_max + 1, 5) if t != 0])
ax.set_xticks([t for t in range(0, CONFIG["x_max"] + 1, 4) if t != 0])

ax.set_title("Mice Survival Curve: Iron Uptake System Vaccine",
             fontsize=10, fontname=FONT, pad=7.8)  # pad increased 30% from 6

plt.tight_layout(pad=0.5)

# ── SAVE ──────────────────────────────────────────────────────────────────
fig.savefig(CONFIG["out_png"], dpi=CONFIG["dpi"], bbox_inches="tight")
fig.savefig(CONFIG["out_svg"], bbox_inches="tight")
print("Saved PNG and SVG.")
