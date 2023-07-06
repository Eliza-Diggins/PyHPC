"""
==================
PyHPC ImageManager
==================
The ``PyHPC`` Image Manager system can be used as an executable linking the ``PlotDirective`` system described in the
documentation for ``PyHPC.PyHPC.PyHPC_Visualization.plot``. This will guide the user through the command line process
for generating plots either in bulk or individually.

Usage
-----

Command Line
^^^^^^^^^^^^
To initiate the executable, the command

.. code-block:: commandline

    python3 ImageManager.py [-flags]

should be executed from the ``PyHPC`` base directory. There are a variety of command line options summarized here:

.. code-block:: commandline

    usage: ImageManager.py [-h] [--simulation_log SIMULATION_LOG] [-nb] [-s]

    optional arguments:
      -h, --help            show this help message and exit
      --simulation_log SIMULATION_LOG
                            A [PATH] to a simulation logger if desired.
      -nb, --no_batch       If active, the execution will not be passed to SLURM.
      -s, --stop            True to not push the executable to SLURM.

Usage Instructions
^^^^^^^^^^^^^^^^^^
Once the system has been loaded, there are several stages through which the imaging pipeline proceeds:

#. **Type**: At this stage, the user is queried to provide either ``0`` indicating that they want to produce plots for
   all of the outputs in the simulation, or a ``1`` indicating that you only want to produce 1 image.

   - If you select option ``1``, you will be asked to specify the particular output you wish to use.

#. **Sim Selection**: At this stage, you are queried to select a simulation from the ``SimulationLog`` for which to
   perform the analysis.
#. **PlotDirective Construction**: This is the key part of the execution process. You must specify the details of your
   plot directive by editing the dictionary information and adding relevant functions.

   .. attention::
        Be aware that only one wildcard arg / kwarg may exist: ``%path%``.
#. **Execution**: The execution will proceed and generate the image.
"""
import argparse
import os
import pathlib as pt
import sys
import warnings

from colorama import Fore, Style

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from PyHPC.PyHPC_Core.configuration import read_config
import logging
from PyHPC.PyHPC_Core.log import configure_logging
from PyHPC.PyHPC_Utils.text_display_utilities import print_title, TerminalString, PrintRetainer, edit_pdir_dictionary
import yaml
from tqdm import tqdm
from time import sleep
from PyHPC.PyHPC_Visualization.plot import PlotDirective
from datetime import datetime
from PyHPC.PyHPC_Core.errors import PyHPC_Error
from PyHPC.PyHPC_Utils.text_display_utilities import option_menu
from PyHPC.PyHPC_System.simulation_management import SimulationLog
from PyHPC.PyHPC_System.io import write_slurm_file

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_executables"
fdbg_string = "[%s]: " % (Fore.GREEN + "PyHPC Execution Wizard" + Style.RESET_ALL)
CONFIG = read_config()
modlog = logging.getLogger(__name__)
printer = PrintRetainer()

# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

# - Organizational Strings -#

done_string = "[" + Fore.CYAN + Style.BRIGHT + "DONE" + Style.RESET_ALL + "]"
fail_string = "[" + Fore.RED + Style.BRIGHT + "FAILED" + Style.RESET_ALL + "]"

#_mdir is used to fill base dictionaries.
with open(os.path.join(pt.Path(__file__).parents[1], "PyHPC", "bin", "lib", "img", "master_directive.yaml")) as file:
    _mdir = yaml.load(file, yaml.FullLoader)

#  Loading Constants
# ----------------------------------------------------------------------------------------------------------------- #
_time_string = datetime.now().strftime('%m-%d-%Y_%H-%M-%S') # Used to determine the path to the output.
_temporary_directory = os.path.join(pt.Path(__file__).parents[1].absolute(), "PyHPC", "bin", ".tmp",
                                    _time_string)

