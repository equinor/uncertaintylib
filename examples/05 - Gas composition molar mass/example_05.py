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

# -*- coding: utf-8 -*-

"""
Example 5: Uncertainty analysis for molar mass calculation from gas composition.

This script:
1. Loads input parameters from a CSV file in the same folder as the script.
2. Defines a molar mass calculation function using AGA8 molar masses.
3. Calculates sensitivity coefficients for each input.
4. Runs a Monte Carlo simulation to propagate input uncertainties.
5. Prints distributions and statistics.
6. Compares Monte Carlo results to conventional uncertainty calculations.

Created on Thu Apr 18 13:11:41 2024
@author: CHHAG
"""

import os
import pandas as pd
import numpy as np
from uncertaintylib import uncertainty_functions

# Load input parameters from CSV file in the same folder as the script
csv_path = os.path.join(os.path.dirname(__file__), 'example_05_input.csv')
mc_input = pd.read_csv(csv_path).set_index('input_name').to_dict()

def calculate_massflow(input_dict):
    aga8_mm = {'N2': 28.01351929,
     'CO2': 44.00979996,
     'C1': 16.0428791,
     'C2': 30.0698204,
     'C3': 44.0967598,
     'iC4': 58.12369919,
     'nC4': 58.12369919,
     'iC5': 72.1506424,
     'nC5': 72.1506424,
     'nC6': 86.17758179,
     'nC7': 100.2044983,
     'nC8': 114.2314606,
     'nC9': 128.2584076,
     'nC10': 142.2852936
     }
    fluid_DF = pd.DataFrame({'moleperc' : input_dict, 'mm' : aga8_mm})
    fluid_DF['moleperc'] = 100*fluid_DF['moleperc']/fluid_DF['moleperc'].sum()
    MM = np.dot(fluid_DF['moleperc'],fluid_DF['mm'])/fluid_DF['moleperc'].sum()
    output_dict = {'MolarMass' : MM}
    return output_dict

# Step 1: Calculate sensitivity coefficients for each input
sensitivities = uncertainty_functions.calculate_sensitivity_coefficients(mc_input, calculate_massflow)
print('Sensitivity coefficients: ')
print(pd.DataFrame(sensitivities['absolute_sensitivity_coefficients']))
print('\nRelative sensitivity coefficients: ')
print(pd.DataFrame(sensitivities['relative_sensitivity_coefficients']))

# Step 2: Run Monte Carlo simulation to propagate input uncertainties
mc_res = uncertainty_functions.monte_carlo_simulation(mc_input, calculate_massflow, 10000)
mc_stats = uncertainty_functions.calculate_monte_carlo_statistics(mc_res)

# Step 3: Print Monte Carlo statistics
print(mc_stats)

# Step 4: Calculate correlations between Monte Carlo output variables
mc_correlations = uncertainty_functions.monte_carlo_output_correlations(mc_res, return_as_dataframe=True)

# Step 5: Calculate conventional uncertainty results
uncertainty_results = uncertainty_functions.calculate_uncertainty(mc_input, calculate_massflow)

# Step 6: Compare Monte Carlo results to conventional uncertainty calculation
comparison = uncertainty_functions.compare_monte_carlo_to_conventional_uncertainty_calculation(
    MC_results=mc_res,
    uncertainty_results=uncertainty_results
)
print(comparison)
