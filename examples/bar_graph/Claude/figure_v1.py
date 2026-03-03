import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy.stats import ttest_ind
import io, re

# ── Font detection ────────────────────────────────────────────────────────────
available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial","Helvetica","DejaVu Sans","Liberation Sans"] if f in available), "sans-serif")
plt.rcParams["font.family"] = FONT

# ── CONFIG ────────────────────────────────────────────────────────────────────
CONFIG = {
    "data_path":   "/mnt/user-data/uploads/boltz_hp3.csv",
    # Cell Press double-column: 174 mm wide → split into two panels
    # 2:3 aspect ratio per panel → width=85mm, height=127.5mm
    "fig_w_in":    (85  / 25.4) * 2 + 0.6,   # two panels + gap
    "fig_h_in":    127.5 / 25.4,
    "dpi":         300,
    "font_size":   7,
    "title_size":  8,
    "tick_size":   6,
    "lw":          0.5,          # bar border & error bar linewidth (0.5 pt)
    "capsize":     3,
    "bar_width":   0.35,
    "colors":      {"hp3": "#E83030", "hp31": "#2457C5"},   # red / blue
    "alpha":       1.0,
    "out_png":     "/mnt/user-data/outputs/figure_v1.png",
    "out_svg":     "/mnt/user-data/outputs/figure_v1.svg",
}

# ── Load & clean data ─────────────────────────────────────────────────────────
raw = pd.read_csv(CONFIG["data_path"], encoding="utf-8-sig")
raw.columns = raw.columns.str.strip()
raw["Value"] = raw["Value"].astype(str).str.replace(",", "").str.strip().astype(float)
raw["Sample"] = raw["Sample"].str.strip()

# ── Group mapping ─────────────────────────────────────────────────────────────
# Canonical labels shown on x-axis
LABEL_MAP = {
    "hp3 kdo3":  ("hp3",  "KDO"),
    "hp3 o-ant": ("hp3",  "O-Ant"),
    "hp31 kdo3": ("hp31", "KDO"),
    "hp31 o-ant":("hp31", "O-Ant"),
}
raw["strain"]   = raw["Sample"].map(lambda s: LABEL_MAP.get(s, (None,None))[0])
raw["receptor"] = raw["Sample"].map(lambda s: LABEL_MAP.get(s, (None,None))[1])

# ── Helper: p → stars ─────────────────────────────────────────────────────────
def p_to_stars(p):
    if p < 0.0001: return "****"
    if p < 0.001:  return "***"
    if p < 0.01:   return "**"
    if p < 0.05:   return "*"
    return "ns"

# ── Helper: stat bracket ──────────────────────────────────────────────────────
def add_stat_bracket(ax, x1, x2, y, p, h=0.03, lw=0.5):
    stars = p_to_stars(p)
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=lw, c="black", clip_on=False)
    ax.text((x1+x2)/2, y+h*1.05, stars, ha="center", va="bottom",
            fontsize=CONFIG["font_size"], clip_on=False)

