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


def test_norsok_i106_nfogm_reference_case1():
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
    print("="*110)
    print(f"{'Comp':<6} {'Conc':<8} {'Expected':<12} {'Calc':<12} {'Error':<10} {'Status':<8} "
          f"{'Expected':<12} {'Calc':<12} {'Error':<10} {'Status'}")
    print(f"{'':6} {'mol%':<8} {'U(k=2)':<12} {'U(k=2)':<12} {'mol%':<10} {'abs':<8} "
          f"{'U%(k=2)':<12} {'U%(k=2)':<12} {'%':<10} {'rel'}")
    print("-"*110)
    
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
        
        # Calculate absolute errors
        abs_error = abs(calculated_expanded_unc - expected_expanded_unc)
        rel_error = abs(calculated_relative_unc - expected_relative_unc)
        
        # Tolerance: 0.01 mol% for absolute uncertainty, 0.5% for relative uncertainty
        abs_status = "PASS" if abs_error < 0.01 else "FAIL"
        rel_status = "PASS" if rel_error < 0.5 else "FAIL"
        
        if abs_status == "FAIL" or rel_status == "FAIL":
            all_passed = False
        
        print(f"{component:<6} {component_conc:<8.2f} {expected_expanded_unc:<12.4f} "
              f"{calculated_expanded_unc:<12.4f} {abs_error:<10.4f} {abs_status:<8} "
              f"{expected_relative_unc:<12.2f} {calculated_relative_unc:<12.2f} "
              f"{rel_error:<10.2f} {rel_status}")
    
    print("-"*110)
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("="*110)
    
    assert all_passed, "Some component uncertainties did not match NFOGM reference within tolerance"


def test_norsok_i106_nfogm_reference_case2():
    """
    Test NORSOK I-106 method against NFOGM reference data (case 2).
    
    Equal mole percent composition to test mass-based factor determination.
    Composition and expected uncertainties from NFOGM Fiscal Gas 
    Metering Station Uncertainty app. The uncertainties are 
    expanded uncertainties at 95% confidence level (k=2).
    """
    # Test composition (mole percent) - equal mole percentages
    composition = {
        'C1': 25.0,
        'C2': 25.0,
        'C3': 25.0,
        'iC4': 25.0
    }
    
    # Expected expanded uncertainties (k=2) from NFOGM app (mol%)
    expected_expanded_uncertainty = {
        'C1': 0.347,
        'C2': 0.370,
        'C3': 0.252,
        'iC4': 0.191
    }
    
    # Expected relative uncertainties (k=2) from NFOGM app (%)
    expected_relative_uncertainty = {
        'C1': 1.39,
        'C2': 1.48,
        'C3': 1.01,
        'iC4': 0.766
    }
    
    # Calculate uncertainties using NORSOK I-106 method
    result = gas_composition.component_uncertainty_from_norsok_I106(composition)
    
    # Check that composition is normalized to 100%
    total_composition = sum(result['mean'].values())
    assert abs(total_composition - 100.0) < 1e-10, "Composition should be normalized to 100%"
    
    print("\nNORSOK I-106 Test Results (Case 2 - Equal Mole %):")
    print("="*110)
    print(f"{'Comp':<6} {'Conc':<8} {'Expected':<12} {'Calc':<12} {'Error':<10} {'Status':<8} "
          f"{'Expected':<12} {'Calc':<12} {'Error':<10} {'Status'}")
    print(f"{'':6} {'mol%':<8} {'U(k=2)':<12} {'U(k=2)':<12} {'mol%':<10} {'abs':<8} "
          f"{'U%(k=2)':<12} {'U%(k=2)':<12} {'%':<10} {'rel'}")
    print("-"*110)
    
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
        
        # Calculate absolute errors
        abs_error = abs(calculated_expanded_unc - expected_expanded_unc)
        rel_error = abs(calculated_relative_unc - expected_relative_unc)
        
        # Tolerance: 0.01 mol% for absolute uncertainty, 0.5% for relative uncertainty
        abs_status = "PASS" if abs_error < 0.01 else "FAIL"
        rel_status = "PASS" if rel_error < 0.5 else "FAIL"
        
        if abs_status == "FAIL" or rel_status == "FAIL":
            all_passed = False
        
        print(f"{component:<6} {component_conc:<8.2f} {expected_expanded_unc:<12.4f} "
              f"{calculated_expanded_unc:<12.4f} {abs_error:<10.4f} {abs_status:<8} "
              f"{expected_relative_unc:<12.2f} {calculated_relative_unc:<12.2f} "
              f"{rel_error:<10.2f} {rel_status}")
    
    print("-"*110)
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("="*110)
    
    assert all_passed, "Some component uncertainties did not match NFOGM reference within tolerance"


