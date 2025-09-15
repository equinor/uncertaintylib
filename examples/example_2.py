from uncertaintylib import uncertainty_functions
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:11:41 2024

@author: CHHAG
"""


import os
import pandas as pd
import sys
sys.path.append('..')
import uncertaintylib.uncertainty_functions as uncertainty_functions

from uncertaintylib import uncertainty_functions

csv_path = os.path.join(os.path.dirname(__file__), 'example_2_input.csv')
mc_input = pd.read_csv(csv_path).set_index('input_name').to_dict()

def calculate_massflow(input_dict):
    
    massflow = input_dict['Q']*input_dict['rho']
    
    output_dict = {'massflow' : massflow}
    
    return output_dict

#%% Calculate relative and absolute sensitivity coefficients
sensitivities = uncertainty_functions.calculate_sensitivity_coefficients(mc_input,calculate_massflow)

print('Sensitivity coefficients: ')
print(pd.DataFrame(sensitivities['absolute_sensitivity_coefficients']))

print('\nRelative sensitivity coefficients: ')
print(pd.DataFrame(sensitivities['relative_sensitivity_coefficients']))

#Run Monte Carlo simulation
mc_res = uncertainty_functions.monte_carlo_simulation(mc_input,calculate_massflow, 10000)
mc_stats = uncertainty_functions.calculate_monte_carlo_statistics(mc_res)

print(mc_stats)

#Calculate correlations between Monte Carlo output
mc_correlations = uncertainty_functions.monte_carlo_output_correlations(mc_res, return_as_dataframe=True)

uncertainty_results = uncertainty_functions.calculate_uncertainty(mc_input, calculate_massflow)

comparison = uncertainty_functions.compare_monte_carlo_to_conventional_uncertainty_calculation(
    MC_results=mc_res, 
    uncertainty_results=uncertainty_results
    )

print(comparison)


