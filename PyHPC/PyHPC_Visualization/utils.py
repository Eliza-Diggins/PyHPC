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

def assert_kwargs(func,kwargs):
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
    if not isinstance(func,str):
        func = func.__name__

    #  Search
    # ----------------------------------------------------------------------------------------------------------------- #
    for k,v in _mdir["Functions"][func]["kwargs"].items():
        if isinstance(v,dict):
            if k in kwargs:
                for item,value in v.items():
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