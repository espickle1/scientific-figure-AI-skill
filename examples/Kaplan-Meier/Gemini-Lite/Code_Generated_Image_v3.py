# Figure v3 | Kaplan-Meier Survival of Mice (4:3) | survival_data.csv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# 1. Data Setup
data = {
    'Time': [8.5, 10, 13, 13, 13, 13, 14, 18, 18, 18, 13, 15, 18, 18, 18, 18, 5, 6.5, 7, 18, 18, 18, 18, 18, 18, 18],
    'Event': [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    'Treatment': ['GST']*10 + ['Vac']*16
}
df = pd.DataFrame(data)

def calculate_survival_counts(df_group):
    df_group = df_group.sort_values('Time')
    times = [0] + sorted(df_group['Time'].unique().tolist())
    initial_n = len(df_group)
    counts = [initial_n]
    current_n = initial_n
    for t in times[1:]:
        deaths = df_group[(df_group['Time'] == t) & (df_group['Event'] == 1)].shape[0]
        current_n -= deaths
        counts.append(current_n)
    return np.array(times), np.array(counts)

def get_p_value(df):
    g1, g2 = df[df['Treatment'] == 'GST'], df[df['Treatment'] == 'Vac']
    all_times = sorted(df['Time'].unique())
    o1, e1 = 0, 0
    n1, n2 = len(g1), len(g2)
    for t in all_times:
        d1 = g1[(g1['Time'] == t) & (g1['Event'] == 1)].shape[0]
        d2 = g2[(g2['Time'] == t) & (g2['Event'] == 1)].shape[0]
        if (n1 + n2) > 0:
            e1 += (d1 + d2) * (n1 / (n1 + n2))
            o1 += d1
        n1 -= len(g1[g1['Time'] == t])
        n2 -= len(g2[g2['Time'] == t])
    chi_sq = (o1 - e1)**2 / e1 + ((df['Event'].sum() - o1) - (df['Event'].sum() - e1))**2 / (df['Event'].sum() - e1)
    return stats.chi2.sf(chi_sq, 1)

p_val = get_p_value(df)

# 2. Plotting
CONFIG = {
    'colors': {'GST': 'blue', 'Vac': 'red'},
    'figsize': (8, 6), # 4:3 Aspect Ratio
    'dpi': 300
}

plt.rcParams['font.family'] = 'Arial' if 'Arial' in plt.rcParams.get('font.family', []) else 'sans-serif'
fig, ax = plt.subplots(figsize=CONFIG['figsize'], dpi=CONFIG['dpi'])
sns.set_style("white")

handles, labels = [], []
for treat in ['GST', 'Vac']: # Defined order
    color = CONFIG['colors'][treat]
    n = len(df[df['Treatment'] == treat])
    t, c = calculate_survival_counts(df[df['Treatment'] == treat])
    line, = ax.step(t, c, where='post', color=color, linewidth=1.0)
    handles.append(line)
    labels.append(f"{treat} (n={n})")
    
    # Censored markers
    subset = df[df['Treatment'] == treat]
    censored = subset[subset['Event'] == 0]
    for ct in censored['Time']:
        idx = np.searchsorted(t, ct, side='right') - 1
        ax.plot(ct, c[idx], marker='+', color=color, markersize=5, mew=0.5)

# Formatting Ticks (Removing 0)
ax.set_xlim(0, 18)
ax.set_ylim(0, 17)
ax.set_xticks([t for t in range(4, 20, 4)])
ax.set_yticks([t for t in range(5, 20, 5)])

ax.set_xlabel("Days post vaccination", fontsize=10)
ax.set_ylabel("Mice surviving", fontsize=10)

# Title
fig.suptitle("Mice Survival Curve: Iron Uptake System Vaccine", fontsize=12, y=0.96)

# Legend at Day 1, Survival 1
leg = ax.legend(handles, labels, loc='lower left', bbox_to_anchor=(1, 1), 
                 bbox_transform=ax.transData, frameon=True, edgecolor='grey', fontsize=9)
leg.get_frame().set_linewidth(0.5)

# Stats
ax.text(0.95, 0.95, f"p-value: {p_val:.4f}", transform=ax.transAxes, 
        ha='right', va='top', fontsize=10)

sns.despine()
plt.tight_layout(rect=[0, 0.03, 1, 0.94])
plt.show()