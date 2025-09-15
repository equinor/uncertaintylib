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


import copy
import pandas as pd
import numpy as np
import scipy.stats

from typing import Callable, Dict, Any, Optional

#%% Uncertainty functions
def calculate_uncertainty(indata: dict, function: Callable[[dict], dict]) -> dict:
    """
    Analyze the uncertainty of output parameters for a given function and input data.
    The method used is the method described as "Determining combined standard uncertainty" for "Uncorrelated input quentities" 
    given in chapter 5 in "JCGM 100:2008 Evaluation of measurement data — Guide to the expression of uncertainty in measurement"
    The equation in use is equation (10) in chapter 5.1.2. 

    Handling of standard uncertainty:
        Both 'standard_uncertainty' and 'standard_uncertainty_percent' can be given. If only one is given, it will use that one. 
        However, If both are given, the code will use the largest of the two (in absolute values). 

    Parameters
    ----------
    indata : dict
        A dictionary that holds the following required keys:
            'mean' : dict
                A dictionary that holds the mean values for each input parameter.
            'standard_uncertainty' : dict
                A dictionary that holds the standard uncertainty values for each input parameter.
            'standard_uncertainty_percent': dict
                A dictionary that holds the percentage standard uncertainty for each input parameter.
    function : callable
        A function that takes an input dictionary and returns a dictionary of output parameters.

    Returns
    -------
    dict
        A dictionary with the following keys and values:
            'varians' : dict
                A dictionary of nested dictionaries that holds the varians for each input parameter for each output parameter.
            'contribution' : dict
                A dictionary of nested dictionaries that contains the percentage contribution of each input variable to the uncertainty in each output variable.
            'u' : dict
                A dictionary of the Combined Standard Uncertainty (u) for each output parameter.
            'U' : dict
                A dictionary of the Expanded Uncertainty (95% confidence level)(U,k=2) for each output parameter.
            'U_perc' : dict
                A dictionary of the Relative Expanded Uncertainty (95% confidence level)(U, k=2) for each output parameter, in %.

    """
    
        
    #retrieve the standard uncertainty to be used in the uncertainty calculation
    #It will use the largest value of the standard uncertainty and the percentage standard uncertainty (if both are given). 
    #If not, it will use the one that is given
    standard_uncertainty_used = standard_uncertainty_selector(indata) 
    
    
    # baseline_results = function(indata['mean']) #Calculate baseline results individually. However, these are also calculated when calculating sensitivity coefficients. Have therefore commented out this line, to improve calculation speed
    
    #Calculate absolute and relative sensitivity coefficients.
    #Baseline results are also calculated. That is the results by using the original input values (without pertubations)
    sensitivity_results = calculate_sensitivity_coefficients(indata, function)
    abs_sensitivity_coefficients = sensitivity_results['absolute_sensitivity_coefficients']
    rel_sensitivity_coefficients = sensitivity_results['relative_sensitivity_coefficients']
    baseline_results = sensitivity_results['baseline_results']
    
    #Nested dictionary of variance for each input parameter for each output parameter
    variance = {}
    
    #Dictionary of Combined Standard Uncertainty (u) for each output parameter
    u = {}
    
    #Dictionary of Expanded Uncertainty (95% confidence level)(U,k=2) for each output parameter
    U = {}
    
    #Dictionary of Relative Expanded Uncertainty (95% confidence level)(U, k=2) for each output parameter, in %
    U_perc = {}
    
    #Dictionary containing the percentage contribution of each input variabel to the uncertainty in an output variabel
    #The contribution is calculated as the % in variance
    contribution = {}
    
    for output in baseline_results:
        output_variance = {}
        #Calculate the variance of each contributor to the uncertainty
        for in_parameter in abs_sensitivity_coefficients:
            #Handle case where the standard uncertainty of the input parameter is nan (for example for settings), or the sensitivity coefficient is nan
            if np.isnan(standard_uncertainty_used[in_parameter]) or np.isnan(abs_sensitivity_coefficients[in_parameter][output]):
                var = 0.0
            else:
                var = (abs_sensitivity_coefficients[in_parameter][output] * standard_uncertainty_used[in_parameter])**2
            output_variance[in_parameter] = var
        variance[output] = output_variance
        #Calculate Combined Standard Uncertainty
        u[output] = np.sqrt(sum(output_variance.values()))
        #Calculate Expanded Uncertainty (95% confidence level)(U,k=2)
        U[output] = u[output]*2
        #Calculate Relative Expanded Uncertainty (95% confidence level)(U, k=2)
        if np.isnan(baseline_results[output]) or baseline_results[output]==0.0:
            U_perc[output] = np.nan
        else:
            U_perc[output] = 100*U[output]/abs(baseline_results[output])
        #Calculate uncertainty contribution using the sigma-normalized derivatives (eq 1.12 in Saltelli, A., et al. (2008). Global sensitivity analysis: the primer, John Wiley & Sons.)
        #First check if the sum of the variances is zero, which will give a divide by zero error
        #This can for example be the case if all sensitivity coefficients are 0
        if sum(output_variance.values())==0:
            contribution[output] = {key : np.nan for key in output_variance}
        else:    
            contribution[output] = {key : 100*val/sum(output_variance.values()) for key, val in output_variance.items()}

    return {'value' : baseline_results,
            'variance' : variance, 
            'contribution' : contribution, 
            'u' : u, 
            'U' : U, 
            'U_perc' : U_perc}



