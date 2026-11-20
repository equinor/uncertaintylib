# Example 05: Gas composition molar mass

This example performs an uncertainty analysis of the molar mass of a natural gas calculated from
its composition.

## Method

The script `example_05.py`:

1. Loads the composition and its uncertainties from `example_05_input.csv`.
2. Defines a function that normalizes the composition to 100 mol% and calculates the molar mass
   as the mole-fraction weighted sum of the component molar masses. The component molar masses
   (AGA8 values, N2 to nC10) are written in the script. The output is `MolarMass`.
3. Calculates absolute and relative sensitivity coefficients.
4. Runs a Monte Carlo simulation with 10,000 perturbations and prints its statistics.
5. Calculates the correlations between the Monte Carlo outputs.
6. Calculates the uncertainty with the conventional method and compares it with the Monte Carlo
   result.

## Input data

`example_05_input.csv` holds the mean value and the absolute standard uncertainty of 14
components (N2, CO2, C1, C2, C3, iC4, nC4, iC5, nC5, nC6, nC7, nC8, nC9, nC10), all with a normal
distribution limited to 0-100. The function normalizes the composition to 100 mol% before
calculating the molar mass.

## Files

- `example_05.py`: the example script
- `example_05_input.csv`: composition and uncertainties
