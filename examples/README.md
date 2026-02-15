# Examples Overview

This folder contains example scripts demonstrating different aspects of uncertainty analysis using the `uncertaintylib` library. Below is a summary of each example:

## 01 - Simple uncertainty with multiple outputs
Illustrates how two inputs can be used to calculate several outputs, and how a fixed setting (not varied in uncertainty analysis) is handled. Demonstrates calculation of sensitivity coefficients and Monte Carlo simulation for a simple function.

## 02 - Mass flow with inline parameters
Shows uncertainty analysis for a basic mass flow calculation. Demonstrates calculation of sensitivity coefficients and Monte Carlo simulation for a function with two inputs. **Input parameters are defined directly as a dictionary in the script.**

## 03 - Orifice meter with visualization
Performs uncertainty analysis for mass flow calculation using an orifice meter. Includes sensitivity analysis, Monte Carlo simulation, and visualization of results and uncertainty contributions.

## 04 - Combined uncertainty calculation
Demonstrates calculation of combined standard uncertaintyfor two cases, based on input uncertainties and sensitivity coefficients, and compares results against other sources.
Divided into two parts:
- **Part 1:** Performs analysis for an orifice meter and compares the results with those from example 03. Sensitivity coefficients are provided. 
- **Part 2:** Performs analysis for an Ultrasonic Flowmeter (USM) and compares the results against a reference case from the NGOFM GasMet uncertainty application. In this case, sensitivity coefficients are not provided, in which the code will assume sensitivity coefficients to be 1. 

## 05 - Gas composition molar mass
Analyzes uncertainty in the calculation of total molar mass from gas composition using AGA8 molar masses. Includes sensitivity analysis and Monte Carlo simulation.

## 06 - Gas metering station (Jupyter)
Comprehensive uncertainty analysis for a gas metering station with an Ultrasonic Flowmeter (USM), Gas Chromatograph (GC), and dual pressure/temperature measurements. **Presented as a Jupyter Notebook.**
- Calculates mass flow and standard volumetric flow
- Uses GERG-2008 equation of state for gas properties
- Includes USM calibration curve interpolation
- Demonstrates both analytical uncertainty calculations and Monte Carlo simulation (10,000 iterations)
- Provides detailed visualization of uncertainty contributions
- Plots calibration curves and operating points
- Input data loaded from CSV file

## 07 - Gas properties from speed of sound (Jupyter)
Demonstrates uncertainty analysis for gas properties (density and molar mass) calculated from measured speed of sound. **Presented as a Jupyter Notebook.**
- Uses GERG-2008 equation of state to calculate isentropic exponent (kappa) and compressibility factor (Z)
- Calculates density and molar mass from measured speed of sound using thermodynamic relationships
- **Includes model uncertainty factors** to account for GERG-2008 equation of state limitations (0.05% uncertainty on kappa and Z)
- Demonstrates both analytical uncertainty calculations and Monte Carlo simulation (10,000 iterations)
- Shows uncertainty contribution analysis to identify dominant uncertainty sources
- Visualizes probability distributions of output parameters
- Separates measurement uncertainty from model uncertainty
- Input data loaded from CSV file

## 08 - Parallel Monte Carlo processing
Demonstrates **parallel processing for Monte Carlo simulations** to reduce computation time for large-scale uncertainty analysis. Based on the same orifice meter mass flow calculation as Example 03.
- Compares sequential vs. parallelized Monte Carlo simulation (1,000,000 perturbations)
- Uses Python's `multiprocessing.Pool` to distribute calculations across all available CPU cores
- Splits simulations into equal-sized batches for parallel execution
- Provides detailed performance metrics: speedup factor, execution time comparison, and percentage time reduction
- Validates that parallel results match sequential results statistically
- Demonstrates how to achieve 4x-8x speedup on multi-core processors
- Shows when parallel processing is beneficial (large N > 100,000 simulations)
- Input data loaded from CSV file (same as Example 03)

---
Each example uses the `uncertaintylib` library to perform uncertainty analysis and visualize results. Input parameters are either loaded from a CSV file in the same folder or, for example 02, defined directly in the code. Examples 06 and 07 are provided as Jupyter Notebooks for interactive exploration and include both analytical and Monte Carlo methods for uncertainty propagation. Example 08 demonstrates how to use parallel processing to accelerate Monte Carlo simulations for computationally intensive uncertainty analyses.
