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
| `C` | 0.5 | 0.25 | |
| `epsilon` | 0.9993 | 0.00311 | |
| `D` | 300 | 0.2 | mm |
| `d` | 150 | 0.035 | mm |
| `deltaP` | 250.2 | 0.03 | mbar |
| `P` | 100 | 0.15 | bara |
| `m/Z` | 0.4 | 0.216 | kg/mol |
| `T` | 323.15 | 0.0464 | C |

Note: the CSV gives the unit of `T` as C, while the value 323.15 and the use of `T` in the gas
law term of the formula correspond to kelvin.

## Files

- `example_03.py`: the example script
- `example_03_input.csv`: input values and uncertainties
