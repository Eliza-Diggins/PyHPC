"""
Utility functions for the ``PyHPC_Visualization`` library.
"""
import json
import logging
import os
import pathlib as pt

import matplotlib.pyplot as plt
import numpy as np

from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.errors import PyHPC_Error
from PyHPC.PyHPC_Utils.text_display_utilities import get_dict_str
import yaml
# -------------------------------------------------------------------------------------------------------------------- #
# SETUP ============================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
_filename = pt.Path(__file__).name.replace(".py", "")
modlog = logging.getLogger(__name__)
CONFIG = read_config()

with open(os.path.join(pt.Path(__file__).parents[1], "bin", "lib", "img", "master_directive.yaml")) as file:
    _mdir = yaml.load(file,yaml.FullLoader)


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

    Examples
    --------
    >>> direct = PlotDirective(str(os.path.join(pt.Path(__file__).parents[2],"tests","examples","directive-2.yaml")))
    >>> assert len(direct.errors)==0
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
                    self.directive = yaml.load(file,yaml.FullLoader)
            except FileNotFoundError:
                modlog.exception("Failed to find directive at %s." % directive)
                raise PyHPC_Error("Failed to find directive at %s." % directive)
        elif not isinstance(directive, dict):
            raise TypeError("The directive had type %s, which is not valid." % type(directive))
        else:
            modlog.debug("Successfully loaded base directive.")
            self.directive = directive

        #  Cleaning the directive
        # ----------------------------------------------------------------------------------------------------------------- #
        f, a, kw, er, stat, msg = parse_directive(self.directive, fail_on_errors=False)

        if not len(er):
            modlog.debug("Initialized the directive successfully")
        else:
            modlog.warning("There are errors in the directive reading.")

        self.functions,self.args,self.kwargs = f,a,kw
        self.errors = er

        #  Generating the grid spec
        # ----------------------------------------------------------------------------------------------------------------- #
        self.figure = plt.figure()

        self.gs,self.axes = generate_gridspec(self.figure,self.directive["gridspec"])


    def assert_kwargs(self,obj,id=None):
        """
        This function asserts directive kwargs onto a specific object. This is done by looking up the name of
        the object and determining if any kwargs apply.
        Parameters
        ----------
        obj: any
            The object onto which to assert itself.
        Returns
        -------
        None
        Examples
        --------
        >>> import matplotlib.pyplot as plt
        >>> import numpy as np
        >>> directive = PlotDirective(str(os.path.join(pt.Path(__file__).parents[2],"tests","examples","directive-2.yaml")))
        >>> fig = plt.Figure()
        >>> assert list(fig.get_size_inches()) == [6.4,4.8]
        >>> directive.assert_kwargs(fig)
        >>> assert list(fig.get_size_inches()) == [10,10]

        """
        if not id:
            id = 0
        if str(type(obj).__name__) in self.kwargs[id]:
            for k,v in self.kwargs[id][type(obj).__name__].items():
                modlog.debug("%s on %s with value %s,%s."%(v["command"],obj,v["args"],v["kwargs"]))
                getattr(obj,v["command"][1:])(*v["args"],**v["kwargs"])
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
    """
    #  Managing typing.
    # ----------------------------------------------------------------------------------------------------------------- #
    if not isinstance(grid_array, np.ndarray):
        grid_array = np.array(grid_array)

    return_dict = {}
    gs = plt.GridSpec(*args, **{k: v for k, v in zip(["ncols", "nrows"], grid_array.shape)}, **kwargs)

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
    return gs,return_dict


def parse_directive(directive, fail_on_errors=True):
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
    list of dict
        The errors.
    bool
        ``True`` if initialization was a success, ``False`` if something failed to execute correct.
    str
        Message about runtime success.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> with open(os.path.join(pt.Path(__file__).parents[2], "tests", "examples", "directive-2.yaml")) as file: data = yaml.load(file,yaml.FullLoader)
    >>> f,a,kw,er,stat,msg = parse_directive(data,fail_on_errors=False)
    >>> assert stat

    """
    #  Debugging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Parsing the directive %s." % get_dict_str(directive))

    #  Pulling functions
    # ----------------------------------------------------------------------------------------------------------------- #
    _ret_functions = []
    args, kwargs = [], []
    errors = []
    for directive_function, directive_data in directive["functions"].items():
        # - Is the function actually in the master directive? - #
        if not directive_function in _mdir["functions"]:
            errors.append({"type": "function", "name": directive_function, "msg": "Failed to find in master_directive"})
            continue
        else:
            pass

        # - Can I add the function to the return functions? - #
        function_root = directive_function.split(".")[0]
        function_name = directive_function.replace(function_root + ".", "")

        try:
            if len(function_name):
                _ret_functions.append(getattr(globals()[function_root], function_name))
            else:
                _ret_functions.append(globals()[function_root])
        except KeyError:
            errors.append(
                {"type": "function", "name": directive_function, "msg": "Failed to find function in globals."})
            continue

        #  Finding args and kwargs
        # ----------------------------------------------------------------------------------------------------------------- #
        # - getting available kwargs / args - #
        _available_args, _available_kwargs = _mdir["functions"][directive_function]["args"], \
                                             _mdir["functions"][directive_function]["kwargs"]

        if "inherits" in _mdir["functions"][directive_function]:
            _available_kwargs = {"main": _available_kwargs,
                                 **{container: {k: v for k, v in _mdir["structures"][container]["kwargs"].items()} for container in
                                    _mdir["functions"][directive_function]["inherits"]}}

        # - checking the args and kwargs - #
        if len(directive_data["args"]) != len(_available_args):
            errors.append({"type": "args", "name": directive_function,
                           "msg" : "Failed to account for %s args in master with %s args in local." % (
                               len(directive_data["args"]), len(_available_args))})
            continue
        for available_family,available_kwargs in _available_kwargs.items():
            if not available_family in directive_data["kwargs"]:
                directive_data["kwargs"][available_family] = available_kwargs
            else:
                for k,v in available_kwargs.items():
                    if k not in directive_data["kwargs"][available_kwargs]:
                        directive_data["kwargs"][available_kwargs][k] = v

        # - Cleaning up kwargs - #
        args.append(directive_data["args"])
        kwargs.append(directive_data["kwargs"])

    if fail_on_errors and len(errors):
        raise ValueError(errors)

    return _ret_functions, args, kwargs, errors, len(errors) == 0, ("pass" if not len(errors) else "failed.")


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np

    directive = PlotDirective(str(os.path.join(pt.Path(__file__).parents[2], "tests", "examples", "directive-2.yaml")))
    fig = plt.Figure()
    assert list(fig.get_size_inches()) == [6.4, 4.8]
    directive.assert_kwargs(fig)
    assert list(fig.get_size_inches()) == [10, 10]
