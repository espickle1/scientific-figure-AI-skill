# v3 | Time series | plate_growth_curve.csv | Time, A1, B1, C1, D1 repeats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from matplotlib.lines import Line2D

# ── CONFIG ────────────────────────────────────────────────
CONFIG = {
    "figsize": (89 / 25.4, 65 / 25.4),
    "colors": {
        "A1": "blue",
        "B1": "green",
        "C1": "violet",
        "D1": "red"
    },
    "fonts": {
        "title": 9,
        "axis": 7,
        "ticks": 8,
        "legend": 7
    },
    "font_family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"]
}

plt.rcParams['font.family'] = CONFIG['font_family']

# 1. Load Data
df = pd.read_csv("plate_growth_curve.csv")

# 2. Process Time Column
time_parts = df['Time'].str.split(':', expand=True).astype(float)
df['Time_hours'] = time_parts[0] + time_parts[1]/60.0 + time_parts[2]/3600.0

target_times = [0, 4, 8, 12, 16, 20, 24]
mask = df['Time_hours'].apply(lambda x: any(np.isclose(x, t, atol=0.01) for t in target_times))
df_filtered = df[mask].copy()

# 3. Calculate Stats
series_names = ["A1", "B1", "C1", "D1"]
results = []

# ── STATS (computed at runtime) ──────────────────────────
# Method: 95% Confidence Interval using Student's t-distribution
# Display: Error bars
for series in series_names:
    cols = [c for c in df_filtered.columns if c.split('.')[0] == series]
    for idx, row in df_filtered.iterrows():
        t = row['Time_hours']
        vals = row[cols].astype(float).values
        n = len(vals)
        mean_val = np.mean(vals)
        
        std_val = np.std(vals, ddof=1) if n > 1 else 0
        sem = std_val / np.sqrt(n) if n > 0 else 0
        ci95 = sem * stats.t.ppf(0.975, n - 1) if n > 1 else 0
        
        results.append({
            'Time': t,
            'Series': series,
            'Mean': mean_val,
            'CI95': ci95
        })

df_stats = pd.DataFrame(results)

# 4. Plot
fig, ax = plt.subplots(figsize=CONFIG["figsize"], dpi=300)

for series in series_names:
    data = df_stats[df_stats['Series'] == series].sort_values('Time')
    if data.empty: continue
    
    # Plotting mean ± 95% CI error bars with thin lines and small markers
    ax.errorbar(data['Time'], data['Mean'], yerr=data['CI95'], 
                color=CONFIG["colors"][series], marker='o', 
                markersize=1.5, lw=0.5, capsize=1.5, capthick=0.5)

# Formatting
ax.set_title("Metabolic Output Over Time", fontsize=CONFIG["fonts"]["title"])
ax.set_xlabel("Time (hours)", fontsize=CONFIG["fonts"]["axis"])
ax.set_ylabel("OD$_{600}$", fontsize=CONFIG["fonts"]["axis"])

ax.tick_params(axis='both', which='major', labelsize=CONFIG["fonts"]["ticks"])
ax.set_xticks(target_times)

# Set x=0 to intersect exactly with the y-axis
ax.set_xlim(left=0, right=max(target_times) + 1)

# Custom legend to exclusively display lines (no marker dots or error bar caps)
custom_handles = [Line2D([0], [0], color=CONFIG["colors"][s], lw=0.5) for s in series_names]
leg = ax.legend(custom_handles, series_names, frameon=True, 
                fontsize=CONFIG["fonts"]["legend"], loc='upper left')
leg.get_frame().set_edgecolor('grey')
leg.get_frame().set_linewidth(0.5)

# Despine
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.show()