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

import sys
import os

from uncertaintylib.uncertainty_models import gas_composition


def test_norsok_i106_nfogm_reference():
    """
    Test NORSOK I-106 method against NFOGM reference data.
    
    Composition and expected uncertainties from NFOGM Fiscal Gas 
    Metering Station Uncertainty app. The uncertainties are 
    expanded uncertainties at 95% confidence level (k=2).
    """
    # Test composition (mole percent)
    composition = {
        'C1': 86.3,
        'C2': 6.01,
        'C3': 3.0,
        'iC4': 1.1,
        'nC4': 0.9,
        'iC5': 0.35,
        'nC5': 0.35,
        'N2': 1.0,
        'CO2': 1.0
    }
    
    # Expected expanded uncertainties (k=2) from NFOGM app (mol%)
    expected_expanded_uncertainty = {
        'C1': 0.724,
        'C2': 0.0966,
        'C3': 0.0659,
        'iC4': 0.05,
        'nC4': 0.05,
        'iC5': 0.0403,
        'nC5': 0.0403,
        'N2': 0.104,
        'CO2': 0.066
    }
    
    # Expected relative uncertainties (k=2) from NFOGM app (%)
    expected_relative_uncertainty = {
        'C1': 0.839,
        'C2': 1.61,
        'C3': 2.2,
        'iC4': 4.54,
        'nC4': 5.55,
        'iC5': 11.5,
        'nC5': 11.5,
        'N2': 10.4,
        'CO2': 6.6
    }
    
    # Calculate uncertainties using NORSOK I-106 method
    result = gas_composition.component_uncertainty_from_norsok_I106(composition)
    
    # Check that composition is normalized to 100%
    total_composition = sum(result['mean'].values())
    assert abs(total_composition - 100.0) < 1e-10, "Composition should be normalized to 100%"
    
    print("\nNORSOK I-106 Test Results:")
    print("="*100)
    print(f"{'Comp':<6} {'Conc':<8} {'Expected':<12} {'Calc':<12} {'Err%':<8} {'Status':<8} "
          f"{'Expected':<12} {'Calc':<12} {'Err%':<8} {'Status'}")
    print(f"{'':6} {'mol%':<8} {'U(k=2)':<12} {'U(k=2)':<12} {'abs':<8} {'abs':<8} "
          f"{'U%(k=2)':<12} {'U%(k=2)':<12} {'rel':<8} {'rel'}")
    print("-"*100)
    
    # Check each component's expanded uncertainty (k=2) - both absolute and relative
    all_passed = True
    for component in expected_expanded_uncertainty.keys():
        calculated_standard_unc = result['standard_uncertainty'][component]
        calculated_expanded_unc = calculated_standard_unc * 2  # Convert k=1 to k=2
        expected_expanded_unc = expected_expanded_uncertainty[component]
        
        # Calculate relative uncertainties (as percentage of concentration)
        component_conc = result['mean'][component]
        if component_conc > 0:
            calculated_relative_unc = (calculated_expanded_unc / component_conc) * 100
        else:
            calculated_relative_unc = 0.0
        expected_relative_unc = expected_relative_uncertainty[component]
        
        # Calculate errors for absolute uncertainty
        if expected_expanded_unc == 0.0:
            abs_error = 0.0 if abs(calculated_expanded_unc) < 1e-4 else float('inf')
            abs_status = "PASS" if abs(calculated_expanded_unc) < 1e-4 else "FAIL"
        else:
            abs_error = abs(calculated_expanded_unc - expected_expanded_unc) / expected_expanded_unc
            # Allow 5% relative tolerance due to rounding in NFOGM app
            abs_status = "PASS" if abs_error < 0.05 else "FAIL"
        
        # Calculate errors for relative uncertainty
        if expected_relative_unc == 0.0:
            rel_error = 0.0 if abs(calculated_relative_unc) < 1e-4 else float('inf')
            rel_status = "PASS" if abs(calculated_relative_unc) < 1e-4 else "FAIL"
        else:
            rel_error = abs(calculated_relative_unc - expected_relative_unc) / expected_relative_unc
            # Allow 5% relative tolerance
            rel_status = "PASS" if rel_error < 0.05 else "FAIL"
        
        if abs_status == "FAIL" or rel_status == "FAIL":
            all_passed = False
        
        print(f"{component:<6} {component_conc:<8.2f} {expected_expanded_unc:<12.4f} "
              f"{calculated_expanded_unc:<12.4f} {abs_error*100:<8.2f} {abs_status:<8} "
              f"{expected_relative_unc:<12.2f} {calculated_relative_unc:<12.2f} "
              f"{rel_error*100:<8.2f} {rel_status}")
    
    print("-"*100)
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("="*100)
    
    assert all_passed, "Some component uncertainties did not match NFOGM reference within tolerance"


if __name__ == '__main__':
    test_norsok_i106_nfogm_reference()
