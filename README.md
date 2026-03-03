# Scientific figure generation with words

Publication-quality scientific figure generation from tabular data (CSV, TSV, XLS/XLSX), packaged as reusable prompts for AI assistants. Two agent variants are included — one for Claude, one for Gemini.

## Repository Structure

```
scientific-figure-AI-skill/
├── examples/                  # Worked examples by figure type
│   ├── Bradfords/
│   ├── heatmap/
│   ├── Kaplan-Meier/
│   ├── bar_graph/
│   ├── Mass_Spec/
│   └── Time-series/
└── src/
    ├── claude/                # Claude version
    └── gemini/                # Gemini version
```

## Quick Start

No coding required. Upload files, describe your figure in plain English, and iterate until it looks right.

### Claude

1. Open a Claude chat
2. Upload `src/claude/SKILL_claude.md` + your data file (CSV/XLSX)
3. Describe the figure you want
4. Revise as needed — Claude edits the script each round

Optional: also upload `statistics_guide_claude.md` if you need statistical tests on the figure.

### Gemini-Gems (recommended for Gemini, requires Advanced)

1. Go to [gemini.google.com](https://gemini.google.com) → **Explore Gems** → **New Gem**
2. Paste contents of `src/gemini/gem_instructions.txt` into the Instructions field
3. Attach `src/gemini/SKILL_gemini.md` and `src/gemini/statistics_guide_gemini.md` as files
4. Save the Gem, open it, upload your data, and describe the figure

### Gemini-Lite (free tier)

1. Open a new Gemini chat
2. Paste the entire contents of `src/gemini/SKILL_gemini_lite.md` as your first message
3. In your second message, upload your data and describe the figure

Budget ~4–6 revision rounds before the context fills up. Batch changes into single messages to save tokens.

---

For full details, see the variant READMEs: [Claude](src/claude/README_claude.md) | [Gemini](src/gemini/README_gemini.md)

## Examples

Each subdirectory under `examples/` represents a different figure type. Every example includes source data, iteratively refined scripts and figures, and full conversation logs.

| Example | Figure type | Workflows | README |
|---------|-------------|-----------|--------|
| [Kaplan-Meier](examples/Kaplan-Meier/) | Survival curve | Claude, Gemini-Gems, Gemini-Lite | [README](examples/Kaplan-Meier/README.md) |
| [Bradfords](examples/Bradfords/) | Standard curve (linear regression) | Claude, Gemini-Gems | [README](examples/Bradfords/README.md) |
| [Time-series](examples/Time-series/) | Growth curve with error bars | Claude, Gemini-Gems | [README](examples/Time-series/README.md) |
| [Mass_Spec](examples/Mass_Spec/) | Hybrid bar chart / dot heatmap | Claude | [README](examples/Mass_Spec/README.md) |
| [bar_graph](examples/bar_graph/) | Grouped bar chart with t-tests | Claude | [README](examples/bar_graph/README.md) |
| [heatmap](examples/heatmap/) | Metabolic output heatmap | Gemini-Gems | [README](examples/heatmap/README.md) |