# ── Plot factory ──────────────────────────────────────────────────────────────
def make_bar(ax, metric, ylabel, title):
    df = raw[raw["Type"] == metric].copy()

    # X positions: KDO=0, O-Ant=1 ; hp3 offset left, hp31 offset right
    bw = CONFIG["bar_width"]
    x_kdo   = 0
    x_oant  = 1
    offsets = {"hp3": -bw/2, "hp31": bw/2}

    bars_info = {}   # strain → (x_center, mean, sem, data_array)
    for strain, color in CONFIG["colors"].items():
        for receptor, xbase in [("KDO", x_kdo), ("O-Ant", x_oant)]:
            vals = df[(df["strain"]==strain) & (df["receptor"]==receptor)]["Value"].values
            m, s = vals.mean(), vals.std(ddof=1)/np.sqrt(len(vals))
            xc = xbase + offsets[strain]
            bars_info[(strain, receptor)] = (xc, m, s, vals)

            bar = ax.bar(xc, m, width=bw, color=color, alpha=CONFIG["alpha"],
                         linewidth=CONFIG["lw"], edgecolor="black",
                         label=f"hp3.1" if strain=="hp31" else "hp3"
                               if receptor=="KDO" else "_nolegend_")
            ax.errorbar(xc, m, yerr=s, fmt="none", elinewidth=CONFIG["lw"],
                        capthick=CONFIG["lw"], capsize=CONFIG["capsize"], color="black")

    # ── T-tests for three pairs ───────────────────────────────────────────────
    # Pair 1: hp3 kdo vs hp3 o-ant
    _, p1 = ttest_ind(bars_info[("hp3","KDO")][3], bars_info[("hp3","O-Ant")][3], equal_var=False)
    # Pair 2: hp3.1 kdo vs hp3.1 o-ant
    _, p2 = ttest_ind(bars_info[("hp31","KDO")][3], bars_info[("hp31","O-Ant")][3], equal_var=False)
    # Pair 3: hp3 (all) vs hp3.1 (all)  — pool both receptors per strain
    hp3_all  = df[df["strain"]=="hp3"]["Value"].values
    hp31_all = df[df["strain"]=="hp31"]["Value"].values
    _, p3 = ttest_ind(hp3_all, hp31_all, equal_var=False)

    # ── Y range for brackets ─────────────────────────────────────────────────
    all_vals = df["Value"].values
    ymax = all_vals.max() + abs(all_vals).max() * 0.05
    pad  = abs(all_vals).max() * 0.12   # vertical step between brackets

    # Pair 1 bracket (hp3 KDO ↔ hp3 O-Ant)
    x1a = bars_info[("hp3","KDO")][0]
    x1b = bars_info[("hp3","O-Ant")][0]
    y1  = ymax
    add_stat_bracket(ax, x1a, x1b, y1, p1, h=pad*0.3)

    # Pair 2 bracket (hp3.1 KDO ↔ hp3.1 O-Ant)
    x2a = bars_info[("hp31","KDO")][0]
    x2b = bars_info[("hp31","O-Ant")][0]
    y2  = ymax
    add_stat_bracket(ax, x2a, x2b, y2, p2, h=pad*0.3)

    # Pair 3 bracket (hp3 centre ↔ hp3.1 centre) — placed higher
    y3 = ymax + pad * 0.6
    xc_hp3  = (bars_info[("hp3","KDO")][0]  + bars_info[("hp3","O-Ant")][0])  / 2
    xc_hp31 = (bars_info[("hp31","KDO")][0] + bars_info[("hp31","O-Ant")][0]) / 2
    add_stat_bracket(ax, xc_hp3, xc_hp31, y3, p3, h=pad*0.3)

    # ── Axes styling (Cell Press) ─────────────────────────────────────────────
    ax.set_xticks([x_kdo, x_oant])
    ax.set_xticklabels(["KDO\nhp3 / hp3.1", "O-Ant\nhp3 / hp3.1"],
                       fontsize=CONFIG["tick_size"])
    ax.set_xlabel("Strain and Receptor", fontsize=CONFIG["font_size"], labelpad=4)
    ax.set_ylabel(ylabel, fontsize=CONFIG["font_size"], labelpad=4)
    ax.set_title(title, fontsize=CONFIG["title_size"], fontweight="bold", pad=6)
    ax.tick_params(axis="both", which="both", labelsize=CONFIG["tick_size"],
                   width=CONFIG["lw"], length=3)
    for spine in ["top","right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left","bottom"]:
        ax.spines[spine].set_linewidth(CONFIG["lw"])

    # Adjust y-limit to show brackets
    ax.set_ylim(bottom=None, top=y3 + pad * 0.9)

    # ── Legend ────────────────────────────────────────────────────────────────
    handles = [
        plt.Rectangle((0,0),1,1, color=CONFIG["colors"]["hp3"],  linewidth=CONFIG["lw"], edgecolor="black"),
        plt.Rectangle((0,0),1,1, color=CONFIG["colors"]["hp31"], linewidth=CONFIG["lw"], edgecolor="black"),
    ]
    ax.legend(handles, ["hp3", "hp3.1"], fontsize=CONFIG["tick_size"],
              frameon=False, loc="upper right", handlelength=1.2, handleheight=1.0)

# ── Build figure ──────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2,
    figsize=(CONFIG["fig_w_in"], CONFIG["fig_h_in"]),
    dpi=CONFIG["dpi"])

make_bar(ax1, "pred_prob",  "Probability of Binding",  "Probability of Binding")
make_bar(ax2, "pred_value", "Prediction Confidence",   "Prediction Confidence")

fig.tight_layout(pad=1.2, w_pad=1.5)

# ── Save ──────────────────────────────────────────────────────────────────────
fig.savefig(CONFIG["out_png"], dpi=CONFIG["dpi"], bbox_inches="tight")
fig.savefig(CONFIG["out_svg"], bbox_inches="tight")
print("Saved PNG and SVG.")
