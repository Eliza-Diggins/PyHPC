"""
The core module of the ``PyHPC_Visualization`` module.
"""
import logging
import os
import pathlib as pt
import warnings

import matplotlib.pyplot as plt
import numpy as np
import yaml
import PyHPC.PyHPC_Visualization.uplots as uplots
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.errors import PyHPC_Error

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_Visualization"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = logging.getLogger(__name__)

# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

with open(os.path.join(pt.Path(__file__).parents[1], "bin", "lib", "img", "master_directive.yaml")) as file:
    _mdir = yaml.load(file, yaml.FullLoader)


class PlotDirective:
    """
    The ``PlotDirective`` class which is an object wrapper for ``.pd`` directive files.

    Parameters
    ----------
    directive_loc: str
        The ``str`` path to the file containing the ``directive`` object.

    Attributes
    ----------

    Notes
    -----

    The format of the underlying file must meet the standards described in the documentation on plotting. To reiterate,

    .. code-block:: yaml

        information: |
            This is never read and can include any important information about the plot.

        #Figure is the core of the Pdirective and contains all of the data
        #corresponding to the intended figure including its subplots.

        Figure:
            grid:
                # The grid can be used to specify the gridspec layout desired.
                - [1,1,2,2]
                - [1,1,2,2]
            Subplots:

            #Subplots are the most important part of the Pdirective. Each one
            #contains the function headers that correspond to the necessary functions
            #to actually produce the visual.
            # !Subplots are indexed by number!
            # ! Each subplot must have "Functions" and "Parameters".
            #
                1:
                    Functions:
                        # Each function in Function should be named by its correct reference (in the code). To use
                        # yt.ProjectionPlot, you title it yt.ProjectionPlot as the key in the entry.
                        #
                        #    ! If you need to re-use a function in a SINGLE subplot, label it (N)function
                        #    ! where N is the index.
                        #
                        # Each function specified must have entries: args and kwargs. These must correspond to those
                        # recognized in the program itself. See the section below on ease of use for more detailed
                        # information on this.
                        #
                        function1:
                            args: ["x","y","z"]
                            kwargs:
                                "color": "red"
                        function2:
                            args: [":ds",":f"]
                            kwargs:
                                "cmap":"Blues"
                    Parameters:
                        # The Parameters are those things which we wish to constrain about the subplot object itself.
                        # Each Parameter must have a command ".something()", its args, and its kwargs. These are
                        # run after each other plotting procedure has been finished and are done in order.
                        .set_xlim:
                            args: [[0,1]]
                            kwargs: {}
                2:
                    Functions:
                        function1:
                            args: ["x","y","z"]
                            kwargs:
                                "color": "red"
                    Parameters: {}
            Parameters:
                # These parameters are the same as those described above for subplots; however, this time they apply
                # specifically to the figure object instead.
                .set_size_inches:
                    args: [[10,10]]
                    kwargs: {}
        PostProcessing:
            # The post processing part of the directive can be excluded if unwanted. With this, you can change the default
            # behavior after execution. There are two settings: post process, which is a pure python script to be executed
            # after the course of the computation is completed.
            #
            # !! WARNING: this uses the exec() function. Because there are no security threats, this fault will be
            #             permitted to persist; however, user idiocy could lead to unintended consequences for the
            #              system.
            #
            # The second option in post processing is the output field, which can specify a save location for the finished
            # plot.
            #
            output: None
            script: |
                pass
    """

    def __init__(self, directive_loc):
        #  Logging
        # ----------------------------------------------------------------------------------------------------------------- #
        modlog.debug("Loading PlotDirective at %s." % directive_loc)

        #  Attempting to load
        # ----------------------------------------------------------------------------------------------------------------- #
        try:
            with open(directive_loc, "r") as file:
                self._raw = yaml.load(file, yaml.FullLoader)
        except FileNotFoundError:
            raise PyHPC_Error("Failed to initialize PlotDirective at %s due to missing file." % directive_loc)

        #  Parsing and generating
        # ----------------------------------------------------------------------------------------------------------------- #
        modlog.debug("Generating the figure...")
        #: The figure connected to the ``directive``.
        self.figure = plt.figure()

        # - Setting figure properties -#
        self._assert_figure_structure()

        # - managing the figure behavior -#
        _shape = np.array(self._raw['Figure']["grid"]).shape
        gs = plt.GridSpec(**{k: v for k, v in zip(["ncols", "nrows"], _shape)})

        # - adding the figures -#
        #: subplots connected with the directive. Indexed by integers.
        self.subplots = {}
        keys = [i for i in sorted([int(k) for k in list(set(list(np.array(self._raw["Figure"]["grid"]).ravel())))])]
        for key in keys:
            matches = np.array(np.where((np.array(self._raw["Figure"]["grid"])) == key))
            x_range, y_range = slice(np.amin(matches[0, :]), np.amax(matches[0, :]) + 1, 1), slice(
                np.amin(matches[1, :]), np.amax(matches[1, :]) + 1, 1)

            self.subplots[key] = self.figure.add_subplot(gs[y_range, x_range])
            self._assert_subplot_structure(key)

        #  Managing Functions
        # ----------------------------------------------------------------------------------------------------------------- #
        #: tracks the initialization errors.
        _errors = []

        #: functions associated with the plots. ``{subplot_id: {f1: {},f2:{},...}``.
        self.functions = {k: {} for k in self.subplots}  #: initializing the self.functions dictionary.

        for subplot, subplot_data in self._raw["Figure"]["Subplots"].items():
            modlog.debug("initializing subplot %s." % subplot)
            for function_key, function_val in subplot_data["Functions"].items():
                # - Is the function actually in the master directive? - #
                if not function_key in _mdir["Functions"]:
                    _errors.append(
                        {"type": "function", "name": function_key, "msg": "Failed to find in master_directive"})
                    continue
                else:
                    pass
            # - Can I add the function to the return functions? - #

            if "." in function_key:
                function_root = function_key.split(".")[0]
                function_name = function_key.replace(function_root + ".", "")
            else:
                function_root = function_key
                function_name = ""

            if function_key[0] == "(":
                function_root = function_root.split(")")[1]

            # - Adding kwargs - #
            kwargs = {**{k: v for k, v in _mdir["Functions"][function_key]["kwargs"].items() if
                         k not in function_val["kwargs"]}, **function_val["kwargs"]}

            try:
                if len(function_name):
                    self.functions[subplot][getattr(globals()[function_root], function_name)] = {
                        "args": function_val["args"], "kwargs": kwargs}

                else:
                    self.functions[subplot][globals()[function_root]] = {"args": function_val["args"], "kwargs": kwargs}

            except KeyError as err:
                _errors.append(
                    {"type": "function", "name": function_key,
                     "msg" : "Failed to find function in globals: %s." % err.__repr__()})
        if len(_errors):
            raise ValueError(_errors)
    # -------------------------------------------------------------------------------------------------------------------- #
    # Methods ============================================================================================================ #
    # -------------------------------------------------------------------------------------------------------------------- #
    def __str__(self):
        return "PlotDirective Object - %s funcs" % (len(self.functions))

    def __repr__(self):
        return "PlotDirective Object - %s" % (self._raw)

    def _assert_figure_structure(self):

        for method, vals in _mdir["Structures"]["Figure"]["commands"].items():
            if method in self._raw["Figure"]["Parameters"]:
                _args, _kwargs = self._raw["Figure"]["Parameters"][method]["args"], self._raw["Figure"]["Parameters"][method]["kwargs"]
            else:
                _args,_kwargs = vals["args"],vals["kwargs"]
            try:
                getattr(self.figure, method)(*_args, **_kwargs)
            except AttributeError:
                modlog.warning("Failed to identify figure attribute %s." % method)

    def _assert_subplot_structure(self, subplot):
        for method, vals in _mdir["Structures"]["Subplot"]["commands"].items():
            if method in self._raw["Figure"]["Subplots"][subplot]["Parameters"]:
                _args, _kwargs = self._raw["Figure"]["Subplots"][subplot]["Parameters"][method]["args"], self._raw["Figure"]["Subplots"][subplot]["Parameters"][method]["kwargs"]
            else:
                _args,_kwargs = vals["args"],vals["kwargs"]

            try:
                getattr(self.subplots[subplot], method)(*_args, **_kwargs)
            except AttributeError:
                modlog.warning("Failed to identify subplot attribute %s." % method)


