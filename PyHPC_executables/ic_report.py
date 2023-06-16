"""
=========================
Initial Condition Reports
=========================

Once the initial conditions are generated, there are many cases in which it is prudent to obtain a report on the
initial conditions to make sure that there have been no errors in the generation process and that your specifications
are, in fact, those that suit your needs.

To run an initial condition report, one simply needs to run

>>> python3 ic-report
    ic_report.py [-h] [-l {pynbody,yt}] [-o OUTPUT] [--simulation_log SIMULATION_LOG] ic
    positional arguments:
      ic                    Name of initial condition or path to the file.
    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            The output location for the report.
      --simulation_log SIMULATION_LOG
                            A [PATH] to a simulation logger if desired.

.. warning::
    If the ``-o`` flag is not used, the report will appear in the current working directory.
"""

import argparse
import json
import os
import pathlib as pt
import sys
import warnings
from datetime import datetime
from time import sleep
import yt
import matplotlib.pyplot as plt

import toml
from colorama import Fore, Style

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.errors import *
import logging
from PyHPC.PyHPC_Core.log import configure_logging
from PyHPC.PyHPC_System.io import write_ramses_nml, write_slurm_file
from PyHPC.PyHPC_System.simulation_management import SimulationLog
from PyHPC.PyHPC_Utils.text_display_utilities import print_title, TerminalString, select_files, PrintRetainer, \
    get_options

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_executables"
_filename = pt.Path(__file__).name.replace(".py", "")
configure_logging(_filename)
_dbg_string = "%s:%s:" % (_location, _filename)
fdbg_string = "%s [%s]: " % (_dbg_string, Fore.GREEN + "Execution Wizard" + Style.RESET_ALL)
CONFIG = read_config()
modlog = logging.getLogger(__name__)
modlog.debug("this is a module level logging call")
printer = PrintRetainer()
# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

# - Organizational Strings -#
done_string = "[" + Fore.CYAN + Style.BRIGHT + "DONE" + Style.RESET_ALL + "]"
fail_string = "[" + Fore.RED + Style.BRIGHT + "FAILED" + Style.RESET_ALL + "]"

# - Grabbing type information -#
with open(os.path.join(pt.Path(__file__).parents[1], "PyHPC", "bin", "lib", "imp", "types.json"), "r") as type_file:
    types = json.load(type_file)

if __name__ == '__main__':
    #  Printing Introduction, etc.
    # ----------------------------------------------------------------------------------------------------------------- #
    term_string = TerminalString()  # Loading a terminal string
    print_title(func=printer.print)  # Printing the title
    printer.print(term_string.str_in_grid(""))
    printer.print(term_string.str_in_grid(Fore.BLUE + "Initial Conditions Report" + Style.RESET_ALL, alignment="center"))
    printer.print(term_string.str_in_grid(""))
    printer.print(term_string.h + "\n")

    #  Argument Parsing
    # ----------------------------------------------------------------------------------------------------------------- #
    printer.print("%sBeginning Execution:" % fdbg_string)
    printer.print("%sLoading command line arguments..." % fdbg_string, end="")

    sleep(0.5)

    # - Generating the arg parser
    argparser = argparse.ArgumentParser()

    # - Adding arguments to the argument parser
    argparser.add_argument("ic", type=str, help="Name of initial condition or path to the file.",
                           default=None)
    argparser.add_argument("-o","--output",type=str,help="The output location for the report.",default=None)
    argparser.add_argument("-c","--cmap",type=str,help="The colormap to use in the output plot.",default="inferno")
    argparser.add_argument("--simulation_log", type=str, help="A [PATH] to a simulation logger if desired.", default=None)
    # - parsing
    user_arguments = argparser.parse_args()
    printer.print(done_string)

    #  Loading
    # ----------------------------------------------------------------------------------------------------------------- #

    printer.print("%sLoading the simulation log..."%fdbg_string,end="")
    modlog.debug("Generating an initial conditions report for %s."%user_arguments.ic)

    #------------------- Loading the simulation log ----------------------------------#
    try:
        simlog = SimulationLog(path=user_arguments.simulation_log)
        modlog.debug("Loaded a simulation log at %s."%simlog)
    except FileNotFoundError as message:
        printer.print("")
        raise ExecutionError(message,logger=modlog,exit=True)

    printer.print(done_string)

    #------------------ Locating the IC file in the simulation log ------------------#
    printer.print("%sLocating the initial condition file..."%fdbg_string,end="")

    _load_status = None # This indicates the status of the loading system

    if user_arguments.ic in simlog.ics:
        # - We found it directly in the simlog
        modlog.debug("Found %s in %s."%(user_arguments.ic,simlog))
        _load_status = "simlog"
    elif os.path.exists(user_arguments.ic):
        modlog.debug("User specified initial condition matches a file.")
        _load_status = "file"
    else:
        pass

    if not _load_status: #-> We failed to succeed in finding the initial condition file
        printer.print("")
        raise ExecutionError("Failed to find %s in either simulation log %s or file system."%(user_arguments.ic,simlog),
                             logger=modlog,
                             exit=True)

    printer.print(done_string)

    #  Generating the IO directory
    # ----------------------------------------------------------------------------------------------------------------- #
    printer.print("%sGenerating the output directories..."%fdbg_string,end="")
    if not user_arguments.output:
        output_directory = pt.Path(os.path.join(os.getcwd(),"Report_%s_%s"%(pt.Path(user_arguments.ic).name,datetime.now().strftime('%m-%d-%Y_%H-%M-%S'))))
    else:
        output_directory = pt.Path(user_arguments.output)

    modlog.debug("output directory was determined to be %s" % str(output_directory))

    output_directory.mkdir(parents=True,exist_ok=True)

    printer.print(done_string)

    # -------------------------------------------------------------------------------------------------------------------- #
    # Imaging ============================================================================================================ #
    # -------------------------------------------------------------------------------------------------------------------- #
    printer.print("%sGenerating the primary image..."%fdbg_string)

    ds = yt.load(user_arguments.ic)
    ds.index
    ad = ds.all_data()

    pz = yt.ParticlePlot(ds,("all","particle_position_x"),("all","particle_position_y"),("all","particle_mass"),depth=(1000,"kpc"))
    pz.set_cmap("all",user_arguments.cmap)
    pz.save(os.path.join(output_directory,"image.png"))

