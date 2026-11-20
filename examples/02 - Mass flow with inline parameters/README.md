# Example 02: Mass flow with inline parameters

This example performs an uncertainty analysis of a simple mass flow calculation, with the input
parameters defined directly in the script as a dictionary.

## Method

The script `example_02.py`:

1. Defines the inputs as a dictionary with the keys `mean`, `standard_uncertainty`,
   `standard_uncertainty_percent`, `distribution`, `min` and `max`.
2. Defines `calculate_massflow`, which returns `massflow = Q * rho`.
3. Calculates absolute and relative sensitivity coefficients.
4. Runs a Monte Carlo simulation with 10,000 perturbations and prints its statistics.
5. Calculates the correlations between the Monte Carlo outputs.
6. Calculates the uncertainty with the conventional method and compares it with the Monte Carlo
   result.

## Input data

| Input | Mean | Standard uncertainty | Standard uncertainty (%) | Distribution | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| `Q` | 370 | 1 | 0.25 | normal | 0 | None |
| `rho` | 54 | 0.03 | 0.1 | normal | 0 | None |

Both an absolute and a relative standard uncertainty are given; the library uses the larger of the
two. No units are given in the script.

The same values are also in `example_02_input.csv`; the script does not read that file.

## Files

- `example_02.py`: the example script
- `example_02_input.csv`: the same input values as a CSV file (not read by the script)
