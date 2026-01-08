# Example 07: Uncertainty in gas properties calculated from measured speed of sound

This example demonstrates how to calculate uncertainty in gas properties (density and molar mass) that are derived from measured speed of sound measurements.

## Overview

The example uses:
- **pvtlib**: For thermodynamic calculations using the GERG-2008 equation of state
- **uncertaintylib**: For uncertainty propagation calculations using both analytical methods and Monte Carlo simulation

## Method

The calculation follows this two-step process:

1. **Calculate reference properties using GERG-2008**: 
   - Input: Gas composition, pressure (P), and temperature (T)
   - Output: Isentropic exponent (kappa) and compressibility factor (Z)
   - Model uncertainty factors are applied to kappa and Z to account for inherent limitations in the GERG-2008 equation of state

2. **Calculate properties from measured speed of sound**:
   - Input: Measured speed of sound, kappa (with model uncertainty), Z (with model uncertainty), P, and T
   - Output: Density and molar mass derived from the speed of sound measurement

The uncertainty analysis propagates uncertainties from all input parameters, including the GERG-2008 model uncertainty, through both calculation steps to determine the combined uncertainty in the final density and molar mass values.

## Input Data

Input parameters are specified in `data.csv`:
- **Pressure** (P): 100.0 bara ± 0.15 bara
- **Temperature** (T): 50.0 °C ± 0.15 °C
- **Measured speed of sound**: 433.0 m/s ± 0.1% (relative uncertainty)
- **Gas composition**: Natural gas with 7 components (N2, CO2, C1, C2, C3, iC4, nC4)
- **GERG model uncertainty factors**: 
  - `GERG_kappa_uncertainty_factor`: Mean = 1.0, uncertainty = 0.05% (accounts for model uncertainty in isentropic exponent)
  - `GERG_Z_uncertainty_factor`: Mean = 1.0, uncertainty = 0.05% (accounts for model uncertainty in compressibility factor)

Each input parameter includes:
- Mean value
- Standard uncertainty (absolute or percentage)
- Distribution type (for Monte Carlo simulations)
- Min/max bounds (for Monte Carlo simulations)

The GERG uncertainty factors are multiplicative factors (nominal value = 1.0) that allow the uncertainty propagation to account for the inherent uncertainty in the GERG-2008 equation of state model itself.

## Output

The notebook calculates and displays:
- **Density from speed of sound** with expanded uncertainty (k=2)
- **Molar mass from speed of sound** with expanded uncertainty (k=2)
- **Uncertainty contribution plots** showing which input parameters contribute most to the output uncertainties
- **Detailed uncertainty breakdown** for both density and molar mass
- **Monte Carlo simulation results** (10,000 iterations) validating the analytical calculations
- **Probability distribution plots** showing the full distribution of density and molar mass from the Monte Carlo simulation

## Files

- `example_07.ipynb`: Jupyter notebook with the complete example
- `data.csv`: Input data including measured values and uncertainties
- `requirements.txt`: Python package dependencies

## Running the Example

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Open the notebook:
   ```
   jupyter notebook example_07.ipynb
   ```

3. Run all cells to see the uncertainty analysis results

## Key Features

- Demonstrates uncertainty propagation through multi-step calculations
- **Accounts for model uncertainty** in the GERG-2008 equation of state through uncertainty factors
- Shows how to structure input data for uncertaintylib
- Illustrates uncertainty contribution analysis to identify dominant uncertainty sources
- Provides visualization of uncertainty sources
- Separates measurement uncertainty (speed of sound, P, T, composition) from model uncertainty (GERG-2008)
- **Includes Monte Carlo simulation** to validate analytical uncertainty calculations
- **Visualizes probability distributions** of output parameters from Monte Carlo results
