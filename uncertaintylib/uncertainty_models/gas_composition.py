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

from typing import Dict, Optional


# GERG-2008 molar masses (g/mol)
GERG_2008_MOLAR_MASSES = {
    'C1': 16.04246,      # Methane
    'N2': 28.0134,       # Nitrogen
    'CO2': 44.0095,      # Carbon dioxide
    'C2': 30.06904,      # Ethane
    'C3': 44.09562,      # Propane
    'iC4': 58.1222,      # Isobutane
    'nC4': 58.1222,      # n-Butane
    'iC5': 72.14878,     # Isopentane
    'nC5': 72.14878,     # n-Pentane
    'nC6': 86.17536,     # Hexane
    'nC7': 100.20194,    # Heptane
    'nC8': 114.22852,    # Octane
    'nC9': 128.2551,     # Nonane
    'nC10': 142.28168,   # Decane
    'H2': 2.01588,       # Hydrogen
    'O2': 31.9988,       # Oxygen
    'CO': 28.0101,       # Carbon monoxide
    'H2O': 18.01528,     # Water
    'H2S': 34.08088,     # Hydrogen sulfide
    'He': 4.002602,      # Helium
    'Ar': 39.948         # Argon
}


def component_uncertainty_from_ASTM_D1945(composition_mole_percent: Dict[str, float]) -> dict:
    """
    Estimate gas composition uncertainty according to ASTM D1945 standard.
    
    This function calculates component uncertainty according to ASTM D1945 
    "Reproducibility" (chapter 10.1.2). The uncertainty values are based on 
    95% confidence level (k=2) and given in absolute terms (mol%). The interpretation 
    follows the NFOGM Fiscal Gas Metering Station Uncertainty (GasMet) tool (https://gasmetapp.web.norce.cloud/).
    
    Parameters
    ----------
    composition_mole_percent : dict
        Gas composition as a dictionary with component names as keys and 
        mole percentages as values. The composition does not need to be 
        normalized to 100%. Supported components: N2, CO2, C1, C2, C3, 
        iC4, nC4, iC5, nC5, nC6, nC7, nC8, nC9, nC10.
        Example: {'C1': 85.0, 'C2': 10.0, 'N2': 5.0}
    
    Returns
    -------
    dict
        A dictionary in standard uncertaintylib format with the following keys:
        
        - 'mean' : dict
            Normalized mole percentages for each component.
        - 'standard_uncertainty' : dict
            Standard uncertainty (k=1) for each component in absolute terms (mol%).
        - 'distribution' : dict
            Distribution type for each component (all set to 'normal').
        - 'min' : dict
            Minimum allowable values for each component (0.0 mol%).
        - 'max' : dict
            Maximum allowable values for each component (100.0 mol%).
    
    Notes
    -----
    The reproducibility values from ASTM D1945 are applied as follows:
    
    - < 0.1 mol%: U = 0.02 mol% (k=2)
    - 0.1 to 1.0 mol%: U = 0.07 mol% (k=2)
    - 1.0 to 5.0 mol%: U = 0.10 mol% (k=2)
    - 5.0 to 10.0 mol%: U = 0.12 mol% (k=2)
    - > 10.0 mol%: U = 0.15 mol% (k=2)
    
    The standard uncertainty is calculated by dividing the expanded uncertainty 
    (k=2) by 2 to obtain the single standard deviation (k=1).
    
    Examples
    --------
    >>> composition = {'C1': 85.0, 'C2': 10.0, 'N2': 5.0}
    >>> uncertainty_data = component_uncertainty_from_ASTM_D1945(composition)
    >>> print(uncertainty_data['standard_uncertainty']['C1'])
    0.075
    """
    allowed_components = ['N2', 'CO2', 'C1', 'C2', 'C3', 'iC4', 'nC4', 'iC5', 'nC5', 'nC6', 'nC7', 'nC8', 'nC9', 'nC10']
    
    # Check if all components are supported
    unsupported_components = [comp for comp in composition_mole_percent.keys() if comp not in allowed_components]
    if unsupported_components:
        raise ValueError(f"Unsupported components: {unsupported_components}. Allowed components: {allowed_components}")
    
    # Normalize composition to 100%
    total_composition = sum(composition_mole_percent.values())
    if total_composition == 0:
        raise ValueError("Total composition is zero. Cannot normalize.")
    
    composition_normalized = {key: (val / total_composition) * 100 for key, val in composition_mole_percent.items()}
    
    # Calculate standard uncertainties
    standard_uncertainty = {}
    
    for component, mole_percent in composition_normalized.items():
        if mole_percent < 0.1:
            expanded_uncertainty = 0.02
        elif mole_percent < 1.0:
            expanded_uncertainty = 0.07
        elif mole_percent < 5.0:
            expanded_uncertainty = 0.10
        elif mole_percent < 10.0:
            expanded_uncertainty = 0.12
        else:
            expanded_uncertainty = 0.15
        
        # Convert from expanded uncertainty (k=2) to standard uncertainty (k=1)
        standard_uncertainty[component] = expanded_uncertainty / 2
    
    # Prepare output in standard uncertaintylib format
    result = {
        'mean': composition_normalized,
        'standard_uncertainty': standard_uncertainty,
        'min': {key: 0.0 for key in composition_normalized},
        'max': {key: 100.0 for key in composition_normalized},
        'distribution': {key: 'normal' for key in composition_normalized}
    }
    
    return result


