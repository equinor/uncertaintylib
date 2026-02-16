# Gas Composition Uncertainty Models

This module provides methods for estimating uncertainties in natural gas composition measurements from gas chromatography (GC) analysis.

## Overview

Accurate uncertainty estimation of gas composition is critical for fiscal metering and custody transfer applications. The composition uncertainty propagates through equation-of-state calculations and significantly affects calculated properties such as mass density, speed of sound and molar mass. 


## Available Methods

### 1. ASTM D1945 - Reproducibility Method

```python
component_uncertainty_from_ASTM_D1945(composition_mole_percent)
```

**Based on:** ASTM D1945 (1998), Standard Test Method for Analysis of Natural Gas by Gas Chromatography, chapter 10.1.2 (Reproducibility)

**Principle:** Assigns fixed expanded uncertainty values (k=2) based on concentration ranges:
- < 0.1 mol%: ±0.02 mol%
- 0.1 to 1.0 mol%: ±0.07 mol%
- 1.0 to 5.0 mol%: ±0.10 mol%
- 5.0 to 10.0 mol%: ±0.12 mol%
- \> 10.0 mol%: ±0.15 mol%

**Applicability:** Pipeline quality natural gas (~38 MJ/m³ gross calorific value). 

**Supported components:** N2, CO2, C1-C10

---

### 2. NORSOK I-106 (2014) - Molar Mass Ratio Method

```python
component_uncertainty_from_norsok_I106(composition_mole_percent)
```

**Based on:** NORSOK I-106 (2014), Fiscal metering systems for hydrocarbon liquid and gas

**Principle:** Calculates uncertainty based on the ratio of average gas molar mass to component molar mass:

$$U_{x_i} = \text{factor} \times \frac{M_{\text{avg}}}{M_i}$$

where the factor depends on concentration:
- 0.5 - 20 mol%: factor = 0.15 (the function also uses this value below 0.5 mol%)
- 20 to 50 mol%: factor = 0.30
- 50 - 100 mol%: factor = 0.60

**Applicability:** Designed for North Sea fiscal metering applications. 

**Limitations:**
- The molar mass ratio approach doesn't capture the analytical challenges of heavy components. The uncertainty prediction from this model increases with component mass, while in reality, the opposite will often be the case.
- Tend to underestimate uncertainty for rich gases even more than ASTM D1945 - particularly for C6+ components
- May slightly overestimate uncertainty for lean pipeline gases

**Supported components:** All GERG-2008 components (C1-C10, N2, CO2, H2, O2, CO, H2O, H2S, He, Ar)

---

### 3. Haagenvik 2024 - Empirical Power Law Method

```python
component_uncertainty_from_haagenvik2024(composition_mole_percent, lower_uncertainty_limit=None)
```

**Based on:** Empirical analysis of parallel GC test data from K-lab facility (Haagenvik et al., 2024)

**Principle:** Uses component-specific power law regressions fitted to actual measurement data:

$$u_i = a \times x_i^b$$

where *a* and *b* are empirically determined coefficients for each component. Methane (C1) uncertainty is set to 0% to account for normalization effects.

**Applicability:** 
- **Recommended for rich natural gases** (condensate, wet gas) with significant C6+ content
- Requires methane content > 60 mol%
- Provides more realistic uncertainty estimates for heavy components (C6-C10)

**Advantages:**
- Based on actual parallel test data from multiple GC systems
- Better captures the increased uncertainty of heavy hydrocarbons
- Accounts for the non-linear relationship between concentration and uncertainty
- More realistic for mass-based property calculations (density, speed of sound)

**Limitations:**
- Empirical model derived from specific laboratory conditions
- Limited to natural gas compositions with high methane content
- Not tested for gas compositions that differs from typical lean/rich natural gases found on the Norwegian Continental Shelf

**Supported components:** N2, CO2, C1-C10


## References

1. **ASTM D1945 (1998)** - Standard Test Method for Analysis of Natural Gas by Gas Chromatography, ASTM International
   - Widely used international standard
   - Reproducibility values for pipeline quality gas

2. **NORSOK I-106 (2014)** - Fiscal metering systems for hydrocarbon liquid and gas
   - Norwegian shelf fiscal metering standard
   - Molar mass ratio method

3. **Haagenvik et al. (2024)** - "Exploring the Relationship between Speed of Sound, Density and Isentropic Exponent"
   - Presented at GFMW 2024
   - Empirical power law models from K-lab parallel tests
   - Available at: https://nfogm.no/wp-content/uploads/2025/08/1-Single-Phase-1-Exploring-the-Relationship-between-Speed-of-Sound-Density-and-Isentropic-Exponent-Christian-Hagenvik_Equinor.pdf

4. **NFOGM Gasmet Tool** - Fiscal Gas Metering Station Uncertainty App
   - Reference implementation: https://gasmetapp.web.norce.cloud/

---

## Example Usage

See [Example 09 - Compositional uncertainties](../../examples/09%20-%20Compositional%20uncertainties) for a complete demonstration comparing all three methods for both lean and rich gas compositions.

```python
from uncertaintylib.uncertainty_models import gas_composition

# Define gas composition
composition = {
    'C1': 85.0, 'C2': 6.0, 'C3': 3.0,
    'iC4': 1.0, 'nC4': 1.0, 'iC5': 0.5,
    'nC5': 0.5, 'nC6': 1.0, 'N2': 1.0, 'CO2': 1.0
}

# Compare methods
result_astm = gas_composition.component_uncertainty_from_ASTM_D1945(composition)
result_norsok = gas_composition.component_uncertainty_from_norsok_I106(composition)
result_hagenvik = gas_composition.component_uncertainty_from_haagenvik2024(composition)

# Use in uncertainty propagation
from uncertaintylib import calculate_uncertainty

density_uncertainty = calculate_uncertainty(
    calculate_density_function,
    parameters=result_hagenvik,
    n_samples=10000
)
```

---

## Important Notes

⚠️ **The choice of compositional uncertainty model is not trivial** and can significantly impact fiscal measurements, especially for rich natural gases.

⚠️ **No single method is perfect** - ASTM and NORSOK are standardized but may not reflect real-world performance for all gas types. Haagenvik is empirical but based on actual measurement data.

⚠️ **Always validate** uncertainty estimates against your specific GC system performance through parallel testing or validation samples when possible.
