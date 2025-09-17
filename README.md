<img src="https://github.com/equinor/uncertaintylib/blob/main/images/uncertaintylib.png" alt="uncertaintylib logo" width="600"/>

`uncertaintylib` is a Python library for estimating and propagating uncertainties in engineering and scientific calculations. It is designed to work with any Python function whose inputs and outputs are flat dictionaries.

## Key Principles

- **Function-agnostic:** You can pass any Python function to the library, as long as its inputs and outputs are flat dictionaries (no nested dicts or lists).
- **Standard-inspired:** Attempts to follow uncertainty propagation principles outlined in JCGM 100:2008 (Guide to the Expression of Uncertainty in Measurement).

## Installation

Install from PyPI:

```bash
pip install uncertaintylib
```

## Usage

The main interface is through functions in `uncertaintylib.uncertainty_functions`. You provide:
- A Python function (inputs: flat dict, outputs: flat dict)
- A dictionary containing 'mean' and 'standard_uncertainty' for each variable. These are provided as sub dictionaries. 
- The standard uncertainty can also be given in relative terms (%), using the 'standard_uncertainty_percent' key
- If both 'standard_uncertainty' and 'standard_uncertainty_percent', the largest of the two will be used. This can be useful for variables where for example noise dominates the uncertainty in the lower region (such as zero stability of a coriolis massflow meter)
- 'min' and 'max' are only used in Monte Carlo calculations, to address the issue of non-physical distributions (for example distribution of mole-% of a component going below 0)
- 'distribution' is used mainly by Monte Carlo, but also in cases where some of the inputs are settings (for example 0 or 1), where you dont want to pertubate or calculate sensitivity coefficients for that spesific input variable. In this case 'distribution' can be set to 'none', which will ignore that parameter. 

Example usage (standard uncertainty calculation):

```python
from uncertaintylib import uncertainty_functions

inputs = {
    'mean': {'Q': 370, 'rho': 54},
    'standard_uncertainty': {'Q': 1, 'rho': 0.03},
    'standard_uncertainty_percent': {'Q': 0.25, 'rho': 0.1},
    'distribution': {'Q': 'normal', 'rho': 'normal'},
    'min': {'Q': 0, 'rho': 0},
    'max': {'Q': None, 'rho': None}
}

def calculate_massflow(inputs):
    outputs = {}
    
    outputs['MassFlow'] = inputs['Q']*inputs['rho']

    return outputs

results = uncertainty_functions.calculate_uncertainty(
    indata=inputs, 
    function=calculate_massflow
    )

print(results)
```

Another example, [Example 06](https://github.com/equinor/uncertaintylib/blob/main/examples/example_06/example_06.ipynb), demonstrates uncertainty calculations for a natural gas metering station, demonstrating usage of many of the functions available in this library. 

## Plotting Functionalities

`uncertaintylib` includes plotting utilities based on matplotlib, available in `uncertaintylib.plot_functions`. These functions help visualize uncertainty propagation and contributions:

- **Monte Carlo Distribution Plots:** Visualize the distribution of output properties from Monte Carlo simulations, including summary tables of mean and uncertainty.
- **Uncertainty Contribution Plots:** Show the percentage contribution of each input variable to the total expanded uncertainty of an output property.

All plots are generated using matplotlib and can be customized or saved using standard matplotlib methods. See the API docstrings in `plot_functions.py` for details.

## Documentation & Examples

- See the `examples/` folder for practical scripts demonstrating usage.
- API documentation is available in the source code docstrings.

## License

MIT License. See `LICENSE` for details.
