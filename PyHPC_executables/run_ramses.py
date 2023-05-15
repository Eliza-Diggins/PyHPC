"""

Runs RAMSES from the command line.

"""
import argparse
import json
import os
import pathlib as pt
import sys
import warnings
from time import sleep

import toml

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from colorama import Fore, Style

from PyHPC_Core.configuration import read_config
from PyHPC_Core.log import get_module_logger
from PyHPC_Core.errors import PyHPC_Error
from PyHPC_Utils.text_display_utilities import print_title, TerminalString, select_files, get_options, print_verbose

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_executables"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
fdbg_string = "%s [%s]: " % (_dbg_string, Fore.GREEN + "Execution Wizard" + Style.RESET_ALL)
CONFIG = read_config()
modlog = get_module_logger(_location, _filename)
# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

# - Organizational Strings -#
initial_conditions_directory = CONFIG["System"]["Directories"]["ic_directory"]
ramses_nml_config = os.path.join(CONFIG["System"]["Directories"]["bin"], "configs", "RAMSES.config")
done_string = "[" + Fore.CYAN + Style.BRIGHT + "DONE" + Style.RESET_ALL + "]"
fail_string = "[" + Fore.RED + Style.BRIGHT + "FAILED" + Style.RESET_ALL + "]"

# - Grabbing type information -#
with open(os.path.join(pt.Path(__file__).parents[1], "bin", "lib", "imp", "types.json"), "r") as type_file:
    types = json.load(type_file)


# -------------------------------------------------------------------------------------------------------------------- #
# Sub-functionality ================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def nml_post_process(nml_settings, software):
    """
    This is a minor sub function which is designed to coerce the ``nml_settings`` to be compatible with the selected
    ``software``.

    :param nml_settings: The .nml dictionary settings.
    :param software: The software to use.
    :return: a fixed nml.
    """
    pass

# -------------------------------------------------------------------------------------------------------------------- #
#   MAIN ============================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
try:
    #  Printing Introduction, etc.
    # ----------------------------------------------------------------------------------------------------------------- #
    term_string = TerminalString()  # Loading a terminal string
    print_title()  # Printing the title
    print(term_string.str_in_grid(""))
    print(term_string.str_in_grid(Fore.BLUE + "RAMSES Pipeline Software" + Style.RESET_ALL, alignment="center"))
    print(term_string.str_in_grid(""))
    print(term_string.h + "\n\n")

    #  Argument Parsing
    # ----------------------------------------------------------------------------------------------------------------- #

    # - Generating the arg parser
    argparser = argparse.ArgumentParser()

    # - Adding arguments to the argument parser
    argparser.add_argument("-v", "--verbose", action="store_true", help="Toggles verbose mode.")
    argparser.add_argument("-i", "--ic", type=str, help="Tag to the initial condition file to initialize.",
                           default=None)
    argparser.add_argument("-n", "--nml", type=str, help="The nml path to use to pass the settings generation stage.",
                           default=None)

    # - parsing
    user_arguments = argparser.parse_args()

    #  Managing initial conditions
    # ----------------------------------------------------------------------------------------------------------------- #
    if not user_arguments.ic:
        # - We have not been given an explicit IC.
        print("%sInitial condition was not provided explicitly. User interaction is necessary." % fdbg_string)
        sleep(2)
        # - Grabbing initial conditions from the user.
        selected_initial_condition_path = select_files([pt.Path(initial_conditions_directory)], max=1,
                                                       condition=lambda f: (f.suffix in types["extensions"][
                                                           "initial_conditions"]) or os.path.isdir(
                                                           f))[0]

    else:
        # - We have been given an explicit initial conditions file.
        selected_initial_condition_path = pt.Path(user_arguments.ic)

        if selected_initial_condition_path.suffix not in types["extensions"]["initial_conditions"]:
            raise PyHPC_Error("The selected initial condition file is not valid.")

    # - Printing results -#
    os.system('cls' if os.name == 'nt' else 'clear')
    print_title()  # Printing the title
    print(term_string.str_in_grid(""))
    print(term_string.str_in_grid(Fore.BLUE + "RAMSES Pipeline Software" + Style.RESET_ALL, alignment="center"))
    print(term_string.str_in_grid(""))
    print(term_string.h + "\n\n")
    sleep(1)
    print("%s Selected the initial condition file %s." % (fdbg_string, selected_initial_condition_path))

    #  Managing RAMSES Params
    # ----------------------------------------------------------------------------------------------------------------- #
    if not user_arguments.nml:
        print("%s The nml file was not specified in tags. Setting nml parameters manually." % fdbg_string)

        print_verbose("Loading the configuration default...", user_arguments.verbose, end="")

        try:
            ramses_config_default = toml.load(ramses_nml_config)
        except FileNotFoundError:
            print_verbose(fail_string, user_arguments.verbose)
            modlog.exception("Failed to locate the ramses configuration file at %s." % ramses_nml_config)
            raise PyHPC_Error("Failed to locate the ramses configuration file at %s." % ramses_nml_config)
        except toml.TomlDecodeError:
            print_verbose(fail_string, user_arguments.verbose)
            modlog.exception("Failed to correctly load the file %s in TOML format." % ramses_nml_config)
            raise PyHPC_Error("Failed to correctly load the file %s in TOML format." % ramses_nml_config)

        print_verbose(done_string, user_arguments.verbose)

        #  Getting settings from the user
        # ----------------------------------------------------------------------------------------------------------------- #
        ramses_config_user = get_options(ramses_config_default, "RAMSES .nml Settings")

    else:
        # - The use did specify a .nml file, but we now need to determine a few additional details.
        print("%sNML file was specified explicitly with flag -n." % fdbg_string)
        print("%sTo proceed with execution, answer the following questions:" % fdbg_string)
        print("%sAvailable software: %s" % (fdbg_string, types["software"]["RAMSES"]))

        software = ""
        while software not in types["software"]["RAMSES"]:
            software = input("%sWhich software would you like to select?" % fdbg_string)

            if software not in types["software"]["RAMSES"]:
                print("%s%s is not a valid software type." % (fdbg_string, software))
            else:
                pass

        os.system('cls' if os.name == 'nt' else 'clear')
    #  Post Processing Measures
    # ----------------------------------------------------------------------------------------------------------------- #
    print_title()  # Printing the title
    print(term_string.str_in_grid(""))
    print(term_string.str_in_grid(Fore.BLUE + "RAMSES Pipeline Software" + Style.RESET_ALL, alignment="center"))
    print(term_string.str_in_grid(""))
    print(term_string.h + "\n\n")
    print("%sRAMSES nml settings were received. Post processing to assure compliance..." % fdbg_string, end="")

    # - TODO: This needs to be written -#

    print(done_string)
except PyHPC_Error:
    print(fdbg_string, Fore.RED + "EXECUTION FAILED" + Style.RESET_ALL + ": See Log.")
    modlog.error("Execution Failed.", exc_info=True)
