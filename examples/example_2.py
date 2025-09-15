# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:11:41 2024

@author: CHHAG
"""

import pandas as pd
import sys
sys.path.append('..')

from uncertainty_functions import (
    calculate_sensitivity_coefficients, 
    monte_carlo_simulation, 
    calculate_monte_carlo_statistics, 
    monte_carlo_output_correlations, 
    calculate_uncertainty, 
    compare_monte_carlo_to_conventional_uncertainty_calculation
)

mc_input = pd.read_csv('example_2_input.csv').set_index('input_name').to_dict()

def calculate_massflow(input_dict):
    
    massflow = input_dict['Q']*input_dict['rho']
    
    output_dict = {'massflow' : massflow}
    
    return output_dict

#%% Calculate relative and absolute sensitivity coefficients
sensitivities = calculate_sensitivity_coefficients(mc_input,calculate_massflow)

print('Sensitivity coefficients: ')
print(pd.DataFrame(sensitivities['absolute_sensitivity_coefficients']))

print('\nRelative sensitivity coefficients: ')
print(pd.DataFrame(sensitivities['relative_sensitivity_coefficients']))

#Run Monte Carlo simulation
mc_res = monte_carlo_simulation(mc_input,calculate_massflow, 10000)
mc_stats = calculate_monte_carlo_statistics(mc_res)

print(mc_stats)

#Calculate correlations between Monte Carlo output
mc_correlations = monte_carlo_output_correlations(mc_res, return_as_dataframe=True)


uncertainty_results = calculate_uncertainty(mc_input, calculate_massflow)


comparison = compare_monte_carlo_to_conventional_uncertainty_calculation(
    MC_results=mc_res, 
    uncertainty_results=uncertainty_results
    )

print(comparison)


