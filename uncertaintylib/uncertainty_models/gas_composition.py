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
Uncertainty estimation models for gas composition measurements by gas chromatography.

This module provides functions to estimate uncertainties in gas composition
based on various methods from standards, scientific papers, and empirical
relationships.
"""

def component_uncertainty_from_ASTM_D1945(gas_dict_input):
    #Calculate component uncertainty according to ASTM D1945 "Reproducibility" (chapter 10.1.2).
    #This uses same interpretation as NFOGM gasmet uncertainty tool (https://gasmetapp.web.norce.cloud/). 
    #It assumes the value is 95 % confidence level and given in absolute terms (i.e. mol%)
    
    allowed_components = ['N2', 'CO2', 'C1', 'C2', 'C3', 'iC4', 'nC4', 'iC5', 'nC5', 'nC6', 'nC7', 'nC8', 'nC9', 'nC10']
    
    gas_dict = {key : val for key,val in gas_dict_input.items() if key in allowed_components}
    
    res = {}
    u = {}
    
    for comp in gas_dict:
        moleperc = gas_dict[comp]
        
        if moleperc < 0.1:
            U = 0.02
        elif moleperc < 1.0:
            U = 0.07
        elif moleperc < 5.0:
            U = 0.10
        elif moleperc < 10.0:
            U = 0.12
        else:
            U = 0.15
    
        u[comp] = U/2
        
    res['mean'] = {key : val for key,val in gas_dict.items()}
    res['standard_uncertainty'] = u
    res['min'] = {key : 0.0 for key in gas_dict}
    res['max'] = {key : 100.0 for key in gas_dict}
    res['distribution'] = {key : 'normal' for key in gas_dict}
        
    return res


def component_uncertainty_from_norsok_I106(gas_dict):

    allowed_components = ['N2', 'CO2', 'C1', 'C2', 'C3', 'iC4', 'nC4', 'iC5', 'nC5', 'nC6', 'nC7', 'nC8', 'nC9', 'nC10']

    res = {}
    
    average_molar_mass = sum([gas_dict[comp]['moleperc'] * gas_dict[comp]['MW'] for comp in gas_dict]) / sum([gas_dict[comp]['moleperc'] for comp in gas_dict])
    
    u = {}
    
    for comp in gas_dict:
        Mi = gas_dict[comp]['MW']
        
        if gas_dict[comp]['moleperc']<20:
            factor = 0.15
        elif gas_dict[comp]['moleperc']<50:
            factor = 0.3
        else:
            factor = 0.6
        
        Uxi = factor*average_molar_mass/Mi
    
        u[comp] = Uxi/2
        
    res['mean'] = {key : val['moleperc'] for key,val in gas_dict.items()}
    res['standard_uncertainty'] = u
    res['min'] = {key : 0.0 for key in gas_dict}
    res['max'] = {key : 100.0 for key in gas_dict}
    res['distribution'] = {key : 'normal' for key in gas_dict}
    
    return res


def component_uncertainty_from_haagenvik2024(gas_dict_input, lower_uncertainty_limit=None):
    '''
    Based on method described in paper Exploring the Relationship between Speed of Sound, Density and Isentropic Exponent (Hagaenvik et al., 2024)
    https://nfogm.no/wp-content/uploads/2025/08/1-Single-Phase-1-Exploring-the-Relationship-between-Speed-of-Sound-Density-and-Isentropic-Exponent-Christian-Hagenvik_Equinor.pdf

    This method should only be applied for gas compositions with significant content of methane (>60 mol%)
    '''    
    
    #TODO TODO: implement allowed components
    allowed_components = ['N2', 'CO2', 'C1', 'C2', 'C3', 'iC4', 'nC4', 'iC5', 'nC5', 'nC6', 'nC7', 'nC8', 'nC9', 'nC10']
    
    gas_dict = {key : val for key,val in gas_dict_input.items() if key in allowed_components}
    
    res = {}
    u = {}
    
    #Power regressions based on K-lab sample parallel test
    power_models = {'C2': {'power_a': 0.04091428801120496, 'power_b': -0.1182080701200473},
     'C3': {'power_a': 0.024688223069947505, 'power_b': 0.9704611942408041},
     'C6': {'power_a': 0.10298556404738195, 'power_b': 0.6828380441670838},
     'CO2': {'power_a': 0.013364503829208868, 'power_b': 0.5141391394943381},
     'N2': {'power_a': 0.034440251394188715, 'power_b': 1.0046922246848706},
     'iC4': {'power_a': 0.017659329050531938, 'power_b': 0.6349129977823975},
     'iC5': {'power_a': 0.01637327039238961, 'power_b': 0.3827312747755224},
     'nC4': {'power_a': 0.02655802473313954, 'power_b': 0.7930216437166208},
     'nC5': {'power_a': 0.02294449038272855, 'power_b': 0.46972041893882455}}
    
    for comp in gas_dict:
        moleperc = gas_dict[comp]
        
        if moleperc == 0:
            u[comp] = 0.0

        elif comp in ['C1']: #['N2', 'CO2', 'C1', 'C2', 'C3', 'iC4', 'nC4', 'iC5', 'nC5']:
            #Uncertainty of methane is set to 0 %. 
            # This is to take into account the normalization effect, which means that the uncertainty of methane
            # which is the component with highest concentration, will be influenced by the uncertainty of all other components when composition is normalized to 100 %. 
            u[comp] = 0.0
        
        #All other components uses power regression
        elif comp in power_models.keys():
            u[comp] = power_models[comp]['power_a']*(moleperc**(power_models[comp]['power_b']))
        
        #C6+ components uses power regression for C6 (or actually C6+)
        elif comp in ['nC6','nC7','nC8','nC9','nC10']: 
            u[comp] = power_models['C6']['power_a']*(moleperc**(power_models['C6']['power_b']))
            
        else: 
            raise Exception(f'{comp} missing!')
        
        # Apply optinal lower uncertainty limit. If the estimated uncertainty is below the limit, the limit value will be used instead. This can be used to avoid unrealistically low uncertainty estimates for components with very low concentration. The choice of lower limit value should be based on expert judgement and knowledge of the measurement system, and should reflect a realistic minimum uncertainty level for the given component.
        if lower_uncertainty_limit is not None and u[comp]<lower_uncertainty_limit:
            u[comp] = lower_uncertainty_limit
        
    res['mean'] = {key : val for key,val in gas_dict.items()}
    res['standard_uncertainty'] = u
    res['min'] = {key : 0.0 for key in gas_dict}
    res['max'] = {key : 100.0 for key in gas_dict}
    res['distribution'] = {key : 'normal' for key in gas_dict}
        
    return res