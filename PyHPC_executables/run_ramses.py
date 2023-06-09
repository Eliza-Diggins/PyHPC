"""

Runs RAMSES from the command line.

"""
import argparse
import json
import os
import pathlib as pt
import sys
import warnings
from datetime import datetime
from time import sleep

import toml
from colorama import Fore, Style

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.errors import *
from PyHPC.PyHPC_Core.log import get_module_logger
from PyHPC.PyHPC_System.io import write_ramses_nml, write_slurm_file
from PyHPC.PyHPC_System.simulation_management import SimulationLog
from PyHPC.PyHPC_Utils.text_display_utilities import print_title, TerminalString, select_files, PrintRetainer, \
    get_options

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
ramses_nml_config = os.path.join(CONFIG["System"]["Directories"]["bin"], "configs", "RAMSES.config")
done_string = "[" + Fore.CYAN + Style.BRIGHT + "DONE" + Style.RESET_ALL + "]"
fail_string = "[" + Fore.RED + Style.BRIGHT + "FAILED" + Style.RESET_ALL + "]"

# - Grabbing type information -#
with open(os.path.join(pt.Path(__file__).parents[1], "PyHPC", "bin", "lib", "imp", "types.json"), "r") as type_file:
    types = json.load(type_file)

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Main  ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
if __name__ == '__main__':

    #  Printing Introduction, etc.
    # ----------------------------------------------------------------------------------------------------------------- #
    term_string = TerminalString()  # Loading a terminal string
    print_title(func=printer.print)  # Printing the title
    printer.print(term_string.str_in_grid(""))
    printer.print(term_string.str_in_grid(Fore.BLUE + "RAMSES Pipeline Software" + Style.RESET_ALL, alignment="center"))
    printer.print(term_string.str_in_grid(""))
    printer.print(term_string.h + "\n")

    #  Argument Parsing
    # ----------------------------------------------------------------------------------------------------------------- #
    printer.print("%sBeginning Execution:" % fdbg_string)
    printer.print("%sLoading command line arguments..." % fdbg_string, end="")
    # - Generating the arg parser
    argparser = argparse.ArgumentParser()
    # - Adding arguments to the argument parser
    argparser.add_argument("-v", "--verbose", action="store_true", help="Toggles verbose mode.")
    ##- Shortcutting argument flags -##
    argparser.add_argument("-i", "--ic", type=str, help="Tag to the initial condition file to initialize.",
                           default=None)
    argparser.add_argument("-n", "--nml", type=str, help="The nml path to use to pass the settings generation stage.",
                           default=None)
    argparser.add_argument("--nml_output", type=str, help='Use this to hard set the .nml output location.', default=None)
    argparser.add_argument("--slurm_output", type=str, help="Use this to hard set the slurm file location.", default=None)
    argparser.add_argument("-s", "--stop", action="store_true",
                           help="Enable this flag to generate only the slurm file but not execute.")
    argparser.add_argument("--simulation_log", type=str, help="A [PATH] to a simulation logger if desired.", default=None)
    # - parsing
    user_arguments = argparser.parse_args()
    printer.print(done_string)

    # -------------------------------------------------------------------------------------------------------------------- #
    # Managing flags ===================================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #

    # - Grabbing the simulation logger - #
    printer.print("%sLoading the simulation log..." % fdbg_string, end="")
    try:
        simlog = SimulationLog(path=user_arguments.simulation_log)
        printer.print(done_string)
    except FileNotFoundError:
        printer.print(fail_string)
        sys.exit()

    # - Accessing files - #
    printer.print("%sGenerating / Accessing necessary setting files..." % fdbg_string)

    if user_arguments.nml:
        # - An .nml file is already provided.
        printer.print("%s\tA user selected .nml file was entered using the -n flag." % fdbg_string)

        printer.print("%s\tChecking that the selected .nml file is valid..." % fdbg_string, end="")
        # - Making sure the .nml is actually real and valid -#
        if os.path.exists(user_arguments.nml) and pt.Path(user_arguments.nml).suffix == ".nml":
            user_nml_path = user_arguments.nml
            printer.print(done_string)
            nml_software = input("%s\t\tPlease enter the software to use at runtime: " % fdbg_string)
        else:
            printer.print(fail_string)
            sys.exit()
        #  Managing the simulation log entry
        # ----------------------------------------------------------------------------------------------------------------- #
        printer.print("%s\tLoading the .nml entry in the simulation log..." % fdbg_string, end="")

        try:
            nml_log = simlog.get_simulation_records()[user_nml_path]
            nml_log.log("Loaded nml_log at %s for run." % user_nml_path, action="LOAD_TO_RUN")
            init_con_log = nml_log.parent
            printer.print(done_string)
        except KeyError:
            # -> Failed to add the simulation log entry.
            printer.print(fail_string)
            printer.print(
                "%s\t [WARNING] Failed to find .nml in the simulation log, running this simulation as incognito.\n\t\tTo keep a record if this simulation, please document the .nml in the simulation log.")
            modlog.exception("Failed to find %s in the simlog %s." % (user_nml_path, simlog))
            nml_log = None  # -> operates as a null sentinel
            init_con_log = None


    else:
        # - We don't have a manually consistent nml
        printer.print("%s\t.nml file was not explicit. Constructing from scratch..." % fdbg_string)
        printer.print("%s\tSeeking initial conditions data..." % fdbg_string)

        #  Obtaining initial conditions from the user / flags
        # ----------------------------------------------------------------------------------------------------------------- #
        if not user_arguments.ic:
            # - The initial conditions are not specified by flag. Fetching.
            printer.print("%s\t\tInitial condition was not provided explicitly. Going to file selection..." % fdbg_string,
                          end="\n")
            sleep(2)
            # - Grabbing initial conditions from the user.
            try:
                selected_initial_condition_path = select_files([pt.Path(initial_conditions_directory)], max=1,
                                                               condition=lambda f: (f.suffix in types["extensions"][
                                                                   "initial_conditions"]) or os.path.isdir(
                                                                   f))[0]
                os.system('cls' if os.name == 'nt' else 'clear')
                printer.reprint(end="")
                printer.print(done_string)
            except IndexError:
                os.system('cls' if os.name == 'nt' else 'clear')
                printer.reprint(end="")
                printer.print(fail_string)
                sys.exit()
        else:
            # - We have been given an explicit initial conditions file.
            printer.print("%s\tInitial condition was provided explicitly. Checking for validity...", end="")
            selected_initial_condition_path = pt.Path(user_arguments.ic)

            if selected_initial_condition_path.suffix not in types["extensions"]["initial_conditions"]:
                raise PyHPC_Error("The selected initial condition file is not valid.")

            printer.print(done_string)

        printer.print("%s\tInitial conditions data successfully obtained." % fdbg_string)

        #  Grabbing the initial condition from the simulation log
        # ---------------------------------------------------------------------------------------------------------------- #
        printer.print("%s\tGrabbing IC data from simulation log..." % fdbg_string, end="")
        try:
            init_con_log = simlog.ics[str(selected_initial_condition_path)]
            printer.print(done_string)
        except KeyError:
            # - We failed to find the record in the simulation log, we now make the entry. - #
            print(fail_string)
            printer.print("%s\t\tFailed to find IC record in simulation log. Generating new record...", end="")

            #  Adding new IC to the log
            # ------------------------------------------------------------------------------------------------------------ #
            simlog.add({
                str(selected_initial_condition_path): {
                    "information": "Auto-generated record from ``run_ramses.py``."
                }
            }, auto_save=True)
            printer.print(done_string)
            init_con_log = simlog.ics[str(selected_initial_condition_path)]

        # ---------------------------------------------------------------------------------------------------------------- #
        # Managing the nml construction ================================================================================== #
        # ---------------------------------------------------------------------------------------------------------------- #
        printer.print("%s\tConstructing the .nml data..." % fdbg_string)
        printer.print("%s\t\tLoading default .nml template..." % (fdbg_string), end="")

        try:
            ramses_config_default = toml.load(ramses_nml_config)
        except FileNotFoundError:
            modlog.exception("Failed to locate the ramses configuration file at %s." % ramses_nml_config)
            raise PyHPC_Error("Failed to locate the ramses configuration file at %s." % ramses_nml_config)
        except toml.TomlDecodeError:
            modlog.exception("Failed to correctly load the file %s in TOML format." % ramses_nml_config)
            raise PyHPC_Error("Failed to correctly load the file %s in TOML format." % ramses_nml_config)

        printer.print(done_string)
        printer.print("%s\t\tEditing .nml preferences..." % fdbg_string, end="\n")

        #  Getting settings from the user
        # ----------------------------------------------------------------------------------------------------------------- #
        ramses_config_user = get_options(ramses_config_default, "RAMSES .nml Settings")

        os.system('cls' if os.name == 'nt' else 'clear')
        printer.reprint(end="")
        printer.print(done_string)

        printer.print("%s\tConstructed the .nml data." % fdbg_string)
        printer.print("%s\tGenerating the .nml file..." % fdbg_string)

        # ---------------------------------------------------------------------------------------------------------------- #
        # Generating the .nml file  ====================================================================================== #
        # ---------------------------------------------------------------------------------------------------------------- #

        # - Setting the IC - #
        ramses_config_user["META"]["ic_file"]["v"] = str(selected_initial_condition_path)
        # - Fetching the software - #
        nml_software = ramses_config_user["META"]["software"]["v"]

        printer.print("%s\t\tSoftware = %s. Recognized = %s." % (
            fdbg_string, nml_software, nml_software in types["software"]["RAMSES"]))

        if nml_software not in types["software"]["RAMSES"]:
            printer.print(fail_string)
            sys.exit()

        # - Fetching the output location -#
        if not user_arguments.nml_output:
            nml_output_loc = os.path.join(CONFIG["System"]["Directories"]["nml_directory"],
                                          input("%sPlease enter a name for the .nml file (*.nml): " % fdbg_string))
        else:
            nml_output_loc = user_arguments.nml_output

        printer.print("%s\tGenerating the .nml file at %s..." % (fdbg_string, nml_output_loc), end="")

        write_ramses_nml(ramses_config_user, nml_output_loc)

        printer.print(done_string)

        #  Adding the .nml to the simulation data
        # ---------------------------------------------------------------------------------------------------------------- #
        init_con_log.add({
            nml_output_loc: {
                "information": "Generated ``.nml`` from ``PyHPC.PyHPC_executables.run_ramses.py``.",
                "meta"       : {
                    "software": nml_software
                }
            }
        }, auto_save=True)
        nml_log = init_con_log.sims[nml_output_loc]
        nml_log.log("Created nml_log object for path=%s." % nml_output_loc, action="CREATED")

    # -------------------------------------------------------------------------------------------------------------------- #
    # Passing command to batch runner ==================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #

    # - Managing the selected nml - #
    if user_arguments.nml:
        nml_location = user_arguments.nml
    else:
        nml_location = nml_output_loc

    # - Generating the correct slurm file - #
    if not user_arguments.slurm_output:
        slurm_output = input("%sPlease enter the desired name of the .slurm file (EXCLUDE .slurm): " % fdbg_string)
        slurm_path = pt.Path(os.path.join(CONFIG["System"]["Directories"]["slurm_directory"], slurm_output))
    else:
        slurm_output = pt.Path(user_arguments.slurm_output).name
        slurm_path = pt.Path(user_arguments.slurm_output)

    #  Grabbing the necessary execution information
    # ----------------------------------------------------------------------------------------------------------------- #
    output_directory = ""

    while not len(output_directory):
        print(
            "%sPlease enter the name of the output directory.\n\t\t[Use only a name to generate a directory in the simulations directory]\n\t\t[Use $'path' to specify a full path]" % fdbg_string)
        output_directory = input("%sPlease enter the desired name of the output directory: " % fdbg_string)

        if not len(output_directory):
            print(fail_string, "The output directory must be specified!")

    if output_directory[0] == "$":
        # This is a full path
        output_directory = pt.Path(output_directory[1:])
    else:
        output_directory = pt.Path(os.path.join(CONFIG["System"]["Simulations"]["simulation_directory"], output_directory))

    if str(output_directory) not in nml_log.raw["outputs"]:
        nml_log.raw["outputs"][str(output_directory)] = {
            "meta": {
                "path"       : str(output_directory),
                "dateCreated": datetime.now().strftime('%m-%d-%Y_%H-%M-%S'),
                "slurm_path" : str(slurm_path)
            }
        }
        nml_log.log("Added output at %s." % str(output_directory), "ADD_OUTPUT")
    else:
        nml_log.raw["outputs"][str(output_directory)]["meta"] = {
                "path"       : str(output_directory),
                "dateCreated": datetime.now().strftime('%m-%d-%Y_%H-%M-%S'),
                "slurm_path" : str(slurm_path)
            }
        nml_log.save()
        nml_log.log("Updated output at %s." % str(output_directory), "UPDATED_OUTPUT")

    #  Generating the slurm file
    # ----------------------------------------------------------------------------------------------------------------- #
    printer.print("%sGenerating the slurm executable..." % fdbg_string, end="\n")

    with open(os.path.join(pt.Path(__file__).parents[1], "PyHPC", "bin", "lib", "templates", "ramses_slurm.template"),
              "r") as template:
        write_slurm_file(template.read(),
                         name=slurm_output,
                         open_mpi_package=CONFIG["System"]["Modules"]["open_mpi_package"],
                         gcc_package=CONFIG["System"]["Modules"]["gcc_package"],
                         nml_path=nml_location,
                         output_dir=output_directory,
                         executable=CONFIG["System"]["Executables"][types["software"]["RAMSES"][nml_software]["exec"]]
                         )

    nml_log.log("Generated slurm file for %s" % str(output_directory), "MADE_SLURM", output=str(output_directory))

    os.system('cls' if os.name == 'nt' else 'clear')
    printer.reprint(end="")
    printer.print(done_string)

    if not user_arguments.stop:
        printer.print("%sAdding the job to the SLURM queue..." % fdbg_string, end="")
        os.system("sbatch %s" % slurm_path)
        nml_log.log("Ran slurm file for %s" % str(output_directory), "RAN_SLURM", output=str(output_directory))

        printer.print(done_string)
