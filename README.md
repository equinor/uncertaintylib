# uncertaintylib

`uncertaintylib` is a Python library for estimating and propagating uncertainties in engineering and scientific calculations. It is designed to work with any Python function whose inputs and outputs are flat dictionaries.

## Key Principles

- **Function-agnostic:** You can pass any Python function to the library, as long as its inputs and outputs are flat dictionaries (no nested dicts or lists).
- **Flexible input format:** The uncertainty inputs are provided as dictionaries describing means, standard uncertainties, and/or percentage uncertainties for each input variable. See function docstrings for details.
- **Standard-compliant:** Implements uncertainty propagation according to JCGM 100:2008 (Guide to the Expression of Uncertainty in Measurement).
- **Sensitivity analysis and Monte Carlo:** Includes methods for sensitivity coefficient analysis and Monte Carlo simulation.

## Installation

Install from PyPI:

```bash
pip install uncertaintylib
```

## Usage

The main interface is through functions in `uncertaintylib.uncertainty_functions`. You provide:
- A Python function (inputs: flat dict, outputs: flat dict)
- Input data as dictionaries specifying means and uncertainties

## Documentation & Examples

- See the `examples/` folder for practical scripts demonstrating usage.
- API documentation is available in the source code docstrings.

## License

MIT License. See `LICENSE` for details.
