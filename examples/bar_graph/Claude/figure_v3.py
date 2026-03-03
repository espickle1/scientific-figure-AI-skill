import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy.stats import ttest_ind

available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial","Helvetica","DejaVu Sans","Liberation Sans"] if f in available), "sans-serif")
plt.rcParams["font.family"] = FONT

CONFIG = {
    "data_path":   "/mnt/user-data/uploads/boltz_hp3.csv",
    "fig_w_in":    (85  / 25.4) * 2 + 0.6,
    "fig_h_in":    127.5 / 25.4,
    "dpi":         300,
    "font_size":   12,      # axis titles: 9 + 3
    "title_size":  8,
    "tick_size":   9,       # tick labels: 7 + 2
    "lw":          0.5,
    "capsize":     3,
    "bar_width":   0.35,
    "colors":      {"hp3": "#E83030", "hp31": "#2457C5"},
    "out_png":     "/mnt/user-data/outputs/figure_v3.png",
    "out_svg":     "/mnt/user-data/outputs/figure_v3.svg",
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

def make_bar(ax, metric, ylabel, title, ystart=None, ytick_interval=0.2):
    df = raw[raw["Type"] == metric].copy()

    bw = CONFIG["bar_width"]
    # X positions: 4 bars total, grouped by strain
    # hp3-KDO=0, hp3-OAnt=1, hp31-KDO=2, hp31-OAnt=3
    xpos = {
        ("hp3",  "KDO"):   0,
        ("hp3",  "O-Ant"): 1,
        ("hp31", "KDO"):   2,
        ("hp31", "O-Ant"): 3,
    }

    bars_info = {}
    for (strain_key, receptor), xc in xpos.items():
        color = CONFIG["colors"][strain_key]
        shade_alpha = 1.0 if receptor == "KDO" else 0.45
        vals = df[(df["strain"]==strain_key) & (df["receptor"]==receptor)]["Value"].values
        m = vals.mean()
        s = vals.std(ddof=1) / np.sqrt(len(vals))
        bars_info[(strain_key, receptor)] = (xc, m, s, vals)

        ax.bar(xc, m, width=bw, color=color, alpha=shade_alpha,
               linewidth=CONFIG["lw"], edgecolor="black")
        ax.errorbar(xc, m, yerr=s, fmt="none", elinewidth=CONFIG["lw"],
                    capthick=CONFIG["lw"], capsize=CONFIG["capsize"], color="black")

    # T-tests: KDO vs O-Ant within each strain
    _, p_hp3  = ttest_ind(bars_info[("hp3",  "KDO")][3],
                          bars_info[("hp3",  "O-Ant")][3], equal_var=False)
    _, p_hp31 = ttest_ind(bars_info[("hp31", "KDO")][3],
                          bars_info[("hp31", "O-Ant")][3], equal_var=False)

    # Bracket placement
    all_vals = df["Value"].values
    data_range = abs(all_vals).max()
    pad = data_range * 0.13
    bar_tops = [bars_info[k][1] + bars_info[k][2] for k in bars_info]
    bracket_base = max(bar_tops) + pad * 0.4

    add_stat_bracket(ax, xpos[("hp3","KDO")], xpos[("hp3","O-Ant")],
                     bracket_base, p_hp3,  h=pad * 0.35)
    add_stat_bracket(ax, xpos[("hp31","KDO")], xpos[("hp31","O-Ant")],
                     bracket_base, p_hp31, h=pad * 0.35)

    top_ylim = bracket_base + pad * 0.95

    # X-axis tick labels: descriptive, one per bar
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(
        ["hp3\nKDO", "hp3\nO-Ant", "hp3.1\nKDO", "hp3.1\nO-Ant"],
        fontsize=CONFIG["tick_size"]
    )
    ax.set_xlabel("Strain and Receptor", fontsize=CONFIG["font_size"], labelpad=6)
    ax.set_ylabel(ylabel, fontsize=CONFIG["font_size"], labelpad=4)
    ax.set_title(title, fontsize=CONFIG["title_size"], fontweight="bold", pad=6)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_linewidth(CONFIG["lw"])

    # Y limits
    if ystart is not None:
        ax.set_ylim(bottom=ystart, top=top_ylim)
    else:
        ax.set_ylim(top=top_ylim)

    # Y-axis tick interval
    ybot = ax.get_ylim()[0]
    ytop = ax.get_ylim()[1]
    start = np.ceil(ybot / ytick_interval) * ytick_interval
    yticks = np.arange(start, ytop, ytick_interval)
    # Remove y=0 tick
    yticks = yticks[~np.isclose(yticks, 0)]
    ax.set_yticks(np.round(yticks, 10))
    ax.tick_params(axis="both", which="both", labelsize=CONFIG["tick_size"],
                   width=CONFIG["lw"], length=3)

fig, (ax1, ax2) = plt.subplots(1, 2,
    figsize=(CONFIG["fig_w_in"], CONFIG["fig_h_in"]),
    dpi=CONFIG["dpi"])

make_bar(ax1, "pred_prob",  "Probability of Binding", "Probability of Binding",
         ystart=None, ytick_interval=0.2)
make_bar(ax2, "pred_value", "Prediction Confidence",  "Prediction Confidence",
         ystart=0,    ytick_interval=0.5)

fig.tight_layout(pad=1.2, w_pad=2.0)

fig.savefig(CONFIG["out_png"], dpi=CONFIG["dpi"], bbox_inches="tight")
fig.savefig(CONFIG["out_svg"], bbox_inches="tight")
print("Done.")
