# v3.0, Kaplan-Meier Plot, Joseph Mice.csv, Time, Event, Treatment
# ── STATS (computed at runtime) ──────────────────────────
# Method: Log-rank test
# Display: Text label with p-value
# Comparisons: GST vs Vac

import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

CONFIG = {
    "figsize": (4, 3),        # 4:3 aspect ratio
    "dpi": 300,
    "linewidth": 0.625,
    "palette": {
        "GST": "#0000FF",     # Exact Blue
        "Vac": "#FF0000"      # Exact Red
    },
    "font_sizes": {
        "title": 10,
        "axis_title": 8,
        "tick": 5,
        "legend": 6,
        "stat": 6
    }
}

plt.rcParams.update({
    "font.family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "axes.titlesize": CONFIG["font_sizes"]["title"],
    "axes.labelsize": CONFIG["font_sizes"]["axis_title"],
    "xtick.labelsize": CONFIG["font_sizes"]["tick"],
    "ytick.labelsize": CONFIG["font_sizes"]["tick"],
    "legend.fontsize": CONFIG["font_sizes"]["legend"],
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

def logrank_test(df, group_col, time_col, event_col):
    """Manual Log-rank test calculation using scipy.stats chi2"""
    groups = df[group_col].unique()
    if len(groups) != 2: return None, None
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
            
    if V == 0: return 1.0, 0.0
    stat = ((O1 - E1)**2) / V
    p_val = stats.chi2.sf(stat, 1)
    return p_val, stat

# 1. Load Data
df = pd.read_csv("Joseph Mice.csv")

# 2. Setup Figure
fig, ax = plt.subplots(figsize=CONFIG["figsize"], dpi=CONFIG["dpi"])

# 3. Plot Data
for treatment, n_label in [("GST", "GST (n=10)"), ("Vac", "Vac (n=16)")]:
    group_df = df[df["Treatment"] == treatment]
    t, s = kaplan_meier(group_df)
    color = CONFIG["palette"].get(treatment, "#000000")
    
    ax.step(t, s, where="post", label=n_label, color=color)
    
    censored = group_df[group_df["Event"] == 0]
    if not censored.empty:
        for c_t in censored["Time"].unique():
            idx = next(i for i, time in reversed(list(enumerate(t))) if time <= c_t)
            c_s = s[idx]
            ax.plot(c_t, c_s, marker='|', color=color, markersize=5, markeredgewidth=CONFIG["linewidth"])

# 4. Axes & Aesthetics
ax.set_title("Mice Survival Curve: Iron Uptake System Vaccine", fontdict={'fontsize': 10, 'fontname': 'Arial'})
ax.set_xlabel("Days post vaccination", fontsize=CONFIG["font_sizes"]["axis_title"])
ax.set_ylabel("Mice surviving", fontsize=CONFIG["font_sizes"]["axis_title"])
ax.set_xlim(0, 18)
ax.set_ylim(0, 18)

# Ticks configuration
ax.set_xticks(np.arange(4, 19, 4))
ax.set_yticks(np.arange(4, 19, 4))
ax.tick_params(axis='both', which='major', labelsize=CONFIG["font_sizes"]["tick"])

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Legend Configuration
leg = ax.legend(frameon=True, loc="lower left", fontsize=CONFIG["font_sizes"]["legend"], edgecolor='grey')
leg.get_frame().set_linewidth(0.5)

# 5. Statistics
p_val, stat = logrank_test(df, "Treatment", "Time", "Event")
print(f"Stats - Method: Log-rank test")
print(f"Stats - Statistic={stat:.2f}, p={p_val:.4f}")

stat_text = f"Log-rank test\n$p$ = {p_val:.2f}"
ax.text(0.95, 0.95, stat_text, transform=ax.transAxes, va="top", ha="right", 
        fontsize=CONFIG["font_sizes"]["stat"], color="#333333")

# 6. Render
plt.tight_layout()
plt.savefig("kaplan_meier_survival_v3.png", bbox_inches="tight")
plt.show()