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


