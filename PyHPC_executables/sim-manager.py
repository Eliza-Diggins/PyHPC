"""
======================
Simulation Log Manager
======================
"""
import os
import pathlib as pt
import sys

import pandas as pd

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from PyHPC.PyHPC_Utils.text_display_utilities import TerminalString,get_yes_no, print_title, KeyLogger,get_dict_str,edit_dictionary
from tqdm import tqdm
from time import sleep
import argparse
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_System.simulation_management import SimulationLog
import logging
from PyHPC.PyHPC_Core.log import configure_logging
import json
from PyHPC.PyHPC_Utils.standard_utils import getFromDict,isInDict
from sshkeyboard import listen_keyboard
# -------------------------------------------------------------------------------------------------------------------- #
# Setup ============================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
CONFIG = read_config()
modlog = logging.getLogger("PyHPC_executables.sim-manager.py")

#  Grabbing core information
# ----------------------------------------------------------------------------------------------------------------- #
with open(os.path.join(pt.Path(__file__).parents[1], "PyHPC", "bin", "lib", "struct", "simlog_struct.json"),
          "r") as _struct:
    struct = json.load(_struct)


# -------------------------------------------------------------------------------------------------------------------- #
# Utilites =========================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def get_frame(simobject, available_columns):
    """
    Gets the relevant frame for the object in question.
    Parameters
    ----------
    simobject: The simulation object in question.

    Returns
    -------

    """
    _name = type(simobject).__name__  #: The name of the simulation object class.
    columns = available_columns[_name]


    data = simobject.listed

    output_frame = pd.DataFrame({**{"Name":[key for key in data]},**{
        column: [getFromDict(data[key], maplist) if isInDict(data[key], maplist) else "N.S." for key in data]  for column, maplist in columns.items()
    }})

    return output_frame


def get_cols(dictionary, location=None):
    if not location:
        location = []
    out = {}

    for k, v in dictionary.items():
        if isinstance(v, dict):
            out = {**out, **get_cols(v, location=location + [k])}
        elif isinstance(v, str):
            out[k] = location + [k]
    return out