def calculate_sensitivity_coefficients(indata: dict, function: Callable[[dict], dict]) -> dict:
    """
    Calculate the absolute and relative sensitivity coefficients for input parameters to a given function.
    
    If an input parameter is set to distribution = 'none', the sensitivity coefficients will be 0 for this variabel. 
    This will for example be the case for settings used as input to the function, where values can be 0,1,2 etc. 
    
    Parameters
    ----------
    indata : dict
        A dictionary containing the input parameters, standard uncertainties, distribution, minimum and maximum values.
        The dictionary must have the following keys:
        - 'mean' : dict
            A dictionary that holds the mean values for each input parameter.
        - 'standard_uncertainty' : dict
            A dictionary that holds the standard uncertainty values for each input parameter.
        - 'standard_uncertainty_percent': dict
            A dictionary that holds the percentage standard uncertainty for each input parameter.
        - 'distribution' : dict, optional 
            A dictionary that holds the distribution used for each parameter. Default is 'normal'
        - 'min': dict, optional
            A dictionary that holds the minimum values for each input parameter. Not specified if missing.
        - 'max': dict, optional
            A dictionary that holds the maximum values for each input parameter. Not specified if missing.
    function : callable
        A function that takes an input dictionary and returns a dictionary of output parameters.

    Returns
    -------
    dict
        A dictionary containing three keys:
        - 'absolute_sensitivity_coefficients': dict
            A dictionary of absolute sensitivity coefficients for each input parameter (key) with respect to each output parameter (sub-key).
        - 'relative_sensitivity_coefficients': dict
            A dictionary of relative sensitivity coefficients (percentage change in output / percentage change in input) for each input parameter (key) with respect to each output parameter (sub-key).
        - 'baseline_results': dict
            A dictionary of output values for the original inputs (given by the 'mean' input dictionary)
    """
    
    input_dict = indata['mean']
    
    # Create a copy of the input dictionary so we can modify it safely
    input_dict_copy = copy.deepcopy(input_dict)

    # Calculate the output of the function for the original inputs
    original_output = function(input_dict_copy)

    # Create dictionaries to hold the sensitivity coefficients
    abs_sensitivity_coefficients = {}
    rel_sensitivity_coefficients = {}

    # Loop over each input variable
    for input_var in input_dict_copy:

            # Create a copy of the original input dictionary
            input_dict_copy2 = copy.deepcopy(input_dict)
            
            if 'distribution' in indata: # Check if the distribution is nan (blank), in which the distribution will be set to 'none'
                if type(indata['distribution'][input_var]) is float and np.isnan(indata['distribution'][input_var]):
                    indata['distribution'][input_var]='none'
            
            #Check if distribution is set to None. In that case, the sensitivity of that parameter is set to 0. 
            #This is done to handle functions that uses settings as input (for example 0 and 1), and that would crash if these values are pertubated
            if 'distribution' in indata and indata['distribution'][input_var].lower()=='none':                
                # Add both sensitivities to their respective dictionaries
                abs_sensitivity_coefficients[input_var] = {key : 0.0 for key in original_output}
                rel_sensitivity_coefficients[input_var] = {key : 0.0 for key in original_output}
            
            else:
                
    
                # Calculate the output with a small perturbation to the input
                perturbation = input_dict_copy2[input_var]*1.01 - input_dict_copy2[input_var] #  # a small perturbation
                
                if perturbation == 0.0:
                    perturbation = 0.0001
                
                input_dict_copy2[input_var] += perturbation
                
                #Calculate pertubated output
                perturbed_output = function(input_dict_copy2)
        
                # Calculate the sensitivity coefficient for this input variable (as a scalar)
                abs_sensitivity_coefficients[input_var] = {}
                rel_sensitivity_coefficients[input_var] = {}
                original_input_value = input_dict_copy[input_var]
                
                for key in original_output:                
                    # Calculate the percent change in the input variable caused by the perturbation
                    #If original_input_value is 0, return nan
                    if original_input_value==0.0:
                        percent_change = np.nan
                    else:
                        percent_change = perturbation / original_input_value * 100
        
                    # Calculate the absolute sensitivity coefficient for this input variable and output variable
                    abs_sensitivity_coefficient = (
                        perturbed_output[key] - original_output[key]
                    ) / perturbation
        
                    # Calculate the relative sensitivity coefficient for this input variable and output variable
                    if original_output[key]==0.0:
                        rel_sensitivity_coefficient = np.nan
                    else:
                        percent_output_change = 100*(perturbed_output[key] - original_output[key])/original_output[key]
                        rel_sensitivity_coefficient = percent_output_change/percent_change
        
        
                    # Add both sensitivities to their respective dictionaries
                    abs_sensitivity_coefficients[input_var][key] = abs_sensitivity_coefficient
                    rel_sensitivity_coefficients[input_var][key] = rel_sensitivity_coefficient

    results = {
        'absolute_sensitivity_coefficients' : abs_sensitivity_coefficients,
        'relative_sensitivity_coefficients' : rel_sensitivity_coefficients,
        'baseline_results' : original_output        
        }

    return results



