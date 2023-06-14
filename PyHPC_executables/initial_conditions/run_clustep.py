"""
Runtime implementation for CLUSTEP to be integrated into the ``PyHPC`` system.
"""
import argparse
import json
import os
import pathlib as pt
import sys
import warnings
from datetime import datetime

import numpy as np
import toml
from colorama import Fore, Style
from tqdm import tqdm


sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[2]))
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.log import get_module_logger
from PyHPC.PyHPC_Utils.text_display_utilities import TerminalString, PrintRetainer, build_options, get_yes_no
from PyHPC.PyHPC_System.simulation_management import SimulationLog
from PyHPC.PyHPC_Utils.analysis_utils import recenter
from PyHPC.PyHPC_Core.utils import write_ini
from PyHPC.PyHPC_System.io import write_slurm_file

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
clustep_ini = toml.load(os.path.join(CONFIG["System"]["Directories"]["bin"], "configs", "CLUSTEP.config"))


# -------------------------------------------------------------------------------------------------------------------- #
# Functions        =================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def get_clustep_report(clustep_data):
    """
    Provides a report of the ``clustep_data`` being passed to the system.

    Parameters
    ----------
    clustep_data: dict
        The data to analyze.

    Returns
    -------
    None

    -------

    """
    #  Setup and Management
    # ----------------------------------------------------------------------------------------------------------------- #
    n_comps = len(clustep_data)
    pos = [comp["position"]["position"]["v"] for comp in clustep_data.values()]
    vel = [comp["position"]["velocity"]["v"] for comp in clustep_data.values()]
    particles = [[int(comp[h]["N_%s" % k]["v"]) for h, k in zip(["dark_matter", "gas"], ["dm", "gas"])] for comp in
                 clustep_data.values()]
    masses = [[np.format_float_scientific(10e10 * float(comp[h]["M_%s" % k]["v"]), precision=3) for h, k in
               zip(["dark_matter", "gas"], ["dm", "gas"])] for comp in clustep_data.values()]

    #  Beginning printing process
    # ----------------------------------------------------------------------------------------------------------------- #
    printer.print("#------------------------ IC Report --------------------------#")
    for i, data in enumerate(zip(pos, vel, particles, masses, [
        [np.format_float_scientific(float(masses[i][j]) / particles[i][j], precision=3) for j in
         range(len(particles[0]))] for i in range(len(particles))])):
        p, v, part, m, mp = data
        printer.print("# Component %s: Position=%s kpc, Velocity=%s km/s" % (i + 1, p, v))
        printer.print("\t\tParticles=%s" % part)
        printer.print("\t\tMasses=%s M_sol" % m)
        printer.print("\t\tMass per particle = %s M_sol" % mp)

    printer.print("#      ------------------  Totals  -----------------          #")
    printer.print("Mass = %s Msol, Particles = %s ." % (
        np.format_float_scientific(np.sum([float(i) for i in np.array(masses).ravel()]), precision=3),
        np.format_float_scientific(np.sum([float(i) for i in np.array(particles).ravel()]), precision=3)))
    printer.print("#------------------------ IC Report --------------------------#")


def reduce_dict(dictionary):
    out_dict = {}
    for k, v in dictionary.items():
        if "v" in v:
            out_dict[k] = v["v"]
        else:
            out_dict[k] = reduce_dict(v)
    return out_dict


