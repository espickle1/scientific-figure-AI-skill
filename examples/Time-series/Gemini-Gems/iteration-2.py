# v2 | Time series | plate_growth_curve.csv | Time, A1, B1, C1, D1 repeats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
        "title": 9,      # decreased by 1
        "axis": 7,       # decreased by 1
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

# 3. Calculate Means (Stats Stripped)
series_names = ["A1", "B1", "C1", "D1"]
results = []

for series in series_names:
    cols = [c for c in df_filtered.columns if c.split('.')[0] == series]
    for idx, row in df_filtered.iterrows():
        t = row['Time_hours']
        vals = row[cols].astype(float).values
        results.append({
            'Time': t,
            'Series': series,
            'Mean': np.mean(vals)
        })

df_mean = pd.DataFrame(results)

# 4. Plot
fig, ax = plt.subplots(figsize=CONFIG["figsize"], dpi=300)

for series in series_names:
    data = df_mean[df_mean['Series'] == series].sort_values('Time')
    if data.empty: continue
    
    # Decreased marker size by 50% (3 -> 1.5) and line width by 50% (1 -> 0.5)
    ax.plot(data['Time'], data['Mean'], label=series, 
            color=CONFIG["colors"][series], marker='o', 
            markersize=1.5, lw=0.5)

# Formatting
ax.set_title("Metabolic Output Over Time", fontsize=CONFIG["fonts"]["title"])
ax.set_xlabel("Time (hours)", fontsize=CONFIG["fonts"]["axis"])
ax.set_ylabel("OD$_{600}$", fontsize=CONFIG["fonts"]["axis"]) # Subscript 600

ax.tick_params(axis='both', which='major', labelsize=CONFIG["fonts"]["ticks"])
ax.set_xticks(target_times)

# Legend Formatting
leg = ax.legend(frameon=True, fontsize=CONFIG["fonts"]["legend"], loc='upper left')
leg.get_frame().set_edgecolor('grey')
leg.get_frame().set_linewidth(0.5)

# Simplify legends - only show line instead of plot point and line
for line in leg.get_lines():
    line.set_marker("None")

# Despine
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.show()