def component_uncertainty_from_norsok_I106(composition_mole_percent: Dict[str, float]) -> dict:
    """
    Estimate gas composition uncertainty according to NORSOK I-106:2014 standard.
    
    This function calculates the expanded uncertainty (k=2) for gas composition 
    components based on the NORSOK I-106:2014 standard. The uncertainty depends on 
    the mole fraction of each component and the ratio of average molar mass to 
    component molar mass. Molar masses are automatically retrieved from GERG-2008 
    reference values. NORSOK I-106 only provides component uncertainty down to 0.5 mol%. 
    This function uses the same uncertainty value below 0.5 mol% to handle low concentration components.

    Note: This method do not take into account increased uncertainty for heavier components, and therefore tend to 
    underestimate compositional uncertainties for rich natural gases. The higher the molar mass of a component,
    the lower the uncertainty according to this method, while in reality the opposite is often the case. 
    
    Parameters
    ----------
    composition_mole_percent : dict
        Gas composition as a dictionary with component names as keys and 
        mole percentages as values. The composition does not need to be 
        normalized to 100%. Supports all GERG-2008 components: C1, N2, CO2, 
        C2, C3, iC4, nC4, iC5, nC5, nC6, nC7, nC8, nC9, nC10, H2, O2, CO, 
        H2O, H2S, He, Ar.
        Example: {'C1': 85.0, 'C2': 10.0, 'N2': 5.0}
    
    Returns
    -------
    dict
        A dictionary in standard uncertaintylib format with the following keys:
        
        - 'mean' : dict
            Normalized mole percentages for each component.
        - 'standard_uncertainty' : dict
            Standard uncertainty (k=1) for each component in absolute terms (mol%).
        - 'distribution' : dict
            Distribution type for each component (all set to 'normal').
        - 'min' : dict
            Minimum allowable values for each component (0.0 mol%).
        - 'max' : dict
            Maximum allowable values for each component (100.0 mol%).
    
    Notes
    -----
    The NORSOK I-106 method calculates uncertainty using the formula:
    
    .. math::
        U_{x_i} = \\text{factor} \\times \\frac{M_{\\text{avg}}}{M_i}
    
    where:
    - U_{x_i} is the expanded uncertainty (k=2) for component i (mol%)
    - M_{avg} is the average molar mass of the gas mixture (g/mol)
    - M_i is the molar mass of component i (g/mol)
    - factor depends on the component's mass percent (not mole percent):
        - < 20 mass%: factor = 0.15
        - 20 to 50 mass%: factor = 0.30
        - > 50 mass%: factor = 0.60
    
    The input composition is provided in mole percent, which is then converted to 
    mass percent to determine the appropriate factor. The calculated uncertainty 
    is returned in mole percent.
    The standard uncertainty is calculated by dividing the expanded uncertainty 
    (k=2) by 2 to obtain the single standard deviation (k=1).
    
    Molar masses are taken from GERG-2008 reference data.
    
    Examples
    --------
    >>> composition = {'C1': 85.0, 'C2': 10.0, 'N2': 5.0}
    >>> uncertainty_data = component_uncertainty_from_norsok_I106(composition)
    >>> print(uncertainty_data['standard_uncertainty']['C1'])
    0.3
    
    References
    ----------
    NORSOK standard I-106:2014: "Fiscal metering systems for hydrocarbon liquid and gas"
    """
    # All GERG-2008 components are allowed
    allowed_components = list(GERG_2008_MOLAR_MASSES.keys())
    
    # Check if all components are supported
    unsupported_components = [comp for comp in composition_mole_percent.keys() if comp not in allowed_components]
    if unsupported_components:
        raise ValueError(f"Unsupported components: {unsupported_components}. Allowed components: {allowed_components}")
    
    # Normalize composition to 100%
    total_composition = sum(composition_mole_percent.values())
    if total_composition == 0:
        raise ValueError("Total composition is zero. Cannot normalize.")
    
    composition_normalized = {key: (val / total_composition) * 100 for key, val in composition_mole_percent.items()}
    
    # Calculate average molar mass of the gas mixture
    average_molar_mass = sum([
        composition_normalized[comp] * GERG_2008_MOLAR_MASSES[comp] 
        for comp in composition_normalized
    ]) / 100  # Divide by 100 because composition is in mol%
    
    # Convert mole percent to mass percent for factor determination
    # mass_i = mole_percent_i * M_i
    total_mass = sum([
        composition_normalized[comp] * GERG_2008_MOLAR_MASSES[comp]
        for comp in composition_normalized
    ])
    
    composition_mass_percent = {
        comp: (composition_normalized[comp] * GERG_2008_MOLAR_MASSES[comp] / total_mass) * 100
        for comp in composition_normalized
    }
    
    # Calculate standard uncertainties
    standard_uncertainty = {}
    
    for component, mole_percent in composition_normalized.items():
        component_molar_mass = GERG_2008_MOLAR_MASSES[component]
        mass_percent = composition_mass_percent[component]
        
        # Determine factor based on MASS percent (not mole percent)
        # According to NORSOK I-106, Table 4
        if mass_percent < 20:
            factor = 0.15
        elif mass_percent < 50:
            factor = 0.30
        else:
            factor = 0.60
        
        # Calculate expanded uncertainty (k=2) according to NORSOK I-106
        # Uncertainty is given in mol%, not mass%
        expanded_uncertainty = factor * average_molar_mass / component_molar_mass
        
        # Convert from expanded uncertainty (k=2) to standard uncertainty (k=1)
        standard_uncertainty[component] = expanded_uncertainty / 2
    
    # Prepare output in standard uncertaintylib format
    result = {
        'mean': composition_normalized,
        'standard_uncertainty': standard_uncertainty,
        'min': {key: 0.0 for key in composition_normalized},
        'max': {key: 100.0 for key in composition_normalized},
        'distribution': {key: 'normal' for key in composition_normalized}
    }
    
    return result


