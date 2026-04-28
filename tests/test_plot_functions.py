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

import matplotlib
matplotlib.use('Agg')  # non-interactive backend, safe for CI

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from uncertaintylib import plot_functions, uncertainty_functions


def _calc_volume(inputs):
    return {
        'volume': inputs['L'] * inputs['W'] * inputs['D'],
        'area': inputs['L'] * inputs['W'],
    }


def test_montecarlo_property_plot_returns_figure():
    np.random.seed(42)
    data = pd.DataFrame({'volume': np.random.normal(8.0, 0.5, 500)})
    fig = plot_functions.montecarlo_property_plot_and_table(data, 'volume')
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_montecarlo_property_plot_with_options():
    np.random.seed(0)
    data = pd.DataFrame({
        'volume': np.random.normal(8.0, 0.5, 500),
        'area': np.random.normal(4.0, 0.2, 500),
    })
    fig = plot_functions.montecarlo_property_plot_and_table(
        data,
        property_id='volume',
        property_name='Volume',
        property_unit='m3',
        xlim=[-10, 10],
    )
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_uncertainty_contribution_returns_figure():
    data = {
        'mean': {'L': 2.0, 'W': 2.0, 'D': 2.0},
        'standard_uncertainty': {'L': 0.3, 'W': 0.1, 'D': 0.2},
    }
    res = uncertainty_functions.calculate_uncertainty(data, _calc_volume)
    fig = plot_functions.plot_uncertainty_contribution(res, 'volume')
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_uncertainty_contribution_with_filter():
    data = {
        'mean': {'L': 2.0, 'W': 2.0, 'D': 2.0},
        'standard_uncertainty': {'L': 0.3, 'W': 0.1, 'D': 0.2},
    }
    res = uncertainty_functions.calculate_uncertainty(data, _calc_volume)
    fig = plot_functions.plot_uncertainty_contribution(res, 'volume', filter_top_x=2)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_uncertainty_contribution_custom_title():
    data = {
        'mean': {'L': 2.0, 'W': 2.0, 'D': 2.0},
        'standard_uncertainty': {'L': 0.3, 'W': 0.1, 'D': 0.2},
    }
    res = uncertainty_functions.calculate_uncertainty(data, _calc_volume)
    fig = plot_functions.plot_uncertainty_contribution(res, 'area', plot_title='Custom Title')
    assert isinstance(fig, plt.Figure)
    plt.close(fig)
