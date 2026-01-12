# Example 08: Parallel Monte Carlo Simulation

## Overview
This example demonstrates how to accelerate Monte Carlo uncertainty propagation calculations using parallel processing. It compares the performance of sequential vs. parallelized Monte Carlo simulations for the same mass flow calculation from Example 03.

## Purpose
The primary goal is to show how to reduce computation time for large Monte Carlo simulations by:
- Utilizing multiple CPU cores through batch processing
- Splitting simulations into equal-sized batches across available processors
- Comparing execution times and validating that parallel results match sequential results

## Description
The script performs uncertainty analysis for mass flow calculation using an orifice meter (based on ISO 5167 equations), but runs it as a batch calculation using Python's `multiprocessing` module.

The script:
1. Loads input parameters with uncertainties from CSV file
2. Runs a **baseline sequential** Monte Carlo simulation (1,000,000 perturbations)
3. Runs a **parallelized batch** Monte Carlo simulation (1,000,000 perturbations split across CPU cores)
4. Compares execution times and speedup metrics
5. Validates that statistical results (mean, std dev) are equivalent between both methods

## Key Features
- **Multiprocessing.Pool**: Uses all available CPU cores for parallel execution
- **Batch Processing**: Divides total simulations equally across processors
- **Performance Metrics**: Calculates speedup factor and percentage time reduction
- **Statistical Validation**: Confirms parallel results match baseline within expected Monte Carlo variability

## Dependencies
- pandas
- numpy
- multiprocessing (standard library)
- uncertaintylib.uncertainty_functions (custom library)

## Input Data
- `example_03_input.csv`: CSV file containing input parameters and their uncertainties (same as Example 03)

## Expected Results
The script outputs:
- **Baseline Statistics**: Mean and standard deviation from sequential Monte Carlo
- **Baseline Execution Time**: Time taken for sequential simulation
- **Parallel Statistics**: Mean and standard deviation from parallel Monte Carlo
- **Parallel Execution Time**: Time taken for parallel simulation
- **Comparison Metrics**:
  - Speedup factor (e.g., 4x-8x depending on CPU cores)
  - Percentage reduction in computation time
  - Statistical differences (should be minimal, within Monte Carlo noise)

## Performance Considerations
- **Speedup**: Typically achieves 4x-8x speedup on modern multi-core processors
- **Overhead**: Multiprocessing has some overhead; most beneficial for large N (>100,000 simulations)
- **Memory**: Each process needs memory; very large N may require consideration of available RAM

## When to Use Parallel Processing
Parallel processing is most beneficial when:
- Running large numbers of Monte Carlo simulations (N > 100,000)
- The calculation function is computationally intensive
- Multiple CPU cores are available
- Execution time of sequential approach is prohibitively long

For smaller simulations (N < 10,000), the overhead of multiprocessing may exceed the benefits.

## Comparison with Example 03
- **Example 03**: Sequential Monte Carlo with 10,000 perturbations + visualization
- **Example 08**: Parallel Monte Carlo with 1,000,000 perturbations + performance comparison

Both use the same orifice meter mass flow calculation and input data, but Example 08 focuses on computational efficiency for large-scale simulations.
