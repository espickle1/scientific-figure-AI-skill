import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Patch
from scipy.stats import ttest_ind

available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial","Helvetica","DejaVu Sans","Liberation Sans"] if f in available), "sans-serif")
plt.rcParams["font.family"] = FONT

CONFIG = {
    "data_path":   "/mnt/user-data/uploads/boltz_hp3.csv",
    "fig_w_in":    (85  / 25.4) * 2 + 0.6,
    "fig_h_in":    127.5 / 25.4,
    "dpi":         300,
    "font_size":   9,
    "title_size":  8,
    "tick_size":   7,
    "legend_size": 8,
    "lw":          0.5,
    "capsize":     3,
    "bar_width":   0.35,
    "colors":      {"hp3": "#E83030", "hp31": "#2457C5"},
    "alpha":       1.0,
    "out_png":     "/mnt/user-data/outputs/figure_v2.png",
    "out_svg":     "/mnt/user-data/outputs/figure_v2.svg",
}

raw = pd.read_csv(CONFIG["data_path"], encoding="utf-8-sig")
raw.columns = raw.columns.str.strip()
raw["Value"] = raw["Value"].astype(str).str.replace(",", "").str.strip().astype(float)
raw["Sample"] = raw["Sample"].str.strip()

LABEL_MAP = {
    "hp3 kdo3":  ("hp3",  "KDO"),
    "hp3 o-ant": ("hp3",  "O-Ant"),
    "hp31 kdo3": ("hp31", "KDO"),
    "hp31 o-ant":("hp31", "O-Ant"),
}
raw["strain"]   = raw["Sample"].map(lambda s: LABEL_MAP.get(s, (None, None))[0])
raw["receptor"] = raw["Sample"].map(lambda s: LABEL_MAP.get(s, (None, None))[1])

def p_to_stars(p):
    if p < 0.0001: return "****"
    if p < 0.001:  return "***"
    if p < 0.01:   return "**"
    if p < 0.05:   return "*"
    return "ns"

def add_stat_bracket(ax, x1, x2, y, p, h, lw=0.5):
    stars = p_to_stars(p)
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=lw, c="black", clip_on=False)
    ax.text((x1+x2)/2, y+h*1.05, stars, ha="center", va="bottom",
            fontsize=CONFIG["tick_size"], clip_on=False)

def make_bar(ax, metric, ylabel, title, ystart=None):
    df = raw[raw["Type"] == metric].copy()

    bw = CONFIG["bar_width"]
    x_hp3  = 0
    x_hp31 = 1
    offsets = {"KDO": -bw/2, "O-Ant": bw/2}

    bars_info = {}

    for strain_key, xbase in [("hp3", x_hp3), ("hp31", x_hp31)]:
        color = CONFIG["colors"][strain_key]
        for receptor, shade_alpha in [("KDO", 1.0), ("O-Ant", 0.45)]:
            vals = df[(df["strain"]==strain_key) & (df["receptor"]==receptor)]["Value"].values
            m = vals.mean()
            s = vals.std(ddof=1) / np.sqrt(len(vals))
            xc = xbase + offsets[receptor]
            bars_info[(strain_key, receptor)] = (xc, m, s, vals)

            ax.bar(xc, m, width=bw, color=color, alpha=shade_alpha,
                   linewidth=CONFIG["lw"], edgecolor="black")
            ax.errorbar(xc, m, yerr=s, fmt="none", elinewidth=CONFIG["lw"],
                        capthick=CONFIG["lw"], capsize=CONFIG["capsize"], color="black")

    _, p_hp3  = ttest_ind(bars_info[("hp3",  "KDO")][3],
                          bars_info[("hp3",  "O-Ant")][3], equal_var=False)
    _, p_hp31 = ttest_ind(bars_info[("hp31", "KDO")][3],
                          bars_info[("hp31", "O-Ant")][3], equal_var=False)

    all_vals = df["Value"].values
    data_range = abs(all_vals).max()
    pad = data_range * 0.13

    bar_tops = [bars_info[k][1] + bars_info[k][2] for k in bars_info]
    bracket_base = max(bar_tops) + pad * 0.4

    x1a = bars_info[("hp3",  "KDO")][0]
    x1b = bars_info[("hp3",  "O-Ant")][0]
    add_stat_bracket(ax, x1a, x1b, bracket_base, p_hp3,  h=pad * 0.35)

    x2a = bars_info[("hp31", "KDO")][0]
    x2b = bars_info[("hp31", "O-Ant")][0]
    add_stat_bracket(ax, x2a, x2b, bracket_base, p_hp31, h=pad * 0.35)

    top_ylim = bracket_base + pad * 0.95

    ax.set_xticks([x_hp3, x_hp31])
    ax.set_xticklabels(["hp3", "hp3.1"], fontsize=CONFIG["tick_size"])
    ax.set_xlabel("Strain and Receptor", fontsize=CONFIG["font_size"], labelpad=4)
    ax.set_ylabel(ylabel, fontsize=CONFIG["font_size"], labelpad=4)
    ax.set_title(title, fontsize=CONFIG["title_size"], fontweight="bold", pad=6)
    ax.tick_params(axis="both", which="both", labelsize=CONFIG["tick_size"],
                   width=CONFIG["lw"], length=3)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_linewidth(CONFIG["lw"])

    if ystart is not None:
        ax.set_ylim(bottom=ystart, top=top_ylim)
    else:
        ax.set_ylim(top=top_ylim)

    # Remove y=0 tick
    ax.figure.canvas.draw()
    yticks = [t for t in ax.get_yticks() if not np.isclose(t, 0)]
    ax.set_yticks(yticks)

    handles = [
        Patch(facecolor="grey", alpha=1.0,  edgecolor="black", linewidth=CONFIG["lw"], label="KDO"),
        Patch(facecolor="grey", alpha=0.45, edgecolor="black", linewidth=CONFIG["lw"], label="O-Ant"),
    ]
    ax.legend(handles=handles, fontsize=CONFIG["legend_size"],
              frameon=False, loc="upper right", handlelength=1.2, handleheight=1.0)

fig, (ax1, ax2) = plt.subplots(1, 2,
    figsize=(CONFIG["fig_w_in"], CONFIG["fig_h_in"]),
    dpi=CONFIG["dpi"])

make_bar(ax1, "pred_prob",  "Probability of Binding", "Probability of Binding", ystart=None)
make_bar(ax2, "pred_value", "Prediction Confidence",  "Prediction Confidence",  ystart=0)

fig.tight_layout(pad=1.2, w_pad=1.5)

fig.savefig(CONFIG["out_png"], dpi=CONFIG["dpi"], bbox_inches="tight")
fig.savefig(CONFIG["out_svg"], bbox_inches="tight")
print("Done.")
