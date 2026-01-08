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

## example_06
Comprehensive uncertainty analysis for a gas metering station with an Ultrasonic Flowmeter (USM), Gas Chromatograph (GC), and dual pressure/temperature measurements. **Presented as a Jupyter Notebook.**
- Calculates mass flow and standard volumetric flow
- Uses GERG-2008 equation of state for gas properties
- Includes USM calibration curve interpolation
- Demonstrates both analytical uncertainty calculations and Monte Carlo simulation (10,000 iterations)
- Provides detailed visualization of uncertainty contributions
- Plots calibration curves and operating points
- Input data loaded from CSV file

## example_07
Demonstrates uncertainty analysis for gas properties (density and molar mass) calculated from measured speed of sound. **Presented as a Jupyter Notebook.**
- Uses GERG-2008 equation of state to calculate isentropic exponent (kappa) and compressibility factor (Z)
- Calculates density and molar mass from measured speed of sound using thermodynamic relationships
- **Includes model uncertainty factors** to account for GERG-2008 equation of state limitations (0.05% uncertainty on kappa and Z)
- Demonstrates both analytical uncertainty calculations and Monte Carlo simulation (10,000 iterations)
- Shows uncertainty contribution analysis to identify dominant uncertainty sources
- Visualizes probability distributions of output parameters
- Separates measurement uncertainty from model uncertainty
- Input data loaded from CSV file

---
Each example uses the `uncertaintylib` library to perform uncertainty analysis and visualize results. Input parameters are either loaded from a CSV file in the same folder or, for example_02, defined directly in the code. Examples 06 and 07 are provided as Jupyter Notebooks for interactive exploration and include both analytical and Monte Carlo methods for uncertainty propagation.
