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
Example 04: Combined standard uncertainty calculation for two cases:

Part 1: Orifice Meter
    - Performs analysis for an orifice meter using hardcoded input uncertainties and sensitivity coefficients.
    - Calculates combined standard uncertainty using the combined_standard_uncertainty function.
    - Compares the result against the conventional calculation from example 03.

Part 2: Ultrasonic Flowmeter (USM)
    - Performs analysis for an ultrasonic flowmeter (USM) with single P&T and GC.
    - Calculates combined standard uncertainty using hardcoded input uncertainties.
    - Compares the result against a reference case from the NFOGM Fiscal Gas Metering Station Uncertainty (GasMet) tool.

Created on Thu May 23 11:14:03 2024
@author: CHHAG
"""

from uncertaintylib import uncertainty_functions

# --- Part 1: Orifice Meter ---
# Input uncertainties and sensitivity coefficients for orifice meter (from example 03)
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

# Calculate combined standard uncertainty (k=1) for orifice meter
U = uncertainty_functions.combined_standard_uncertainty(u, ci)
U_expanded = U * 2
print('Orifice Meter: Based on combined_standard_uncertainty function (k=2)')
print(U_expanded)

# Compare to value from example 03 (conventional calculation)
U_example_3 = 0.5892192204199442
print('\nOrifice Meter: Based on calculate_uncertainty function (example 03)')
print(U_example_3)

# --- Part 2: Ultrasonic Flowmeter (USM) ---
# Input uncertainties for USM with single P&T and GC
u2 = {
      'calb_ref': 0.1,
      'calib_rep': 0.05,
      'calib_dev': 0.145,
      'field_uncertainty': 0.0,
      'pressure': 0.15,
      'temperature': 0.0464,
      'm/Z': 0.216
}

# Calculate combined standard uncertainty (k=2) for USM
U2 = uncertainty_functions.combined_standard_uncertainty(u2) * 2
print('\nUltrasonic Flowmeter (USM): Based on combined_standard_uncertainty function (k=2)')
print(round(U2, 5))
print('Reference from NFOGM Fiscal Gas Metering Station Uncertainty (GasMet) tool: 0.647')