def monte_carlo_simulation(mc_input: dict, function: Callable[[dict], dict], n: int) -> pd.DataFrame:
    """
    Runs a Monte Carlo simulation for the given input arguments and the provided function and returns the evaluation of the function 
    with Monte Carlo data as a pandas DataFrame.

    Handling of standard uncertainty:
        The input standard uncertainty is used as standard deviation when generating distributions of the input parameters used in the monte carlo. 
        Both 'standard_uncertainty' and 'standard_uncertainty_percent' can be given. If only one is given, it will use that one. 
        However, If both are given, the code will use the largest of the two (in absolute values). 
        

    Parameters
    ----------
    mc_input : dict
        A nested dictionary containing the following sub-dictionaries:
            'mean' : dict
                A dictionary with input parameter names as keys and mean values as values.
            'standard_uncertainty' : dict
                A dictionary with input parameter names as keys and standard uncertainty values as values. 
            'standard_uncertainty_percent' : dict
                A dictionary with input parameter names as keys and percentages of the standard uncertainty as values. 
            'distribution' : dict, optional
                A dictionary with input parameter names as keys and distribution types ('normal', 'uniform', or 'none') as values. Default is 'normal'.
                    - 'normal': Generates random samples using a normal distribution with input parameter mean and standard uncertainty value.
                    - 'uniform': Generates random samples using a uniform distribution with input parameter minimum and maximum values.
                    - 'none': Generates a fixed value with input parameter mean.
            'min' : dict, optional
                A dictionary with input parameter names as keys and minimum values for each parameter as values. If not present in 'mc_input', the distribution will not be truncated at a minimum value.
            'max' : dict, optional
                A dictionary with input parameter names as keys and maximum values for each parameter as values. If not present in 'mc_input', the distribution will not be truncated at a maximum value.
    function : callable
        The function to be evaluated
    n : int
        The number of Monte Carlo perturbations to run

    Returns
    -------
    pd.DataFrame
        A DataFrame of the function evaluations with Monte Carlo data generated from the provided parameters

    """
    
    #TODO update based on new std logic
    #retrieve the standard uncertainty to be used in the uncertainty calculation
    #It will use the largest value of the standard uncertainty and the percentage standard uncertainty (if both are given). 
    #If not, it will use the one that is given
    standard_uncertainty_used = standard_uncertainty_selector(mc_input) 
    
    
    # Generate all input data first
    random_input_data = {}
    for input_var in mc_input['mean']:
        mean = mc_input['mean'][input_var]
        stddev = standard_uncertainty_used[input_var]
        
        #set distribution. If not given, defaults to normal distribution
        if 'distribution' in mc_input and type(mc_input['distribution'][input_var])==str:
            distribution=mc_input['distribution'][input_var].lower()
        else:
            distribution = 'normal'
        
        #Get minimum and maximum values. If not present, or set to nan, these values are set to infinity
        if 'min' in mc_input and not np.isnan(mc_input['min'][input_var]):
            min_value = mc_input['min'][input_var]
        else:
            min_value = -np.inf
        
        if 'max' in mc_input and not np.isnan(mc_input['max'][input_var]):
            max_value = mc_input['max'][input_var]
        else:
            max_value = np.inf


        if stddev == 0:
            # If standard uncertainty is zero, use the mean value directly (no need to generate a sample)
            random_input_data[input_var] = np.full(n, mean)
        else:
            if distribution == 'normal':

                random_input_data[input_var] = generate_normal_distribution(
                    mean, 
                    stddev, 
                    n, 
                    lower_boundary=min_value, 
                    upper_boundary=max_value
                    )

            elif distribution == 'uniform':
                # Generate random sample using uniform distribution
                random_input_data[input_var] = np.random.uniform(low=min_value, high=max_value, size=n)
            
            elif distribution == 'none':
                random_input_data[input_var] = np.full(n,mean)

    # Loop through all input data and evaluate function
    output_dicts = []
    for i in range(n):
        random_input_dict = {input_var: random_input_data[input_var][i] for input_var in mc_input['mean']}
        output_dict = function(random_input_dict)
        output_dicts.append(output_dict)

    # Combine output dictionaries into a single dataframe
    output_df = pd.DataFrame(output_dicts)
    return output_df



