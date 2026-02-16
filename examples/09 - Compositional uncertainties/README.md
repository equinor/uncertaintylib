# Example 09: Compositional Uncertainties and Impact on Gas Density

This example demonstrates how to estimate uncertainties in gas composition using different methods from standards and scientific literature, and how these compositional uncertainties propagate to calculated gas density using the GERG-2008 equation of state.

## Overview

The example compares three methods for estimating gas composition uncertainty:
1. **ASTM D1945 (1998)** - Standard reproducibility values
2. **NORSOK I-106 (2014)** - Molar mass-based uncertainty estimation
3. **Haagenvik et al. (2024)** - Empirical power law method from K-lab parallel tests

### Why Method Choice Matters

Different methods give significantly different results, especially for **rich natural gases**:

- **ASTM D1945 (1998)**: Based on pipeline quality gas (~38 MJ/m³). Tends to **underestimate** uncertainty for heavy components (C6+) in rich gases.
- **NORSOK I-106 (2014)**: Uses molar mass ratios. **Underestimates uncertainty even more than ASTM** for rich gases, particularly for C6+ components.
- **Haagenvik 2024**: Based on actual parallel test data. Provides **more realistic estimates** for rich gases with significant heavy hydrocarbon content.

For **lean pipeline gases**, ASTM and NORSOK may slightly overestimate uncertainty. For **rich gases** (condensate, wet gas), they significantly underestimate uncertainty in density and other mass-based properties.

**This example demonstrates these differences** by comparing calculated density uncertainties for both lean and rich gas cases.

## Cases

Two gas compositions are analyzed:

### Rich Gas
- High C2+ content
- Conditions: 100 bara, 85°C

### Lean Gas
- High methane content
- Conditions: 100 bara, 20°C

## Key Features

- Uses `uncertaintylib.uncertainty_models.gas_composition` for uncertainty estimation
- Integrates with GERG-2008 equation of state via `pvtlib`
- Isolates compositional effects by setting pressure and temperature uncertainties to zero
- Compares uncertainty propagation between different estimation methods

## Requirements

```
uncertaintylib
pvtlib
pandas
numpy
```

## Usage

```bash
python example_09.py
```

## Results

The script outputs:
- Estimated compositional uncertainties from each method
- Calculated density values
- Uncertainty in density (absolute and relative)
- Comparison between methods
