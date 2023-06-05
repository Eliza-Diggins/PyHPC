"""
Runs the initial condition generator for the PyHPC system.
"""
import json
import os
import pathlib as pt
import sys
import warnings

from colorama import Fore, Style

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.log import get_module_logger
from PyHPC.PyHPC_Utils.text_display_utilities import print_title, TerminalString, PrintRetainer, option_menu

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_executables"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
fdbg_string = "%s [%s]: " % (_dbg_string, Fore.GREEN + "Execution Wizard" + Style.RESET_ALL)
CONFIG = read_config()
modlog = get_module_logger(_location, _filename)

printer = PrintRetainer()
# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

# - Organizational Strings -#
initial_conditions_directory = CONFIG["System"]["Directories"]["ic_directory"]
done_string = "[" + Fore.CYAN + Style.BRIGHT + "DONE" + Style.RESET_ALL + "]"
fail_string = "[" + Fore.RED + Style.BRIGHT + "FAILED" + Style.RESET_ALL + "]"

# - Grabbing type information -#
with open(os.path.join(pt.Path(__file__).parents[1], "PyHPC", "bin", "lib", "imp", "types.json"), "r") as type_file:
    types = json.load(type_file)

# -------------------------------------------------------------------------------------------------------------------- #
# Core Execution   =================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
#  Title Printing
# ----------------------------------------------------------------------------------------------------------------- #
term_string = TerminalString()  # Loading a terminal string
print_title(func=printer.print)  # Printing the title
printer.print(term_string.str_in_grid(""))
printer.print(
    term_string.str_in_grid(Fore.BLUE + "Initial Conditions Generation Pipeline" + Style.RESET_ALL, alignment="center"))
printer.print(term_string.str_in_grid(""))
printer.print(term_string.h + "\n")

#  Parsing arguments passed to system
# ----------------------------------------------------------------------------------------------------------------- #
arguments = sys.argv[1:]

if "-h" in arguments or "--help" in arguments:
    # -> We have been asked to display a help screen.
    cwd = os.getcwd()
    printer.print(
        """
\n\nHELP INFORMATION
--------------------
\n
Below are the help information scripts for each of the available initial condition generators implemented:
\n""")
    for command in os.listdir(os.path.join(pt.Path(__file__).parents[0], "Initial Conditions")):
        print(Fore.GREEN + "python3 '%s' -h" % os.path.join(pt.Path(__file__).parents[1], "PyHPC_executables",
                                                            "Initial Conditions", command) + Style.RESET_ALL)
        os.system(
            "python3 '%s' -h" % os.path.join(pt.Path(__file__).parents[1], "PyHPC_executables", "Initial Conditions",
                                             command))
    exit()

else:
    # -> We just need to pass these through to the next stage.
    command_line_args = ""
    for command in arguments:
        command_line_args += " %s" % command

#  Selecting the pass through command
# ----------------------------------------------------------------------------------------------------------------- #
command_options = {
    k: types["software"]["initial_conditions"][k]["path"] for k in list(types["software"]["initial_conditions"].keys())
}

os.system('cls' if os.name == 'nt' else 'clear')
selection = option_menu(command_options, title="Software Selector")
os.system('cls' if os.name == 'nt' else 'clear')
printer.reprint()

printer.print("%sPassing initial condition generation to %s." % (fdbg_string, selection))

#  running
# ----------------------------------------------------------------------------------------------------------------- #
print("%sExecuting command: python3 '%s' %s" % (fdbg_string,os.path.join("PyHPC_executables",*command_options[selection]), command_line_args))
os.system("python3 '%s' %s" % (os.path.join("PyHPC_executables",*command_options[selection]), command_line_args))
