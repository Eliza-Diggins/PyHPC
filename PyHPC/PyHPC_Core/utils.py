"""
Simply, Core utilities for the PyHPC project.
"""
import inspect
import json
import logging
import os
import pathlib as pt
from functools import wraps
from time import perf_counter
from types import SimpleNamespace
import sys
import numpy as np

# -------------------------------------------------------------------------------------------------------------------- #
#  setup    ========================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
__proj_directory = os.path.join(pt.Path(__file__).parents[1])

# - Variables -#
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
    # - Finding the version -#
    with open(os.path.join(__proj_directory, "bin", "lib", "ver.json"), "r") as f:
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
    global _time_tabs
    if not _time_logger:
        _time_logger = logging.getLogger("time")

    @wraps(func)
    def wrapper_function(*args, **kwargs):
        global _time_logger
        global _time_tabs
        _time_logger.info(("\t" * _time_tabs) + "%s:%s: Running." % (
            str(pt.Path(inspect.getfile(func)).absolute().relative_to(__proj_directory)),
            func.__name__))
        t_in = perf_counter()
        _time_tabs += 1
        res = func(*args, **kwargs)
        _time_tabs -= 1
        t_out = perf_counter()
        _time_logger.info(("\t" * _time_tabs) + "%s:%s: %s s." % (
            str(pt.Path(inspect.getfile(func)).absolute().relative_to(__proj_directory)),
            func.__name__,
            np.format_float_scientific(t_out - t_in, precision=3)))
        return res

    return wrapper_function


# -------------------------------------------------------------------------------------------------------------------- #
# File Management functions ========================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
class NonStandardEncoder(json.JSONEncoder):
    """
    Specialized ``json.JsonEncoder`` object to manage non-standard data types which need to be written to
    ``.json`` format.
    """

    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
                              np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def write_ini(dictionary, file):
    """
    Writes a ``.ini`` file (``toml`` without the usual `"` marks around the strings). The ``dictionary`` should be a
    standard ``toml`` formatted dictionary. ``file`` should be a readable.

    Parameters
    ----------
    dictionary : dict
        The dictionary to write to a .ini
    file : writable
        The file object to write the output to.

    Returns
    -------
    None

    """

    def _recur(d, f):
        for k, v in d.items():
            if isinstance(v, dict):
                f.write("[%s]\n" % k)
                _recur(v, f)
            else:
                f.write("%s = %s\n" % (k, v))

    _recur(dictionary, file)

# -------------------------------------------------------------------------------------------------------------------- #
# Analysis Directives ================================================================================================ #
# -------------------------------------------------------------------------------------------------------------------- #
def directive(function,directive):
    """
    Directive is a special function in ``PyHPC``, which is used to direct the code towards to correct version of a
    command depending on the intended software to use. In this case, we use it to differentiate between ``pynbody`` usage
    and ``yt`` usage. This allows us to develop software for both and easily tell the system which directive to use
    at any given stage of the execution.

    Parameters
    ----------
    function: callable
        The function that needs to be redirected towards the correct
    directive

    Returns
    -------

    """
    try:
        return sys.modules[function.__module__].__dict__[function.__name__+"_"+directive]
    except KeyError:
        return function


if __name__ == '__main__':
    get_system_info()