if __name__ == '__main__':
    # -------------------------------------------------------------------------------------------------------------------- #
    # Pre-Management ===================================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #
    available_columns = {
        k: get_cols(struct[k]["format"]) for k in list(struct.keys())[1:]
    }
    # -------------------------------------------------------------------------------------------------------------------- #
    # Title Page ========================================================================================================= #
    # -------------------------------------------------------------------------------------------------------------------- #
    configure_logging(__file__)
    terminal = TerminalString()
    print_title(print)
    print(terminal.str_in_grid(""))
    print(terminal.str_in_grid("Simulation Manager", alignment="center"))
    print(terminal.str_in_grid(""))
    print(terminal.h)
    # -------------------------------------------------------------------------------------------------------------------- #
    # Argument Parsing =================================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--simlog", "-s", help="The simulation log to link to", default=None)
    args = arg_parser.parse_args()
    #  False Loading Screen
    # ----------------------------------------------------------------------------------------------------------------- #
    for i in tqdm(range(100), desc="[Sim-Manager]: Loading...", bar_format="{desc}: {percentage:3.0f}%|{bar}|",
                  ncols=terminal.dim_alt[0]):
        sleep(0.01)
    input("[Sim-Manager]: Press any key to continue...")

    #  Loading the simulation log
    # ----------------------------------------------------------------------------------------------------------------- #
    try:
        _simulation_log = SimulationLog(path=args.simlog)
    except FileNotFoundError:
        modlog.exception("Failed to find the simulation log at %s." % args.simlog)
        print("[Sim-Manager]: (CRITICAL) Failed to load simulation log...")
        print("[Sim-Manager]: Exiting...")
        sys.exit()

    print("[Sim-Manager]: Successfully loaded %s." % _simulation_log)
    sleep(1)
    # -------------------------------------------------------------------------------------------------------------------- #
    # Main Cycle ========================================================================================================= #
    # -------------------------------------------------------------------------------------------------------------------- #
    #  Setup
    # ----------------------------------------------------------------------------------------------------------------- #
    klog = KeyLogger(object=_simulation_log,  # The simulation log
                     position=0,  # The position in the list
                     selected=[], # The selected objects
                     command=None,  # The command to run
                     location=[_simulation_log],  # The full position
                     exit=False,
                     reframe=True)  # True to exit

    #  Entering main cycle
    # ----------------------------------------------------------------------------------------------------------------- #
    frame = None
    while not klog.exit:
        os.system('cls' if os.name == 'nt' else 'clear')

        #  Printing
        # ----------------------------------------------------------------------------------------------------------------- #
        if not isinstance(klog.object,dict):
            if klog.reframe:
                frame = get_frame(klog.object,available_columns)
                klog.reframe = False

            terminal.print_frame(frame,location=klog.position,selected=klog.selected)

            listen_keyboard(klog.sim_manager_keylog)

            if klog.command:
                #  Klog command is active
                # ----------------------------------------------------------------------------------------------------------------- #
                if klog.command == "enter":
                    #- We are moving down a level -#
                    ##- Reseting klog -##
                    if len(klog.object.listed)> 0 and len(klog.location)<3:
                        if type(klog.object).__name__ == "SimRec":
                            klog.object = klog.object[["outputs",list(klog.object.listed.keys())[klog.position]]]
                        else:
                            klog.object = klog.object[list(klog.object.listed.keys())[klog.position]]
                            klog.reframe = True

                        klog.location += [klog.object if not isinstance(klog.object,dict) else list(klog.location[-1].listed.keys())[klog.position]]
                        klog.position = 0
                        klog.selected = []

                if klog.command == "log" and len(klog.location) >= 1:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    if type(klog.object).__name__ != "SimRec":
                        print(get_dict_str(klog.object[list(klog.object.listed.keys())[klog.position]].raw["action_log"]))
                    else:
                        print(get_dict_str(klog.object["outputs"][list(klog.object.listed.keys())[klog.position]]["action_log"]))
                    input("[Sim-Manager]: Hit any key and enter to return")
                if klog.command == "back":
                    if type(klog.object).__name__ != "SimulationLog":
                        if not isinstance(klog.location[-1],str):
                            klog.position = list(klog.location[-2].listed.keys()).index(klog.location[-1].name)
                        else:
                            klog.position = list(klog.location[-2].listed.keys()).index(klog.location[-1])
                        klog.object = klog.object.parent
                        klog.reframe = True
                        klog.location = klog.location[:-1]
                    else:
                        val = get_yes_no("Exit Simulation Manager?")

                        if val:
                            exit()
                if klog.command == "select":
                    if klog.position not in klog.selected:
                        klog.selected += [klog.position]
                    else:
                        klog.selected.remove(klog.position
                                             )
                if klog.command == "delete":
                    verify = get_yes_no("[Sim-Manager]: Delete %s Items from %s?"%(len(klog.selected),_simulation_log))

                    if verify:
                        for id in klog.selected:
                            if type(klog.object).__name__ != "SimRec":
                                obj = klog.object[list(klog.object.listed.keys())[id]]
                            else:
                                obj = klog.object.listed[list(klog.object.listed.keys())[id]]

                            print("Sim-Manager]: Deleting %s."%obj)
                            if not isinstance(obj,dict):
                                obj.delete()
                            else:
                                #- This is a dictionary
                                del klog.location[-1].raw["outputs"][list(klog.location[-1].raw["outputs"].keys())[id]]
                                klog.location[-1].save()


                        input("[Sim-Manager]: Press any key to proceed...")
                        _simulation_log.save()
                        klog.reframe = True
                        klog.position = 0
                        klog.object = klog.location[-1]
                        klog.selected = []
                if klog.command == "edit":
                    if type(klog.object).__name__ == "SimRec":
                        klog.object["outputs"][list(klog.object.listed.keys())[klog.position]]=  edit_dictionary(
                            klog.object["outputs"][list(klog.object.listed.keys())[klog.position]], "Simulation Log Editor")
                        klog.object.save()
                    else:
                        klog.object[list(klog.object.listed.keys())[klog.position]].raw =edit_dictionary(klog.object[list(klog.object.listed.keys())[klog.position]].raw,"Simulation Log Editor")
                        klog.object.save()

                    klog.reframe = True
                if klog.command == "add":
                    klog.object.add(edit_dictionary({},"Create the preferred dictionary"))
                    klog.reframe = True


            klog.command = None
        else:
            print(get_dict_str(klog.object))
            input("[Sim-Manager]: Hit any key and enter to return")
            klog.object=klog.location[-2]
            klog.reframe=True