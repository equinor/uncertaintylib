# -*- coding: utf-8 -*-

"""
Example 3: Uncertainty analysis for mass flow calculation using an orifice meter.

This script:
1. Loads input parameters from a CSV file in the same folder as the script.
2. Defines a mass flow calculation function based on physical equations.
3. Calculates sensitivity coefficients for each input.
4. Runs a Monte Carlo simulation to propagate input uncertainties.
5. Prints distributions and statistics.
6. Compares Monte Carlo results to conventional uncertainty calculations.
7. Plots Monte Carlo results and uncertainty contributions.

Created on Thu Apr 18 13:11:41 2024
@author: CHHAG
"""

import os
import pandas as pd
import numpy as np
import math
from uncertaintylib import uncertainty_functions

# Load input parameters from CSV file in the same folder as the script
csv_path = os.path.join(os.path.dirname(__file__), 'example_03_input.csv')
mc_input = pd.read_csv(csv_path).set_index('input_name').to_dict()

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

# Step 7: Plot Monte Carlo results and uncertainty contributions
from uncertaintylib import plot_functions
import matplotlib.pyplot as plt
plt.close('all')

figure = plot_functions.montecarlo_property_plot_and_table(
    data=mc_res,
    property_id='qm',
    xlim=[-2, 2],
    property_name='Mass flow from orifice',
    property_unit='kg/s',
    round_props={'mean': 1, 'std': 2, 'stdperc': 2}
)

fig2 = plot_functions.plot_uncertainty_contribution(
    res=uncertainty_results,
    property_id='qm'
)