def test_norsok_i106_nfogm_reference_case3():
    """
    Test NORSOK I-106 method against NFOGM reference data (case 3).
    
    Equal 10% mole percent composition across C1-C8 to test mass-based factor 
    determination for heavier components. Composition and expected uncertainties 
    from NFOGM Fiscal Gas Metering Station Uncertainty app. The uncertainties 
    are expanded uncertainties at 95% confidence level (k=2).
    """
    # Test composition (mole percent) - equal 10% for all components
    composition = {
        'C1': 10.0,
        'C2': 10.0,
        'C3': 10.0,
        'iC4': 10.0,
        'nC4': 10.0,
        'iC5': 10.0,
        'nC5': 10.0,
        'nC6': 10.0,
        'nC7': 10.0,
        'nC8': 10.0
    }
    
    # Expected expanded uncertainties (k=2) from NFOGM app (mol%)
    expected_expanded_uncertainty = {
        'C1': 0.609,
        'C2': 0.325,
        'C3': 0.222,
        'iC4': 0.168,
        'nC4': 0.168,
        'iC5': 0.135,
        'nC5': 0.135,
        'nC6': 0.113,
        'nC7': 0.0975,
        'nC8': 0.0855
    }
    
    # Expected relative uncertainties (k=2) from NFOGM app (%)
    expected_relative_uncertainty = {
        'C1': 6.09,
        'C2': 3.25,
        'C3': 2.22,
        'iC4': 1.68,
        'nC4': 1.68,
        'iC5': 1.35,
        'nC5': 1.35,
        'nC6': 1.13,
        'nC7': 0.975,
        'nC8': 0.855
    }
    
    # Calculate uncertainties using NORSOK I-106 method
    result = gas_composition.component_uncertainty_from_norsok_I106(composition)
    
    # Check that composition is normalized to 100%
    total_composition = sum(result['mean'].values())
    assert abs(total_composition - 100.0) < 1e-10, "Composition should be normalized to 100%"
    
    print("\nNORSOK I-106 Test Results (Case 3 - Equal 10% Mole %, C1-C8):")
    print("="*110)
    print(f"{'Comp':<6} {'Conc':<8} {'Expected':<12} {'Calc':<12} {'Error':<10} {'Status':<8} "
          f"{'Expected':<12} {'Calc':<12} {'Error':<10} {'Status'}")
    print(f"{'':6} {'mol%':<8} {'U(k=2)':<12} {'U(k=2)':<12} {'mol%':<10} {'abs':<8} "
          f"{'U%(k=2)':<12} {'U%(k=2)':<12} {'%':<10} {'rel'}")
    print("-"*110)
    
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
        
        # Calculate absolute errors
        abs_error = abs(calculated_expanded_unc - expected_expanded_unc)
        rel_error = abs(calculated_relative_unc - expected_relative_unc)
        
        # Tolerance: 0.01 mol% for absolute uncertainty, 0.5% for relative uncertainty
        abs_status = "PASS" if abs_error < 0.01 else "FAIL"
        rel_status = "PASS" if rel_error < 0.5 else "FAIL"
        
        if abs_status == "FAIL" or rel_status == "FAIL":
            all_passed = False
        
        print(f"{component:<6} {component_conc:<8.2f} {expected_expanded_unc:<12.4f} "
              f"{calculated_expanded_unc:<12.4f} {abs_error:<10.4f} {abs_status:<8} "
              f"{expected_relative_unc:<12.2f} {calculated_relative_unc:<12.2f} "
              f"{rel_error:<10.2f} {rel_status}")
    
    print("-"*110)
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("="*110)
    
    assert all_passed, "Some component uncertainties did not match NFOGM reference within tolerance"


