"""
Simply, Core utilities for the PyHPC project.
"""
import logging
from types import SimpleNamespace
import os
import pathlib as pt
import json
from functools import wraps
from time import perf_counter
import numpy as np
import inspect
# -------------------------------------------------------------------------------------------------------------------- #
#  setup    ========================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
__proj_directory = os.path.join(pt.Path(__file__).parents[1])

#- Variables -#
_time_logger = None
_time_tabs = 0
# -------------------------------------------------------------------------------------------------------------------- #
# System Info  ======================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
def get_system_info():
    """
    Fetches all of the system info.
    :return: an object containing all of the desired data.
    """
    #- Finding the version -#
    with open(os.path.join(__proj_directory,"bin","lib","ver.json"),"r") as f:
        project_data = json.load(f)

    return SimpleNamespace(**project_data)
# -------------------------------------------------------------------------------------------------------------------- #
# Timing Utilities  ================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def time_function(func):
    """
    Times the run speed of a given function.
    :param func: The function being timed.
    :return: None
    """
    global _time_logger
    if not _time_logger:
        _time_logger = logging.getLogger("time")
    @wraps(func)
    def wrapper_function(*args,**kwargs):
        _time_logger.info("%s:%s: Running."%(str(pt.Path(inspect.getfile(func)).relative_to(__proj_directory)),
                                          func.__name__))
        t_in = perf_counter()
        res= func(*args,**kwargs)
        t_out = perf_counter()
        _time_logger.info("%s:%s: %s s."%(str(pt.Path(inspect.getfile(func)).relative_to(__proj_directory)),
                                          func.__name__,
                                          np.format_float_scientific(t_out-t_in,precision=3)))
        return res
    return wrapper_function

if __name__ == '__main__':
    get_system_info()