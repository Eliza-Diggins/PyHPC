import os
import pathlib as pt
import sys

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from colorama import Fore, Style, Back
from PyHPC_Core.log import get_module_logger
from PyHPC_Core.configuration import read_config
import pathlib as pt
import subprocess
import warnings
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_Utils"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = get_module_logger(_location,_filename)

# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

# -------------------------------------------------------------------------------------------------------------------- #
# Core IO Functions ================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def rclone_listdir(directory) -> list:
    """
    functions as list dir for rclone remote data.
    :param directory: the directory to get the listdir for.
    :return: List of the directory (tuple).
    """
    #  Setup and Debug
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Finding remote ls for directory %s."%directory)

    # performing the command #
    output = subprocess.check_output(["rclone", "lsf", directory, "--max-depth", "1"])
    output = output.decode("utf8").split("\n")[:-1]

    return output

def rclone_isfile(directory)->bool:
    if pt.Path(directory).suffix == "":
        return False
    else:
        return True

def rclone_isdir(directory)->bool:
    if pt.Path(directory).suffix == "":
        return True
    else:
        return False