if __name__ == '__main__':
    # -------------------------------------------------------------------------------------------------------------------- #
    # Core Execution   =================================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #
    #  Argument Parsing
    # ----------------------------------------------------------------------------------------------------------------- #
    printer.print("%sLoading command line arguments..." % fdbg_string, end="\n")
    # - Generating the arg parser

    argparser = argparse.ArgumentParser()

    # - Adding arguments to the argument parser
    argparser.add_argument("-s", "--stop", action="store_true", help="Enable tag to stop prior to execution.")
    argparser.add_argument("-nb", "--no_batch", action="store_true",
                           help="Enable to proceed without passing to SLURM scheduler.")
    argparser.add_argument("--simulation_log", help="The path to the prefered simulation log. (OPTIONAL)", default=None)
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
    printer.print("%sGetting user inputs..." % fdbg_string, end="")

    # - Loading the defaults -  #
    os.system('cls' if os.name == 'nt' else 'clear')
    clustep_options = build_options(clustep_ini, "Select CLUSTEP runtime options")
    printer.print(done_string)
    os.system('cls' if os.name == 'nt' else 'clear')
    printer.reprint()

    printer.print("%sFixing position / velocity formatting issues..." % fdbg_string, end="")

    for key in clustep_options:
        clustep_options[key]["position"]["position"]["v"] = [float(i) for i in
                                                             clustep_options[key]["position"]["position"]["v"].split(",")]
        clustep_options[key]["position"]["velocity"]["v"] = [float(i) for i in
                                                             clustep_options[key]["position"]["velocity"]["v"].split(",")]
    printer.print(done_string)
    #  Showing the report
    # ----------------------------------------------------------------------------------------------------------------- #
    printer.print("%sCreating options report..."%fdbg_string)
    get_clustep_report(clustep_options)
    input("%sPress any key to continue" % fdbg_string)

    #  Coercing particle masses
    # ----------------------------------------------------------------------------------------------------------------- #

    printer.print("%sChecking that particle masses are consistent..." % fdbg_string)
    # - Computing necessary arrays - #
    particles = [[int(comp[h]["N_%s" % k]["v"]) for h, k in zip(["dark_matter", "gas"], ["dm", "gas"])] for comp in
                 clustep_options.values()]
    masses = [[10e10 * float(comp[h]["M_%s" % k]["v"]) for h, k in
               zip(["dark_matter", "gas"], ["dm", "gas"])] for comp in clustep_options.values()]

    m_p = np.array(
        [[float(masses[i][j]) / particles[i][j] for j in range(len(particles[0]))] for i in range(len(particles))])

    mins = np.amin(m_p, axis=0)
    # - Checking the array - #
    errs = []
    for col in range(m_p.shape[-1]):
        if len(list(set(list(m_p[:, col])))) > 1:
            errs.append(col)
            printer.print("%s\tFound inconsistencies in column %s" % (fdbg_string, col))
        else:
            pass

    # - Fixing - #
    if not len(errs):
        printer.print("%sConsistency check passed." % fdbg_string)
    else:
        for col in errs:
            printer.print("%s\tFixing inconsistency in column %s by setting mass/particle to %s." % (fdbg_string, col, mins[col]))
            for entry, component in enumerate(clustep_options):
                clustep_options[component][["dark_matter", "gas"][col]]["N_%s" % (["dm", "gas"][col])]["v"] = \
                    np.array(masses)[entry, col] / mins[col]
            printer.print("%s\tFixed inconsistency in column %s." % (fdbg_string, col))

    get_clustep_report(clustep_options)

    #  Setting up the run
    # ----------------------------------------------------------------------------------------------------------------- #
    # At this stage, we need to first generate each of the clusters by executing clustep on the correct .ini file. As such,
    #  1. We first generate the .ini in a temp file.
    #  2. We run through the clustep operations, then through snapgadget.
    printer.print("\n\n%sPreparing to proceed with the execution process..." % fdbg_string)
    # -------------------------------------------------------------------------------------------------------------------- #
    # Managing Simulation Logging ======================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #
    printer.print("%s\tManaging simulation logging..." % fdbg_string)
    simlog = SimulationLog(path=user_arguments.simulation_log)  # loading the simulation log

    # - Checking name - #
    _procedure_check = False  # -> used to check the loop
    ic_name = ""
    while not _procedure_check:
        ic_name = pt.Path(os.path.join(CONFIG["System"]["Directories"]["ic_directory"],
                                       input(
                                           "%s\t\tPlease enter a name for the IC file. [Relative to IC directory]: " % fdbg_string)))

        # - Figuring out the correct name - #
        if ic_name.suffix == "":
            ic_name = pt.Path(str(ic_name) + ".dat")

        ##- Is it a duplicate? -##
        if str(ic_name) in simlog.ics:
            os.system('cls' if os.name == 'nt' else 'clear')
            printer.reprint()
            _yn = get_yes_no("%sIC file %s already exists. Overwrite?" % (fdbg_string,str(ic_name)))

            if _yn:
                _procedure_check = True
            else:
                pass
        else:
            _procedure_check = True

    # - Adding - #
    simlog.add({str(ic_name): {
        "components" : reduce_dict(clustep_options),
        "information": "Initial Condition generated by Clustep with %s Components." % len(clustep_options)
    }})
    printer.print("%sCompleted simlog compliance."%fdbg_string)
    #  Computing COM locations in sequence.
    # ----------------------------------------------------------------------------------------------------------------- #
    printer.print("%sRelocating positions to facilitate generation..." % fdbg_string, end="")
    pos = [np.array(comp["position"]["position"]["v"]) for comp in clustep_options.values()]
    masses = np.sum(masses, axis=-1).ravel()

    new_pos = recenter(pos, masses)

    for index, comp in enumerate(clustep_options):
        clustep_options[comp]["position"]["position"]["v"] = list(new_pos[:, index])
    printer.print(done_string)

    # -------------------------------------------------------------------------------------------------------------------- #
    # Writing the .ini file ============================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #
    _temporary_directory = os.path.join(pt.Path(__file__).parents[2].absolute(), "PyHPC", "bin", ".tmp",
                                        datetime.now().strftime('%m-%d-%Y_%H-%M-%S'))
    printer.print("%sGenerated the temporary directory at %s..."%(fdbg_string,_temporary_directory),end="")

    if not os.path.exists(_temporary_directory):
        pt.Path(_temporary_directory).mkdir(parents=True)

    for index, cluster in enumerate(tqdm(clustep_options), 1):
        # - Fetching the usable part of the dictionary to pass through - #
        _ini_writable_dict = reduce_dict(
            {k: v for k, v in clustep_options[cluster].items() if k not in ["tags", "position"]})

        with open(os.path.join(_temporary_directory, "Cluster%s.ini" % index), "w+") as ini_file:
            write_ini(_ini_writable_dict, ini_file)

    printer.print(done_string)
    simlog.ics[str(ic_name)].log(
        "generated .ini files in %s." % (_temporary_directory),
        "CREATE-INI")

    # -------------------------------------------------------------------------------------------------------------------- #
    # Writing snapgadget exec     ======================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #
    if len(clustep_options) != 1:
        # ! We need to generate a snapgadget directive because we are going to have to combine things.
        printer.print("%sGenerating the snapgadget directives for execution..."%fdbg_string,end="")
        with open(os.path.join(_temporary_directory, "snapgadget_directive.txt"), "w+") as snapfile:
            for index in range(1, len(clustep_options)):
                # Iterate through all of the clustep objects.
                if index == 1:
                    # This is the first line of the file #
                    line = "%s+%s+%s+%s+%s+%s+%s+%s+%s\n" % tuple([os.path.join(_temporary_directory, "Cluster1.dat"),
                                                                   os.path.join(_temporary_directory, "Cluster2.dat"),
                                                                   os.path.join(_temporary_directory, "temp.dat"),
                                                                   *clustep_options[list(clustep_options.keys())[index]][
                                                                       "position"]["position"]["v"],
                                                                   *clustep_options[list(clustep_options.keys())[index]][
                                                                       "position"]["velocity"]["v"]])
                else:
                    line = "%s+%s+%s+%s+%s+%s+%s+%s+%s\n" % tuple([os.path.join(_temporary_directory, "temp.dat"),
                                                                   os.path.join(_temporary_directory,
                                                                                "Cluster%s.dat" % (index + 1)),
                                                                   os.path.join(_temporary_directory, "temp.dat"),
                                                                   *clustep_options[list(clustep_options.keys())[index]][
                                                                       "position"]["position"]["v"],
                                                                   *clustep_options[list(clustep_options.keys())[index]][
                                                                       "position"]["velocity"]["v"]])
                snapfile.write(line)
        print(done_string)
        simlog.ics[str(ic_name)].log(
            "generated snapgadget_directive.txt file in %s." % (os.path.join(_temporary_directory)),
            "CREATE-SNAP-DIRECTIVE")
    # -------------------------------------------------------------------------------------------------------------------- #
    # Writing the executable script ====================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #
    if user_arguments.no_batch:
        printer.print("%sGenerating the executable..." % fdbg_string, end="\n")

        with open(os.path.join(pt.Path(__file__).parents[2], "PyHPC", "bin", "lib", "templates", "clustep_exe.template"),
                  "r") as template:
            with open(os.path.join(_temporary_directory, "exec.sh"), "w+") as writer:
                writer.write(template.read() % {
                    "csh_interp"       : CONFIG["System"]["Modules"]["csh_interp"],
                    "python_env_script": CONFIG["System"]["Modules"]["python_env_script"],
                    "python_exec"      : CONFIG["System"]["Modules"]["python_exec_name"],
                    "components"       : len(clustep_options),
                    "output_dir"       : str(ic_name.parents[0]),
                    "temp_dir"         : str(_temporary_directory),
                    "working_directory": CONFIG["System"]["Executables"]["clustep_executable_directory"],
                    "output_name"      : str(ic_name),
                    "snapgadget"       : os.path.join(CONFIG["System"]["Modules"]["snapgadget_dir"], "snapjoin.py"),
                    "fdbg" : fdbg_string
                })
        printer.print(done_string)
        simlog.ics[str(ic_name)].log(
            "created exec.sh in %s." % (os.path.join(_temporary_directory)),
            "CREATE-SLURM",slurm=False)

        os.system("chmod 777 %s" % (os.path.join(_temporary_directory, "exec.sh")))

        os.system('cls' if os.name == 'nt' else 'clear')
        printer.reprint()
        os.system((os.path.join(_temporary_directory, "exec.sh"))+" &")

        simlog.ics[str(ic_name)].log(
            "ran exec.sh in %s." % (os.path.join(_temporary_directory)),
            "RAN-SLURM",slurm=False)
    else:
        slurm_output = input("%sPlease enter the desired name of the .slurm file (EXCLUDE .slurm): " % fdbg_string)
        slurm_path = pt.Path(os.path.join(CONFIG["System"]["Directories"]["slurm_directory"], slurm_output))
        printer.print("%sGenerating the executable..." % fdbg_string, end="\n")
        with open(os.path.join(pt.Path(__file__).parents[2], "PyHPC", "bin", "lib", "templates", "clustep_slurm.template"),
                  "r") as template:
            write_slurm_file(template.read(), name=slurm_output, **{
                "csh_interp"       : CONFIG["System"]["Modules"]["csh_interp"],
                "python_env_script": CONFIG["System"]["Modules"]["python_env_script"],
                "python_exec"      : CONFIG["System"]["Modules"]["python_exec_name"],
                "components"       : len(clustep_options),
                "output_dir"       : str(ic_name.parents[0]),
                "temp_dir"         : str(_temporary_directory),
                "working_directory": CONFIG["System"]["Executables"]["clustep_executable_directory"],
                "output_name"      : str(ic_name),
                "snapgadget"       : os.path.join(CONFIG["System"]["Modules"]["snapgadget_dir"], "snapjoin.py")
            })
        printer.print(done_string)
        #  Managing final execution
        # ----------------------------------------------------------------------------------------------------------------- #
        simlog.ics[str(ic_name)].log(
            "created %s"%slurm_path,
            "CREATED-SLURM",slurm=True)

        os.system('cls' if os.name == 'nt' else 'clear')
        printer.reprint(end="")
        printer.print(done_string)

        if not user_arguments.stop:
            printer.print("%sAdding the job to the SLURM queue..." % fdbg_string, end="")
            os.system("sbatch %s" % slurm_path+".SLURM")
            simlog.ics[str(ic_name)].log(
                "ran %s" % slurm_path,
                "RAN-SLURM", slurm=True)
            printer.print(done_string)
