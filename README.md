# uncertaintylib

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
- Input data as dictionaries specifying means and uncertainties
  
Example input dictionary:

```python
inputs = {
    "Q": {
        "mean": 370,
        "standard_uncertainty": 1,
        "distribution": "normal",
        "min": 0,
        "max": None
    },
    "rho": {
        "mean": 54,
        "standard_uncertainty": 0.03,
        "distribution": "normal",
        "min": 0,
        "max": None
    }
}
```

- Each key is an input variable name.
- Values are dictionaries specifying mean, standard uncertainty, distribution type, and optional min/max bounds.


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
