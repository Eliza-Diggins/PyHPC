"""
The core module of the ``PyHPC_Visualization`` module.
"""
import logging
import os
import pathlib as pt
import warnings

import matplotlib.pyplot as plt
import yaml

from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.errors import PyHPC_Error
from PyHPC.PyHPC_Visualization import uplots
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
                    modifiers: {} # These are additional functions to act on the retured object.
                function2:
                    args: [":ds",":f"]
                    kwargs:
                        "cmap":"Blues"
                    modifiers: {}

    Examples
    --------
    >>> import os
    >>> import pathlib as pt
    >>> import numpy as np
    >>> plot_directive = PlotDirective(os.path.join(pt.Path(__file__).parents[2],"tests","test_data","directive-2.yaml"))
    >>> q = plot_directive.get_all_special_entities()
    >>> assert all(i in ["x","y1","y2"] for i in q)
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

        #  Managing Functions
        # ----------------------------------------------------------------------------------------------------------------- #
        #: tracks the initialization errors.
        _errors = []

        #: functions associated with the plots. ``{subplot_id: {f1: {},f2:{},...}``.
        self.functions = []  #: initializing the self.functions dictionary.
        for function_key, function_val in self._raw["Figure"]["Functions"].items():
            # - Is the function actually in the master directive? - #
            _left_over_function_key = function_key
            if "\\\\" in function_key:
                function_key = function_key.split("\\\\")[0]

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

            # - Adding kwargs - #
            kwargs = self._get_kwargs(self._raw["Figure"]["Functions"][_left_over_function_key]["kwargs"],
                                      _mdir["Functions"][function_key]["kwargs"])

            try:
                if len(function_name):
                    self.functions.append({getattr(globals()[function_root], function_name): {
                        "args": function_val["args"], "kwargs": kwargs}})

                else:
                    self.functions.append({globals()[function_root]: {"args": function_val["args"], "kwargs": kwargs}})

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
                _args, _kwargs = self._raw["Figure"]["Parameters"][method]["args"], \
                                 self._raw["Figure"]["Parameters"][method]["kwargs"]
            else:
                _args, _kwargs = vals["args"], vals["kwargs"]
            try:
                getattr(self.figure, method)(*_args, **_kwargs)
            except AttributeError:
                modlog.warning("Failed to identify figure attribute %s." % method)

    def _get_kwargs(self, explicit_kwargs, master_kwargs):
        kwargs = explicit_kwargs
        for k, v in master_kwargs.items():
            if isinstance(v, dict) and k in explicit_kwargs:
                try:
                    kwargs[k] = self._get_kwargs(explicit_kwargs[k], master_kwargs[k])
                except KeyError:
                    raise ValueError("Failed to find %s in the master directive or the explicit directive." % k)
            elif isinstance(v, dict) and k not in explicit_kwargs:
                kwargs[k] = v
            else:
                if k not in explicit_kwargs:
                    kwargs[k] = v
                else:
                    kwargs[k] = explicit_kwargs[k]
        return kwargs

    def get_all_special_entities(self, dictionary=None):
        """
        Returns all of the ``special`` kwargs present in the ``PlotDirective``.

        Returns
        -------
        list
            The special values.
        """
        if dictionary is None:
            dictionary = self._raw

        specials = []
        for k, v in dictionary.items():
            if isinstance(v, dict):
                specials += self.get_all_special_entities(dictionary=v)
            elif isinstance(v, list):
                specials += [i for i in v if i[0] == "%" and i[-1] == "%"]
            else:
                if len(str(v)) and (str(v)[0] == "%" and str(v)[-1] == "%"):
                    specials += v

        return list(set([i.replace("%", "") for i in specials]))


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
    tuple of str,plt.Figure
        ``(status,figure)``.


    Examples
    --------

    Example 1
    ^^^^^^^^^

    **PlotDirective:**

    .. include:: ../../tests/test_data/directive-2.yaml
        :code:

    >>> import os
    >>> import pathlib as pt
    >>> import numpy as np
    >>> plot_directive = PlotDirective(os.path.join(pt.Path(__file__).parents[2],"tests","test_data","directive-2.yaml"))
    >>> x = np.linspace(0,2*np.pi,1000)
    >>> y1,y2 = np.sin(x),np.cos(x)
    >>> fig = generate_image(plot_directive,x=x,y1=y1,y2=y2)[1]
    >>> pt.Path(os.path.join(pt.Path(__file__).parents[2],"tests","outputs")).mkdir(parents=True,exist_ok=True)
    >>> plt.savefig(os.path.join(pt.Path(__file__).parents[2],"tests","outputs","directive-2.png"))

    .. figure:: ../../tests/outputs/directive-2.png

        Corresponding image output from example 1.

    Example 2
    ^^^^^^^^^

    **PlotDirective:**

    .. include:: ../../tests/test_data/directive-1.yaml
        :code:

    >>> import os
    >>> import pathlib as pt
    >>> import numpy as np
    >>> import yt
    >>> plot_directive = PlotDirective(os.path.join(pt.Path(__file__).parents[2],"tests","test_data","directive-1.yaml"))
    >>> fig = generate_image(plot_directive,
    ...                      path=os.path.join(pt.Path(__file__).parents[2],"tests","test_core","output_00001"),
    ...                      field = ("gas","temperature"))[1]
    >>> plt.savefig(os.path.join(pt.Path(__file__).parents[2],"tests","outputs","directive-1.png"))

        .. figure:: ../../tests/outputs/directive-1.png

        Corresponding image output from example 2.
    """
    # Logging and Setup
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Generating image from a directive...")

    #  Selecting by directive type
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("\tDetermining the directive's correct path.")
    if list(image_directive._raw["Figure"]["Functions"].keys()) == ["uplots.volume_render"]:
        modlog.debug("\t\tPATH=volume_render.")
        f = image_directive.functions[0]
        func = list(f.keys())[0]
        vals = f[func]

        _args = [i if (str(i)[0] != "%") else kwargs[str(i).replace("%", "")] for i in list(vals["args"])]
        _kwargs = _parse_kwargs(vals["kwargs"], kwargs)
        return "volume_render", func(*_args, **_kwargs)
    else:
        modlog.debug("\t\tPATH=STANDARD")
        for f in image_directive.functions:
            modlog.debug("Generating function %s." % f)
            func = list(f.keys())[0]
            vals = f[func]
            if not "special" in vals["kwargs"]:
                vals["kwargs"]["special"] = {}
            vals["kwargs"]["special"]["figure"] = image_directive.figure

            _args = [i if (str(i)[0] != "%") else kwargs[str(i).replace("%", "")] for i in list(vals["args"])]
            _kwargs = _parse_kwargs(vals["kwargs"], kwargs)
            func(*_args, **_kwargs)

        return "normal", image_directive.figure


def _parse_kwargs(dictionary, kwargs):
    _out = {}
    for k, v in dictionary.items():
        if isinstance(v, dict):
            _out[k] = _parse_kwargs(v, kwargs)
        else:
            _out[k] = (v if str(v)[0] != "%" else kwargs[str(v).replace("%", "")])

    return _out
