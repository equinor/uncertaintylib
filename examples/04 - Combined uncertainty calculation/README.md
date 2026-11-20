# Example 04: Combined uncertainty calculation

This example calculates a combined standard uncertainty directly from given input uncertainties
and sensitivity coefficients with `uncertainty_functions.combined_standard_uncertainty`, for two
cases.

## Part 1: Orifice meter

- The input uncertainties `u` and sensitivity coefficients `ci` for the inputs of the orifice
  meter in [Example 03](../03%20-%20Orifice%20meter%20with%20visualization) are written in the
  script.
- The combined standard uncertainty is calculated and multiplied by 2 (k=2).
- The result is printed next to the value from the conventional calculation in Example 03
  (`0.5892192204199442`, written in the script).

## Part 2: Ultrasonic flowmeter (USM)

- Input uncertainties for a USM with a single pressure and temperature measurement and a gas
  chromatograph are written in the script (`calb_ref`, `calib_rep`, `calib_dev`,
  `field_uncertainty`, `pressure`, `temperature`, `m/Z`).
- No sensitivity coefficients are given, so the function uses 1 for every input.
- The combined standard uncertainty is multiplied by 2 (k=2), rounded to 5 decimals and printed
  next to the reference value 0.647 from the NFOGM Fiscal Gas Metering Station Uncertainty
  (GasMet) tool, as written in the script.

## Files

- `example_04_combined_uncertainty.py`: the example script (all inputs are in the script)