def combined_standard_uncertainty(u_xi: Dict[str, float], ci: Optional[Dict[str, float]] = None) -> float:
    """
    Calculates the combined standard uncertainty from a dictionary of input uncertainties `u_xi` and a dictionary 
    of sensitivity coefficients `ci`. Both the uncertainties and the sensitivity coefficients can be given either 
    as relative (%) values or absolute values. If relative values are given, the result will also be a relative 
    uncertainty, while if absolute values are used, the uncertainty will also be absolute. The function assumes that 
    all input uncertainties and sensitivity coefficients are given as single standard uncertainties (k=1).
    
    If sensitivity coefficients are not given, sensitivity coefficients of 1 will be used. 
    
    Parameters
    ----------
    u_xi : dict
        Dictionary of input uncertainties, with keys corresponding to variable names and values corresponding
        to the uncertainty values.
    ci : dict, optional
        Dictionary of sensitivity coefficients, with keys corresponding to variable names and values corresponding 
        to the sensitivity coefficient values. Default is None, in which case a sensitivity value of 1.0 is assumed 
        for all input variables.
    
    Returns
    -------
    float
        The combined standard uncertainty, calculated as the square root of the sum of the squares of the 
        product of each input uncertainty with its corresponding sensitivity coefficient.
    
    """
    
    # if 'ci' is not provided, assume it's a dictionary with all values set to 1.0
    if ci is None:
        ci = {key: 1.0 for key in u_xi}
    
    # get the values from the dictionaries and make sure they're in the same order
    values_xi = [u_xi[k] for k in ci.keys()]
    values_ci = [ci[k] for k in ci.keys()]
    
    # convert the values to numpy arrays
    xi = np.array(values_xi)
    c = np.array(values_ci)
    
    # calculate the combined standard uncertainty
    U = np.sqrt(np.sum(c**2 * xi**2))
    
    return U



