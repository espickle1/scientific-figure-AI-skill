# Statistics Reference for Scientific Figures

Recipes for common statistical operations and how to annotate results on figures.
All examples assume `import pandas as pd, numpy as np, scipy.stats as stats`.

## Table of Contents
1. [Descriptive Statistics](#descriptive-statistics)
2. [Linear Fit / Regression](#linear-fit)
3. [Student's t-test](#t-test)
4. [ANOVA + Post-Hoc](#anova)
5. [Non-Parametric Alternatives](#non-parametric)
6. [Multiple Comparison Correction](#multiple-comparison-correction)
7. [Annotating Figures](#annotating-figures)

---

## Descriptive Statistics

```python
# Per-group summary
summary = df.groupby("group")["value"].agg(
    mean="mean", std="std", sem="sem",
    median="median", count="count",
    q25=lambda x: x.quantile(0.25),
    q75=lambda x: x.quantile(0.75),
)

# IQR
summary["iqr"] = summary["q75"] - summary["q25"]

# 95% CI of the mean
from scipy.stats import t as t_dist
summary["ci95"] = summary["sem"] * t_dist.ppf(0.975, summary["count"] - 1)
```

Report as: mean ± SD (n = X), or median [IQR]. Nature requires describing
center values and error bars in the figure legend.

---

## Linear Fit

```python
from scipy.stats import linregress

result = linregress(df["x"], df["y"])
# result: slope, intercept, rvalue, pvalue, stderr

# Annotate on plot
ax.plot(x_fit, result.slope * x_fit + result.intercept, "--k", linewidth=0.8)
ax.text(0.05, 0.95, f"R² = {result.rvalue**2:.3f}\np = {result.pvalue:.2e}",
        transform=ax.transAxes, va="top", fontsize=7,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
```

For multiple regression or polynomial fits:
```python
import numpy as np
coeffs = np.polyfit(df["x"], df["y"], deg=2)
poly_fn = np.poly1d(coeffs)

# Or use statsmodels for full regression table
import statsmodels.api as sm
X = sm.add_constant(df[["x1", "x2"]])
model = sm.OLS(df["y"], X).fit()
print(model.summary())
```

---

## T-Test

```python
from scipy.stats import ttest_ind, ttest_rel

# Independent (unpaired) two-sample t-test
t_stat, p_val = ttest_ind(group_a, group_b, equal_var=False)  # Welch's

# Paired t-test
t_stat, p_val = ttest_rel(before, after)

# One-sample t-test against a reference value
from scipy.stats import ttest_1samp
t_stat, p_val = ttest_1samp(sample, popmean=0)
```

**Assumptions to check:**
- Normality: `scipy.stats.shapiro(data)` — if p < 0.05, consider Mann-Whitney instead
- Equal variance: `scipy.stats.levene(a, b)` — if violated, Welch's t-test (default above)

---

## ANOVA

### One-Way ANOVA
```python
from scipy.stats import f_oneway

groups = [df[df["group"] == g]["value"].values for g in df["group"].unique()]
f_stat, p_val = f_oneway(*groups)
```

### Two-Way ANOVA (with interaction)
```python
import statsmodels.api as sm
from statsmodels.formula.api import ols

model = ols("value ~ C(factor1) * C(factor2)", data=df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
```

### Post-Hoc Pairwise Comparisons (always with correction)
```python
# Tukey HSD — standard post-hoc for ANOVA (correction is built-in)
from statsmodels.stats.multicomp import pairwise_tukeyhsd

tukey = pairwise_tukeyhsd(df["value"], df["group"], alpha=0.05)
print(tukey.summary())

# Or Dunn's test (non-parametric post-hoc after Kruskal-Wallis)
# ⚠ Must specify p_adjust — never use without correction
# pip install scikit-posthocs --break-system-packages -q
import scikit_posthocs as sp
dunn = sp.posthoc_dunn(df, val_col="value", group_col="group", p_adjust="bonferroni")
```

---

## Non-Parametric Alternatives

Use when normality assumption is violated or sample size is small.

| Parametric | Non-Parametric | Use case |
|---|---|---|
| Independent t-test | `mannwhitneyu(a, b)` | 2 unpaired groups |
| Paired t-test | `wilcoxon(before, after)` | 2 paired groups |
| One-way ANOVA | `kruskal(*groups)` | ≥3 unpaired groups |
| Repeated-measures ANOVA | `friedmanchisquare(*groups)` | ≥3 paired groups |

All from `scipy.stats`.

---

## Multiple Comparison Correction

**Applied by default** when more than one pairwise comparison is made. Do not display uncorrected
pairwise p-values on a figure unless the user explicitly requests them. Tukey HSD has built-in
correction; for all other pairwise methods, apply one of the following:

```python
from statsmodels.stats.multitest import multipletests

raw_pvals = [0.03, 0.01, 0.08, 0.001]

# Bonferroni (conservative)
reject, corrected, _, _ = multipletests(raw_pvals, method="bonferroni")

# Benjamini-Hochberg FDR (less conservative, common in genomics)
reject, corrected, _, _ = multipletests(raw_pvals, method="fdr_bh")

# Holm-Bonferroni (step-down, generally preferred over plain Bonferroni)
reject, corrected, _, _ = multipletests(raw_pvals, method="holm")
```

---

## Annotating Figures

### Significance Stars Convention

| Symbol | Meaning |
|--------|---------|
| ns | p ≥ 0.05 |
| * | p < 0.05 |
| ** | p < 0.01 |
| *** | p < 0.001 |
| **** | p < 0.0001 |

```python
def p_to_stars(p):
    if p < 0.0001: return "****"
    if p < 0.001:  return "***"
    if p < 0.01:   return "**"
    if p < 0.05:   return "*"
    return "ns"
```

### Manual Bracket Annotation (default — zero dependencies)

```python
def add_stat_bracket(ax, x1, x2, y, p, h=0.02, lw=0.8):
    """Draw a significance bracket between two x positions."""
    stars = p_to_stars(p)
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=lw, c="black")
    ax.text((x1+x2)/2, y+h, stars, ha="center", va="bottom", fontsize=8)
```

### Displaying Stats in Text Box

```python
stat_text = f"ANOVA: F={f_stat:.2f}, p={p_val:.2e}\nPost-hoc: Tukey HSD"
ax.text(0.98, 0.98, stat_text, transform=ax.transAxes,
        va="top", ha="right", fontsize=6,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
```

### Using statannotations (optional convenience library)

```python
# pip install statannotations --break-system-packages -q
from statannotations.Annotator import Annotator

pairs = [("Control", "Drug_A"), ("Control", "Drug_B"), ("Drug_A", "Drug_B")]
annotator = Annotator(ax, pairs, data=df, x="group", y="value")
annotator.configure(test="Mann-Whitney", text_format="star",
                    loc="inside", comparisons_correction="bonferroni")
annotator.apply_and_annotate()
```

---

## Decision Tree: Which Test?

```
How many groups?
├── 1 group vs. reference → one-sample t / Wilcoxon signed-rank
├── 2 groups
│   ├── Paired? → paired t / Wilcoxon signed-rank
│   └── Unpaired? → Welch's t / Mann-Whitney U
└── ≥3 groups
    ├── Paired? → repeated-measures ANOVA / Friedman
    │   └── Significant? → post-hoc with correction (see below)
    └── Unpaired? → one-way ANOVA / Kruskal-Wallis
        └── Significant? → post-hoc with correction (see below)

Post-hoc with correction (single indivisible step):
  Parametric:     Tukey HSD (has built-in correction)
  Non-parametric: Dunn's test with p_adjust="bonferroni" or "holm"
  Manual pairwise: apply multipletests() correction before annotation

  ⚠ Do not display uncorrected pairwise p-values unless the user explicitly requests them.
```
