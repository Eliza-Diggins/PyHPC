"""
Utility functions for the ``PyHPC_Visualization`` library.
"""
import json
import logging
import pathlib as pt

import numpy as np
import os
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.errors import PyHPC_Error
from PyHPC.PyHPC_Utils.text_display_utilities import get_dict_str
# -------------------------------------------------------------------------------------------------------------------- #
# SETUP ============================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
_filename = pt.Path(__file__).name.replace(".py", "")
modlog = logging.getLogger(__name__)
CONFIG = read_config()

with open(os.path.join(pt.Path(__file__).parents[1],"bin","lib","img","master_directive.json")) as file:
    _mdir = json.load(file)

# -------------------------------------------------------------------------------------------------------------------- #
#  Class ============================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
class PlotDirective:
    """
    The ``PlotDirective`` class is a realization / data container for the underlying data contained in the ``directive``
    dictionary passed to the ``PlotDirective`` initializer. This reads and manages all of the ``args`` and ``kwargs``
    associated with the execution process and prepares them to be executed.

    Parameters
    ----------
    directive: dict or str
        The directive associated with the plotting procedure. if ``str``, then we assume this is a file path and will
        read the ``json`` data directly from the file; otherwise, the dictionary should already be in the form of
        the specified directive.
    """

    def __init__(self, directive):
        #  Debugging and Management
        # ------------------------------------------------------------------------------------------------------------ #
        modlog.debug("Generating a ``PlotDirective`` object from directive type %s." % (type(directive)))

        #  Reading the directive
        # ----------------------------------------------------------------------------------------------------------------- #
        if isinstance(directive, str):
            try:
                with open(directive, "r+") as file:
                    self.directive = json.load(file)
            except FileNotFoundError:
                modlog.exception("Failed to find directive at %s." % directive)
                raise PyHPC_Error("Failed to find directive at %s." % directive)
        elif not isinstance(directive, dict):
            raise TypeError("The directive had type %s, which is not valid." % type(directive))
        else:
            modlog.debug("Successfully loaded base directive.")
            self.directive = directive


# -------------------------------------------------------------------------------------------------------------------- #
# Functions ========================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def generate_gridspec(figure, grid_array, *args, **kwargs):
    """
    Generates a ``gridspec`` object for plotting from the passed ``grid_array``.
    Parameters
    ----------
    figure: plt.figure
        The ``mathplotlib`` figure object which is the holder of the gridspec.
    grid_array: ndarray or list of list of str
        The ``grid_array`` shows the visual layout of the desired grid. Each subplot should be numbered starting with
        ``0`` and increasing. Blank spaces in the grid should have ``""`` as filler values.

    Returns
    -------
    dict
        The dictionary containing the sub-grids. ``{grid_number:axes}``.
    plt.gridspec.GridSpec
        The overall gridspec object for the plot.
    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> fig = plt.figure()
    >>> grid = generate_gridspec(fig,[["1","1"],["2","2"]])
    GridSpec(2, 2) {'1': <AxesSubplot:>, '2': <AxesSubplot:>}
    """
    #  Managing typing.
    # ----------------------------------------------------------------------------------------------------------------- #
    if not isinstance(grid_array, np.ndarray):
        grid_array = np.array(grid_array)

    return_dict = {}
    gs = plt.GridSpec(**{k: v for k, v in zip(["ncols", "nrows"], grid_array.shape)}, *args, **kwargs)

    keys = [str(i) for i in sorted([int(k) for k in list(set(list(grid_array.ravel())))])]
    for key in keys:
        matches = np.array(np.where((grid_array) == key))
        x_range, y_range = (np.amin(matches[:, 0]), np.amax(matches[:, 0])), (
            np.amin(matches[:, 1]), np.amax(matches[:, 1]))

        if x_range[1] == x_range[0]:
            x_range = (x_range[0], x_range[1] + 1)
        if y_range[1] == y_range[0]:
            y_range = (y_range[0], y_range[1] + 1)

        return_dict[key] = figure.add_subplot(gs[x_range[0]:x_range[1], y_range[0]:y_range[1]])

    print(gs, return_dict)

def parse_directive(directive,fail_on_errors = True):
    """
    parses the input directive and checks the formatting.
    Parameters
    ----------
    directive: dict
        The directive to parse through.

    fail_on_errors: bool
        If ``True``, this will fail if there are any errors at all, which will keep behavior consistent.

        .. attention::
            Turn off this setting at your own risk. This can produce odd behavior if you don't know what you're doing.

    Returns
    -------
    list of callable
        The ``functions`` specified in the directive.
    list of list of any
        The ``args``.
    list of dict
        The ``kwargs``.
    np.ndarray
        The ``gridspec`` grid specified in the ``plotting_directive``. If it is not included, then this will
        return with the value ``None``.
    bool
        ``True`` if initialization was a success, ``False`` if something failed to execute correct.
    str
        Message about runtime success.

    """
    #  Debugging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Parsing the directive %s."%get_dict_str(directive))

    #  Pulling functions
    # ----------------------------------------------------------------------------------------------------------------- #
    _ret_functions = []
    errors = []
    for directive_function in directive["functions"]:
        # - Is the function actually in the master directive? - #
        if not directive_function in _mdir["functions"]:
            errors.append({"type":"function","name":directive_function,"msg":"Failed to find in master_directive"})
        else:
            pass

        # - Can I add the function to the return functions? - #
        try:
            exit()
        except:
            pass


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    fig = plt.figure()
    grid = generate_gridspec(fig, [["1", "1"], ["2", "2"]])
