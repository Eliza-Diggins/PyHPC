"""
=============================
Initial Conditions Generation
=============================

One of the core pieces of a hydrodynamic simulation is the initial conditions. These are essentially lists of
values for various parameters throughout either the grid (AMR) or the set of particles (SPH) which provide the starting
point for the simulation to run.

``PyHPC.PyHPC_executables.run_ic_gen.py`` links up all of the available initial conditions generators in the system
to allow for the general construction of initial conditions with relative ease. Further sections will describe in
detail the functionality of each case.

General Execution
-----------------
:py:mod:`PyHPC_executables.run_ic_gen` is essentially a wrapper for a variety of different implementations of
3rd party softwares which must be installed and configured separately. Installation instructions for each of these
softwares can be found in the :doc:`software guide <../software>`. To use the IC generator, the command line should
be used,

>>> python3 'PyHPC_executables/run_ic_gen.py'
optional arguments:
  -h, --help            show this help message and exit
  -s, --stop            Enable tag to stop prior to execution.
  -nb, --no_batch       Enable to proceed without passing to SLURM
                        scheduler.
  --simulation_log SIMULATION_LOG
                        The path to the prefered simulation log.
                        (OPTIONAL)

The script will allow the user to choose which of the software options to use and will guide the user through the process
of running each of the initial condition generators.

============================
Available Software Packages
============================

CLUSTEP
-------

.. note::
    **Generation Note:** ``.ini -> .dat``

``Clustep`` is the simplest of the available initial conditions softwares. It generates spherically symmetric
clusters or groups of clusters which are in hydrostatic equilibrium.

To generate an initial condition in ``Clustep``, run

>>> python3 'PyHPC_executables/run_ic_gen.py'
+-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=+
|                                                                                                                                                        |
|                                                                    Software Selector                                                                   |
|                                                                                                                                                        |
+-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=+
+-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=+
| clustep : [ | ] --- ['initial_conditions', 'run_clustep.py']                                                                                           |
+-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=+

select ``clustep`` from the list of available softwares and hit ``enter``. The user can then select options for the various
values of the components.

.. code-block:: commandline

    +-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=+
    | Select the option to edit...                                                                                                                           |
    +-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=+
    | Component 1                                                                                                                                            |
    +-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=+
    'backspace': move up level
    'enter': move down level / edit
    '+': add component
    '-': remove component
    'd': reset

Information pertaining to each of the settings for any given component are documented in the system or in the associated
`documentation <https://github.com/elvismello/clustep>`_. Each component can be located at a specific location in the
simulation box and may have a different mass, velocity, or other structural data pertaining to them.

Once the options have been selected and entered, an initial conditions report will appear:

.. code-block:: commandline

    PyHPC_executables:run_clustep: [Execution Wizard]: Beginning Execution:
    PyHPC_executables:run_clustep: [Execution Wizard]: Getting user inputs...[DONE]
    PyHPC_executables:run_clustep: [Execution Wizard]: Fixing position / velocity formatting issues...[DONE]
    PyHPC_executables:run_clustep: [Execution Wizard]: Creating options report...
    #------------------------ IC Report --------------------------#
    # Component 1: Position=[0.0, 0.0, 0.0] kpc, Velocity=[0.0, 0.0, 0.0] km/s
                    Particles=[100000, 100000]
                    Masses=['5.e+15', '1.5e+15'] M_sol
                    Mass per particle = ['5.e+10', '1.5e+10'] M_sol
    # Component 2: Position=[0.0, 0.0, 0.0] kpc, Velocity=[0.0, 0.0, 0.0] km/s
                    Particles=[100000, 100000]
                    Masses=['5.e+15', '1.5e+15'] M_sol
                    Mass per particle = ['5.e+10', '1.5e+10'] M_sol
    #      ------------------  Totals  -----------------          #
    Mass = 1.3e+16 Msol, Particles = 4.e+05 .
    #------------------------ IC Report --------------------------#
    PyHPC_executables:run_clustep: [Execution Wizard]: Press any key to continue
    PyHPC_executables:run_clustep: [Execution Wizard]: Checking that particle masses are consistent...
    PyHPC_executables:run_clustep: [Execution Wizard]: Consistency check passed.
    #------------------------ IC Report --------------------------#
    # Component 1: Position=[0.0, 0.0, 0.0] kpc, Velocity=[0.0, 0.0, 0.0] km/s
                    Particles=[100000, 100000]
                    Masses=['5.e+15', '1.5e+15'] M_sol
                    Mass per particle = ['5.e+10', '1.5e+10'] M_sol
    # Component 2: Position=[0.0, 0.0, 0.0] kpc, Velocity=[0.0, 0.0, 0.0] km/s
                    Particles=[100000, 100000]
                    Masses=['5.e+15', '1.5e+15'] M_sol
                    Mass per particle = ['5.e+10', '1.5e+10'] M_sol
    #      ------------------  Totals  -----------------          #
    Mass = 1.3e+16 Msol, Particles = 4.e+05 .
    #------------------------ IC Report --------------------------#

The user may review and proceed if the information is correct.

.. attention::
    During the recombination process, simulation components must all share the same mass / particle in order to
    actually function once passed to a simulation software. Therefore, the software will **automatically** force
    the number of particles in each component to adjust to make the mass per particle of each type equal across
    all components.

The user will then be asked to provide some basic input of the chosen initial conditions:

>>> Please enter a name for the IC file. [Relative to IC directory]: "example.dat"

At this stage, the software will generate all of the necessary data to execute the construction process. If you have
selected to use slurm (by not using the ``-nb`` flag), then you will be directed to configure slurm as usual. Otherwise,
execution will begin immediately.

**Clustep Diagram**

.. mermaid::

    flowchart TD
    A[Component Configuration] -- Add Components<br/>Change Settings --> A;
    A --Setup Finished --> B[IC Report]
    B --Particle mass normalization --> B
    B --> C[Select IC Name]
    C --> D[Add IC to Simulation Log]
    D -- Already Exists --> E[Ask permission to overwrite]
    D -- Doesn't exist --> F["Proceed to processing"]
    E --> F
    F -- ``-nb`` used --> G[.sh ccript written]
    F -- ``-nb`` not used --> H[.slurm script written]
    H -- ``-s`` used --> Z["Finish"]
    H -- ``-s`` not used --> I[Add to queue.]
    I --> Z
    G -- Execute Script --> Z
    J["Clustep Execution"] --> K[Count Components -C-]
    K --> L[Generate Component initial condition <br/>in -temp_dir- as -Cluster_n.ini-.]
    L -- Loop over all components --> L
    L -- All components generated in temp file <br/>now preparing to conjoin them --> M[Compute necessary positions]
    M -- Generate sequential final outputs --> N[Move final output to chosen directory] --> O["END"]

"""
import json
import os
import pathlib as pt
import sys
import warnings

