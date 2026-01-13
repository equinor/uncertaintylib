"""MIT License

Copyright (c) 2025 Equinor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
"""
Monte Carlo Batch Processing Comparison Script

This script compares the performance of sequential vs. parallelized Monte Carlo simulations
for uncertainty propagation in mass flow calculations.

Comparison:
-----------
- Sequential: Single-process Monte Carlo simulation
- Parallel: Multi-process batch Monte Carlo simulation using {num_processes} CPU cores
- Number of perturbations: {N} simulations per method

The script performs the following:
1. Loads input parameters with uncertainties from a CSV file
2. Runs a baseline sequential Monte Carlo simulation
3. Runs a parallelized batch Monte Carlo simulation
4. Compares execution times and statistical results (mean, std dev)

The mass flow calculation is based on ISO 5167 orifice plate equations,
propagating uncertainties through the calculation using Monte Carlo methods.

Key Features:
-------------
- Utilizes multiprocessing.Pool for parallel execution
- Splits simulations into equal-sized batches across available CPU cores
- Provides detailed timing and statistical comparison metrics
- Validates parallel results against baseline sequential results

Dependencies:
-------------
- pandas, numpy, multiprocessing
- uncertaintylib.uncertainty_functions (custom library)

Input:
------
- example_03_input.csv: CSV file containing input parameters and their uncertainties

Output:
-------
- Baseline and parallel Monte Carlo statistics (mean, std dev, etc.)
- Execution time comparison and speedup metrics
- Statistical validation comparing both methods
"""
import pandas as pd
import numpy as np
import math
import time
from multiprocessing import Pool, cpu_count
from uncertaintylib import uncertainty_functions

def calculate_massflow(input_dict):
    R = 8.314 #J/molK
    C = input_dict['C']
    epsilon = input_dict['epsilon']
    D = input_dict['D']/1000 #m
    d = input_dict['d']/1000 #m
    deltaP = input_dict['deltaP']*100 #Pa
    P1 = input_dict['P'] * 10**5 #Pa
    T = input_dict['T']
    m_div_Z = input_dict['m/Z'] #kg/mol
    qm = (C/np.sqrt(1-((d/D)**4)))*(epsilon*math.pi*(d**2)/4)*np.sqrt((2*P1*deltaP*m_div_Z)/(R*T))
    output_dict = {'qm' : qm}
    return output_dict

# Function to run a single batch
def run_batch(batch_size):
    """Run Monte Carlo simulation for a single batch"""
    # Load input parameters inside the function to avoid pickling issues
    csv_path = os.path.join(os.path.dirname(__file__), 'example_03_input.csv')
    mc_input = pd.read_csv(csv_path).set_index('input_name').to_dict()
    return uncertainty_functions.monte_carlo_simulation(mc_input, calculate_massflow, batch_size)

if __name__ == '__main__':
    # Load input parameters from CSV file in the same folder as the script
    csv_path = os.path.join(os.path.dirname(__file__), 'example_03_input.csv')
    mc_input = pd.read_csv(csv_path).set_index('input_name').to_dict()
    
    N = 1000000
    SEP = "="*80  # Separator line for output formatting

    print(SEP)
    print("BASELINE: Sequential Monte Carlo Simulation")
    print(SEP)

    # Step 1: Run Monte Carlo simulation to propagate input uncertainties
    start_time = time.time()
    mc_res = uncertainty_functions.monte_carlo_simulation(mc_input, calculate_massflow, N)
    mc_stats = uncertainty_functions.calculate_monte_carlo_statistics(mc_res)
    end_time = time.time()
    baseline_time = end_time - start_time

    # Step 2: Print Monte Carlo statistics
    print("\nBaseline Statistics:")
    print(mc_stats)
    print(f"\nBaseline Execution time: {baseline_time:.2f} seconds")

    print("\n" + SEP)
    print("PARALLEL: Batch Monte Carlo Simulation")
    print(SEP)

    # Parallel processing
    num_processes = cpu_count()  # Use all available CPU cores

    if num_processes>4:
        num_processes=4

    batch_size = N // num_processes

    print(f"\nNumber of processes: {num_processes}")
    print(f"Batch size per process: {batch_size}")
    print(f"Total simulations: {num_processes * batch_size}")

    # Prepare arguments for parallel execution - just pass batch_size
    batch_args = [batch_size for _ in range(num_processes)]

    # Run parallel batches
    start_time_parallel = time.time()
    with Pool(processes=num_processes) as pool:
        batch_results = pool.map(run_batch, batch_args)
    end_time_parallel = time.time()

    # Concatenate results
    mc_res_parallel = pd.concat(batch_results, ignore_index=True)
    mc_stats_parallel = uncertainty_functions.calculate_monte_carlo_statistics(mc_res_parallel)
    parallel_time = end_time_parallel - start_time_parallel

    print("\nParallel Statistics:")
    print(mc_stats_parallel)
    print(f"\nParallel Execution time: {parallel_time:.2f} seconds")

    print("\n" + SEP)
    print("COMPARISON")
    print(SEP)
    print(f"\nComparing sequential vs parallel Monte Carlo simulation:")
    print(f"  - Total perturbations (N): {N}")
    print(f"  - Number of parallel processes: {num_processes}")
    print(f"  - Perturbations per process: {batch_size}")
    print("\nPerformance Metrics:")
    print(SEP)
    print(f"Baseline time: {baseline_time:.2f} seconds")
    print(f"Parallel time: {parallel_time:.2f} seconds")
    print(f"Difference: {baseline_time - parallel_time:.2f} seconds")
    print(f"Speedup: {baseline_time / parallel_time:.2f}x")
    print(f"Percentage reduction in time: {(1 - parallel_time/baseline_time)*100:.1f}%")

    print("\nStatistics Comparison:")
    print(f"Baseline mean: {mc_stats.loc['qm', 'mean']:.6f}")
    print(f"Parallel mean: {mc_stats_parallel.loc['qm', 'mean']:.6f}")
    print(f"Difference: {abs(mc_stats.loc['qm', 'mean'] - mc_stats_parallel.loc['qm', 'mean']):.6e}")

    print(f"\nBaseline std: {mc_stats.loc['qm', 'std_dev']:.6f}")
    print(f"Parallel std: {mc_stats_parallel.loc['qm', 'std_dev']:.6f}")
    print(f"Difference: {abs(mc_stats.loc['qm', 'std_dev'] - mc_stats_parallel.loc['qm', 'std_dev']):.6e}")

