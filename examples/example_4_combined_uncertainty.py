# -*- coding: utf-8 -*-

"""
Example 4: Combined standard uncertainty calculation for orifice meter and USM.

This script:
1. Demonstrates calculation of combined standard uncertainty using hardcoded input values.
2. Compares results from the combined_standard_uncertainty function and conventional calculation.
3. Shows results for two different sets of uncertainty inputs.

Created on Thu May 23 11:14:03 2024
@author: CHHAG
"""

from uncertaintylib import uncertainty_functions

# Input uncertainties and sensitivity coefficients for orifice meter (from example 3)
u = {
      'C': 0.25,
      'epsilon': 0.00311,
      'D': 0.2,
      'd': 0.035,
      'deltaP': 0.03,
      'P': 0.15,
      'm/Z': 0.216,
      'T': 0.0464
}

ci = {
      'C': 1.0000000000000107,
      'epsilon': 1.0000000000000087,
      'D': -0.12981231163619467,
      'd': 2.1483481065099674,
      'deltaP': 0.4987562112088981,
      'P': 0.4987562112089,
      'm/Z': 0.49875621120889957,
      'T': -0.4962809790010803
}



# Step 1: Calculate combined standard uncertainty (k=1)
U = uncertainty_functions.combined_standard_uncertainty(u, ci)
U_expanded = U * 2
print('Based on combined_standard_uncertainty function')
print(U_expanded)

# Step 2: Compare to value from example 3 (conventional calculation)
U_example_3 = 0.5892192204199442
print('\nBased on calculate_uncertainty function')
print(U_example_3)




# Step 3: Calculate combined uncertainty for USM with single P&T and GC
u2 = {
      'calb_ref': 0.1,
      'calib_rep': 0.05,
      'calib_dev': 0.145,
      'field_uncertainty': 0.0,
      'pressure': 0.15,
      'temperature': 0.0464,
      'm/Z': 0.216
}
U2 = uncertainty_functions.combined_standard_uncertainty(u2) * 2
print('\nGasmet NFOGM tool, USM with single P&T and GC:')
print(round(U2, 5))
print('From NFOGM tool: 0.647')

