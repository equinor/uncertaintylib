# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:11:41 2024

@author: CHHAG
"""


import os
import pandas as pd
import sys
sys.path.append('..')
from uncertaintylib import uncertainty_functions

csv_path = os.path.join(os.path.dirname(__file__), 'example_1_input.csv')
mc_input = pd.read_csv(csv_path).set_index('input_name').to_dict()

def my_function(input_dict):
    x = input_dict['x']
    y = input_dict['y']
    setting_A = input_dict['setting_A']
    
        
    a = x + y
    b = y - x
    c = x * y
    
    setting_A = 0
    
    if setting_A==0:
        d = y / x
    else:
        d = y / (x+1)
    
    if setting_A%1!=0:
        raise Exception('Some exception')
    
    output_dict = {'a': a, 'b': b, 'c': c, 'd': d, 'x_used' : x, 'y_used' : y, 'setting_A_used' : setting_A}
    
    return output_dict

#%% Calculate relative and absolute sensitivity coefficients
sensitivities = uncertainty_functions.calculate_sensitivity_coefficients(mc_input,my_function)

print('Sensitivity coefficients: ')
print(pd.DataFrame(sensitivities['absolute_sensitivity_coefficients']))

print('\nRelative sensitivity coefficients: ')
print(pd.DataFrame(sensitivities['relative_sensitivity_coefficients']))

#Run Monte Carlo simulation
mc_res = uncertainty_functions.monte_carlo_simulation(mc_input,my_function, 10000)
mc_stats = uncertainty_functions.calculate_monte_carlo_statistics(mc_res)

import matplotlib.pyplot as plt
plt.close('all')
plt.hist(mc_res['x_used'],bins=50)
plt.xlabel('Distribution of "x" input value used in Monte Carlo')
plt.ylabel('Count')

plt.figure()
plt.hist(mc_res['a'],bins=50)
plt.xlabel('Distribution of result value "a" from Monte Carlo')
plt.ylabel('Count')

print(mc_stats)

#Calculate correlations between Monte Carlo output
mc_correlations = uncertainty_functions.monte_carlo_output_correlations(mc_res, return_as_dataframe=True)

uncertainty_results = uncertainty_functions.calculate_uncertainty(mc_input, my_function)

comparison = uncertainty_functions.compare_monte_carlo_to_conventional_uncertainty_calculation(
    MC_results=mc_res, 
    uncertainty_results=uncertainty_results
    )

print(comparison)
