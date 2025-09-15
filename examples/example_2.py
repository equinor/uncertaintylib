# -*- coding: utf-8 -*-

"""
Example 2: Uncertainty analysis for a simple mass flow calculation.

This script:
1. Loads input parameters from a CSV file in the same folder as the script.
2. Defines a mass flow calculation function.
3. Calculates sensitivity coefficients for each input.
4. Runs a Monte Carlo simulation to propagate input uncertainties.
5. Prints distributions and statistics.
6. Compares Monte Carlo results to conventional uncertainty calculations.

Created on Thu Apr 18 13:11:41 2024
@author: CHHAG
"""


import os
import pandas as pd
import sys
sys.path.append('..')

from uncertaintylib import uncertainty_functions


# Load input parameters from CSV file in the same folder as the script
csv_path = os.path.join(os.path.dirname(__file__), 'example_2_input.csv')
mc_input = pd.read_csv(csv_path).set_index('input_name').to_dict()

def calculate_massflow(input_dict):
    """
    Calculates mass flow from input dictionary containing 'Q' and 'rho'.
    Returns a dictionary with the result.
    """
    
    massflow = input_dict['Q']*input_dict['rho']
    
    output_dict = {'massflow' : massflow}
    
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


