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

"""
Example 09: Compositional Uncertainties and Density Calculation

This example demonstrates:
1. Estimating uncertainties in gas composition using different methods
   - ASTM D1945
   - NORSOK I-106
   - Hagenvik et al. (2024)
2. Propagating compositional uncertainties to gas density using GERG-2008
3. Comparing uncertainty results between different estimation methods

Two gas compositions are analyzed:
- Rich gas (high C2+ content) at 100 bara and 85°C
- Lean gas (high methane content) at 100 bara and 20°C
"""

import pvtlib
from uncertaintylib import uncertainty_functions
from uncertaintylib.uncertainty_models import gas_composition
import pandas as pd


# Define gas compositions (mole percent)
rich_gas_composition = {
    'N2': 0.83,
    'CO2': 1.84,
    'C1': 83.34,
    'C2': 5.62,
    'C3': 1.73,
    'iC4': 0.45,
    'nC4': 2.77,
    'iC5': 1.19,
    'nC5': 1.16,
    'nC6': 0.53,
    'nC7': 0.35,
    'nC8': 0.14,
    'nC9': 0.03,
    'nC10': 0.01
}

lean_gas_composition = {
    'N2': 1.2,
    'CO2': 2.5,
    'C1': 93.8,
    'C2': 2.0,
    'C3': 0.5
}

# Operating conditions
rich_gas_conditions = {
    'pressure': 100.0,  # bara
    'temperature': 85.0  # °C
}

lean_gas_conditions = {
    'pressure': 100.0,  # bara
    'temperature': 20.0  # °C
}


def calculate_density_from_composition(input_dict):
    """
    Calculate gas density using GERG-2008 equation of state.
    
    This function is used by uncertaintylib to calculate density and 
    propagate uncertainties from input parameters.
    
    Parameters
    ----------
    input_dict : dict
        Dictionary containing:
        - Gas composition components (N2, CO2, C1, C2, etc.) in mole percent
        - 'pressure' in bara
        - 'temperature' in °C
    
    Returns
    -------
    dict
        Dictionary with 'rho' key containing mass density in kg/m³
    """
    # Separate composition from P and T
    composition = {key: val for key, val in input_dict.items() 
                   if key not in ['pressure', 'temperature']}
    pressure = input_dict['pressure']
    temperature = input_dict['temperature']
    
    # Initialize GERG-2008 equation of state
    gerg = pvtlib.AGA8('GERG-2008')
    
    # Calculate properties
    properties = gerg.calculate_from_PT(
        composition=composition,
        pressure=pressure,
        temperature=temperature
    )
    
    return {'rho': properties['rho']}


