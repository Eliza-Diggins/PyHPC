import logging
import logging.config
import os
import pathlib as pt
from datetime import datetime

import yaml

from PyHPC_Core.configuration import read_config
from PyHPC_Utils.text_display_utilities import get_dict_str

# -------------------------------------------------------------------------------------------------------------------- #
#  Setup ============================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "PyHPC_Core"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s" % (_location, _filename)
__logging_data = {}
CONFIG = read_config()


# -------------------------------------------------------------------------------------------------------------------- #
# Core Functions ===================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def set_logging(filename,
                root_level=CONFIG["System"]["Logging"]["default_root_level"],
                formats=CONFIG["System"]["Logging"]["formats"],
                output_to_file=CONFIG["System"]["Logging"]["output_to_file"]):
    """
    Loads the logging information to create the logging infrastructure.
    :param filename: The filename acting as the main channel. This is used to determine the location of the
                    placement for the output files.

    :param root_level: The root level.

    :param formats: The formats for the different formatters.

    :param output_to_file: True to generate files, False to not generate files.

    :return:
    """
    # ------------------------------------------------------------------------------------------------------------------#
    # Managing files ================================================================================================= #
    # ------------------------------------------------------------------------------------------------------------------#
    global __logging_data
    log_directory = os.path.join(CONFIG["System"]["Directories"]["log_directory"], pt.Path(filename).name,
                                 datetime.now().strftime('%m-%d-%Y_%H-%M-%S'))

    # - do we need to manage files at all? -#
    if output_to_file:
        pt.Path(log_directory).mkdir(parents=True)
    else:
        pass
    # ---------------------------------------------------------------------------------------------------------------- #
    #  Managing log info ============================================================================================= #
    # ---------------------------------------------------------------------------------------------------------------- #
    __logging_data = {
        "files": output_to_file,
        "dir"  : log_directory,
    }
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
    log_config_dict["formatters"] = formats
    # File output management
    # ------------------------------------------------------------------------------------------------------------------#
    file_handlers = [handler for handler in log_config_dict["handlers"] if "file" in handler]
    if not output_to_file:
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
            log_config_dict["handlers"][handler]["filename"] = os.path.join(log_directory,
                                                                            log_config_dict["handlers"][handler][
                                                                                "filename"])

    # Levels
    # ------------------------------------------------------------------------------------------------------------------#
    log_config_dict["root"]["level"] = root_level

    # ---------------------------------------------------------------------------------------------------------------- #
    # Generating the loggers   ======================================================================================= #
    # ---------------------------------------------------------------------------------------------------------------- #
    logging.config.dictConfig(log_config_dict)

    # ---------------------------------------------------------------------------------------------------------------- #
    # Debriefing ===================================================================================================== #
    # ---------------------------------------------------------------------------------------------------------------- #
    meta_logger = logging.getLogger("meta")
    meta_logger.info("Completed log setup with settings \n%s." % get_dict_str(log_config_dict))


def get_module_logger(group,
                      module,
                      level=CONFIG["System"]["Logging"]["default_root_level"],
                      frmt=CONFIG["System"]["Logging"]["formats"]["module_file"]["format"]):
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
    set_logging(_filename, output_to_file=True)
    logger = get_module_logger(_location, _filename)
    logger.debug("Shit went down!!")
