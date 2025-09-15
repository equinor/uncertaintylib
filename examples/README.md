# Examples Overview

This folder contains example scripts demonstrating different aspects of uncertainty analysis using the `uncertaintylib` library. Below is a summary of each example:

## example_01
Illustrates how two inputs can be used to calculate several outputs, and how a fixed setting (not varied in uncertainty analysis) is handled. Demonstrates calculation of sensitivity coefficients and Monte Carlo simulation for a simple function.

## example_02
Shows uncertainty analysis for a basic mass flow calculation. Demonstrates calculation of sensitivity coefficients and Monte Carlo simulation for a function with two inputs. **Input parameters are defined directly as a dictionary in the script.**

## example_03
Performs uncertainty analysis for mass flow calculation using an orifice meter. Includes sensitivity analysis, Monte Carlo simulation, and visualization of results and uncertainty contributions.

## example_04
Demonstrates calculation of combined standard uncertaintyfor two cases, based on input uncertainties and sensitivity coefficients, and compares results against other sources.
Divided into two parts:
- **Part 1:** Performs analysis for an orifice meter and compares the results with those from example 03. Sensitivity coefficients are provided. 
- **Part 2:** Performs analysis for an Ultrasonic Flowmeter (USM) and compares the results against a reference case from the NGOFM GasMet uncertainty application. In this case, sensitivity coefficients are not provided, in which the code will assume sensitivity coefficients to be 1. 

## example_05
Analyzes uncertainty in the calculation of total molar mass from gas composition using AGA8 molar masses. Includes sensitivity analysis and Monte Carlo simulation.

---
Each example uses the `uncertaintylib` library to perform uncertainty analysis and visualize results. Input parameters are either loaded from a CSV file in the same folder or, for example_02, defined directly in the code.
