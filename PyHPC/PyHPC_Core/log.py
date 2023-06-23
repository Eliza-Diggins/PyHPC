"""
==============
PyHPC Logging
==============
The ``PyHPC`` system uses a sophisticated set of logging methodologies to produce comprehensive communicative methods
for users. Generally speaking, the configuration information for logging is stored in the ``CONFIG.config`` file;
which is where most user level options are stored and in the ``/bin/inst/log/logcon.yaml`` file, which holds most of
the backend for the logging system.

Overview
--------
The logging information from any given execution of PyHPC code is found in the ``/logging/`` directory filed under
first the top level executable that was running and then by the date. In each directory there will be several directories
of different log files organized as follows:

- **Top Level Loggers**
    - ``root``: The ``root`` logger is the base logger for the system. By default, ``root`` logging messages are passed
    to ``/<logging file>/root.log`` which collects *all of the logging messages through any logger*. Additionally,
    if a message of level ``CRITICAL`` arises it will be logged to the ``crit.log`` file.
    - ``time``: The ``time`` module is mostly used for development debugging. This keeps track of the fine details of
    all of the functions and methods run during execution and their timing.
    - ``meta``: The ``meta`` logger is used only in the ``log.py`` module and is specifically used to log information
    about the logging system during execution.
    - ``console``: The console logger is the ``PyHPC`` equivalent of ``print()``. This will print a message with a configurable
    output to the stdout stream.

- **Sub Loggers**
    - Each module and submodule gets its own logger named ``PyHPC.<>.<>...`` which logs to a file specific to its name.
    Each of these loggers is also inherited and therefore passes up the ladder of logs.
"""
import logging
import logging.config
import os
import pathlib as pt
import sys
from datetime import datetime
import pkgutil

import yaml

from PyHPC.PyHPC_Core.configuration import read_config

# -------------------------------------------------------------------------------------------------------------------- #
#  Setup ============================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "PyHPC_Core"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s" % (_location, _filename)
CONFIG = read_config()
__logtime = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
__logging_data = {"dir"  : os.path.join(CONFIG["System"]["Directories"]["log_directory"],
                                        str(pt.Path(sys.modules["__main__"].__file__).name if hasattr(
                                            sys.modules["__main__"], "__file__") else "console")),
                  "files": CONFIG["System"]["Logging"]["output_to_file"]}


with open(os.path.join(pt.Path(__file__).parents[1], "bin", "inst", "log", "logcon.yaml"), "r") as f:
    log_config_dict = yaml.load(f, Loader=yaml.FullLoader)

# Formatters
# ------------------------------------------------------------------------------------------------------------------#

#: ``log_config_dict["formatters"]`` contains the data from ``CONFIG["System"]["Logging"]["formats"]``, which the
#: user can configure to customize the logging output for different modules.
log_config_dict["formatters"] = CONFIG["System"]["Logging"]["formats"]
# -------------------------------------------------------------------------------------------------------------------- #
# Utility Functions ================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def get_dict_str(di, tabs=0):
    str = ""
    for k, v in di.items():
        if isinstance(v, dict):
            str += ("\t" * tabs) + "%s: {\n" % k
            str += get_dict_str(v, tabs=tabs + 1)
            str += ("\t" * tabs) + "}\n"
        else:
            str += ("\t" * tabs + "%s: %s\n" % (k, v))

    return str


def _get_modules(path, mod_name=""):
    out = []
    for mod in pkgutil.iter_modules([path]):
        out.append(mod_name + mod.name)
        out += _get_modules(os.path.join(path, mod.name), mod_name=mod_name + mod.name + ".")

    return out


def configure_logging(location):
    """
    The ``configure_logging`` function forms the basis of the logging in ``H20``. This should always be called
    anytime the system is
    Returns
    -------
    None

    """
    # Managing Filenames
    # ------------------------------------------------------------------------------------------------------------ #
    for k, v in log_config_dict["handlers"].items():
        if "filename" in v:
            exec('log_config_dict["handlers"][k]["filename"] = \'%s\'' % str(
                v["filename"] % {"log_dir": __logging_data["dir"],
                                 "time"   : __logtime,
                                 "loc"    : pt.Path(location).name.replace(pt.Path(location).suffix, "")}))
            if not os.path.exists(pt.Path(log_config_dict["handlers"][k]["filename"]).parents[0]):
                pt.Path(log_config_dict["handlers"][k]["filename"]).parents[0].mkdir(parents=True)

    # Generating modules
    # ------------------------------------------------------------------------------------------------------------ #
    for mod in _get_modules(str(pt.Path(__file__).parents[2])):
        log_config_dict["loggers"][mod] = {"level"    : "DEBUG",
                                  "handlers" : ["%s_handler" % mod],
                                  "propagate": True}
        log_config_dict["handlers"]["%s_handler" % mod] = {
            "level"    : "DEBUG",
            "filename" : os.path.join(__logging_data["dir"],
                                      pt.Path(location).name.replace(pt.Path(location).suffix, ""),__logtime,
                                      *mod.split("."), "log.log"),
            "class"    : "logging.FileHandler",
            "formatter": "fileFormatter"
        }
        if not os.path.exists(pt.Path(log_config_dict["handlers"]["%s_handler" % mod]["filename"]).parents[0]):
            pt.Path(log_config_dict["handlers"]["%s_handler" % mod]["filename"]).parents[0].mkdir(parents=True)

    logging.config.dictConfig(log_config_dict)

    metalog = logging.getLogger("meta")
    metalog.debug(log_config_dict)
    # Custom modules
    # ------------------------------------------------------------------------------------------------------------ #


if __name__ == '__main__':
    logger = logging.getLogger("root")
    configure_logging(__file__)
    logger.debug("heres something!")
    logging.warning("Something bad is happening")
