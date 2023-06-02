"""
Subroutines for finding and managing the simulations produced in the course of use.
"""
import os
import pathlib as pt
import sys

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from PyHPC.PyHPC_Core.log import get_module_logger
from PyHPC.PyHPC_Core.configuration import read_config
import pathlib as pt
import threading as t
import warnings

# generating screen locking #
screen_lock = t.Semaphore(value=1)  # locks off multi-threaded screen.
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_System"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = get_module_logger(_location, _filename)
# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')


# -------------------------------------------------------------------------------------------------------------------- #
# Simulation Log Object ============================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
class SimulationLog:
    """
    Defines the core class of simulation logging functionality.
    """
    def __init__(self,path=None):
        """
        Initializes the SimulationLog object
        :param path: the path to the simulation log.
        """
        #  Introduction debug
        # ------------------------------------------------------------------------------------------------------------ #
        modlog.debug("Loading a SimulationLog from path %s"%path)

        #  Path Coercion
        # ------------------------------------------------------------------------------------------------------------ #
        if path:
            self.path = pt.Path(path)
        else:
            self.path = pt.Path(CONFIG["System"]["Directories"]["bin"],"configs","Simlog.json")
            modlog.info("self.path was None, loading simulationlog from default location %s."%self.path)

        #  Reading
        # ------------------------------------------------------------------------------------------------------------ #


if __name__ == '__main__':
    pass
