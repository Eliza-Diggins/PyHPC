"""
Standard utility functions for wide useage throughout the system.
"""
import json
import operator
import os
import pathlib as pt
from functools import reduce

import numpy as np

from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.log import get_module_logger

# -------------------------------------------------------------------------------------------------------------------- #
#  Setup  ============================================================================================================ #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "PyHPC:PyHPC_Utils"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
__text_file_directory = os.path.join(pt.Path(__file__).parents[1], "bin", "str")
modlog = get_module_logger(_location, _filename)
CONFIG = read_config()
__GSV = {}  # -> This global variable allows for communication between the listener and the function


# -------------------------------------------------------------------------------------------------------------------- #
#  Functions    ====================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def getFromDict(dataDict, mapList):
    """
    Fetches the values from a nested ``dataDict``.
    Parameters
    ----------
    dataDict: dict
        The nested dictionary from which to pull the data.
    mapList: list of str
        The list of keys at which to locate the value.

    Returns
    -------
    any
        The value at ``dataDict[mapList[0]][mapList[...]][mapList[-1]]``.
    """
    return reduce(operator.getitem, mapList, dataDict)


def setInDict(dataDict, mapList, value):
    """
    Sets the value of ``dataDict`` at ``mapList`` to ``value``.
    Parameters
    ----------
    dataDict : dict
        The dictionary in which to set the data.
    mapList : list of str
        The sequence of keys to locate the entry to change.
    value : any
        The value to set.

    Returns
    -------
    None

    """
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value

