# v1.0, Kaplan-Meier Plot, Joseph Mice.csv, Time, Event, Treatment
# ── STATS (computed at runtime) ──────────────────────────
# Method: Log-rank test
# Display: Text label with p-value
# Comparisons: GST vs Vac

import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

CONFIG = {
    "figsize": (3.5, 2.5),       # Nature single-column width
    "dpi": 300,
    "fontsize": 7,
    "palette": {                 # Wong colorblind-safe palette
        "GST": "#E69F00",        # Orange
        "Vac": "#0072B2"         # Blue
    }, 
    "linewidth": 1.25,
}

# Apply Nature-style formatting
plt.rcParams.update({
    "font.family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "font.size": CONFIG["fontsize"],
    "axes.labelsize": CONFIG["fontsize"],
    "axes.titlesize": CONFIG["fontsize"] + 1,
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
        current_alive -= censored  # Censored mice drop from risk pool, but not from visual line
        
    return times, alive

def logrank_test(df, group_col, time_col, event_col):
    """Manual Log-rank test calculation using scipy.stats chi2"""
    groups = df[group_col].unique()
    if len(groups) != 2: 
        return None, None
    
    df_sorted = df.sort_values(time_col)
    times = df_sorted[df_sorted[event_col] == 1][time_col].unique()
    
    O1, E1, O2, E2, V = 0, 0, 0, 0, 0
    for t in times:
        at_risk1 = len(df[(df[group_col] == groups[0]) & (df[time_col] >= t)])
        at_risk2 = len(df[(df[group_col] == groups[1]) & (df[time_col] >= t)])
        events1 = len(df[(df[group_col] == groups[0]) & (df[time_col] == t) & (df[event_col] == 1)])
        events2 = len(df[(df[group_col] == groups[1]) & (df[time_col] == t) & (df[event_col] == 1)])
        
        n_at_risk = at_risk1 + at_risk2
        n_events = events1 + events2
        
        if n_at_risk > 1:
            O1 += events1
            E1 += n_events * (at_risk1 / n_at_risk)
            O2 += events2
            E2 += n_events * (at_risk2 / n_at_risk)
            V += (n_events * at_risk1 * at_risk2 * (n_at_risk - n_events)) / (n_at_risk**2 * (n_at_risk - 1))
            
    if V == 0: 
        return 1.0, 0.0
    
    stat = ((O1 - E1)**2) / V
    p_val = stats.chi2.sf(stat, 1)
    return p_val, stat

# 1. Load Data
df = pd.read_csv("Joseph Mice.csv")

# 2. Setup Figure
fig, ax = plt.subplots(figsize=CONFIG["figsize"], dpi=CONFIG["dpi"])

# 3. Plot Data
for treatment in ["Vac", "GST"]:  # Plot Vac first to define z-order cleanly
    group_df = df[df["Treatment"] == treatment]
    t, s = kaplan_meier(group_df)
    color = CONFIG["palette"].get(treatment, "#000000")
    
    # Draw standard step curve
    ax.step(t, s, where="post", label=treatment, color=color)
    
    # Add vertical tick marks for censored subjects
    censored = group_df[group_df["Event"] == 0]
    if not censored.empty:
        for c_t in censored["Time"].unique():
            # Find the corresponding survival height at the time of censoring
            idx = next(i for i, time in reversed(list(enumerate(t))) if time <= c_t)
            c_s = s[idx]
            ax.plot(c_t, c_s, marker='|', color=color, markersize=5, markeredgewidth=1)

# 4. Axes & Aesthetics
ax.set_xlabel("Time (days)")
ax.set_ylabel("Number of mice remaining")
ax.set_xlim(0, 18)
ax.set_ylim(0, 18)  # Matches absolute maximum to provide breathing room
ax.set_yticks(np.arange(0, 19, 2))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(frameon=False, loc="upper right")

# 5. Statistics
p_val, stat = logrank_test(df, "Treatment", "Time", "Event")
print(f"Stats - Method: Log-rank test")
print(f"Stats - Statistic={stat:.2f}, p={p_val:.4f}")

stat_text = f"Log-rank test\n$p$ = {p_val:.2f}"
ax.text(0.05, 0.05, stat_text, transform=ax.transAxes, va="bottom", ha="left", color="#333333")

# 6. Render
plt.tight_layout()
plt.savefig("kaplan_meier_survival.png", bbox_inches="tight")
plt.show()