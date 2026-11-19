# Example 01: Simple uncertainty with multiple outputs

This example shows how two uncertain inputs are used to calculate several outputs, and how an
input that is a fixed setting is kept out of the uncertainty analysis.

## Method

The script `example_01.py`:

1. Loads the inputs from `example_01_input.csv`.
2. Defines `my_function`, which calculates from the inputs `x` and `y`:
   - `a = x + y`
   - `b = y - x`
   - `c = x * y`
   - `d = y / x` if `setting_A` is 0, otherwise `d = y / (x + 1)`

   It also returns the input values used (`x_used`, `y_used`, `setting_A_used`), and raises an
   exception if `setting_A` is not a whole number.
3. Calculates absolute and relative sensitivity coefficients with
   `calculate_sensitivity_coefficients`.
4. Runs a Monte Carlo simulation with 10,000 perturbations (`monte_carlo_simulation`) and
   calculates its statistics (`calculate_monte_carlo_statistics`).
5. Plots histograms of the `x` values used and of the output `a` from the Monte Carlo simulation.
6. Calculates the correlations between the Monte Carlo outputs
   (`monte_carlo_output_correlations`).
7. Calculates the uncertainty with the conventional method (`calculate_uncertainty`) and compares
   it with the Monte Carlo result
   (`compare_monte_carlo_to_conventional_uncertainty_calculation`).

## Input data

`example_01_input.csv`:

| Input | Mean | Standard uncertainty | Distribution | Min |
| --- | --- | --- | --- | --- |
| `x` | 5 | 1 | normal | 0 |
| `y` | 5 | 1 | normal | 0 |
| `setting_A` | 2 | - | none | - |
| `z` | 3 | 2 | normal | - |

`setting_A` has distribution `none`, so it is treated as a constant: no sensitivity coefficient is
calculated for it and it is not perturbed in the Monte Carlo simulation. `z` is in the input file
but is not used by `my_function`.

## Files

- `example_01.py`: the example script
- `example_01_input.csv`: input values and uncertainties
