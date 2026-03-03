# Statistics Reference — Gemini

scipy-only recipes. All examples use `import scipy.stats as stats, numpy as np, pandas as pd`.

**Do not import** statsmodels, scikit_posthocs, or statannotations. They are not available.

## When to Use This Guide

Only when the user explicitly requests statistics. The figure workflow does not include stats by default. When triggered, follow this sequence: check normality → select test → compute → correct if multiple comparisons → print results → annotate figure.

Always print results to stdout before annotating so the user can verify.

## Descriptive Statistics

```python
summary = df.groupby("group")["value"].agg(
    mean="mean", std="std", sem="sem",
    median="median", count="count",
    q25=lambda x: x.quantile(0.25),
    q75=lambda x: x.quantile(0.75),
)
summary["iqr"] = summary["q75"] - summary["q25"]
summary["ci95"] = summary["sem"] * stats.t.ppf(0.975, summary["count"] - 1)
```

Report as: mean ± SD (n = X), or median [IQR].

## Test Selection (exact function calls)

### Normality check (always run first)
```python
for name, group in df.groupby("group")["value"]:
    w, p = stats.shapiro(group)
    print(f"  {name}: Shapiro W={w:.3f}, p={p:.4f} {'(normal)' if p >= 0.05 else '(non-normal)'}")
    if len(group) < 5:
        print(f"  WARNING: {name} has n={len(group)}, results may be unreliable")
```
If any group p < 0.05, use non-parametric test.

### 2 groups, unpaired
```python
# Normal
t_stat, p_val = stats.ttest_ind(a, b, equal_var=False)  # Welch's
# Non-normal
u_stat, p_val = stats.mannwhitneyu(a, b, alternative='two-sided')
```

### 2 groups, paired
```python
# Normal
t_stat, p_val = stats.ttest_rel(before, after)
# Non-normal
w_stat, p_val = stats.wilcoxon(before, after)
```

### 1 group vs reference
```python
t_stat, p_val = stats.ttest_1samp(sample, popmean=0)
```

### ≥3 groups, unpaired
```python
# Normal
f_stat, p_val = stats.f_oneway(*groups)
# Non-normal
h_stat, p_val = stats.kruskal(*groups)
```

### Post-hoc (after significant ANOVA/Kruskal-Wallis)
```python
# Try scipy's tukey_hsd first (scipy ≥1.8)
try:
    result = stats.tukey_hsd(*groups)
    for i in range(len(group_names)):
        for j in range(i+1, len(group_names)):
            p = result.pvalue[i][j]
            print(f"  {group_names[i]} vs {group_names[j]}: p={p:.4f} ({p_to_stars(p)})")
except AttributeError:
    # Fallback: pairwise Mann-Whitney with Bonferroni
    print("  tukey_hsd not available, using pairwise Mann-Whitney + Bonferroni")
    raw_pvals = []
    pairs = []
    for i in range(len(group_names)):
        for j in range(i+1, len(group_names)):
            _, p = stats.mannwhitneyu(groups[i], groups[j], alternative='two-sided')
            raw_pvals.append(p)
            pairs.append((group_names[i], group_names[j]))
    corrected = bonferroni_holm(raw_pvals, method="holm")
    for (g1, g2), p_raw, p_adj in zip(pairs, raw_pvals, corrected):
        print(f"  {g1} vs {g2}: p_raw={p_raw:.4f}, p_adj={p_adj:.4f} ({p_to_stars(p_adj)})")
```

### ≥3 groups, paired
```python
# Normal: repeated-measures (limited without statsmodels — report F from friedman as approximation)
# Non-normal
x_stat, p_val = stats.friedmanchisquare(*groups)
```

Note: two-way ANOVA is not available without statsmodels. If the user requests it, explain the limitation and suggest running the script in Colab with statsmodels installed.

## Linear Regression

```python
result = stats.linregress(df["x"], df["y"])
print(f"Slope={result.slope:.4f}, Intercept={result.intercept:.4f}")
print(f"R²={result.rvalue**2:.4f}, p={result.pvalue:.2e}")

# Annotate on plot
x_fit = np.linspace(df["x"].min(), df["x"].max(), 100)
ax.plot(x_fit, result.slope * x_fit + result.intercept, "--k", lw=0.8)
ax.text(0.05, 0.95, f"R² = {result.rvalue**2:.3f}\np = {result.pvalue:.2e}",
        transform=ax.transAxes, va="top", fontsize=7,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
```

Polynomial: `np.polyfit(x, y, deg=N)` + `np.poly1d(coeffs)`.

Correlation: `stats.pearsonr(x, y)` (normal) or `stats.spearmanr(x, y)` (non-normal).

## Multiple Comparison Correction (inline, no statsmodels)

```python
def bonferroni_holm(pvals, method="holm"):
    """Correct p-values for multiple comparisons. Methods: 'bonferroni', 'holm'."""
    import numpy as np
    pvals = np.array(pvals)
    n = len(pvals)
    if method == "bonferroni":
        return np.minimum(pvals * n, 1.0)
    # Holm step-down
    order = np.argsort(pvals)
    corrected = np.empty(n)
    for rank, idx in enumerate(order):
        corrected[idx] = pvals[idx] * (n - rank)
    # Enforce monotonicity
    cummax = corrected[order].copy()
    for i in range(1, n):
        cummax[i] = max(cummax[i], cummax[i-1])
    corrected[order] = cummax
    return np.minimum(corrected, 1.0)
```

Always apply correction when making more than one pairwise comparison. Never display uncorrected pairwise p-values when multiple comparisons are made.

## Annotating Figures

### Significance stars
```python
def p_to_stars(p):
    if p < 0.0001: return "****"
    if p < 0.001:  return "***"
    if p < 0.01:   return "**"
    if p < 0.05:   return "*"
    return "ns"
```

### Manual bracket
```python
def add_stat_bracket(ax, x1, x2, y, p, h=0.02, lw=0.8):
    """Draw a significance bracket between two x positions."""
    stars = p_to_stars(p)
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=lw, c="black")
    ax.text((x1+x2)/2, y+h, stars, ha="center", va="bottom", fontsize=8)
```

### Stats text box
```python
stat_text = f"Test: {test_name}\nH={stat:.2f}, p={p_val:.2e}"
ax.text(0.98, 0.98, stat_text, transform=ax.transAxes,
        va="top", ha="right", fontsize=6,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
```

## Script Metadata for Stats

When stats are computed, add a comment block to the script recording method and display intent only — never numerical results:

```python
# ── STATS (computed at runtime) ──────────────────────────
# Method: Kruskal-Wallis → pairwise Mann-Whitney, Holm correction
# Display: brackets with stars
# Comparisons: Control vs Drug_A, Control vs Drug_B
```

## Decision Tree

```
How many groups?
├── 1 vs reference → ttest_1samp / wilcoxon
├── 2 groups
│   ├── Paired → ttest_rel / wilcoxon
│   └── Unpaired → ttest_ind (Welch's) / mannwhitneyu
└── ≥3 groups
    ├── Paired → friedmanchisquare
    └── Unpaired → f_oneway / kruskal
        └── Significant → tukey_hsd / pairwise mannwhitneyu + holm
```

Always: check normality first → pick parametric or non-parametric → correct for multiple comparisons → print results → then annotate.
