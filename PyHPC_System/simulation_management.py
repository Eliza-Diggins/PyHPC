"""
Subroutines for finding and managing the simulations produced in the course of use.
"""
import os
import pathlib as pt
import sys

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
from PyHPC_Core.log import get_module_logger
from PyHPC_Core.configuration import read_config
from PyHPC_Utils.remote_utils import rclone_listdir
import pathlib as pt
import threading as t
import warnings
from PyHPC_Core.utils import time_function
import json
from datetime import datetime
from time import perf_counter
import numpy as np
from colorama import Fore,Style,Back
# generating screen locking #
screen_lock = t.Semaphore(value=1)  # locks off multi-threaded screen.
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_System"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = get_module_logger(_location, _filename)
# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

# -------------------------------------------------------------------------------------------------------------------- #
# Simulation Log Object ============================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
class SimulationLog:
    """
    Contains the core structure of simulation logging tasks.
    """
    _required = [
        "r_path"
    ]
    def __init__(self,path=os.path.join(CONFIG["System"]["Directories"]["bin"],"configs","Simlog.json")):
        """
        Initializes the Simulation Log
        :param path: The path to the simulation log. If none, a blank is generated.
        """
        #  Intro debugging
        # ----------------------------------------------------------------------------------------------------------------- #
        modlog.debug("Loading a SimulationLog object at %s."%path)

        #  Setup
        # ----------------------------------------------------------------------------------------------------------------- #
        self.path = path
        if self.path:
            try:
                modlog.debug("Attempting to load simulation log from %s."%self.path)
                with open(self.path,"r") as file:
                    self.log = json.load(file)

                modlog.debug("Successfully loaded %s."%self.path)

            except json.JSONDecodeError:
                modlog.exception("Failed to load the simulation log at %s. Proceeding as blank."%self.path)
                self.path = None
            except FileNotFoundError:
                modlog.exception("Failed to find the simulation log file at %s. Proceeding as blank"%self.path)
                self.path = None


        if not self.path:  # -> We need to generate a value.
            modlog.debug("No path was specified so SimulationLog object is initialized blank.")
            self.log = {"info":[],
                        "sims":{},
                        "ics":{}}

        #  Separating parts
        # ----------------------------------------------------------------------------------------------------------------- #
        try:
            self.sims, self.ics = self.log["sims"],self.log["ics"]
        except KeyError:
            modlog.exception("either 'sims' or 'ics' is not in the log correctly.")
            raise SyntaxError("The simulation log does not have the correct format.")

    def __len__(self):
        return len(self.sims),len(self.ics)

    def __repr__(self):
        return "SimulationLog Object - path = %s - size = %s"%(self.path,self.__len__())

    def __str__(self):
        return "SimulationLog Object - path = %s"%self.path

    def keys(self):
        return list(self.sims.keys()),list(self.ics.keys())

    def __setitem__(self, key, value):
        keys = self.keys()

        if key not in keys[0]+keys[1]:
            raise KeyError("The key %s is not in %s. Use .add to add an new value."%(key,self.__str__()))
        elif (key in keys[0]) and (key in keys[1]):
            modlog.warning("The key %s appears twice in the simulation log. Setting the simulation")
            self.log["sims"][key] = value

        elif key in keys[0]:
            self.log["sims"][key] = value

        else:
            self.log["ics"][key] = value


    def __contains__(self, item):
        if item in self.keys():
            return True
        else:
            pass

    def add(self,category,name,**kwargs):
        """
        Adds a new entry to the simulation log object.
        :param category: "sims" or "ics"
        :param name: The name of the new element to generate.
        :param kwargs: Parameters to give the new entry.
        :return: None
        """
        #  Intro debugging
        # ----------------------------------------------------------------------------------------------------------------- #
        modlog.debug("Adding item %s to category %s of %s."%(name,category,self.__str__()))

        #  Sanity Check
        # ----------------------------------------------------------------------------------------------------------------- #
        if name in self.log[category]:
            raise ValueError("%s is already in %s. Delete it first to replace."%(name,self.__str__()))

        if any([i not in kwargs for i in self._required]):
            raise ValueError("New entry with kwargs = %s failed to contain all required fields %s."%(kwargs,self._required))

        #- Checking for duplication issues -#
        if any([i["r_path"] == kwargs["r_path"] for i in self.log[category]]):
            raise ValueError("There is a matched path behavior between %s and another entry."%name)

        #  Managing kwarg parsing
        # ----------------------------------------------------------------------------------------------------------------- #
        #- Fixing the creation time -#
        if "r_creation_time" not in kwargs:
            modlog.debug("'r_creation_time' not in kwargs, but is required. Generating time now.")
            kwargs["r_creation_time"] = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')

        if "initial_conditions_file" in kwargs and category == "sims": #- Simulation listed ics
            modlog.debug("Searching for matched ICs for name = %s and ic_path = %s."%(name,kwargs["initial_conditions_file"]))
            #- Searching for matches -#
            src = self.search("ics",r_path = kwargs["initial_conditions_file"])

            if len(src):
                modlog.debug("Found match to %s."%src)
                self.log["ics"][src[0]]["used_in"] = name

            else:
                modlog.debug("Adding new ic file with name %s_ic."%name)
                self.add("ics","%s_ic"%name,used_in = name,r_path=kwargs["initial_conditions_file"])




    def remove(self,category,name):
        del self.log[category][name]

    def search(self,category,**kwargs):
        out = []
        for k,v in self.log[category].items():
            match = (all([vi==vk for vi,vk in zip([v[j] for j in list(kwargs.keys())],
                                                  list(kwargs.values()))
                          ]) if set(kwargs.keys()) <= set(v.keys()) else False)
            if match:
                out.append(k)
            else:
                pass

        return out





if __name__ == '__main__':
    simlog = SimulationLog()
    print(simlog.log)
    print(simlog.search("sims",r_path="/home/ediggins"))