"""
Remote usage utilities for file transfer management and interaction with the RCLONE interface.

"""
import os
import pathlib as pt
import sys

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from PyHPC.PyHPC_Core.log import get_module_logger
from PyHPC.PyHPC_Core.configuration import read_config
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
modlog = get_module_logger(_location, _filename)

# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')


# -------------------------------------------------------------------------------------------------------------------- #
# Core IO Functions ================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def rclone_listdir(directory) -> list:
    """
    Functions as the equivalent to ``os.listdir`` in remote directories as configured by the RCLONE
    settings in ``CONFIG.config``.

    Parameters
    ----------
    directory : str
        The directory path to list directories from. Must be a valid directory in the remote location.

    Returns
    -------
    list
        A list of the resulting objects.

    """
    #  Setup and Debug
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Finding remote ls for directory %s." % directory)

    # performing the command #
    output = subprocess.check_output(["rclone", "lsf", directory, "--max-depth", "1"])
    output = output.decode("utf8").split("\n")[:-1]

    return output


def rclone_isfile(directory) -> bool:
    """
    Checks if ``directory`` is a file on RCLONE.
    Parameters
    ----------
    directory: str
        The directory to check.

    Returns
    -------
    bool
        ``True`` if the object is a file, ``False`` otherwise.

    """
    if pt.Path(directory).suffix == "":
        return False
    else:
        return True


def rclone_isdir(directory) -> bool:
    """
    Checks if ``directory`` is a directory on RCLONE.
    Parameters
    ----------
    directory: str
        The directory to check.

    Returns
    -------
    bool
        ``True`` if the object is a directory, ``False`` otherwise.

    """
    if pt.Path(directory).suffix == "":
        return True
    else:
        return False
