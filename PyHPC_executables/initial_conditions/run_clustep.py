"""
Clustep runtime implementation
"""
import json
import os
import pathlib as pt
import sys
import warnings
import argparse
import toml

from colorama import Fore, Style

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[2]))
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.log import get_module_logger
from PyHPC.PyHPC_Utils.text_display_utilities import print_title, TerminalString, PrintRetainer,build_options

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
with open(os.path.join(pt.Path(__file__).parents[2], "PyHPC", "bin", "lib", "imp", "types.json"), "r") as type_file:
    types = json.load(type_file)

# - grabbing defaults - #
clustep_ini = toml.load(os.path.join(CONFIG["System"]["Directories"]["bin"],"configs","CLUSTEP.config"))

# -------------------------------------------------------------------------------------------------------------------- #
# Core Execution   =================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
#  Argument Parsing
# ----------------------------------------------------------------------------------------------------------------- #
printer.print("%sLoading command line arguments..." % fdbg_string, end="\n")
# - Generating the arg parser

argparser = argparse.ArgumentParser()

# - Adding arguments to the argument parser
argparser.add_argument("-s","--stop",action="store_true",help="Enable tag to stop prior to execution.")
argparser.add_argument("-nb","--no_batch",action="store_true",help="Enable to proceed without passing to SLURM scheduler.")

# - parsing
user_arguments = argparser.parse_args()
printer.print(done_string)


#  Title Printing
# ----------------------------------------------------------------------------------------------------------------- #
term_string = TerminalString()  # Loading a terminal string
printer.print(term_string.h)
printer.print(term_string.str_in_grid(""))
printer.print(
    term_string.str_in_grid(Fore.BLUE + "Clustep Initial Conditions Generator" + Style.RESET_ALL, alignment="center"))
printer.print(term_string.str_in_grid(""))
printer.print(term_string.h + "\n")


printer.print("%sBeginning Execution:" % fdbg_string)

#  Grabbing clustep defaults
# ----------------------------------------------------------------------------------------------------------------- #
printer.print("%sGetting user inputs..." %fdbg_string,end="")

# - Loading the defaults -  #
build_options(clustep_ini,"Select CLUSTEP runtime options")
