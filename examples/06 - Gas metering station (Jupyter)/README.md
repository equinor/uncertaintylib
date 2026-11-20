# Example 06: Gas metering station (Jupyter)

This notebook calculates the uncertainty of a gas metering station with an ultrasonic flowmeter
(USM), a gas chromatograph (GC) and dual pressure and temperature measurements. It uses both the
conventional uncertainty calculation (sensitivity coefficients and input uncertainties) and the
Monte Carlo method.

## Method

`example_06.ipynb`:

1. Reads the inputs from `data.csv` and converts them to the dictionary format of uncertaintylib.
2. Defines `calculate_gas_metering_station`, which:
   - averages the two pressures (bara) and the two temperatures (C),
   - calculates density, compressibility factor and molar mass with the GERG-2008 equation of
     state from pvtlib, and multiplies the density by `GERG_uncertainty_factor` to include the
     model uncertainty of GERG-2008,
   - interpolates the USM calibration error (%) at the measured volume flow from a six-point
     calibration curve, and corrects the volume flow (m3/h) for it,
   - calculates the mass flow (kg/h) and the volume flow at standard conditions (Sm3/h) at
     288.15 K and 101.325 kPa.

   The composition passed to GERG-2008 (at operating and at standard conditions) uses the values
   of all seven components N2, CO2, C1, C2, C3, iC4 and nC4 from the function input, so each
   component's uncertainty is included in both the conventional and the Monte Carlo calculation.
3. Calculates the uncertainty with `calculate_uncertainty` and prints the gas properties and
   flow rates with their expanded uncertainty (k=2).
4. Plots the ten largest contributions to the uncertainty of the standard volume flow.
5. Plots the USM calibration curve with error bars (k=2) and the operating point.
6. Runs a Monte Carlo simulation with 10,000 perturbations, prints the flow rates with their
   uncertainty (k=2) and plots the distribution of the standard volume flow.

## Input data

`data.csv` holds, with units and uncertainties:

- USM pressures A and B (bara) and temperatures A and B (C)
- the measured USM volume flow (m3/h)
- six calibration points: volume flow (m3/h) and calibration error (%)
- the gas composition N2, CO2, C1, C2, C3, iC4, nC4 (mol%)
- `GERG_uncertainty_factor` (mean 1.0, 0.05 % standard uncertainty)

## Files

- `example_06.ipynb`: the notebook
- `data.csv`: input values and uncertainties
- `requirements.txt`: Python packages needed to run the notebook

## Running the example

```
pip install -r requirements.txt
jupyter notebook example_06.ipynb
```
