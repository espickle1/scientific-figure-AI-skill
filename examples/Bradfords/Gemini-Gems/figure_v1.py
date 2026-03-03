# Figure v1 | X-Y scatter of OD600 by mg/mL | black/orange
# Data: Bradford Curves.csv
# Columns used: ['mg/mL', 'OD600']

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import scipy.stats as stats

# Font detection (Arial/Helvetica fallback for Nature-style)
available = {f.name for f in fm.fontManager.ttflist}
FONT = next((f for f in ["Arial","Helvetica","DejaVu Sans","Liberation Sans"] if f in available), "sans-serif")

CONFIG = {
    "figsize": (3.5, 2.625), # Nature single col: 89 mm wide
    "dpi": 300,
    "palette": ["#000000", "#D55E00"], # Black for standards, orange-red for unknown
    "font_size": 7
}

plt.rcParams.update({
    "font.family": FONT,
    "font.size": CONFIG["font_size"],
    "axes.labelsize": CONFIG["font_size"],
    "xtick.labelsize": CONFIG["font_size"],
    "ytick.labelsize": CONFIG["font_size"],
    "legend.fontsize": CONFIG["font_size"],
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Load data
df = pd.read_csv("Bradford Curves.csv")

# Extract standards (first 5 rows are 0 to 1 mg/mL BSA)
standards = df.iloc[:5].copy()
standards['mg/mL'] = standards['mg/mL'].astype(float)
standards['OD600'] = standards['OD600'].astype(float)

# Extract unknown sample (apoHb)
unknown_row = df[df['mg/mL'] == 'apoHb']
y_unknown = unknown_row['OD600'].values[0]

# Linear Regression
slope, intercept, r_value, p_value, std_err = stats.linregress(standards['mg/mL'], standards['OD600'])

# Interpolate unknown (x = (y - intercept) / slope)
x_interp = (y_unknown - intercept) / slope

# Plot setup
fig, ax = plt.subplots(figsize=CONFIG["figsize"], dpi=CONFIG["dpi"])

# Scatter standards
ax.scatter(standards['mg/mL'], standards['OD600'], color=CONFIG["palette"][0], 
           alpha=0.8, s=20, label='BSA Standards', zorder=3)

# Regression line
x_fit = np.linspace(0, standards['mg/mL'].max() * 1.1, 100)
y_fit = slope * x_fit + intercept
ax.plot(x_fit, y_fit, "--k", lw=1.0, label='Linear Fit', zorder=2)

# Interpolated unknown point
ax.scatter([x_interp], [y_unknown], color=CONFIG["palette"][1], s=30, zorder=4, label='apoHb')

# Dashed lines for interpolation marking
ax.plot([x_interp, x_interp], [0, y_unknown], color=CONFIG["palette"][1], linestyle=":", lw=1.0, zorder=1)
ax.plot([0, x_interp], [y_unknown, y_unknown], color=CONFIG["palette"][1], linestyle=":", lw=1.0, zorder=1)

# Text box for equation, R² and interpolated value
text_str = f"y = {slope:.3f}x + {intercept:.3f}\n$R^2$ = {r_value**2:.4f}\napoHb = {x_interp:.2f} mg/mL"
ax.text(0.05, 0.95, text_str, transform=ax.transAxes, va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.8))

# Axis formatting
ax.set_xlabel("Concentration (mg/mL)")
ax.set_ylabel("OD600")
ax.set_xlim(left=0, right=1.1)
ax.set_ylim(bottom=0.15)
ax.legend(loc="lower right", frameon=False)

fig.tight_layout()
plt.show()