#%% Helping functions - used by the uncertainty functions
def generate_normal_distribution(
    mean: float,
    stddev: float,
    N: int,
    lower_boundary: float = -np.inf,
    upper_boundary: float = np.inf,
    iteration_limit: int = 1000
) -> np.ndarray:
    """
    Generates a random sample from a truncated normal distribution using rejection sampling.
    I.e. values outside the boundaries will be resampled. 
    
    Parameters
    ----------
    mean : float
        Mean of the normal distribution.
    stddev : float
        standard deviation of the normal distribution.
    N : int
        Number of random samples to generate.
    lower_boundary : float, optional
        Lower boundary for the truncated distribution (default is -inf).
    upper_boundary : float, optional
        Upper boundary for the truncated distribution (default is inf).
    iteration_limit : int, optional
        Maximum number of iterations allowed for rejection sampling (default is 1000).
    
    Returns
    -------
    samples : numpy.ndarray
        Array of size N containing the truncated normal distribution.
        
    Raises
    ------
    ValueError
        If lower_boundary is greater than upper_boundary.
    
    Notes
    -----
    This function generates a random sample of size N from a normal distribution with mean and standard deviation
    specified by `mean` and `stddev`, respectively, and removes samples that are outside of the lower and upper
    boundaries specified by `lower_boundary` and `upper_boundary`, respectively. Samples that fall outside of these
    boundaries are removed using rejection sampling. If the total number of samples generated is less than N, the
    function will continue to generate additional samples using rejection sampling until N samples have been
    generated or until the maximum number of iterations (specified by `iteration_limit`) has been reached.
    """
    
    # Check if lower_boundary is greater than upper_boundary
    if lower_boundary > upper_boundary:
        raise ValueError('lower_boundary cannot be greater than upper_boundary.')
    
    # Initialize the number of iterations
    i=0
    
    # Generate an initial set of random samples from a normal distribution
    normal = np.random.normal(mean, stddev, N)
    
    # Remove samples outside of the lower and upper boundaries using rejection sampling
    normal = normal[(normal >= lower_boundary) & (normal<=upper_boundary)]
    
    # If the total number of samples is less than N, add new samples using rejection sampling
    while len(normal) < N and i < iteration_limit:
        
        # Generate additional samples from the normal distribution
        extra = np.random.normal(mean, stddev, N - len(normal))
        
        # Remove samples outside of the lower and upper boundaries using rejection sampling
        extra = extra[(extra >= lower_boundary) & (extra<=upper_boundary)]
        
        # Add the new samples to the original set of samples
        normal = np.concatenate((normal, extra))
        
        # Increment the counter
        i += 1
        
    # If the maximum number of iterations is reached, return an array of NaNs of the requested size
    if len(normal) < N:
        return np.zeros(N) * np.nan
        
    return normal



def standard_uncertainty_selector(indata: dict) -> dict:
    """
    Selects either standard uncertainty or percentage-based standard uncertainty for each
    input parameter in a given dictionary, and returns the largest of the two.
    
    The reason for utilizing a max selector, is because many measurement principle have uncertainties that are given as a percentage in certain ranges
    while in lower ranges the uncertainty is dominated by other factors (such as noise), which is better represented by an absolute uncertainty value
    
    Parameters
    ----------
    indata : dict
        A dictionary that holds the following required keys:
        'mean' : dict
            A dictionary that holds the mean values for each input parameter.
        'standard_uncertainty' : dict
            A dictionary that holds the standard uncertainty values for each input parameter.
        'standard_uncertainty_percent' : dict, optional
            A dictionary that holds the percentage standard uncertainty for each input parameter.
    
    Returns
    -------
    dict
        A dictionary that holds the standard uncertainty used for each input parameter,
        either from the 'standard_uncertainty' column or calculated from the
        'standard_uncertainty_percent' column, whichever is larger.
        This is the standard uncertainty in absolute value (same unit as the mean), not the percentage standard uncertainty. 
        This standard uncertainty is the one being used in uncertainty calculations (such as monte carlo or traditional uncertainty calculation)
    
    Notes
    -----
    If the 'standard_uncertainty_percent' key is not present in the input dictionary, the
    function returns the 'standard_uncertainty' key.
    """
    
    
    standard_uncertainty_used = {}
    
    #Check if standard_uncertainty_percent is given for the dataset
    if 'standard_uncertainty_percent' in indata:
        for key in indata['standard_uncertainty']:
            
            std = indata['standard_uncertainty'][key] #standard uncertainty from the standard_uncertainty column
            std_from_perc = indata['standard_uncertainty_percent'][key]*indata['mean'][key]/100 #standard uncertainty calculated from the standard_uncertainty_percent column

            # check if both std and std_from_perc are nan
            if np.isnan(std) and np.isnan(std_from_perc):
                standard_uncertainty_used[key] = np.nan
            
            # check if std is nan and std_from_perc is a number
            elif np.isnan(std) and not np.isnan(std_from_perc):
                standard_uncertainty_used[key] = std_from_perc
            
            # check if std_from_perc is nan and std is a number
            elif np.isnan(std_from_perc) and not np.isnan(std):
                standard_uncertainty_used[key] = std
            
            # check if both std and std_from_perc are numbers
            elif not np.isnan(std) and not np.isnan(std_from_perc):
                standard_uncertainty_used[key] = np.max([std, std_from_perc])
    
    #If standard_uncertainty_percent is not given, the function returns the standard_uncertainty column
    else:
        standard_uncertainty_used = {key : abs(val) for key, val in indata['standard_uncertainty'].items()}
    
    return {key : abs(val) for key, val in standard_uncertainty_used.items()}



