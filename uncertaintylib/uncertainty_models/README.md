# Gas Composition Uncertainty Models

This module provides methods for estimating uncertainties in natural gas composition measurements from gas chromatography (GC) analysis.

## Overview

Accurate uncertainty estimation of gas composition is critical for fiscal metering and custody transfer applications. The composition uncertainty propagates through equation-of-state calculations and significantly affects calculated properties such as:

- **Molar mass** - direct linear relationship with composition
- **Mass density** - strong dependency on heavy hydrocarbon content
- **Speed of sound** - sensitive to both light (N2, CO2) and heavy components
- **Energy content** - affected by all components

## Available Methods

### 1. ASTM D1945 - Reproducibility Method

```python
component_uncertainty_from_ASTM_D1945(composition_mole_percent)
```

**Based on:** ASTM D1945 standard for natural gas analysis, chapter 10.1.2 (Reproducibility)

**Principle:** Assigns fixed expanded uncertainty values (k=2) based on concentration ranges:
- < 0.1 mol%: ±0.02 mol%
- 0.1 to 1.0 mol%: ±0.07 mol%
- 1.0 to 5.0 mol%: ±0.10 mol%
- 5.0 to 10.0 mol%: ±0.12 mol%
- > 10.0 mol%: ±0.15 mol%

**Applicability:** Pipeline quality natural gas (~38 MJ/m³ gross calorific value). The reproducibility values are derived from round-robin testing of typical pipeline quality gases with limited heavy hydrocarbon content.

**Limitations:**
- **Tends to underestimate uncertainty for rich natural gases** with significant C5+ content
- Does not account for the higher uncertainty of heavy components (C5-C10)
- May overestimate uncertainty for very lean gases

**Supported components:** N2, CO2, C1-C10 (linear and branched)

---

### 2. NORSOK I-106 - Molar Mass Ratio Method

```python
component_uncertainty_from_norsok_I106(composition_mole_percent)
```

**Based on:** NORSOK I-106:2014 standard for fiscal measurement systems

**Principle:** Calculates uncertainty based on the ratio of average gas molar mass to component molar mass:

$$U_{x_i} = \text{factor} \times \frac{M_{\text{avg}}}{M_i}$$

where the factor depends on concentration:
- < 20 mol%: factor = 0.15
- 20 to 50 mol%: factor = 0.30
- > 50 mol%: factor = 0.60

**Applicability:** Designed for North Sea fiscal metering applications. Works reasonably well for typical natural gas compositions.

**Limitations:**
- **Still tends to underestimate uncertainty for rich gases** with high C5+ content
- The molar mass ratio approach doesn't fully capture the analytical challenges of heavy components
- May overestimate uncertainty for lean pipeline gases

**Supported components:** All GERG-2008 components (C1-C10, N2, CO2, H2, O2, CO, H2O, H2S, He, Ar)

---

### 3. Hagenvik 2024 - Empirical Power Law Method

```python
component_uncertainty_from_haagenvik2024(composition_mole_percent, lower_uncertainty_limit=None)
```

**Based on:** Empirical analysis of parallel GC test data from K-lab facility (Hagenvik et al., 2024)

**Principle:** Uses component-specific power law regressions fitted to actual measurement data:

$$u_i = a \times x_i^b$$

where *a* and *b* are empirically determined coefficients for each component. Methane (C1) uncertainty is set to 0% to account for normalization effects.

**Applicability:** 
- **Recommended for rich natural gases** (condensate, wet gas) with significant C5+ content
- Requires methane content > 60 mol%
- Provides more realistic uncertainty estimates for heavy components (C5-C10)

**Advantages:**
- Based on actual parallel test data from multiple GC systems
- Better captures the increased uncertainty of heavy hydrocarbons
- Accounts for the non-linear relationship between concentration and uncertainty
- More realistic for mass-based property calculations (density, speed of sound)

**Limitations:**
- Empirical model derived from specific laboratory conditions
- May overestimate uncertainty for very lean pipeline gases
- Limited to natural gas compositions with high methane content

**Supported components:** N2, CO2, C1-C10

---

## Method Selection Guidance

### For Pipeline Quality Gas (Lean Gas, ~38 MJ/m³)
- **ASTM D1945** is the traditional choice and widely accepted
- May slightly overestimate uncertainty for calculated properties
- Consider **Hagenvik 2024** if you find ASTM results too conservative

### For Rich Natural Gas (Wet Gas, Condensate, > 42 MJ/m³)
- **Hagenvik 2024 is recommended** - provides more realistic estimates
- ASTM D1945 and NORSOK I-106 will likely **underestimate** uncertainty
- Heavy component uncertainties have significant impact on density and speed of sound

### For North Sea Fiscal Applications
- **NORSOK I-106** is the regulatory standard
- Consider comparing with Hagenvik 2024 for rich gases

### General Recommendation
When in doubt, **compare all three methods** as demonstrated in [Example 09](../../examples/09%20-%20Compositional%20uncertainties). The differences between methods reveal the inherent challenges in compositional uncertainty estimation.

---

## Impact on Property Calculations

The choice of compositional uncertainty model significantly affects calculated property uncertainties:

| Property | Sensitivity to Heavy Components | Impact of Method Choice |
|----------|----------------------------------|-------------------------|
| Molar mass | High - linear relationship | Moderate |
| Density | Very high - strong C5+ dependence | **High** |
| Speed of sound | High - sensitive to both light and heavy | **High** |
| Energy content | Moderate - all components contribute | Moderate |

For **rich gases**, using ASTM D1945 or NORSOK I-106 can underestimate density uncertainty by 30-50% compared to Hagenvik 2024.

---

## References

1. **ASTM D1945** - Standard Test Method for Analysis of Natural Gas by Gas Chromatography
   - Widely used international standard
   - Reproducibility values for pipeline quality gas

2. **NORSOK I-106:2014** - Fiscal measurement systems for hydrocarbon gas
   - Norwegian shelf fiscal metering standard
   - Molar mass ratio method

3. **Hagenvik et al. (2024)** - "Exploring the Relationship between Speed of Sound, Density and Isentropic Exponent"
   - Presented at NFOGM 2024
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

⚠️ **No single method is perfect** - ASTM and NORSOK are standardized but may not reflect real-world performance for all gas types. Hagenvik is empirical but based on actual measurement data.

⚠️ **Always validate** uncertainty estimates against your specific GC system performance through parallel testing or validation samples when possible.
