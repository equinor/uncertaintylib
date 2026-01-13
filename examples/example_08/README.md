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
  - Speedup factor (varies significantly by CPU - see Performance Considerations below)
  - Percentage reduction in computation time
  - Statistical differences (should be minimal, within Monte Carlo noise)

**Note**: The speedup factor is highly CPU-dependent. Results may range from 0.8x (slower) to 4x (faster) depending on your hardware.

## Performance Considerations

**Important**: Performance improvements from parallel processing are **highly dependent on CPU architecture** and system configuration.

### CPU Architecture Matters

Different CPUs show vastly different parallelization benefits:

#### Older/Desktop CPUs (e.g., Intel i5-4670K, i7-4790K)
- **Architecture**: Homogeneous cores (all cores have equal performance)
- **TDP**: Higher power budget (65-95W), no aggressive throttling
- **Expected speedup**: 30-50% improvement with 4 processes
- **Why it works well**: All cores run at similar frequencies, minimal overhead

#### Modern Hybrid CPUs (e.g., Intel 12th+ gen, Core Ultra series)
- **Architecture**: P-cores (Performance) + E-cores (Efficiency)
- **Performance variation**: P-cores are 2-3x faster than E-cores
- **Expected speedup**: 0-30% improvement, sometimes slower than sequential
- **Challenges**:
  - Windows may schedule processes to slow E-cores
  - Process creation overhead can exceed parallelization benefit
  - Single P-core turbo boost (up to 5+ GHz) may outperform multiple cores at lower sustained frequencies

#### Mobile/Laptop CPUs (especially Ultra-Low Power)
- **TDP**: Low power budget (15-28W), aggressive thermal throttling
- **Single-core boost**: Very high single-core turbo, lower multi-core sustained frequency
- **Expected speedup**: May see **no improvement or slower performance**
- **Why**: 
  - 1 core at 5 GHz often beats 4 cores at 3 GHz for moderate workloads
  - Thermal limits kick in faster with multiple cores active
  - Windows multiprocessing overhead is significant

### General Guidelines

- **Overhead**: Multiprocessing has significant overhead on Windows; most beneficial for large N (>100,000 simulations)
- **Memory**: Each process needs memory; very large N may require consideration of available RAM
- **Process count**: More processes ≠ better performance. For N=1,000,000, limiting to 4 processes often yields best results
- **Platform**: Linux/Unix systems typically show better parallelization due to more efficient `fork()` vs Windows `spawn()`

### Recommendation

**Always benchmark on your specific hardware!** What works well on one CPU may not work on another. The example is designed to demonstrate the technique, but actual performance gains will vary based on:
- Your CPU architecture (homogeneous vs hybrid)
- Power settings (high performance vs balanced)
- Thermal conditions (desktop vs laptop cooling)
- Operating system (Windows vs Linux)
- Workload size (N value)

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