from colorama import Fore, Style

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from PyHPC.PyHPC_Core.configuration import read_config
import logging
from PyHPC.PyHPC_Core.log import configure_logging
from PyHPC.PyHPC_Utils.text_display_utilities import print_title, TerminalString, PrintRetainer, option_menu

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_executables"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
fdbg_string = "%s [%s]: " % (_dbg_string, Fore.GREEN + "Execution Wizard" + Style.RESET_ALL)
CONFIG = read_config()
modlog = logging.getLogger(__name__)

printer = PrintRetainer()
# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

# - Organizational Strings -#
initial_conditions_directory = CONFIG["System"]["Directories"]["ic_directory"]
done_string = "[" + Fore.CYAN + Style.BRIGHT + "DONE" + Style.RESET_ALL + "]"
fail_string = "[" + Fore.RED + Style.BRIGHT + "FAILED" + Style.RESET_ALL + "]"

if __name__ == '__main__':

    # - Grabbing type information -#
    with open(os.path.join(pt.Path(__file__).parents[1], "PyHPC", "bin", "lib", "imp", "types.json"), "r") as type_file:
        types = json.load(type_file)

    configure_logging(_location)

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
        for command in os.listdir(os.path.join(pt.Path(__file__).parents[0], "initial_conditions")):
            print(Fore.GREEN + "python3 '%s' -h" % os.path.join(pt.Path(__file__).parents[1], "PyHPC_executables",
                                                                "initial_conditions", command) + Style.RESET_ALL)
            os.system(
                "python3 '%s' -h" % os.path.join(pt.Path(__file__).parents[1], "PyHPC_executables", "initial_conditions",
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
