# Figure v2 | Kaplan-Meier Survival of Mice by Days | survival_data.csv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# CONFIGURATION
CONFIG = {
    'font_family': ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif'],
    'colors': {'Vac': 'red', 'GST': 'blue'},
    'figsize': (7, 5),
    'dpi': 300,
    'filename': 'survival_data.csv'
}

# 1. Load Data
df = pd.read_csv(CONFIG['filename'])

def calculate_survival_counts(df_group):
    """Calculates step values for counts of surviving individuals."""
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
    """Simplified Log-rank Test calculation using scipy."""
    groups = df['Treatment'].unique()
    g1, g2 = df[df['Treatment'] == groups[0]], df[df['Treatment'] == groups[1]]
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
    # Chi-square calculation
    chi_sq = (o1 - e1)**2 / e1 + ((df['Event'].sum() - o1) - (df['Event'].sum() - e1))**2 / (df['Event'].sum() - e1)
    return stats.chi2.sf(chi_sq, 1)

p_val = get_p_value(df)

# 2. Setup Plot
for font in CONFIG['font_family']:
    try:
        plt.rcParams['font.family'] = font
        break
    except: continue

fig, ax = plt.subplots(figsize=CONFIG['figsize'], dpi=CONFIG['dpi'])
sns.set_style("white")

# 3. Plot Curves
for treat, color in CONFIG['colors'].items():
    t, c = calculate_survival_counts(df[df['Treatment'] == treat])
    # 50% thinner line (1.0 vs default 2.0)
    ax.step(t, c, where='post', label=treat, color=color, linewidth=1.0) 
    
    # Censored ticks
    subset = df[df['Treatment'] == treat]
    censored = subset[subset['Event'] == 0]
    for ct in censored['Time']:
        idx = np.searchsorted(t, ct, side='right') - 1
        ax.plot(ct, c[idx], marker='+', color=color, markersize=5, mew=0.5)

# 4. Formatting & Axes
ax.set_xlim(0, 18)
ax.set_ylim(0, 17)
ax.xaxis.set_major_locator(plt.MultipleLocator(4))
ax.yaxis.set_major_locator(plt.MultipleLocator(5))
ax.set_xlabel("Days post vaccination", fontsize=10)
ax.set_ylabel("Mice surviving", fontsize=10)

# Titles
fig.suptitle("Mice Survival Curve: Iron Uptake System Vaccine", fontsize=12, y=0.98)
ax.set_title("Kaplan-Meier Estimator", fontsize=10, pad=25) # 25% spacing increase

# Legend: Located precisely at Day 1, Survival 1 using data coordinates
leg = ax.legend(loc='lower left', bbox_to_anchor=(1, 1), 
                 bbox_transform=ax.transData, frameon=True, edgecolor='grey', fontsize=9)
leg.get_frame().set_linewidth(0.5)

# Statistics Annotation
ax.text(0.95, 0.95, f"p-value: {p_val:.4f}", transform=ax.transAxes, 
        ha='right', va='top', fontsize=10)

sns.despine()
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()