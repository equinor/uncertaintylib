# -*- coding: utf-8 -*-

"""
Example 1: Demonstrates uncertainty analysis using sensitivity coefficients and Monte Carlo simulation.

This script:
1. Loads input parameters from a CSV file in the same folder as the script.
2. Defines a simple function with multiple outputs.
3. Calculates sensitivity coefficients for each input.
4. Runs a Monte Carlo simulation to propagate input uncertainties.
5. Plots distributions of input and output values.
6. Compares Monte Carlo results to conventional uncertainty calculations.

Created on Thu Apr 18 13:11:41 2024
@author: CHHAG
"""


import os
import pandas as pd
from uncertaintylib import uncertainty_functions


# Load input parameters from CSV file in the same folder as the script
csv_path = os.path.join(os.path.dirname(__file__), 'example_1_input.csv')
mc_input = pd.read_csv(csv_path).set_index('input_name').to_dict()

def my_function(input_dict):
    """
    Example calculation function for uncertainty propagation.

    This function illustrates:
    - How two inputs (x and y) can be used in the calculation of several outputs (a, b, c, d).
    - How a function input can be a fixed setting (setting_A), which is not varied in uncertainty analysis.

    In the input CSV (examples/example_1_input.csv), a setting is handled by setting its distribution to 'none'.
    This means the code will not calculate sensitivity coefficients for that particular input value, treating it as a constant.

    Args:
        input_dict (dict): Dictionary of input values.

    Returns:
        dict: Dictionary of output values.
    """
    x = input_dict['x']
    y = input_dict['y']
    setting_A = input_dict['setting_A']
    
        
    a = x + y
    b = y - x
    c = x * y
    
    if setting_A==0:
        d = y / x
    else:
        d = y / (x+1)
    
    if setting_A%1!=0:
        raise Exception('Some exception')
    
    output_dict = {'a': a, 'b': b, 'c': c, 'd': d, 'x_used' : x, 'y_used' : y, 'setting_A_used' : setting_A}
    
    return output_dict


# Step 1: Calculate sensitivity coefficients for each input
sensitivities = uncertainty_functions.calculate_sensitivity_coefficients(mc_input, my_function)
print('Sensitivity coefficients: ')
print(pd.DataFrame(sensitivities['absolute_sensitivity_coefficients']))
print('\nRelative sensitivity coefficients: ')
print(pd.DataFrame(sensitivities['relative_sensitivity_coefficients']))

# Step 2: Run Monte Carlo simulation to propagate input uncertainties
mc_res = uncertainty_functions.monte_carlo_simulation(mc_input, my_function, 10000)
mc_stats = uncertainty_functions.calculate_monte_carlo_statistics(mc_res)

# Step 3: Plot distributions of input and output values
import matplotlib.pyplot as plt
plt.close('all')
plt.hist(mc_res['x_used'], bins=50)
plt.xlabel('Distribution of "x" input value used in Monte Carlo')
plt.ylabel('Count')

plt.figure()
plt.hist(mc_res['a'], bins=50)
plt.xlabel('Distribution of result value "a" from Monte Carlo')
plt.ylabel('Count')

# Step 4: Print Monte Carlo statistics
print(mc_stats)

# Step 5: Calculate correlations between Monte Carlo output variables
mc_correlations = uncertainty_functions.monte_carlo_output_correlations(mc_res, return_as_dataframe=True)

# Step 6: Calculate conventional uncertainty results
uncertainty_results = uncertainty_functions.calculate_uncertainty(mc_input, my_function)

# Step 7: Compare Monte Carlo results to conventional uncertainty calculation
comparison = uncertainty_functions.compare_monte_carlo_to_conventional_uncertainty_calculation(
    MC_results=mc_res,
    uncertainty_results=uncertainty_results
)
print(comparison)
