"""
Standard utility functions for wide useage throughout the system.
"""
import operator
import os
import pathlib as pt
from functools import reduce

from PyHPC_Core.configuration import read_config
from PyHPC_Core.log import get_module_logger

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
    return reduce(operator.getitem, mapList, dataDict)


def setInDict(dataDict, mapList, value):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value