#%% Post-analysis functions - Used to post-process results from uncertainty calculations or to filter and compare results
def calculate_percentage_deviation_from_mean(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the percentage deviation from mean of each column in a given pandas DataFrame. 

    Parameters
    ----------
    dataframe : pandas DataFrame
        The DataFrame to calculate the percentage deviation.

    Returns
    -------
    pandas DataFrame
        A DataFrame where each column contains the percentage deviation from mean of the respective column in the input DataFrame.
        The percentage deviation of each element in a column is calculated as the difference between the value of each element and 
        the mean value of that column, divided by the mean value of that column, and then multiplied by 100. This calculation is 
        commonly used in statistical analysis to understand how much each data point in a column varies from the mean of that column.
    """
    percentage_deviation = pd.DataFrame()

    for column in dataframe.columns:
        mean = dataframe[column].mean()
        deviation = ((dataframe[column] - mean) / mean) * 100
        percentage_deviation[column] = deviation

    return percentage_deviation

def calculate_monte_carlo_statistics(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates descriptive statistics on a given pandas DataFrame using Monte Carlo simulation.

    Parameters
    ----------
    dataframe : pandas DataFrame
        The DataFrame for which to calculate the Monte Carlo statistics. Each column of the DataFrame should contain a result vector
        from a Monte Carlo simulation.

    Returns
    -------
    pandas DataFrame
        A DataFrame containing the mean, standard deviation (std_dev), standard deviation as a percentage of the mean (std_dev_percent), 
        two times the standard deviation (std_dev_k2), and two times the standard deviation as a percentage of the mean (std_dev_percent_k2)
        for each column of the original DataFrame. If the mean of a column is zero, the standard deviation as a percentage and two times the 
        standard deviation as a percentage are set to NaN because they are not defined.
    """
    
    statistics = {}

    for column in dataframe.columns:
        
        mean = dataframe[column].mean()
        std_dev = dataframe[column].std()
        std_dev_k2 = 2 * std_dev

        if mean == 0:
            std_dev_percent = np.nan  # Mean is zero, so percentage is not defined
            std_dev_percent_k2 = np.nan
        else:
            std_dev_percent = (std_dev / abs(mean)) * 100
            std_dev_percent_k2 = (std_dev_k2 / abs(mean)) * 100

        #statistics[column] = [mean, std_dev, std_dev_percent, std_dev_k2, std_dev_percent_k2]
        
        stats = {
            'mean'                  : mean, 
            'std_dev'               : std_dev, 
            'std_dev_percent'       : std_dev_percent, 
            'std_dev_k2'            : std_dev_k2, 
            'std_dev_percent_k2'    : std_dev_percent_k2
            }
        
        statistics[column] = stats
    #statistics.index = ['mean', 'std_dev', 'std_dev_percent', 'std_dev_k2', 'std_dev_percent_k2']

    statistics_df = pd.DataFrame(statistics)

    return statistics_df.T


def monte_carlo_output_correlations(outputs: pd.DataFrame, return_as_dataframe: bool = False) -> Any:
    """
    Calculate the Pearson correlation coefficients between each pair of outputs.

    Parameters:
    -----------
    outputs : pandas DataFrame
        A DataFrame containing the output variables.
    return_as_dataframe : boolean, default False
        If True, return the results as a DataFrame.
        If False, return the results as a dictionary.

    Returns:
    --------
    If return_as_dataframe is True:
        correlations : pandas DataFrame
            A DataFrame containing the pairwise correlation coefficients between the output variables.
    If return_as_dataframe is False:
        results : dictionary
            A dictionary containing the pairwise correlation coefficients between the output variables.
            The keys are in the format "output1 and output2".
    """
    # Calculate the correlation coefficients between each pair of outputs
    corr_matrix = outputs.corr()

    # Create an empty dataframe to store the results
    results = pd.DataFrame(columns=corr_matrix.columns, index=corr_matrix.columns)

    # Loop over every pair of outputs and store the correlation coefficient
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            output1 = corr_matrix.columns[i]
            output2 = corr_matrix.columns[j]
            corr_coeff, p_value = scipy.stats.pearsonr(outputs[output1], outputs[output2])
            results.loc[output1, output2] = corr_coeff
            results.loc[output2, output1] = corr_coeff # Add symmetry to the dataframe

    if return_as_dataframe:
        return results
    
    # Create a dictionary to store the results
    results_dict = {}
    for i in range(len(results.columns)):
        for j in range(i + 1, len(results.columns)):
            output1 = results.columns[i]
            output2 = results.columns[j]
            results_dict[f"{output1} and {output2}"] = results.loc[output1, output2]

    return results_dict



def filter_uncertainty_results(tag_filter_string: str, uncertainty_results: dict) -> dict:
    """
    Filter uncertainty (from calculate_uncertainty) results by a specific tag.
    This is useful when calculate_uncertainty is applied for functions returning thousands of outputs
    
    Parameters:
    -----------
    tag_filter_string : str
        A string used to filter the uncertainty results based on the key.
    uncertainty_results : dict
        A nested dictionary containing uncertainty results for different parameters.
    
    Returns:
    --------
    filtered_results: dict
        A nested dictionary containing filtered uncertainty results based on the tag filter string.
    """
    
    filtered_results = {key : {} for key in uncertainty_results}
    
    for parameter, value in uncertainty_results.items():
        for key, val in value.items():
            if tag_filter_string in key:
                filtered_results[parameter][key] = val
    
    return filtered_results
  
  
    
def compare_monte_carlo_to_conventional_uncertainty_calculation(MC_results: pd.DataFrame, uncertainty_results: dict) -> pd.DataFrame:
    '''
    Parameters
    ----------
    MC_results : pandas DataFrame
        Dataframe containing results from Monte Carlo simulation (returned by monte_carlo_simulation function)
    uncertainty_results : dict
        Dictionary containing all results from traditional uncertainty calculations (returned by calculate_uncertainty function)

    Returns
    -------
    df : pandas DataFrame
        Dataframe containing comparison between relative uncertainty (k=2) from conventional uncertainty calculations and monte carlo.

    '''    
    #Comare conventional uncertainty analysis to Monte Carlo results

    # Calculate the percentage deviation of Monte Carlo results from the mean value
    MC_results_relative = calculate_percentage_deviation_from_mean(MC_results)
    MC_stats = calculate_monte_carlo_statistics(MC_results)
    # cases[case_name]['Sensitivity_coefficients'] = uncertainty_functions.calculate_sensitivity_coefficients(mc_input_case['mean'], calculate_gas_properties)
    # monte_carlo_output_correlations = monte_carlo_output_correlations(MC_results, True)
    
    res = {'Conventional U [%], k=2' : uncertainty_results['U_perc'],
           'Monte Carlo U [%], k=2' : MC_stats['std_dev_percent_k2'].to_dict()
           }
    
    df = pd.DataFrame(res)
    
    return df