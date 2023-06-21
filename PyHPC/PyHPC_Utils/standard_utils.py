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
import logging

# -------------------------------------------------------------------------------------------------------------------- #
#  Setup  ============================================================================================================ #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "PyHPC:PyHPC_Utils"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
__text_file_directory = os.path.join(pt.Path(__file__).parents[1], "bin", "str")
modlog = logging.getLogger(__name__)
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
        The value at ``dataDict[mapList[0]][mapList[...]][mapList[-1]]``.
    """
    return reduce(operator.getitem, mapList, dataDict)

def isInDict(dataDict,mapList):
    try:
        reduce(operator.getitem, mapList, dataDict)
        return True
    except KeyError:
        return False
def setInDict(dataDict, mapList, value):
    """
    sets the value located at ``mapList`` to ``value`` in ``dataDict``.

    Parameters
    ----------
    dataDict : dict
        The dictionary in which to set the value.
    mapList: list
        The correct placement location.
    value: any
        The value to set.

    Returns
    -------


    """
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value