def component_uncertainty_from_haagenvik2024(
    composition_mole_percent: Dict[str, float], 
    lower_uncertainty_limit: Optional[float] = None
) -> dict:
    """
    Estimate gas composition uncertainty using the Hagenvik et al. (2024) method.
    
    This function estimates component uncertainty based on the empirical method 
    described in "Exploring the Relationship between Speed of Sound, Density and 
    Isentropic Exponent" (Hagenvik et al., 2024). The method uses power law 
    regressions fitted to parallel test data from the K-lab facility.
    
    **Important**: This method should only be applied for gas compositions with 
    significant methane content (minimum 60 mol%).
    
    Parameters
    ----------
    composition_mole_percent : dict
        Gas composition as a dictionary with component names as keys and 
        mole percentages as values. The composition does not need to be 
        normalized to 100%. Supported components: N2, CO2, C1, C2, C3, 
        iC4, nC4, iC5, nC5, nC6, nC7, nC8, nC9, nC10.
        Example: {'C1': 85.0, 'C2': 10.0, 'N2': 5.0}
    lower_uncertainty_limit : float, optional
        Optional lower limit for uncertainty estimates (mol%). If the calculated 
        uncertainty for a component is below this limit, the limit value will be 
        used instead. This prevents unrealistically low uncertainty estimates 
        for components with very low concentrations. The choice should be based 
        on expert judgment and knowledge of the measurement system. Default is None 
        (no lower limit applied).
    
    Returns
    -------
    dict
        A dictionary in standard uncertaintylib format with the following keys:
        
        - 'mean' : dict
            Normalized mole percentages for each component.
        - 'standard_uncertainty' : dict
            Standard uncertainty (k=1) for each component in absolute terms (mol%).
        - 'distribution' : dict
            Distribution type for each component (all set to 'normal').
        - 'min' : dict
            Minimum allowable values for each component (0.0 mol%).
        - 'max' : dict
            Maximum allowable values for each component (100.0 mol%).
    
    Notes
    -----
    The uncertainty for each component (except C1) is estimated using a power law:
    
    .. math::
        u_i = a \\times x_i^b
    
    where u_i is the standard uncertainty, x_i is the mole percentage of component i,
    and a and b are fitted parameters from parallel test data.
    
    The uncertainty of methane (C1) is set to 0% to account for the normalization 
    effect. Since methane typically has the highest concentration and the composition 
    is normalized to 100%, the uncertainty in methane is implicitly influenced by 
    the uncertainties in all other components.
    
    For heavy components (C6+), the same power law coefficients as C6 are used.
    
    Power law coefficients (from K-lab parallel test data):
    
    - N2: a=0.034, b=1.005
    - CO2: a=0.013, b=0.514
    - C2: a=0.041, b=-0.118
    - C3: a=0.025, b=0.970
    - iC4: a=0.018, b=0.635
    - nC4: a=0.027, b=0.793
    - iC5: a=0.016, b=0.383
    - nC5: a=0.023, b=0.470
    - C6+: a=0.103, b=0.683
    
    Examples
    --------
    >>> composition = {'C1': 85.0, 'C2': 8.0, 'C3': 4.0, 'N2': 3.0}
    >>> uncertainty_data = component_uncertainty_from_haagenvik2024(composition)
    >>> print(uncertainty_data['standard_uncertainty']['C2'])
    0.038
    
    >>> # With lower uncertainty limit
    >>> uncertainty_data = component_uncertainty_from_haagenvik2024(
    ...     composition, 
    ...     lower_uncertainty_limit=0.01
    ... )
    
    References
    ----------
    Hagenvik, C., et al. (2024). "Exploring the Relationship between Speed of Sound, 
    Density and Isentropic Exponent." Presented at NFOGM 2024.
    https://nfogm.no/wp-content/uploads/2025/08/1-Single-Phase-1-Exploring-the-Relationship-between-Speed-of-Sound-Density-and-Isentropic-Exponent-Christian-Hagenvik_Equinor.pdf
    """
    allowed_components = ['N2', 'CO2', 'C1', 'C2', 'C3', 'iC4', 'nC4', 'iC5', 'nC5', 'nC6', 'nC7', 'nC8', 'nC9', 'nC10']
    
    # Check if all components are supported
    unsupported_components = [comp for comp in composition_mole_percent.keys() if comp not in allowed_components]
    if unsupported_components:
        raise ValueError(f"Unsupported components: {unsupported_components}. Allowed components: {allowed_components}")
    
    # Normalize composition to 100%
    total_composition = sum(composition_mole_percent.values())
    if total_composition == 0:
        raise ValueError("Total composition is zero. Cannot normalize.")
    
    composition_normalized = {key: (val / total_composition) * 100 for key, val in composition_mole_percent.items()}
    
    # Power law regression coefficients from K-lab sample parallel tests
    power_models = {
        'N2': {'power_a': 0.034, 'power_b': 1.005},
        'CO2': {'power_a': 0.013, 'power_b': 0.514},
        'C2': {'power_a': 0.041, 'power_b': -0.118},
        'C3': {'power_a': 0.025, 'power_b': 0.970},
        'iC4': {'power_a': 0.018, 'power_b': 0.635},
        'nC4': {'power_a': 0.027, 'power_b': 0.793},
        'iC5': {'power_a': 0.016, 'power_b': 0.383},
        'nC5': {'power_a': 0.023, 'power_b': 0.470},
        'C6': {'power_a': 0.103, 'power_b': 0.683}
    }
    
    # Calculate standard uncertainties
    standard_uncertainty = {}
    
    for component, mole_percent in composition_normalized.items():
        if mole_percent == 0:
            # Zero concentration means zero uncertainty
            standard_uncertainty[component] = 0.0
        
        elif component == 'C1':
            # Methane uncertainty is set to 0% to account for normalization effect.
            # Since methane has the highest concentration and composition is normalized 
            # to 100%, its uncertainty is implicitly influenced by uncertainties in 
            # all other components.
            standard_uncertainty[component] = 0.0
        
        elif component in power_models:
            # Apply power law regression for components with available models
            params = power_models[component]
            standard_uncertainty[component] = params['power_a'] * (mole_percent ** params['power_b'])
        
        elif component in ['nC6', 'nC7', 'nC8', 'nC9', 'nC10']:
            # C6+ components use the C6 power law regression
            params = power_models['C6']
            standard_uncertainty[component] = params['power_a'] * (mole_percent ** params['power_b'])
        
        else:
            raise ValueError(f"Component '{component}' is not supported by this method.")
        
        # Apply optional lower uncertainty limit
        if lower_uncertainty_limit is not None and standard_uncertainty[component] < lower_uncertainty_limit:
            standard_uncertainty[component] = lower_uncertainty_limit
    
    # Prepare output in standard uncertaintylib format
    result = {
        'mean': composition_normalized,
        'standard_uncertainty': standard_uncertainty,
        'min': {key: 0.0 for key in composition_normalized},
        'max': {key: 100.0 for key in composition_normalized},
        'distribution': {key: 'normal' for key in composition_normalized}
    }
    
    return result