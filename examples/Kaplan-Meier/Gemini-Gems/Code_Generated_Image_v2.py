# v2.0, Kaplan-Meier Plot, Joseph Mice.csv, Time, Event, Treatment
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

CONFIG = {
    "figsize": (3.5, 2.5),
    "dpi": 300,
    "fontsize": 7,
    "palette": {
        "GST": "#0072B2",  # Blue
        "Vac": "#D55E00"   # Red
    }, 
    "linewidth": 0.625,    # Decreased by 50%
}

# Apply Nature-style formatting
plt.rcParams.update({
    "font.family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "font.size": CONFIG["fontsize"],
    "axes.labelsize": CONFIG["fontsize"],
    "axes.titlesize": 10,
    "xtick.labelsize": CONFIG["fontsize"],
    "ytick.labelsize": CONFIG["fontsize"],
    "legend.fontsize": CONFIG["fontsize"] - 1,
    "lines.linewidth": CONFIG["linewidth"],
})

def kaplan_meier(df_group):
    """Computes survival curve points (time, number of mice surviving)"""
    df_g = df_group.sort_values("Time")
    n = len(df_g)
    times = [0.0]
    alive = [n]
    
    current_alive = n
    for t, g in df_g.groupby("Time"):
        events = g["Event"].sum()
        censored = len(g) - events
        if events > 0:
            current_alive -= events
        times.append(t)
        alive.append(current_alive)
        current_alive -= censored
        
    return times, alive

# 1. Load Data
df = pd.read_csv("Joseph Mice.csv")

# 2. Setup Figure
fig, ax = plt.subplots(figsize=CONFIG["figsize"], dpi=CONFIG["dpi"])

# 3. Plot Data
# Iterate in explicit order to ensure GST is on top of the legend
for treatment, n_label in [("GST", "GST (n=10)"), ("Vac", "Vac (n=16)")]:
    group_df = df[df["Treatment"] == treatment]
    t, s = kaplan_meier(group_df)
    color = CONFIG["palette"].get(treatment, "#000000")
    
    # Draw standard step curve
    ax.step(t, s, where="post", label=n_label, color=color)
    
    # Add vertical tick marks for censored subjects
    censored = group_df[group_df["Event"] == 0]
    if not censored.empty:
        for c_t in censored["Time"].unique():
            # Find corresponding survival height at the time of censoring
            idx = next(i for i, time in reversed(list(enumerate(t))) if time <= c_t)
            c_s = s[idx]
            ax.plot(c_t, c_s, marker='|', color=color, markersize=5, markeredgewidth=CONFIG["linewidth"])

# 4. Axes & Aesthetics
ax.set_title("Mice Survival Curve: Iron Uptake System Vaccine", fontdict={'fontsize': 10, 'fontname': 'Arial'})
ax.set_xlabel("Days post vaccination")
ax.set_ylabel("Mice surviving")
ax.set_xlim(0, 18)
ax.set_ylim(0, 18)

# Tick intervals = 4, specifically excluding 0
ax.set_xticks(np.arange(4, 19, 4))
ax.set_yticks(np.arange(4, 19, 4))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Place legend in the lower left, replacing the old stats box position
ax.legend(frameon=False, loc="lower left")

# 5. Render
plt.tight_layout()
plt.savefig("kaplan_meier_survival_v2.png", bbox_inches="tight")
plt.show()