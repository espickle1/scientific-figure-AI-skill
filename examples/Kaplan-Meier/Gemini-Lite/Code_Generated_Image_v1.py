# Figure v1 | Kaplan-Meier Survival of Treatment by Time | survival_data.csv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# CONFIGURATION
CONFIG = {
    'font_family': ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif'],
    'colors': {'Vac': '#d62728', 'GST': '#1f77b4'}, # Red and Blue
    'figsize': (7, 5),
    'dpi': 300,
    'filename': 'survival_data.csv'
}

def calculate_km(df_group):
    """Calculates Kaplan-Meier estimate manually."""
    df_group = df_group.sort_values('Time')
    times = sorted(df_group['Time'].unique())
    
    km_times = [0]
    km_surv = [1.0]
    
    current_surv = 1.0
    n_at_risk = len(df_group)
    
    for t in times:
        d_t = df_group[(df_group['Time'] == t) & (df_group['Event'] == 1)].shape[0]
        if n_at_risk > 0:
            current_surv *= (1 - d_t / n_at_risk)
        
        # update n_at_risk for the next time point
        n_at_risk -= df_group[df_group['Time'] == t].shape[0]
        
        km_times.append(t)
        km_surv.append(current_surv)
        
    return np.array(km_times), np.array(km_surv)

# Load data
df = pd.read_csv(CONFIG['filename'])

# Set font
for font in CONFIG['font_family']:
    try:
        plt.rcParams['font.family'] = font
        break
    except:
        continue

# Create plot
plt.figure(figsize=CONFIG['figsize'], dpi=CONFIG['dpi'])
sns.set_style("white")

for treat, color in CONFIG['colors'].items():
    subset = df[df['Treatment'] == treat]
    t, s = calculate_km(subset)
    
    # Plot survival step line
    plt.step(t, s, where='post', label=treat, color=color, linewidth=2)
    
    # Mark censored points with '+'
    censored = subset[subset['Event'] == 0]
    for c_time in censored['Time']:
        # Find survival level at censoring time
        idx = np.searchsorted(t, c_time, side='right') - 1
        plt.plot(c_time, s[idx], marker='+', color=color, markersize=8, mew=1.5)

# Formatting
plt.xlim(0, 18)
plt.ylim(0, 1.05)
plt.xlabel('Time (since beginning of experiment)')
plt.ylabel('Survival Probability')
plt.title('Kaplan-Meier Survival Curve')
plt.legend(loc='lower left', frameon=False)

sns.despine(top=True, right=True)
plt.tight_layout()

plt.show()