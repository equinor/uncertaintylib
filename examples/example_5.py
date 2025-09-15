# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:11:41 2024

@author: CHHAG
"""

import os
import pandas as pd
import numpy as np
import sys
sys.path.append('..')
from uncertaintylib import uncertainty_functions

csv_path = os.path.join(os.path.dirname(__file__), 'example_5_input.csv')
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
    
    #Normalize
    fluid_DF['moleperc'] = 100*fluid_DF['moleperc']/fluid_DF['moleperc'].sum()
    
    #Calculate total molar mass
    MM = np.dot(fluid_DF['moleperc'],fluid_DF['mm'])/fluid_DF['moleperc'].sum()
    
    output_dict = {'MolarMass' : MM}
    
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


