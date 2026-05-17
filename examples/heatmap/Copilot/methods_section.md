# Methods

## Data Source and Preprocessing
Metabolic output data for *Bacillus cereus* were obtained from a Biolog microplate assay and organized as an 8 × 12 matrix. Rows correspond to plate positions (A–H), and columns correspond to nutrient identifiers (1–12). Data were imported into Python and converted to numeric format, with no missing values detected.

## Data Standardization
Values were standardized using z-score normalization across the entire dataset:

z = (x - μ) / σ

where x is the raw value, μ is the overall mean, and σ is the standard deviation across all cells.

For visualization, the color mapping range was restricted to −0.5 to 0.5 standardized units, and values beyond this range were visually saturated.

## Heatmap Construction
The heatmap was generated using Matplotlib with the `pcolormesh` function to ensure square cell rendering and precise border control.

- Each data point is represented as a square cell
- No numeric values are displayed within cells
- Cell borders are drawn at 0.8 pt thickness
- Aspect ratio is fixed to ensure square cells

## Color Mapping
A custom diverging colormap was used:

- Green (#008000): lowest values
- White (#FFFFFF): midpoint (z = 0)
- Red (#CC0000): highest values

## Figure Layout and Styling
The figure was formatted to approximate Cell Press style guidelines:

- Font: Arial (fallback to system sans-serif)
- Title font size: 9 pt
- Axis labels: 7 pt
- Tick labels: 7 pt
- Background: white

Axis labels:
- X-axis: Nutrient ID
- Y-axis: Nutrient ID

Tick parameters:
- Tick length reduced by 50%
- Tick width: 1 pt

## Color Scale (Legend)
The color scale was placed to the right of the heatmap with:

- Height: one-third of heatmap height
- Aspect ratio: 1:12 (width:height)
- Border width: 1 pt

Legend styling:
- Tick length reduced by 50%
- Tick thickness reduced by 50%
- Font size reduced by 25% (~5 pt)
- Label: Standardized output (z-score)

## Figure Export
The figure was exported as a high-resolution PNG:

- Resolution: 600 DPI
- Tight bounding box
- White background

## Reproducibility
All data processing and figure generation steps were performed in Python using a single script and Jupyter notebook, ensuring full reproducibility.