def analyze_composition_uncertainty(composition, conditions, gas_name):
    """
    Analyze compositional uncertainties using different methods and 
    calculate their impact on gas density.
    
    Parameters
    ----------
    composition : dict
        Gas composition in mole percent
    conditions : dict
        Operating conditions (pressure and temperature)
    gas_name : str
        Name of the gas case for reporting
    
    Returns
    -------
    dict
        Results from all three uncertainty estimation methods
    """
    print(f"\n{'='*80}")
    print(f"  {gas_name}")
    print(f"{'='*80}")
    print(f"Conditions: P = {conditions['pressure']} bara, T = {conditions['temperature']} °C")
    print(f"\nComposition (mole %):")
    for comp, value in composition.items():
        print(f"  {comp:>5}: {value:6.2f}")
    
    # Dictionary to store results from different methods
    results = {}
    
    # Method 1: ASTM D1945
    print(f"\n{'-'*80}")
    print("Method 1: ASTM D1945")
    print(f"{'-'*80}")
    
    uncertainty_astm = gas_composition.component_uncertainty_from_ASTM_D1945(composition)
    
    # Combine with P and T (zero uncertainty to isolate compositional effects)
    uncertainty_input_astm = {
        'mean': {**uncertainty_astm['mean'], **conditions},
        'standard_uncertainty': {
            **uncertainty_astm['standard_uncertainty'],
            'pressure': 0.0,
            'temperature': 0.0
        },
        'distribution': {
            **uncertainty_astm['distribution'],
            'pressure': 'normal',
            'temperature': 'normal'
        }
    }
    
    # Calculate uncertainty in density
    density_uncertainty_astm = uncertainty_functions.calculate_uncertainty(
        uncertainty_input_astm,
        calculate_density_from_composition
    )
    
    results['ASTM_D1945'] = {
        'compositional_uncertainty': uncertainty_astm,
        'density_results': density_uncertainty_astm
    }
    
    print(f"Density: {density_uncertainty_astm['value']['rho']:.4f} kg/m³")
    print(f"Expanded uncertainty (k=2): {density_uncertainty_astm['U']['rho']:.6f} kg/m³")
    print(f"Relative uncertainty (k=2): {density_uncertainty_astm['U_perc']['rho']:.4f} %")
    
    # Method 2: NORSOK I-106
    print(f"\n{'-'*80}")
    print("Method 2: NORSOK I-106")
    print(f"{'-'*80}")
    
    uncertainty_norsok = gas_composition.component_uncertainty_from_norsok_I106(composition)
    
    uncertainty_input_norsok = {
        'mean': {**uncertainty_norsok['mean'], **conditions},
        'standard_uncertainty': {
            **uncertainty_norsok['standard_uncertainty'],
            'pressure': 0.0,
            'temperature': 0.0
        },
        'distribution': {
            **uncertainty_norsok['distribution'],
            'pressure': 'normal',
            'temperature': 'normal'
        }
    }
    
    density_uncertainty_norsok = uncertainty_functions.calculate_uncertainty(
        uncertainty_input_norsok,
        calculate_density_from_composition
    )
    
    results['NORSOK_I106'] = {
        'compositional_uncertainty': uncertainty_norsok,
        'density_results': density_uncertainty_norsok
    }
    
    print(f"Density: {density_uncertainty_norsok['value']['rho']:.4f} kg/m³")
    print(f"Expanded uncertainty (k=2): {density_uncertainty_norsok['U']['rho']:.6f} kg/m³")
    print(f"Relative uncertainty (k=2): {density_uncertainty_norsok['U_perc']['rho']:.4f} %")
    
    # Method 3: Hagenvik et al. (2024)
    print(f"\n{'-'*80}")
    print("Method 3: Hagenvik et al. (2024)")
    print(f"{'-'*80}")
    
    uncertainty_hagenvik = gas_composition.component_uncertainty_from_haagenvik2024(
        composition,
        lower_uncertainty_limit=0.001  # 0.001 mol% minimum uncertainty
    )
    
    uncertainty_input_hagenvik = {
        'mean': {**uncertainty_hagenvik['mean'], **conditions},
        'standard_uncertainty': {
            **uncertainty_hagenvik['standard_uncertainty'],
            'pressure': 0.0,
            'temperature': 0.0
        },
        'distribution': {
            **uncertainty_hagenvik['distribution'],
            'pressure': 'normal',
            'temperature': 'normal'
        }
    }
    
    density_uncertainty_hagenvik = uncertainty_functions.calculate_uncertainty(
        uncertainty_input_hagenvik,
        calculate_density_from_composition
    )
    
    results['Hagenvik2024'] = {
        'compositional_uncertainty': uncertainty_hagenvik,
        'density_results': density_uncertainty_hagenvik
    }
    
    print(f"Density: {density_uncertainty_hagenvik['value']['rho']:.4f} kg/m³")
    print(f"Expanded uncertainty (k=2): {density_uncertainty_hagenvik['U']['rho']:.6f} kg/m³")
    print(f"Relative uncertainty (k=2): {density_uncertainty_hagenvik['U_perc']['rho']:.4f} %")
    
    # Summary comparison
    print(f"\n{'-'*80}")
    print("Summary Comparison - Density Uncertainty")
    print(f"{'-'*80}")
    
    comparison_data = {
        'Method': ['ASTM D1945', 'NORSOK I-106', 'Hagenvik et al. (2024)'],
        'Density [kg/m³]': [
            density_uncertainty_astm['value']['rho'],
            density_uncertainty_norsok['value']['rho'],
            density_uncertainty_hagenvik['value']['rho']
        ],
        'U (k=2) [kg/m³]': [
            density_uncertainty_astm['U']['rho'],
            density_uncertainty_norsok['U']['rho'],
            density_uncertainty_hagenvik['U']['rho']
        ],
        'U (k=2) [%]': [
            density_uncertainty_astm['U_perc']['rho'],
            density_uncertainty_norsok['U_perc']['rho'],
            density_uncertainty_hagenvik['U_perc']['rho']
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    print(df_comparison.to_string(index=False))
    
    # Display top uncertainty contributors for Hagenvik method
    print(f"\n{'-'*80}")
    print("Top 5 Contributors to Density Uncertainty (Hagenvik et al. 2024)")
    print(f"{'-'*80}")
    
    contributions = density_uncertainty_hagenvik['contribution']['rho']
    # Filter out pressure and temperature
    comp_contributions = {k: v for k, v in contributions.items() 
                         if k not in ['pressure', 'temperature']}
    sorted_contributions = sorted(comp_contributions.items(), 
                                 key=lambda x: x[1], reverse=True)[:5]
    
    for i, (component, contribution) in enumerate(sorted_contributions, 1):
        print(f"{i}. {component:>5}: {contribution:6.2f} %")
    
    return results


if __name__ == '__main__':
    print("\n" + "="*80)
    print("  Example 09: Compositional Uncertainties and Density Calculation")
    print("="*80)
    print("\nThis example demonstrates the impact of different compositional")
    print("uncertainty estimation methods on calculated gas density.")
    
    # Analyze rich gas
    rich_gas_results = analyze_composition_uncertainty(
        rich_gas_composition,
        rich_gas_conditions,
        "RICH GAS ANALYSIS"
    )
    
    # Analyze lean gas
    lean_gas_results = analyze_composition_uncertainty(
        lean_gas_composition,
        lean_gas_conditions,
        "LEAN GAS ANALYSIS"
    )
    
    print(f"\n{'='*80}")
    print("  Analysis Complete")
    print(f"{'='*80}\n")
