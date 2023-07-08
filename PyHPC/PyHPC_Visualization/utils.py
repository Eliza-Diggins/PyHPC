import logging
import os
import pathlib as pt
import warnings

import numpy as np
import sympy as sym
import yaml
import yt

from PyHPC.PyHPC_Core.configuration import read_config

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

# -------------------------------------------------------------------------------------------------------------------- #
# Constants ========================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #

def assert_kwargs(func, kwargs):
    """
    This is a utility function to force all of the plotting functions to have valid kwargs.

    Parameters
    ----------
    func: str or callaable
        The name of the function which is being assembled.
    kwargs: dict of any
        The dictionary containing the provided (but not complete) list of kwargs.

    Returns
    -------
    kwargs: dict
        The completed set of kwargs drawn from the supplied values and from ``_mdir``.

    Examples
    --------
    >>> data = assert_kwargs("uplots.projection_plot",{"main":{}})
    >>> assert len(data)
    """
    #  Cleanup
    # ----------------------------------------------------------------------------------------------------------------- #
    if not isinstance(func, str):
        func = func.__name__

    #  Search
    # ----------------------------------------------------------------------------------------------------------------- #
    for k, v in _mdir["Functions"][func]["kwargs"].items():
        if isinstance(v, dict):
            if k in kwargs:
                for item, value in v.items():
                    if (item not in kwargs[k]) and (value != None):
                        kwargs[k][item] = value
                    else:
                        pass
            else:
                kwargs[k] = v
        else:
            if k not in kwargs and v is not None:
                kwargs[k] = v

    return kwargs

# -------------------------------------------------------------------------------------------------------------------- #
# Builtin Alpha RAMPS================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
def linramp(vals, minval, maxval):
    return (vals - vals.min()) / (vals.max() - vals.min())