if __name__ == '__main__':
    # ---------------------------------------------------------------------------------------------------------------- #
    # Loading and Configuring ======================================================================================== #
    # ---------------------------------------------------------------------------------------------------------------- #
    #- Cleaning configuration and logging -#
    os.system('cls' if os.name == 'nt' else 'clear')
    configure_logging(__file__)
    modlog.debug("Loading the plot generator.")

    #- Print Management
    term_string = TerminalString()  # Loading a terminal string
    print_title(func=printer.print)  # Printing the title
    printer.print(term_string.str_in_grid(""))
    printer.print(
        term_string.str_in_grid(Fore.BLUE + "Image Generation Software" + Style.RESET_ALL, alignment="center"))
    printer.print(term_string.str_in_grid(""))
    printer.print(term_string.h + "\n")

    # Arg-parsing
    # ----------------------------------------------------------------------------------------------------------------- #
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulation_log", type=str, help="A [PATH] to a simulation logger if desired.",
                        default=None)
    parser.add_argument("-nb", "--no_batch", help="A [PATH] to a simulation logger if desired.",
                        action="store_true")
    parser.add_argument("-s", "--stop", help="True to not push the executable to SLURM.",
                        action="store_true")
    args = parser.parse_args()

    # ---------------------------------------------------------------------------------------------------------------- #
    # Core Execution ================================================================================================= #
    # ---------------------------------------------------------------------------------------------------------------- #
    for i in tqdm(range(100), desc="%sLoading..." % fdbg_string, bar_format="{desc}: {percentage:3.0f}%|{bar}|",
                  ncols=term_string.dim_alt[0]):
        sleep(0.01)

    input("%sPress any key to continue..." % fdbg_string)

    #  Getting User Data
    # ----------------------------------------------------------------------------------------------------------------- #
    # - Printing the settings header.
    printer.print("\n")
    printer.print(term_string.h)
    printer.print(
        term_string.str_in_grid(Fore.CYAN + "SETUP" + Style.RESET_ALL, alignment="left"))
    printer.print(term_string.h + "\n")

    # - determine if we are plotting singular or across an entire simulation -#
    type_setting = None
    while type_setting not in ["0", "1"]:
        type_setting = input("%sGenerate image for entire simulation (0) or single snapshot (1)? " % fdbg_string)

    modlog.debug("User selected type_setting = %s"%type_setting)

    #  Loading a simulation
    # ----------------------------------------------------------------------------------------------------------------- #
    printer.print("%sLoading the simulation log..." % fdbg_string, end="")
    try:
        simlog = SimulationLog(path=args.simulation_log)
        printer.print(done_string)
    except FileNotFoundError:
        printer.print(fail_string)
        sys.exit()

    # - Getting the chosen simulation -#
    available_simulations = []
    for rec in list(simlog.get_simulation_records().values()):
        available_simulations += [i for i in rec.raw["outputs"] if os.path.exists(i)]

    try:
        if not len(available_simulations):
           raise IndexError("No available simulations were found...")

    except IndexError:
        modlog.exception("No available simulations found.")
        printer.print("%sFailed to find any valid simulations." % fdbg_string)
        printer.print(fail_string)
        sys.exit()

    os.system('cls' if os.name == 'nt' else 'clear')

    # - Choosing the desired simulation - #
    _selected_simulation_directory = option_menu({k: str(len(os.listdir(k))) for k in available_simulations}, desc=True,
                                                 title="Select a Simulation")
    os.system('cls' if os.name == 'nt' else 'clear')
    printer.reprint()
    printer.print(fdbg_string + "Loaded simulation %s" % _selected_simulation_directory)
    modlog.debug("Selected %s."%_selected_simulation_directory)

    # - Post Selection Logging to Action Log - #
    simrec = [sr for key,sr in simlog.get_simulation_records().items() if _selected_simulation_directory in sr.raw["outputs"]][0]
    modlog.debug("Found simrec %s corresponding to the selected output %s."%(simrec,_selected_simulation_directory))

    #  Type of Execution / Selecting a snap.
    # ----------------------------------------------------------------------------------------------------------------- #
    # - Selecting a simulation snapshot number if one applies - #
    if type_setting == "1":
        available_outputs = len([i for i in os.listdir(_selected_simulation_directory) if "output" in i])
        snap_choice = 0
        while not (1 <= snap_choice <= len(os.listdir(_selected_simulation_directory))):
            snap_choice = int(input(
                fdbg_string + f"Which snapshot do you want to select? (1-{available_outputs})..."))
            os.system('cls' if os.name == 'nt' else 'clear')
            printer.reprint()
    else:
        snap_choice = 0

    # -------------------------------------------------------------------------------------------------------------------- #
    # Setting up the directive =========================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #
    printer.print("\n")
    printer.print(term_string.h)
    printer.print(
        term_string.str_in_grid(Fore.CYAN + "DIRECTIVE CONSTRUCTION" + Style.RESET_ALL, alignment="left"))
    printer.print(term_string.h + "\n")
    for i in tqdm(range(100), desc="%sLoading Directive Options..." % fdbg_string,
                  bar_format="{desc}: {percentage:3.0f}%|{bar}|",
                  ncols=term_string.dim_alt[0]):
        sleep(0.01)

    input("%sPress any key to continue..." % fdbg_string)

    # ---------------------------------------------------------------------------------------------------------------- #
    # Constructing the PlotDirective ================================================================================= #
    # ---------------------------------------------------------------------------------------------------------------- #
    _user_pdir_dict = {"Information": "",
                       "Figure"     : {
                           "Functions" : {
                           },
                           "Parameters": {
                           }
                       }
                       }
    os.system('cls' if os.name == 'nt' else 'clear')
    _user_pdir_dict = edit_pdir_dictionary(_user_pdir_dict, title="Edit The Plotting Directive", _mdir=_mdir)

    #  Processing
    # ----------------------------------------------------------------------------------------------------------------- #
    os.system('cls' if os.name == 'nt' else 'clear')
    printer.reprint()
    printer.print(fdbg_string + "Successfully received user settings for execution.")
    printer.print(
        fdbg_string + f"Writing the plot directive to:\n\t\t {os.path.join(_temporary_directory, 'directive.yaml')}...",
        end="")
    try:
        pt.Path(_temporary_directory).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(_temporary_directory, 'directive.yaml'), "w+") as file:
            yaml.dump(_user_pdir_dict, file)
    except yaml.YAMLError:
        modlog.exception("Failed to write pdir")
        printer.print(fdbg_string + fail_string)
        printer.print(fdbg_string + "Failed to successfully write the pdir to file...")
        exit()

    printer.print(done_string)

    printer.print(fdbg_string + "Loading the plotting directive", end="")

    try:
        pdir = PlotDirective(os.path.join(_temporary_directory, 'directive.yaml'))
    except PyHPC_Error:
        modlog.exception("Failed to read pdir")
        printer.print(fdbg_string + fail_string)
        printer.print(fdbg_string + "Failed to successfully read the pdir from file...")
        exit()
    printer.print(done_string)
    os.system('cls' if os.name == 'nt' else 'clear')

    #  Managing Processing Stages
    # ----------------------------------------------------------------------------------------------------------------- #
    if len(pdir.get_all_special_entities()) > 1:
        modlog.exception("Pdir has too many unknowns.")
        printer.print(fdbg_string + fail_string)
        printer.print(fdbg_string + "Pdir has too many unknowns")
        exit()

    # ---------------------------------------------------------------------------------------------------------------- #
    # Passing to the batch system ==================================================================================== #
    # ---------------------------------------------------------------------------------------------------------------- #
    output_directory = os.path.join(CONFIG["System"]["Directories"]["figures_directory"],
                                    pt.Path(_selected_simulation_directory).name, _time_string)
    simrec.log("Generating figures at %s."%output_directory,"FIG-GEN",object_rec=_selected_simulation_directory)
    if args.no_batch:
        #  we are running to an exe system.
        # ----------------------------------------------------------------------------------------------------------------- #
        printer.print("%sGenerating the executable -No Batch-..." % fdbg_string, end="")

        with open(
                os.path.join(pt.Path(__file__).parents[1], "PyHPC", "bin", "lib", "templates", "image_exe.template"),
                "r") as template:
            with open(os.path.join(_temporary_directory, "exec.sh"), "w+") as writer:
                writer.write(template.read() % {
                    "csh_interp"         : CONFIG["System"]["Modules"]["csh_interp"],
                    "python_env_script"  : CONFIG["System"]["Modules"]["python_env_script"],
                    "python_exec"        : CONFIG["System"]["Modules"]["python_exec_name"],
                    "type"               : int(type_setting),
                    "output_directory"   : output_directory,
                    "output"             : f"output_{snap_choice:05d}",
                    "temp_dir"           : str(_temporary_directory),
                    "root_directory"     : str(pt.Path(__file__).parents[1]),
                    "simulation_location": _selected_simulation_directory,
                    "fdbg"               : fdbg_string
                })
        printer.print(done_string)
        os.system("chmod 777 %s" % (os.path.join(_temporary_directory, "exec.sh")))
        os.system('cls' if os.name == 'nt' else 'clear')
        printer.reprint()
        os.system((os.path.join(_temporary_directory, "exec.sh")))
    else:
        #  Running the executable with no batching.
        # ----------------------------------------------------------------------------------------------------------------- #
        slurm_output = input("%sPlease enter the desired name of the .slurm file (EXCLUDE .slurm): " % fdbg_string)
        slurm_path = pt.Path(os.path.join(CONFIG["System"]["Directories"]["slurm_directory"], slurm_output))
        printer.print("%sGenerating the executable..." % fdbg_string, end="\n")
        with open(os.path.join(pt.Path(__file__).parents[1], "PyHPC", "bin", "lib", "templates",
                               "image_slurm.template"),
                  "r") as template:
            write_slurm_file(template.read(), name=slurm_output, **{
                "csh_interp"       : CONFIG["System"]["Modules"]["csh_interp"],
                "python_env_script": CONFIG["System"]["Modules"]["python_env_script"],
                "python_exec"      : CONFIG["System"]["Modules"]["python_exec_name"],
                "type"               : int(type_setting),
                "output_directory"   : output_directory,
                "temp_dir"           : str(_temporary_directory),
                "root_directory"     : str(pt.Path(__file__).parents[1]),
                "output": f"output_{snap_choice:05d}",
                "simulation_location": _selected_simulation_directory,
                "slurm_out"        : os.path.join(CONFIG["System"]["Directories"]["reports_directory"], "slurm_outputs",
                                                  slurm_output, "parallel.log"),
            })
        printer.print(done_string)
        #  Managing final execution
        # ----------------------------------------------------------------------------------------------------------------- #

        os.system('cls' if os.name == 'nt' else 'clear')
        printer.reprint(end="")
        printer.print(done_string)

        if not args.stop:
            printer.print("%sAdding the job to the SLURM queue..." % fdbg_string, end="")
            os.system("sbatch %s" % slurm_path + ".SLURM")

            printer.print(done_string)