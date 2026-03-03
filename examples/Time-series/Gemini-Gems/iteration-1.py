# v1 | Time series | plate_growth_curve.csv | Time, A1, B1, C1, D1 repeats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# ── CONFIG ────────────────────────────────────────────────
CONFIG = {
    "figsize": (89 / 25.4, 65 / 25.4), # Nature single column: 89mm width
    "colors": {
        "A1": "blue",
        "B1": "green",
        "C1": "violet",
        "D1": "red"
    },
    "fonts": {
        "title": 10,
        "axis": 8,
        "ticks": 8,
        "legend": 7
    },
    "font_family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"]
}

# ── SETUP ─────────────────────────────────────────────────
plt.rcParams['font.family'] = CONFIG['font_family']

# 1. Load Data
df = pd.read_csv("plate_growth_curve.csv")

# 2. Process Time Column (Convert H:MM:SS to hours)
time_parts = df['Time'].str.split(':', expand=True).astype(float)
df['Time_hours'] = time_parts[0] + time_parts[1]/60.0 + time_parts[2]/3600.0

# Filter to keep only 4-hour multiples
target_times = [0, 4, 8, 12, 16, 20, 24]
mask = df['Time_hours'].apply(lambda x: any(np.isclose(x, t, atol=0.01) for t in target_times))
df_filtered = df[mask].copy()

# 3. Calculate Stats
series_names = ["A1", "B1", "C1", "D1"]
results = []

for series in series_names:
    # Find all replicates for this series (e.g., A1, A1.1, A1.2)
    cols = [c for c in df_filtered.columns if c.split('.')[0] == series]
    
    # Calculate mean and 95% CI (t-distribution) for each timepoint
    for idx, row in df_filtered.iterrows():
        t = row['Time_hours']
        vals = row[cols].astype(float).values
        n = len(vals)
        mean_val = np.mean(vals)
        
        # ── STATS (computed at runtime) ──────────────────────────
        # Method: 95% Confidence Interval using Student's t-distribution
        # Display: Error bars
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
    
    ax.errorbar(data['Time'], data['Mean'], yerr=data['CI95'], 
                label=series, color=CONFIG["colors"][series], 
                marker='o', markersize=3, capsize=2, lw=1)

# Formatting
ax.set_title("Metabolic Output Over Time", fontsize=CONFIG["fonts"]["title"])
ax.set_xlabel("Time (hours)", fontsize=CONFIG["fonts"]["axis"])
ax.set_ylabel("Metabolic Output", fontsize=CONFIG["fonts"]["axis"])

ax.tick_params(axis='both', which='major', labelsize=CONFIG["fonts"]["ticks"])
ax.set_xticks(target_times)

# Legend
ax.legend(frameon=False, fontsize=CONFIG["fonts"]["legend"], loc='upper left')

# Despine
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.show()