_ramp_functions = {
    "linear": linramp
}
# -------------------------------------------------------------------------------------------------------------------- #
# Transfer Functions ================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
def build_transfer_function(directive):
    """
    Builds a ``TransferFunction`` for volume rendering from a ``directive`` dictionary.

    Parameters
    ----------
    directive: dict
        The ``directive`` containing all of the necessary settings to specify the transfer function.

    Returns
    -------
    yt.ColorTransferFunction
        The resulting transfer function

    Notes
    -----

    The Directive
    ^^^^^^^^^^^^^
    Like many ``PyHPC`` functions, this function is designed to be versatile to use via a directive dictionary, typically
    linked to a ``PlotDirective`` ``.yaml`` file somewhere. The directive structure for the ``TransferFunction`` is somewhat
    unique, and so we describe it here.

    The ``Directive`` is structured as follows:

    .. code-block:: yaml
        #
        # -- Transfer Function (Model) Directive
        #
        args:
            - "<MODE>" #--> MODE specifies what type of transfer function to create.
            - "<BOUNDS>" #--> TUPLE of the bounds on this transfer function.
        kwargs:
            main:
                grey_opacity: true #-> This determines if low values are opaque or not. False will brighten things.
                cmap: "plt.cm.ice"
                log: true
                ramp_function: "<expression>" # (Optional)
            layers:
                #
                # -- Layers are only important if ``mode == "continuous"``.
                #
                layer_i:
                    position: "<x-position>" where in the domain to position the layer.
                    width: "<width>" The width of the corresponding gaussian.
                    color: "<color>" (SEE NOTES)
                    scale: null
                layer_2: {}

    Details
    ^^^^^^^
    There are some important details to keep track of here:

    - **COLOR**: Color is determined by the form of the ``color`` kwarg in each layer. There are 3 possibilities:
      #. (``cmap`` specified in ``main`` and ``color`` is a ``str``): In this case, ``color`` is interpretted as a **colormap**
      and overrides ``cmap``.

      .. attention::
        The sample from the colormap is done based on the ``position`` of the layer.

      #. (``cmap`` specified in ``main`` and ``color`` not included): We assume that the sampling is done from ``cmap``.
      #. (``color`` is a 4-tuple / list): This specifies the value of the color manually for that layer.
      #. (``color`` and ``cmap`` are missing): ``raise ValueError``.
    - **POSITION**: Each layer may be specified with a given position; however, if the position is not specified, then
      one of two things will occur:
      #. If ``position`` is missing in **all** layers: they are then evenly distributed in order specified.
      #. If ``position`` is only missing for some items: ``raise ValueError``.
    - **MODE**: There are 2 modes: ``continuous`` and ``discrete``. If a ``TransferFunction`` is ``continuous``, then
      any specified ``layers`` are ignored, and the sample is done continuously from ``cmap``. If the ``mode`` is
      ``discrete``, then the layers are specifically specified.
      - If ``mode`` is ``continuous``, then the additional ``kwarg`` ``ramp_function`` can also be included. If it exists,
        it will specify the ``alpha`` transition as a function of field value. These must match one of the implemented functions.

    Examples
    --------

    EX. 1
    ^^^^^

    >>> ds = yt.load(os.path.join(pt.Path(__file__).parents[2],"tests","test_core","output_00001"))
    >>> sc = yt.create_scene(ds, lens_type="perspective")
    >>> source = sc[0]
    >>> c = source.set_log(True)
    >>> direc = {
    ...          "args":["continuous",(1e-31,5e-27)],
    ...          "kwargs": {
    ...                    "cmap":"inferno",
    ...                    "log": True,
    ...                    "ramp_function":"linear"
    ...                    }
    ...          }
    >>> tf = build_transfer_function(direc)
    >>> source.tfh.tf = tf
    >>> source.tfh.bounds = (1e-31,5e-27)
    >>> source.tfh.plot(os.path.join(pt.Path(__file__).parents[2],"tests","outputs","tf_test1.png"))

    An Example of a continuous transfer function

    .. image:: ../../tests/outputs/tf_test1.png

    EX. 2
    ^^^^^

    >>> ds = yt.load(os.path.join(pt.Path(__file__).parents[2],"tests","test_core","output_00001"))
    >>> sc = yt.create_scene(ds, lens_type="perspective")
    >>> source = sc[0]
    >>> c = source.set_log(True)
    >>> direc = {
    ...          "args":["discrete",(1e-31,5e-27)],
    ...          "kwargs": {
    ...                    "cmap":"hsv",
    ...                    "log": True,
    ...                    "layers": {
    ...                         "layer_1":{
    ...                     },
    ...                     "layer_2":{
    ...                     },
    ...                     "layer_3":{
    ...                     },
    ...                     "layer_4":{
    ...                     },
    ...                     "layer_5":{
    ...                     }
    ...                    }
    ...                    }
    ...          }
    >>> tf = build_transfer_function(direc)
    >>> source.tfh.tf = tf
    >>> source.tfh.bounds = (1e-31,5e-27)
    >>> source.tfh.plot(os.path.join(pt.Path(__file__).parents[2],"tests","outputs","tf_test2.png"))

        .. image:: ../../tests/outputs/tf_test2.png

    """
    #  Logging and debugging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug(f"Initializing a TransferFunction object with mode {directive['args'][1]}.")

    assert directive["args"][0] in ["continuous", "discrete"], "Specified mode was invalid."
    assert isinstance(directive["args"][1], (tuple, list)) and len(directive["args"][1]) == 2, "Bounds were invalid."

    mode, bounds = directive["args"]

    # - Correcting bounds -#
    if "log" in directive["kwargs"] and directive["kwargs"]["log"]:
        log = True
        bounds = np.log10(bounds)
    else:
        log = False
        pass

    #  Building the base transfer function
    # ----------------------------------------------------------------------------------------------------------------- #
    tf = yt.ColorTransferFunction(bounds)

    # Parsing
    # ----------------------------------------------------------------------------------------------------------------- #
    if mode == "continuous":
        # - Initializing the continuous transfer function option.
        assert "cmap" in directive["kwargs"], "Mode = continuous requires that the colormap is specified."

        # - can we initialize a ramp function.
        if 'ramp_function' in directive["kwargs"] and directive["kwargs"]["ramp_function"] is not None:
            # - located a ramp-function, attempting a conversion
            try:
                ramp_function = _ramp_functions[directive["kwargs"]["ramp_function"]]
            except KeyError:
                modlog.warning(f"Failed to recognize the ramp function {directive['kwargs']['ramp_function']}.")
                ramp_function = None
        else:
            ramp_function = None

        # Initializing the proper transfer function -------------------------------------------------#
        modlog.debug(f"{bounds},{directive['kwargs']['cmap']} and {ramp_function}")
        tf.map_to_colormap(*bounds, colormap=directive["kwargs"]["cmap"], scale_func=ramp_function)

        return tf


    else:
        # --> mode is discrete, we need to establish layers.
        assert "layers" in directive["kwargs"], "Mode = discrete requires that layers are specified."

        if all("position" in v for v in directive["kwargs"]["layers"].values()) and ("cmap" in directive["kwargs"] or all(
            "color" in v  for v in directive["kwargs"]["layers"].values())):

            #  Coercing the colors
            # ----------------------------------------------------------------------------------------------------------------- #
            for layer,data in directive["kwargs"]["layers"].items():
                if "color" not in data:
                    directive["kwargs"]["layers"]["color"] = directive["kwargs"]["cmap"]

            #  Adding
            # ----------------------------------------------------------------------------------------------------------------- #
            for layer,data in directive["kwargs"]["layers"].items():
                if isinstance(data["color"],str):
                    tf.sample_colormap(np.log10(data["position"]) if log else data["position"],
                                       w=data["width"],
                                       scale=data["scale"],
                                       colormap=data["color"]
                                       )
                else:
                    tf.add_gaussian(np.log10(data["position"]) if log else data["position"],
                                       w=data["width"],
                                       height=data["color"])

        elif (not any("position" in v for v in directive["kwargs"]["layers"].values()) and (
                "cmap" in directive["kwargs"])):
            tf.add_layers(len(directive["kwargs"]["layers"]),
                          colormap=directive["kwargs"]["cmap"])
        else:
            raise SyntaxError("The directive did not have compatible color values.")

        return tf