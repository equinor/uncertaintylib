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

Example of input data format. Some of the inputs are only used in Monte Carlo. 
    data = {
        "mean": {
            "L": 2.0,
            "W": 2.0,
            "D": 2.0
        },
        "standard_uncertainty": {
            "L": 0.3,
            "W": 0.1,
            "D": 0.2
        },
        # "standard_uncertainty_percent": {
        #     "L": np.nan,
        #     "W": np.nan,
        #     "D": np.nan
        # },
        # "distribution": {
        #     "L": "normal",
        #     "W": "normal",
        #     "D": "normal"
        # },
        # "min": {
        #     "L": np.nan,
        #     "W": np.nan,
        #     "D": np.nan
        # },
        # "max": {
        #     "L": np.nan,
        #     "W": np.nan,
        #     "D": np.nan
        # }
    }

"""

from uncertaintylib import uncertainty_functions
import numpy as np


def _calculate_volume(inputs):
    outputs = {}
    outputs['volume'] = inputs['L']*inputs['W']*inputs['D']
    outputs['area'] = inputs['L']*inputs['W']

    return outputs

def test_calculate_uncertainty_01():
    # Test case where standard uncertainties are given
    data = {
        "mean": {
            "L": 2.0,
            "W": 2.0,
            "D": 2.0
        },
        "standard_uncertainty": {
            "L": 0.3,
            "W": 0.1,
            "D": 0.2
        }
    }

    # Calculate the uncertainty
    result = uncertainty_functions.calculate_uncertainty(data,_calculate_volume)

    assert round(result['u']['volume'],4) == 1.4967, 'Error in volume standard uncertainty'
    assert round(result['U_perc']['volume'],2) == 37.42, 'Error in volume relative expanded standard uncertainty'
    assert round(result['u']['area'],4) == 0.6325, 'Error in area standard uncertainty'
    assert round(result['U_perc']['area'],2) == 31.62, 'Error in area relative expanded standard uncertainty'


def test_calculate_uncertainty_02():
    # Test case where standard uncertainties are given as a percentage
    data = {
        "mean": {
            "L": 2.0,
            "W": 2.0,
            "D": 2.0
        },
        "standard_uncertainty": {
            "L": np.nan,
            "W": np.nan,
            "D": np.nan
        },
        "standard_uncertainty_percent": {
            "L": 15,
            "W": 5,
            "D": 10
        },
    }

    # Calculate the uncertainty
    result = uncertainty_functions.calculate_uncertainty(data,_calculate_volume)

    assert round(result['u']['volume'],4) == 1.4967, 'Error in volume standard uncertainty'
    assert round(result['U_perc']['volume'],2) == 37.42, 'Error in volume relative expanded standard uncertainty'
    assert round(result['u']['area'],4) == 0.6325, 'Error in area standard uncertainty'
    assert round(result['U_perc']['area'],2) == 31.62, 'Error in area relative expanded standard uncertainty'


def test_calculate_uncertainty_03():
    # Test case where both standard uncertainties and standard uncertainties as a percentage, in which the code will use the larger of the two
    data = {
        "mean": {
            "L": 2.0,
            "W": 2.0,
            "D": 2.0
        },
        "standard_uncertainty": {
            "L": 0.3,
            "W": 0.001,
            "D": 0.2
        },
        "standard_uncertainty_percent": {
            "L": 1,
            "W": 5,
            "D": 10
        },
    }

    # Calculate the uncertainty
    result = uncertainty_functions.calculate_uncertainty(data,_calculate_volume)

    assert round(result['u']['volume'],4) == 1.4967, 'Error in volume standard uncertainty'
    assert round(result['U_perc']['volume'],2) == 37.42, 'Error in volume relative expanded standard uncertainty'
    assert round(result['u']['area'],4) == 0.6325, 'Error in area standard uncertainty'
    assert round(result['U_perc']['area'],2) == 31.62, 'Error in area relative expanded standard uncertainty'


def _orifice_calculation(inputs):
    # Used for testing uncertainty calculation for orifice against data from NGOFM uncertainty app    
    from pvtlib.metering.differential_pressure_flowmeters import _calculate_flow_DP_meter

    outputs = _calculate_flow_DP_meter(
        C=inputs['C'],
        D=inputs['D'],
        d=inputs['d'],
        epsilon= inputs['epsilon'],
        dP=inputs['dP'],
        rho1=inputs['rho'],        
        )

    return outputs


def test_calculate_uncertainty_04():
    # Test case for orifice calculation with standard uncertainties
    # The case is retrieved from the NFOGM gasmetapp uncertainty web application https://gasmetapp.web.norce.cloud/flowmeas (2025)
    # Uses the default setup with single meter, orifice, single pressure and temperature, single densitometer (has temperature). Using default values and input uncertainties. 
    
    data = {
        "mean": {
            "C": 0.6021,
            "D": 0.3,
            "d": 0.15,
            "epsilon": 0.9993,
            "dP": 249.5,
            "rho": 86.376
        },
        "standard_uncertainty": {
            "C": 0.00151,
            "D": 0.0006,
            "d": 0.0000525,
            "epsilon": 0.0000309783,
            "dP": 0.075,
            "rho": 0.13
        }
    }

    # Calculate the uncertainty
    result = uncertainty_functions.calculate_uncertainty(data,_orifice_calculation)

    # The value given by the NFOGM gasmetapp is 0.546%. Assert the test results with 2 decimals
    assert round(result['U_perc']['MassFlow'],2) == 0.55, 'Error in orifice mass flow rate standard uncertainty'


def _usm_metering_station(inputs):
    """
    Calculates gas properties and mass flowrate for a USM (Ultrasonic Flow Meter) 
    based on input gas composition (GC), pressure, temperature, and volumetric flowrate (USM).
    Parameters:
        inputs (dict): Dictionary containing gas composition fractions (N2, CO2, C1, C2, C3, iC4, nC4, iC5, nC5, C6),
                       pressure in bara ('pressure_bara'), temperature in Celsius ('temperature_C'),
                       and volumetric flowrate ('Qv').
    Returns:
        dict: Dictionary with calculated gas density ('rho'), molecular weight over compressibility ('m/Z'),
              and mass flowrate ('Qm').
    """

    outputs = {}

    if not hasattr(_usm_metering_station, "_cached_data"):
        
        # Only run once, as it is time consuming
        import pvtlib
        gerg = pvtlib.AGA8('GERG-2008')

        _usm_metering_station._cached_data = gerg

    gerg = _usm_metering_station._cached_data

    # Set up composition
    composition = {
        'N2' : inputs['N2'],
        'CO2' : inputs['CO2'],
        'C1' : inputs['C1'],
        'C2' : inputs['C2'],
        'C3' : inputs['C3'],
        'iC4' : inputs['iC4'],
        'nC4' : inputs['nC4'],
        'iC5' : inputs['iC5'],
        'nC5' : inputs['nC5'],
        'C6' : inputs['C6'],
    }

    # Calculate gas properties
    gas_properties = gerg.calculate_from_PT(
        composition=composition,
        pressure=inputs['pressure_bara'],
        temperature=inputs['temperature_C'],
    )

    # Get selected gas properties
    outputs['rho'] = gas_properties['rho']
    outputs['m/Z'] = gas_properties['mm']/gas_properties['z']

    # Calculate mass flowrate from ultrasonic flowmeter
    outputs['Qm'] = outputs['rho'] * inputs['Qv'] # kg/h

    return outputs

def test_calculate_uncertainty_05():
    '''
    Calculates relative expanded uncertainty in mass flow rate calculated from an ultrasonic flowmeter, composition from a GC and pressure and temperature measurements

    The test is based on example from NFOGM GasMet app (https://gasmetapp.web.norce.cloud/)
    using a single ultrasonic flowmeter with online GC, single P&T.
    Compositional uncertainties are set to NORSOK I-106
    '''

    # Define input data for uncertainty analysis
    data = {
        "mean": {
            "pressure_bara": 100.0,
            "temperature_C": 50.0,
            "N2": 1.0,
            "CO2": 1.0,
            "C1": 86.3,
            "C2": 6.01,
            "C3": 3.0,
            "iC4": 1.1,
            "nC4": 0.9,
            "iC5": 0.35,
            "nC5": 0.25,
            "C6": 0.1,
            "Qv": 1000.0
        },
        "standard_uncertainty": {
            "pressure_bara": np.nan,
            "temperature_C": np.nan,
            "N2": 0.066/2,
            "CO2": 0.104/2,
            "C1": 0.725/2,
            "C2": 0.0967/2,
            "C3": 0.0659/2,
            "iC4": 0.05/2,
            "nC4": 0.05/2,
            "iC5": 0.0403/2,
            "nC5": 0.0403/2,
            "C6": 0.0,
            'Qv': np.nan
        },
        "standard_uncertainty_percent": {
            "pressure_bara": 0.15,
            "temperature_C": 0.0464,
            "N2": np.nan,
            "CO2": np.nan,
            "C1": np.nan,
            "C2": np.nan,
            "C3": np.nan,
            "iC4": np.nan,
            "nC4": np.nan,
            "iC5": np.nan,
            "nC5": np.nan,
            "C6": np.nan,
            "Qv": 0.2  # Volume flowrate is given as a relative uncertainty
        }
    }

    # Define uncertainties for ultrasonic flowmeter, including sensitivity coefficients
    u = {
        'Calib. Reference' : 0.2/2, #%
        'Calib. Repeatability' : 0.1/2, #%
        'Calib. Deviation' : 0.289/2, #% 
    }

    # Calculate combined standard uncertainty for volume flowrate (sensitivity coefficients are not provided, using default value of 1 on all of them)
    data['standard_uncertainty_percent']['Qv'] = uncertainty_functions.combined_standard_uncertainty(u)

    # Calculate the uncertainty using standard method
    result = uncertainty_functions.calculate_uncertainty(data,_usm_metering_station)

    # Calculate the uncertainty using the Monte Carlo method
    mc_result = uncertainty_functions.monte_carlo_simulation(data, _usm_metering_station, 5000)
    mc_stats = uncertainty_functions.calculate_monte_carlo_statistics(mc_result) # Retrieve mean, standard deviations etc from the output distributions

    # Compare Monte Carlo results to conventional uncertainty results
    comparison = uncertainty_functions.compare_monte_carlo_to_conventional_uncertainty_calculation(
        uncertainty_results=result,
        MC_results=mc_result,
    )

    # Print comparison results
    if True:
        print(comparison)

    # Target uncertainties from NFOGM GasMetApp
    target_uncertainties = {
        'rho' : 0.534,
        'm/Z' : 0.432,
        'Qm' : 0.647
    }

    CRITERIA = 0.02

    for key in target_uncertainties.keys():
        # Check that both "Conventional U [%], k=2" and "Monte Carlo U [%], k=2" are within +-CRITERIA % of target
        conventional = comparison['Conventional U [%], k=2'][key]
        monte_carlo = comparison['Monte Carlo U [%], k=2'][key]
        target = target_uncertainties[key]

        assert target - CRITERIA <= conventional <= target + CRITERIA, f"Conventional uncertainty for {key} is out of bounds: {conventional}"
        assert target - CRITERIA <= monte_carlo <= target + CRITERIA, f"Monte Carlo uncertainty for {key} is out of bounds: {monte_carlo}"

