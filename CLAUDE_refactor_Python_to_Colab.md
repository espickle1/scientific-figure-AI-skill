# CLAUDE.md — Python Script → Google Colab

This Python script already works. You are not rewriting it. You are restructuring it
into a Colab notebook so it runs in an ephemeral, browser-hosted cloud environment and
can be understood and re-run top-to-bottom by someone who has never seen the codebase.

Start by reading the script in full. Identify the canonical pipeline stages before
you create a single cell.

## Principles

**1. Emit jupytext percent format.**
Delimit cells with `# %%` markers; markdown cells with `# %% [markdown]` followed by
`#`-prefixed lines. This is the VS Code / Colab-compatible standard. Convert to `.ipynb`
via `jupytext --to ipynb script.py`. Never hand-craft raw JSON.

**2. One meaningful step per cell. Hard cap: ~100 lines.**
A cell does exactly one of: import, configure, load, inspect, transform, model, train,
evaluate, visualize, or export. If you'd say "and then" to describe it, split it.
The last expression in each code cell is its output — design for that.

**3. Follow the canonical section order.**
Each section gets a `# %% [markdown]` H2 header. Use only the sections that apply;
never reorder them.

    1. Title + 1-paragraph purpose
    2. Imports  (all imports, once, grouped: stdlib / third-party / local)
    3. Config   (paths, seeds, hyperparameters — one cell, near the top)
    4. Load data
    5. Inspect / EDA
    6. Clean / transform
    7. Feature engineering
    8. Model definition + training  ← training in its own isolated cell
    9. Evaluation
   10. Conclusion + export          ← mandatory; the most commonly omitted section

**4. Isolate expensive operations.**
Data loads, API calls, model training, and file writes each get their own cell.
This is not style — it prevents accidental re-execution of long-running steps.
Each plot gets its own cell, followed immediately by a markdown cell interpreting it.

**5. Ephemerality is the central constraint.**
Colab runtimes reset silently. Every notebook must survive a cold start. All
installation (`!pip install`) and Google Drive mounting go in a single Setup cell
that runs first, before any import. Never assume a file or package persists from
a previous session.

**6. Config cell replaces argparse.**
CLI arguments (`argparse`, `sys.argv`) do not work in a notebook. Move all tunable
values — paths, model names, hyperparameters, seeds — into the Config cell as plain
assignments. Add a Papermill `# parameters` tag if the notebook will be run
programmatically. Use `#@param` annotations for values a human will adjust interactively.

**7. Data persistence is a deliberate choice — document it.**
Three options exist: Google Drive (persistent across sessions), `/content/` (fast,
ephemeral), `google.colab.files` (manual upload/download). Pick the right one for
each artifact and add a markdown note explaining why. Never silently write to a path
that will vanish.

**8. Secrets stay out of cells.**
Replace any plaintext API keys or passwords with `google.colab.userdata.get('KEY_NAME')`.
If the script uses environment variables, load them via userdata in the Config cell.

**9. The reproducibility contract.**
The finished notebook must pass Restart-Kernel-and-Run-All from top to bottom without
error. No forward references. No variable reused to mean two different things. After
three copy-pasted cells, extract a function instead. Relative paths only.

**10. Every non-trivial code cell is preceded by a markdown cell.**
The markdown cell states *why* this step exists, not just what it does. The Conclusion
cell (section 10) is not optional — it is the most commonly missing element in
research notebooks and the one that makes the difference between a notebook and a log.

## Reference

Colab docs: https://colab.research.google.com/  
Jupytext percent format: https://jupytext.readthedocs.io/en/latest/formats-scripts.html  
Colab + Drive: https://colab.research.google.com/notebooks/io.ipynb
