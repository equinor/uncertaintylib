# Example 03: Orifice meter with visualization

This example performs an uncertainty analysis of the mass flow through an orifice meter and
visualizes the results and the uncertainty contributions.

## Method

The script `example_03.py`:

1. Loads the inputs from `example_03_input.csv`.
2. Defines `calculate_massflow`, which calculates the mass flow `qm` as

   ```
   qm = C / sqrt(1 - (d/D)^4) * epsilon * pi * d^2 / 4 * sqrt(2 * P1 * deltaP * (m/Z) / (R * T))
   ```

   with `R = 8.314` J/(mol K). Inside the function `D` and `d` are converted from mm to m,
   `deltaP` from mbar to Pa and `P` from bara to Pa.
3. Calculates absolute and relative sensitivity coefficients.
4. Runs a Monte Carlo simulation with 10,000 perturbations and prints its statistics.
5. Calculates the correlations between the Monte Carlo outputs.
6. Calculates the uncertainty with the conventional method and compares it with the Monte Carlo
   result.
7. Plots the Monte Carlo distribution of the mass flow with a summary table
   (`plot_functions.montecarlo_property_plot_and_table`, labelled in kg/s) and the contribution of
   each input to the uncertainty of the mass flow (`plot_functions.plot_uncertainty_contribution`).

## Input data

`example_03_input.csv` (all uncertainties given as relative standard uncertainty in %, normal
distribution):

| Input | Mean | Standard uncertainty (%) | Unit in the CSV |
| --- | --- | --- | --- |
| `C` | 0.60282 | 0.25 | (dimensionless) |
| `epsilon` | 0.99935 | 0.00311 | (dimensionless) |
| `D` | 300 | 0.2 | mm |
| `d` | 150 | 0.035 | mm |
| `deltaP` | 250.2 | 0.03 | mbar |
| `P` | 100 | 0.15 | bara |
| `m/Z` | 0.021019 | 0.216 | kg/mol |
| `T` | 323.15 | 0.0464 | K |

`m/Z` is the molar mass divided by the compressibility factor. With `R` in J/(mol K) and `T` in
K, `P1 * (m/Z) / (R * T)` is the gas density in kg/m3, and `qm` is in kg/s.

### Source of the input values

- `m/Z` = 0.021019 kg/mol: molar mass M = 18.125 g/mol and Z = 0.86232, calculated with
  pvtlib 1.16.1, AGA8 GERG-2008, at P = 100 bara and T = 323.15 K. The gas is the dry natural gas
  composition from pvtlib example "01 Gas Properties from AGA8" (mol%: N2 1.0, CO2 1.0, C1 90.0,
  C2 5.0, C3 2.0, iC4 0.5, nC4 0.5).
- `epsilon` = 0.99935: ISO 5167-2:2022 orifice expansibility (pvtlib
  `calculate_expansibility_orifice`), with isentropic exponent kappa = 1.4236 from GERG-2008 for
  the same gas and state.
- `C` = 0.60282: ISO 5167-2:2022 Reader-Harris/Gallagher discharge coefficient for an orifice
  plate with corner tappings (pvtlib default), D = 300 mm, d = 150 mm (beta = 0.5). It is solved
  iteratively with the Reynolds number in pvtlib `calculate_flow_orifice`, which gives
  Re_D = 6.37e6. The density is 78.230 kg/m3 from GERG-2008, and the viscosity is 1.450e-5 Pa s
  from pvtlib `natural_gas_viscosity_Lee_et_al` (Lee, Gonzalez and Eakin, 1966).
- The relative standard uncertainty of `C` (0.25 %) corresponds to the ISO 5167-2 value of
  0.5 % (k=2) for 0.2 <= beta <= 0.6.

The example script itself does not depend on pvtlib. The values above are fixed inputs in the CSV.
The calculated mass flow is about 21.75 kg/s, with an expanded uncertainty of about 0.59 % (k=2).

## Files

- `example_03.py`: the example script
- `example_03_input.csv`: input values and uncertainties
