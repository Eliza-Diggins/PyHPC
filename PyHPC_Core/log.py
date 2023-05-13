import logging
import logging.config
import sys
import os
import pathlib as pt
from datetime import datetime
import yaml
from PyHPC_Core.utils import time_function
from PyHPC_Core.configuration import read_config

# -------------------------------------------------------------------------------------------------------------------- #
#  Setup ============================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "PyHPC_Core"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s" % (_location, _filename)
CONFIG = read_config()
__logging_data = {"dir":os.path.join(CONFIG["System"]["Directories"]["log_directory"],
                                     str(pt.Path(sys.modules["__main__"].__file__).name if hasattr(sys.modules["__main__"],"__file__") else "console"),
                                     datetime.now().strftime('%m-%d-%Y_%H-%M-%S')),
                  "files":CONFIG["System"]["Logging"]["output_to_file"]}

# -------------------------------------------------------------------------------------------------------------------- #
# Utility Functions ================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def get_dict_str(di,tabs=0):
    str = ""
    for k,v in di.items():
        if isinstance(v,dict):
            str += ("\t"*tabs) + "%s: {\n"%k
            str += get_dict_str(v,tabs=tabs+1)
            str +=("\t"*tabs) + "}\n"
        else:
            str += ("\t"*tabs+"%s: %s\n"%(k,v))

    return str
# ------------------------------------------------------------------------------------------------------------------#
# Managing files ================================================================================================= #
# ------------------------------------------------------------------------------------------------------------------#


# - do we need to manage files at all? -#
if CONFIG["System"]["Logging"]["output_to_file"]:
    pt.Path(__logging_data["dir"]).mkdir(parents=True)
else:
    pass

# ---------------------------------------------------------------------------------------------------------------- #
#  Loading the .yaml file ======================================================================================== #
# ---------------------------------------------------------------------------------------------------------------- #
with open(os.path.join(pt.Path(__file__).parents[1], "bin", "inst", "log", "logcon.yaml"), "r") as f:
    log_config_dict = yaml.load(f, Loader=yaml.FullLoader)

# ---------------------------------------------------------------------------------------------------------------- #
# Managing Alterations =========================================================================================== #
# ---------------------------------------------------------------------------------------------------------------- #
# Formatters
# ------------------------------------------------------------------------------------------------------------------#
log_config_dict["formatters"] = CONFIG["System"]["Logging"]["formats"]
# File output management
# ------------------------------------------------------------------------------------------------------------------#
file_handlers = [handler for handler in log_config_dict["handlers"] if "file" in handler]
if not CONFIG["System"]["Logging"]["output_to_file"]:
    # We need to remove all of the file based handlers #

    log_config_dict["handlers"] = {k: v for k, v in log_config_dict["handlers"].items() if k not in file_handlers}

    for logger in log_config_dict["loggers"]:
        log_config_dict["loggers"][logger]["handlers"] = [hand for hand in
                                                          log_config_dict["loggers"][logger]["handlers"] if
                                                          hand not in file_handlers]

    # - root -#
    log_config_dict["root"]["handlers"] = [hand for hand in log_config_dict["root"]["handlers"] if
                                           hand not in file_handlers]
else:
    # Managing the file handler locations
    for handler in file_handlers:
        log_config_dict["handlers"][handler]["filename"] = os.path.join(__logging_data["dir"],
                                                                        log_config_dict["handlers"][handler][
                                                                            "filename"])

# Levels
# ------------------------------------------------------------------------------------------------------------------#
log_config_dict["root"]["level"] = CONFIG["System"]["Logging"]["default_root_level"]

# ---------------------------------------------------------------------------------------------------------------- #
# Generating the loggers   ======================================================================================= #
# ---------------------------------------------------------------------------------------------------------------- #
logging.config.dictConfig(log_config_dict)

# ---------------------------------------------------------------------------------------------------------------- #
# Debriefing ===================================================================================================== #
# ---------------------------------------------------------------------------------------------------------------- #
meta_logger = logging.getLogger("meta")
meta_logger.info("Completed log setup with settings \n%s." % get_dict_str(log_config_dict))

# -------------------------------------------------------------------------------------------------------------------- #
#   Functions   ====================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def get_module_logger(group,
                      module,
                      level=CONFIG["System"]["Logging"]["default_root_level"],
                      frmt=CONFIG["System"]["Logging"]["formats"]["file_module"]["format"]):
    global __logging_data

    # Grabbing the logger
    # ------------------------------------------------------------------------------------------------------------------#
    logger = logging.getLogger("%s.%s" % (group, module))
    logger.setLevel(level)

    # Creating the handlers
    # ------------------------------------------------------------------------------------------------------------------#
    if __logging_data["files"]:
        file = os.path.join(__logging_data["dir"], group)

        if not os.path.exists(file):
            pt.Path(file).mkdir(parents=True)
        else:
            pass

        handler = logging.FileHandler(
            filename=os.path.join(file, "%s.log" % module),
        )
        handler.setFormatter(logging.Formatter(frmt))
        logger.addHandler(handler)

    return logger


if __name__ == '__main__':
    pass