# -------------------------------------------------------------------------------------------------------------------- #
#  Functions ========================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #

def generate_image(image_directive, **kwargs):
    """
    Generates the image based on the directive ``image_directive``. The data must be provided with appropriate keys
    through the ``kwargs``.

    .. attention::
        For further information on ``PlotDirective`` objects and the entire plotting process in ``PyHPC``, see documentation
        for ``PyHPC.PyHPC_Visualization``.

    Parameters
    ----------
    image_directive: PlotDirective
        The ``PlotDirective`` object corresponding to the plotting routine.
    kwargs: dict
        The dictionary containing the information on data sources. For any wildcard value in ``kwargs`` or ``args`` to
        the ``directive``, an associated data specifier must be included in args.


    Returns
    -------
    plt.Figure
        The figure object.

    Examples
    --------

    Example 1
    ^^^^^^^^^

    **PlotDirective:**

    .. include:: ../../tests/examples/directive-2.yaml
        :code:

    >>> import os
    >>> import pathlib as pt
    >>> import numpy as np
    >>> plot_directive = PlotDirective(os.path.join(pt.Path(__file__).parents[2],"tests","examples","directive-2.yaml"))
    >>> x = np.linspace(0,2*np.pi,1000)
    >>> y1,y2 = np.sin(x),np.cos(x)
    >>> fig = generate_image(plot_directive,x=x,y1=y1,y2=y2)
    >>> plt.savefig(os.path.join(pt.Path(__file__).parents[2],"tests","examples","directive-2.png"))

    .. figure:: ../../tests/examples/directive-2.png

        Corresponding image output from example 1.
    """
    # Logging and Setup
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Generating image for directive %s.")
    #  Reading information from the directive.
    # ----------------------------------------------------------------------------------------------------------------- #
    for subplot_id, subplot in image_directive.subplots.items():
        for func, vals in image_directive.functions[subplot_id].items():
            kwargs['a'] = subplot
            _args = [i if (str(i)[0] != "%") else kwargs[str(i).replace("%", "")] for i in list(vals["args"])]

            _kwargs = {k: (v if str(v)[0] != "%" else kwargs[str(v).replace("%", "")]) for k, v
                       in vals["kwargs"].items()}
            func(*_args, **_kwargs, axes=subplot)

    return image_directive.figure
