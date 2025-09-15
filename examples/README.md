# Examples Overview

This folder contains example scripts demonstrating different aspects of uncertainty analysis using the `uncertaintylib` library. Below is a summary of each example:

## example_1.py
Illustrates how two inputs can be used to calculate several outputs, and how a fixed setting (not varied in uncertainty analysis) is handled. Demonstrates calculation of sensitivity coefficients and Monte Carlo simulation for a simple function.

## example_2.py
Shows uncertainty analysis for a basic mass flow calculation. Demonstrates calculation of sensitivity coefficients and Monte Carlo simulation for a function with two inputs.

## example_3.py
Performs uncertainty analysis for mass flow calculation using an orifice meter. Includes sensitivity analysis, Monte Carlo simulation, and visualization of results and uncertainty contributions.

## example_4_combined_uncertainty.py
Demonstrates calculation of combined standard uncertainty for an orifice meter and a USM (ultrasonic meter) using hardcoded input values. Compares results from different calculation methods.

## example_5.py
Analyzes uncertainty in the calculation of total molar mass from gas composition using AGA8 molar masses. Includes sensitivity analysis and Monte Carlo simulation.

---
Each example loads its input parameters from a CSV file in the same folder, and uses the `uncertaintylib` library to perform uncertainty analysis and visualize results.
