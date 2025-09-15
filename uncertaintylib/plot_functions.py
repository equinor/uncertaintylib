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


import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional, Sequence, Dict

def montecarlo_property_plot_and_table(
    data: pd.DataFrame,
    property_id: str,
    xlim: Optional[Sequence[float]] = None,
    property_name: str = '',
    property_unit: str = '',
    case_title: str = '',
    round_props: Optional[Dict[str, int]] = None
) -> plt.Figure:
    """
    Create a plot and table for a given property for a Monte Carlo run

    Parameters
    ----------
    data : pd.DataFrame
        A DataFrame with Monte Carlo data generated from the provided parameters.
        This is the output from the "monte_carlo_simulation" function in uncertainty_functions
    property_id : str
        Property to plot, which needs to correspond to the column heading in the Monte Carlo results.
    xlim : list, optional
        List containing percentage range of the property to plot. For example, [-2, 2] means the plot will plot from the mean-2
        % to mean + 2 %, by default [].
    property_name : str, optional
        The name to be used in titles in the plot. Defaults to '', which will use the property_id as the property_name.
    property_unit : str, optional
        Unit to be displayed in plots, defaults to ''.
    round_props : dict, optional
        Dictionary determining how the mean and standard deviations in the table should be rounded. Default is {'mean': 1,
        'std': 2, 'stdperc': 2}.
    case_title : str, optional
        Title displayed above the plot. Default is generated based on the property name
    Returns
    -------
    matplotlib.figure.Figure
        The generated figure.
    """
    
    if round_props is None:
        round_props = {'mean': 1, 'std': 2, 'stdperc': 2}
    if xlim is None:
        xlim = []
    if case_title=='':
        case_title = f'Monte Carlo uncertainty distribution - {property_name}'
    
    # Import inside function to avoid module-level exposure
    from . import uncertainty_functions
    mc_stats = uncertainty_functions.calculate_monte_carlo_statistics(data)
    
    if property_name == '':
        property_name = property_id

    fontsize = 12

    # Define the bins for the histogram
    bins = 200

    # Define the figure and axes
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(8, 6), gridspec_kw={'height_ratios': [10, 1]})

    fig.suptitle(case_title, fontsize=14)

    # Plot the histogram
    axs[0].hist(data[property_id], bins=bins, alpha=1, color='#008080', zorder=2)
    axs[0].set_xlabel(f'{property_name} [{property_unit}]', fontsize=fontsize)
    axs[0].set_ylabel('Count', fontsize=fontsize)
    # axs[0].legend(fontsize=fontsize)
    axs[0].grid(True, zorder=1)

    # Create variables for the table
    std_perc_k2 = mc_stats.loc[property_id,'std_dev_percent_k2']

    std_k2 = mc_stats.loc[property_id,'std_dev_k2']

    mean = mc_stats.loc[property_id,'mean']

    if xlim != []:
        max_mean = mean
        axs[0].set_xlim([max_mean + max_mean*xlim[0]/100, max_mean + max_mean*xlim[1]/100])
    
    # Add table
    table_data = [[f'Mean [{property_unit}]', round(mean, round_props['mean'])],
                  [fr'2$\sigma$ [{property_unit}]', round(std_k2, round_props['std'])],
                  [r'2$\sigma$ [%]', round(std_perc_k2, round_props['stdperc'])]]

    table = axs[1].table(cellText=table_data, loc='bottom')

    # Remove ticks from the x and y axes of the second subplot
    axs[1].get_xaxis().set_ticks([])
    axs[1].get_yaxis().set_ticks([])

    table.scale(0.8, 1.2)
    table.set_fontsize(12)

    # #Mark % standard deviation in yellow
    # table._cells[(2, 1)].set_facecolor("yellow")

    # Center the text in the table
    for cell in table.get_celld():
        cell_text = table[cell].get_text()
        cell_text.set_ha('center')
        cell_text.set_va('center')

    # Remove the border around the plot
    for spine in axs[1].spines.values():
        spine.set_visible(False)

    # Adjust the layout of the figure
    fig.subplots_adjust(hspace=0.3)

     # Adjust the layout of the figure
    fig.tight_layout()

    fig_title = f'{property_id} Monte Carlo distribution'
    try:
        fig.canvas.manager.window.setWindowTitle(fig_title)
    except Exception:
        pass

    # fig.savefig(f'plots\{fig_title}.png')

    # # Display the plot and table
    fig.show()
    
    return fig


def plot_uncertainty_contribution(
    res: dict,
    property_id: str,
    plot_title: Optional[str] = '',
    filter_top_x: int = 0
) -> plt.Figure:
    """
    Plots the contribution of the input parameters to the total expanded uncertainty of a property.

    Parameters
    ----------
    res : dict
        A dictionary that contains the uncertainty calculation results. This is the output from the "calculate_uncertainty" function in uncertainty_functions
    property_id : str
        A string that corresponds to the id of the property to plot.
    plot_title : str
        Title of the plot, Optional. If left empty, the plot will generate a standard plot title
        If plot_title is set to None, plot title is not included
    filter_top_x : bool
        For uncertainty results with large number of outputs, it can be convenient to filter out the top contributors to uncertainty. 
        If filter_top_x is 0, all contributors will be included. If it is set to a number, the function will retrieve the X
        numbers of top contributors and only include theses in the plot. 

    Returns
    -------
    matplotlib.figure.Figure
        A Figure object that contains the plot.
    """
    
    # Import inside function to avoid module-level exposure
    from . import uncertainty_functions
    case_res = res['contribution'][property_id]

    if filter_top_x != 0:
        # Sort the dictionary by value in descending order and retrieve the first filter_top_x keys
        top_x_dict = dict(sorted(case_res.items(), key=lambda item: item[1], reverse=True)[:filter_top_x])
        case_res = top_x_dict

    fig, ax = plt.subplots(figsize=(10, 6))

    # Change the color of the bars
    bars = ax.barh(list(case_res.keys()), case_res.values(), color='#008080', alpha=0.7)

    # Add some edgecolor to the bars
    for i in bars:
        i.set_edgecolor('#5f9ea0')

    # Invert the y-axis so that the highest contribution appears at the top
    ax.invert_yaxis()

    # Add a grid to the plot
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    # Add percentage labels to the bars
    for i, v in enumerate(case_res.values()):
        ax.text(v+0.5, i, f'{v:.1f}%', color='#4b4b4b', fontweight='bold')

    # # Add line labels to the bars
    # for i, v in enumerate(case_res.keys()):
    #     ax.text(-2, i, v, color='#4b4b4b', fontweight='bold', fontfamily='serif')

    # Change the axis colors, labels, and tick sizes
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_color('#4b4b4b')
    ax.spines['left'].set_color('#4b4b4b')
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_xlabel('% contribution to total expanded uncertainty', fontsize=14)
    ax.set_ylabel('Input variables', fontsize=14)

    # Add a plot title with a subtitle
    if plot_title == '':
        ax.set_title(f'Contribution to Total Expanded Uncertainty in {property_id}', fontsize=16, y=1.0)
    elif plot_title == None:
        #Dont include title if plot_title is set to None
        pass
    else:
        ax.set_title(plot_title, fontsize=16, y=1.0)

    plt.tight_layout()
    return fig