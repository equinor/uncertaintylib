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
Example 3: Uncertainty analysis for mass flow calculation using an orifice meter.

This script:
1. Loads input parameters from a CSV file in the same folder as the script.
2. Defines a mass flow calculation function based on physical equations.
3. Calculates sensitivity coefficients for each input.
4. Runs a Monte Carlo simulation to propagate input uncertainties.
5. Prints distributions and statistics.
6. Compares Monte Carlo results to conventional uncertainty calculations.
7. Plots Monte Carlo results and uncertainty contributions.

Units: C and epsilon [-], D and d [mm], deltaP [mbar], P [bara], m/Z [kg/mol],
T [K], R = 8.314 J/(mol K). Output qm [kg/s].

Source of m/Z = 0.021019 kg/mol: molar mass M = 18.125 g/mol and Z = 0.86232
calculated with pvtlib 1.16.1, AGA8 GERG-2008, at P = 100 bara and T = 323.15 K,
for the dry natural gas composition in pvtlib example "01 Gas Properties from AGA8"
(mol%: N2 1.0, CO2 1.0, C1 90.0, C2 5.0, C3 2.0, iC4 0.5, nC4 0.5).
The relative standard uncertainty of m/Z (0.216 %) is unchanged.

Source of C = 0.60282 and epsilon = 0.99935: pvtlib 1.16.1, ISO 5167-2:2022,
orifice plate with corner tappings (pvtlib default), D = 300 mm, d = 150 mm
(beta = 0.5), deltaP = 250.2 mbar, P = 100 bara, same gas and state as above.
- epsilon: calculate_expansibility_orifice with isentropic exponent
  kappa = 1.4236 from AGA8 GERG-2008.
- C: Reader-Harris/Gallagher equation, solved iteratively with the Reynolds
  number in calculate_flow_orifice (Re_D = 6.37e6). Density 78.230 kg/m3 from
  GERG-2008, viscosity 1.450e-5 Pa s from pvtlib natural_gas_viscosity_Lee_et_al
  (Lee, Gonzalez and Eakin, 1966). C changes by about 0.01 % for a +/-20 %
  change in viscosity.
The relative standard uncertainties of C (0.25 %, equal to the ISO 5167-2 value
of 0.5 % at k=2 for 0.2 <= beta <= 0.6) and epsilon (0.00311 %) are unchanged.

Created on Thu Apr 18 13:11:41 2024
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