def test_astm_d1945_nfogm_reference_case1():
    """
    Test ASTM D1945 method against NFOGM reference data.
    
    Composition and expected uncertainties tested against NFOGM Fiscal Gas 
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
        'N2': 0.9,
        'CO2': 1.1
    }
    
    # Expected expanded uncertainties (k=2) from NFOGM app (mol%)
    expected_expanded_uncertainty = {
        'C1': 0.15,
        'C2': 0.12,
        'C3': 0.1,
        'iC4': 0.1,
        'nC4': 0.07,
        'iC5': 0.07,
        'nC5': 0.07,
        'N2': 0.07,
        'CO2': 0.1
    }
    
    # Expected relative uncertainties (k=2) from NFOGM app (%)
    expected_relative_uncertainty = {
        'C1': 0.174,
        'C2': 2.0,
        'C3': 3.33,
        'iC4': 9.09,
        'nC4': 7.78,
        'iC5': 20.0,
        'nC5': 20.0,
        'N2': 7.78,
        'CO2': 9.09
    }
    
    # Calculate uncertainties using ASTM D1945 method
    result = gas_composition.component_uncertainty_from_ASTM_D1945(composition)
    
    # Check that composition is normalized to 100%
    total_composition = sum(result['mean'].values())
    assert abs(total_composition - 100.0) < 1e-10, "Composition should be normalized to 100%"
    
    print("\nASTM D1945 Test Results:")
    print("="*110)
    print(f"{'Comp':<6} {'Conc':<8} {'Expected':<12} {'Calc':<12} {'Error':<10} {'Status':<8} "
          f"{'Expected':<12} {'Calc':<12} {'Error':<10} {'Status'}")
    print(f"{'':6} {'mol%':<8} {'U(k=2)':<12} {'U(k=2)':<12} {'mol%':<10} {'abs':<8} "
          f"{'U%(k=2)':<12} {'U%(k=2)':<12} {'%':<10} {'rel'}")
    print("-"*110)
    
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
        
        # Calculate absolute errors
        abs_error = abs(calculated_expanded_unc - expected_expanded_unc)
        rel_error = abs(calculated_relative_unc - expected_relative_unc)
        
        # Tolerance: 0.01 mol% for absolute uncertainty, 0.5% for relative uncertainty
        abs_status = "PASS" if abs_error < 0.01 else "FAIL"
        rel_status = "PASS" if rel_error < 0.5 else "FAIL"
        
        if abs_status == "FAIL" or rel_status == "FAIL":
            all_passed = False
        
        print(f"{component:<6} {component_conc:<8.2f} {expected_expanded_unc:<12.4f} "
              f"{calculated_expanded_unc:<12.4f} {abs_error:<10.4f} {abs_status:<8} "
              f"{expected_relative_unc:<12.2f} {calculated_relative_unc:<12.2f} "
              f"{rel_error:<10.2f} {rel_status}")
    
    print("-"*110)
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("="*110)
    
    assert all_passed, "Some component uncertainties did not match NFOGM reference within tolerance"


def test_astm_d1945_nfogm_reference_case2():
    """
    Test ASTM D1945 method against NFOGM reference data (case 2).
    
    Composition with varying concentrations across different ASTM ranges.
    Composition and expected uncertainties from NFOGM Fiscal Gas 
    Metering Station Uncertainty app. The uncertainties are 
    expanded uncertainties at 95% confidence level (k=2).
    """
    # Test composition (mole percent)
    composition = {
        'C1': 60.0,
        'C2': 20.0,
        'C3': 10.0,
        'iC4': 5.0,
        'nC4': 5.0
    }
    
    # Expected expanded uncertainties (k=2) from NFOGM app (mol%)
    expected_expanded_uncertainty = {
        'C1': 0.15,
        'C2': 0.15,
        'C3': 0.15,
        'iC4': 0.12,
        'nC4': 0.12
    }
    
    # Expected relative uncertainties (k=2) from NFOGM app (%)
    expected_relative_uncertainty = {
        'C1': 0.25,
        'C2': 0.75,
        'C3': 1.5,
        'iC4': 2.4,
        'nC4': 2.4
    }
    
    # Calculate uncertainties using ASTM D1945 method
    result = gas_composition.component_uncertainty_from_ASTM_D1945(composition)
    
    # Check that composition is normalized to 100%
    total_composition = sum(result['mean'].values())
    assert abs(total_composition - 100.0) < 1e-10, "Composition should be normalized to 100%"
    
    print("\nASTM D1945 Test Results (Case 2):")
    print("="*110)
    print(f"{'Comp':<6} {'Conc':<8} {'Expected':<12} {'Calc':<12} {'Error':<10} {'Status':<8} "
          f"{'Expected':<12} {'Calc':<12} {'Error':<10} {'Status'}")
    print(f"{'':6} {'mol%':<8} {'U(k=2)':<12} {'U(k=2)':<12} {'mol%':<10} {'abs':<8} "
          f"{'U%(k=2)':<12} {'U%(k=2)':<12} {'%':<10} {'rel'}")
    print("-"*110)
    
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
        
        # Calculate absolute errors
        abs_error = abs(calculated_expanded_unc - expected_expanded_unc)
        rel_error = abs(calculated_relative_unc - expected_relative_unc)
        
        # Tolerance: 0.01 mol% for absolute uncertainty, 0.5% for relative uncertainty
        abs_status = "PASS" if abs_error < 0.01 else "FAIL"
        rel_status = "PASS" if rel_error < 0.5 else "FAIL"
        
        if abs_status == "FAIL" or rel_status == "FAIL":
            all_passed = False
        
        print(f"{component:<6} {component_conc:<8.2f} {expected_expanded_unc:<12.4f} "
              f"{calculated_expanded_unc:<12.4f} {abs_error:<10.4f} {abs_status:<8} "
              f"{expected_relative_unc:<12.2f} {calculated_relative_unc:<12.2f} "
              f"{rel_error:<10.2f} {rel_status}")
    
    print("-"*110)
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("="*110)
    
    assert all_passed, "Some component uncertainties did not match NFOGM reference within tolerance"


def test_hagenvik2024_reference_case1():
    """
    Test Hagenvik 2024 method against calculated reference data.
    
    This test is based on calculations from the Hagenvik 2024 publication,
    not verified against NFOGM app as this method is not available there.
    The uncertainties are expanded uncertainties at 95% confidence level (k=2).
    """
    # Test composition (mole percent)
    composition = {
        'N2': 1.0,
        'CO2': 2.0,
        'C1': 85.0,
        'C2': 5.0,
        'C3': 3.0,
        'iC4': 1.0,
        'nC4': 1.0,
        'iC5': 0.5,
        'nC5': 0.5,
        'nC6': 1.0
    }
    
    # Expected expanded uncertainties (k=2) from calculation (mol%)
    expected_expanded_uncertainty = {
        'N2': 0.0680,
        'CO2': 0.0371,
        'C1': 0.0000,
        'C2': 0.0678,
        'C3': 0.1451,
        'iC4': 0.0360,
        'nC4': 0.0540,
        'iC5': 0.0245,
        'nC5': 0.0332,
        'nC6': 0.2060
    }
    
    # Expected relative uncertainties (k=2) calculated as (U/concentration)*100
    expected_relative_uncertainty = {
        'N2': 6.80,
        'CO2': 1.855,
        'C1': 0.000,
        'C2': 1.356,
        'C3': 4.837,
        'iC4': 3.60,
        'nC4': 5.40,
        'iC5': 4.90,
        'nC5': 6.64,
        'nC6': 20.60
    }
    
    # Calculate uncertainties using Hagenvik 2024 method
    result = gas_composition.component_uncertainty_from_haagenvik2024(composition)
    
    # Check that composition is normalized to 100%
    total_composition = sum(result['mean'].values())
    assert abs(total_composition - 100.0) < 1e-10, "Composition should be normalized to 100%"
    
    print("\nHagenvik 2024 Test Results:")
    print("="*110)
    print(f"{'Comp':<6} {'Conc':<8} {'Expected':<12} {'Calc':<12} {'Error':<10} {'Status':<8} "
          f"{'Expected':<12} {'Calc':<12} {'Error':<10} {'Status'}")
    print(f"{'':6} {'mol%':<8} {'U(k=2)':<12} {'U(k=2)':<12} {'mol%':<10} {'abs':<8} "
          f"{'U%(k=2)':<12} {'U%(k=2)':<12} {'%':<10} {'rel'}")
    print("-"*110)
    
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
        
        # Calculate absolute errors
        abs_error = abs(calculated_expanded_unc - expected_expanded_unc)
        rel_error = abs(calculated_relative_unc - expected_relative_unc)
        
        # Tolerance: 0.01 mol% for absolute uncertainty, 0.5% for relative uncertainty
        abs_status = "PASS" if abs_error < 0.01 else "FAIL"
        rel_status = "PASS" if rel_error < 0.5 else "FAIL"
        
        if abs_status == "FAIL" or rel_status == "FAIL":
            all_passed = False
        
        print(f"{component:<6} {component_conc:<8.2f} {expected_expanded_unc:<12.4f} "
              f"{calculated_expanded_unc:<12.4f} {abs_error:<10.4f} {abs_status:<8} "
              f"{expected_relative_unc:<12.2f} {calculated_relative_unc:<12.2f} "
              f"{rel_error:<10.2f} {rel_status}")
    
    print("-"*110)
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("="*110)
    
    assert all_passed, "Some component uncertainties did not match reference within tolerance"


def test_hagenvik2024_reference_case2():
    """
    Test Hagenvik 2024 method against calculated reference data (case 2).
    
    This test is based on calculations from the Hagenvik 2024 publication,
    not verified against NFOGM app as this method is not available there.
    The uncertainties are expanded uncertainties at 95% confidence level (k=2).
    """
    # Test composition (mole percent)
    composition = {
        'N2': 3.0,
        'CO2': 4.0,
        'C1': 87.0,
        'C2': 2.0,
        'C3': 1.0,
        'iC4': 1.0,
        'nC4': 1.0,
        'iC5': 0.25,
        'nC5': 0.25,
        'nC6': 0.5
    }
    
    # Expected expanded uncertainties (k=2) from calculation (mol%)
    expected_expanded_uncertainty = {
        'N2': 0.2051,
        'CO2': 0.0530,
        'C1': 0.0000,
        'C2': 0.0756,
        'C3': 0.0500,
        'iC4': 0.0360,
        'nC4': 0.0540,
        'iC5': 0.0188,
        'nC5': 0.0240,
        'nC6': 0.1283
    }
    
    # Expected relative uncertainties (k=2) calculated as (U/concentration)*100
    expected_relative_uncertainty = {
        'N2': 6.837,
        'CO2': 1.325,
        'C1': 0.000,
        'C2': 3.78,
        'C3': 5.00,
        'iC4': 3.60,
        'nC4': 5.40,
        'iC5': 7.52,
        'nC5': 9.60,
        'nC6': 25.66
    }
    
    # Calculate uncertainties using Hagenvik 2024 method
    result = gas_composition.component_uncertainty_from_haagenvik2024(composition)
    
    # Check that composition is normalized to 100%
    total_composition = sum(result['mean'].values())
    assert abs(total_composition - 100.0) < 1e-10, "Composition should be normalized to 100%"
    
    print("\nHagenvik 2024 Test Results (Case 2):")
    print("="*110)
    print(f"{'Comp':<6} {'Conc':<8} {'Expected':<12} {'Calc':<12} {'Error':<10} {'Status':<8} "
          f"{'Expected':<12} {'Calc':<12} {'Error':<10} {'Status'}")
    print(f"{'':6} {'mol%':<8} {'U(k=2)':<12} {'U(k=2)':<12} {'mol%':<10} {'abs':<8} "
          f"{'U%(k=2)':<12} {'U%(k=2)':<12} {'%':<10} {'rel'}")
    print("-"*110)
    
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
        
        # Calculate absolute errors
        abs_error = abs(calculated_expanded_unc - expected_expanded_unc)
        rel_error = abs(calculated_relative_unc - expected_relative_unc)
        
        # Tolerance: 0.01 mol% for absolute uncertainty, 0.5% for relative uncertainty
        abs_status = "PASS" if abs_error < 0.01 else "FAIL"
        rel_status = "PASS" if rel_error < 0.5 else "FAIL"
        
        if abs_status == "FAIL" or rel_status == "FAIL":
            all_passed = False
        
        print(f"{component:<6} {component_conc:<8.2f} {expected_expanded_unc:<12.4f} "
              f"{calculated_expanded_unc:<12.4f} {abs_error:<10.4f} {abs_status:<8} "
              f"{expected_relative_unc:<12.2f} {calculated_relative_unc:<12.2f} "
              f"{rel_error:<10.2f} {rel_status}")
    
    print("-"*110)
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("="*110)
    
    assert all_passed, "Some component uncertainties did not match reference within tolerance"


if __name__ == '__main__':
    test_norsok_i106_nfogm_reference()
    test_norsok_i106_nfogm_reference_case2()
    test_norsok_i106_nfogm_reference_case3()
    test_astm_d1945_nfogm_reference()
    test_astm_d1945_nfogm_reference_case2()
    test_hagenvik2024_reference()
    test_hagenvik2024_reference_case2()
