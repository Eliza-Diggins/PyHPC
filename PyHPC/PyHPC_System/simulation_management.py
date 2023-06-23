"""
Simulation management tools for the PyHPC system. The core object ``SimulationLog`` is used by the backend to
store and manage simulations throughout the generation pipeline.
"""
import builtins
import json
import logging
import operator
import os
import pathlib as pt
import shutil
import threading as t
import warnings
from datetime import datetime
from functools import reduce
from inspect import getframeinfo, stack

from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Core.errors import PyHPC_Error
from PyHPC.PyHPC_Core.utils import NonStandardEncoder

# generating screen locking #
screen_lock = t.Semaphore(value=1)  # locks off multi-threaded screen.
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_System"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = logging.getLogger(__name__)
_structure_file = os.path.join(pt.Path(os.path.realpath(__file__)).parents[1], "bin", "lib", "struct",
                               "simlog_struct.json")

# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')


# -------------------------------------------------------------------------------------------------------------------- #
# Simulation Log Object ============================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
class SimulationLog:
    """
    The ``SimulationLog`` class is the super class object for simulation management and contains all the simulation
    data corresponding to a single log file.

    Parameters
    ----------
    path: str or pt.Path
        The path to the corresponding logging file.

    Notes
    -----
    The formatting for the simulation management objects is dictated by the ``/bin/bin/lib/struct/simlog_struct.json`` file,
    which has constraints on the formatting of each of the logging objects. The format is determined as follows:

    .. include:: ../../PyHPC/bin/lib/struct/simlog_struct.json
        :code:

    """

    def __init__(self, path=None):
        #  Introduction debug
        # ------------------------------------------------------------------------------------------------------------ #
        modlog.debug("Loading a SimulationLog from path %s" % path)

        #  Path Coercion
        # ------------------------------------------------------------------------------------------------------------ #
        if path:
            #: The path variable indicating the location of the underlying ``.json`` file.
            self.path = pt.Path(path)
        else:
            self.path = pt.Path(CONFIG["System"]["Directories"]["bin"], "configs", "Simlog.json")
            modlog.info("self.path was None, loading simulationlog from default location %s." % self.path)

        # Reading the path data
        # ------------------------------------------------------------------------------------------------------------ #
        #: ``self.raw`` (``dict``) is the core variable containing the raw data
        with open(self.path, "r+") as simfile:
            self.raw = json.load(simfile)

    # ---------------------------------------------------------------------------------------------------------------- #
    # Defining and Managing Properties =============================================================================== #
    # ---------------------------------------------------------------------------------------------------------------- #

    @property
    def ics(self):
        """
        Contains the dictionary of ``InitCon`` objects to use during execution.

        Returns
        -------
        val : dict of {str : InitCon}
            The dictionary of ``InitCon`` objects.
        """
        return {
            k: InitCon(k, v, parent=self) for k, v in self.raw.items()
        }

    @property
    def listed(self) -> dict:
        """Contains the ``self.raw`` object as a ``property``. This allows for a more uniform development structure."""
        return self.raw

    # ---------------------------------------------------------------------------------------------------------------- #
    # Dunder Methods ================================================================================================= #
    # ---------------------------------------------------------------------------------------------------------------- #

    def __repr__(self):
        """
        Defines the representation string for the ``SimulationLog`` object.

        Returns
        -------
        The string representation.
        """
        return "SimulationLog @ %(path)s; len=%(len)s" % {"path": self.path, "len": len(self.ics)}

    def __str__(self):
        """
        Defines ths string representation of the ``SimulationLog`` object.

        Returns
        -------
        The string representation.
        """
        return "SimulationLog @ %(path)s" % {"path": self.path}

    def __getitem__(self, item: list):
        """
        Defines the capacity to get items from the ``self.raw`` variable.
        Parameters
        ----------
        item : list
            The item position to pull from.

        Returns
        -------
        dict
            The dictionary sub-position generated.
        """
        if not isinstance(item, list):
            item = [item]
        try:
            return reduce(operator.getitem, item, self.ics)
        except KeyError:
            modlog.exception(
                "Failed to find key path %s in self.raw for SimulationLog object %s." % (item, self.__repr__()))
            self.__missing__(item)

    def __setitem__(self, keys: list, value):
        if not isinstance(keys, list):
            keys = [keys]
        self.__getitem__(keys[:-1])[keys[-1]] = value

    def __len__(self):
        return len(self.ics)

    def __contains__(self, item):
        return item in self.ics

    def __delitem__(self, key_list):
        if not isinstance(key_list, list):
            key_list = [key_list]
        del self.__getitem__(key_list[:-1])[key_list[-1]]

    def __iter__(self):
        return iter(self.ics)

    def __missing__(self, key):
        return None

    def get_simulation_records(self) -> dict:
        """
        Fetches all the ``SimRec`` objects in the ``SimulationLog``.

        Returns
        -------
        dict
            Dictionary of all the ``SimRec`` objects in the format ``{name:SimRec}``.
        """
        obs = {}
        for ic in self.ics.values():
            obs = {**obs, **ic.sims}

        return obs

    def search(self,
               search_kwargs: dict,
               search_for: str = "sim",
               return_by: str = "sim") -> list:
        """
        Searches the ``SimulationLog`` object for entries with data matching those stated in the ``search_kwargs``.
        The ``search_for`` and ``return_by`` parameters can be used to control the granularity of the search.

        Parameters
        ----------
        search_kwargs : ``dict``
            The ``kwargs`` to use for the search. Should be a set of ``{k:v,...}``.
            All objects matching the level of granularity specified by ``search_for`` will be queried to see if ``obj.raw`` includes the given kwargs.
            If the ``kwargs`` dictionary has ``list`` type entries, the search will be done based on an ``OR`` boolean search approach.
            Individual entries in the ``kwargs`` are searched based on ``AND`` booleans.
        search_for : ``str``
            The level of granularity to use in the search. can be ``sim`` or ``ic``.
        return_by : ``str``
            The level of granularity to return by. Can be ``sim`` or ``ic``.

        Returns
        -------
        Returns a list of matching objects.

        """
        #  Logging
        # ------------------------------------------------------------------------------------------------------------ #
        modlog.debug("Searching %s for %s by %s and for %s." % (repr(self), search_kwargs, search_for, return_by))

        #  Grabbing necessary pieces of data.
        # ------------------------------------------------------------------------------------------------------------ #
        search_group = self.ics if search_for == "ic" else list(self.get_simulation_records().values())
        modlog.debug("Search for %s in %s has %s search items." % (search_kwargs, repr(self), len(search_group)))

        # Performing the group search
        # ------------------------------------------------------------------------------------------------------------ #
        return_group = [item for item in search_group if all(
            (item[key] in value if isinstance(value, list) else item[key] == value) for key, value in search_kwargs)]

        #  Unsorting
        # ------------------------------------------------------------------------------------------------------------ #
        if return_by == search_for:
            # Return by and search for are the same so we can return exactly what we found.
            return return_group
        elif search_for == "ics":
            # search for is ics, return by is sims, so we need to get a list of all such simulations.
            ret_group = []
            for item in return_group:
                ret_group += item.sims

            return ret_group
        else:
            # Search is for sims, but we want to return ics.
            return list(set([item.parent for item in return_group]))

    def add(self, entries, auto_save=True, force=False):
        """
        adds the entry contained in ``**kwargs`` to the ``SimulationLog`` object. The ``entries`` may contain any number
        of individual entries to add.

        Parameters
        ----------
        auto_save : bool
            ``auto_save=True`` will immediately write the simulation log to file once alterations are made.
        entries : dict
            The entries to add to the ``SimulationLog``. Each entry should have the standard format for ``InitCon``:

            .. include:: ../../PyHPC/bin/lib/struct/simlog_struct.json
                :code:

        force : bool
            Forces the Simulation log to accommodate the structure used regardless of if it meets the standard format

            .. warning::
                This could have catastrophic consequences and should be used only if sure of the result.

        Returns
        -------
        None
        """
        #  Debugging
        # ------------------------------------------------------------------------------------------------------------ #
        modlog.debug("Adding %s to %s" % (entries, repr(self)))

        #  Checking structure
        # ------------------------------------------------------------------------------------------------------------ #
        if not force:

            # - Loading the structure information -#
            try:
                with open(_structure_file, "r") as struc_file:
                    _struct = json.load(struc_file)
            except FileNotFoundError:
                modlog.exception(
                    "Failed to locate the simulation log structure file at %s. Check installation." % _structure_file)
                raise PyHPC_Error(
                    "Failed to locate the simulation log structure file at %s. Check installation." % _structure_file)
            except json.JSONDecoder:
                modlog.exception(
                    "Failed to parse the simulation log structure file at %s. Check installation." % _structure_file)
                raise PyHPC_Error(
                    "Failed to parse the simulation log structure file at %s. Check installation." % _structure_file)

            #  Cleaning up the structure
            # -------------------------------------------------------------------------------------------------------- #
            ##- Trying to add any issues -##
            generation_time = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
            new_entries = {}
            for item, data in entries.items():
                new = data.copy()

                # - Adding necessary headers -#
                for header, obj in zip(["information", "meta", "simulations", "core", "action_log"],
                                       ["", {}, {}, {}, {}]):
                    if header not in data:
                        new[header] = obj

                # - Dealing with specialized items -#
                if "dateCreated" not in new["meta"]:
                    new["meta"]["dateCreated"] = generation_time
                if "lastEdited" not in new["meta"]:
                    new["meta"]["lastEdited"] = generation_time

                new_entries[item] = new
            entries = new_entries

            for item, data in entries.items():
                if not check_dictionary_structure(_struct["SimulationLog"]["format"], data):
                    raise SyntaxError(
                        "SimulationLog %s failed to add entry %s due to item %s which failed to match structure." % (
                            repr(self), entries, item))

        else:
            modlog.warning("parameter ``force`` was specified in execution of SimulationLog.add on %s." % (repr(self)))

        #  Adding
        # ------------------------------------------------------------------------------------------------------------ #
        self.raw = {**self.raw, **entries}

        #  Managing Saves
        # ------------------------------------------------------------------------------------------------------------ #
        if auto_save:
            self.save()

    def save(self):
        """
        Saves the current simulation log.

        Returns
        -------
        None
        """
        #  Debugging
        # ------------------------------------------------------------------------------------------------------------ #
        modlog.debug("Saving %s." % repr(self))

        #  Saving
        # ------------------------------------------------------------------------------------------------------------ #
        with open(self.path, "w+") as simlog_file:
            json.dump(self.raw, simlog_file, cls=NonStandardEncoder)


class InitCon:
    """
    The ``InitCon`` class contains data concerning a **single** initial condition file in any format. It is stored
    in a ``SimulationLog`` and is read from the underlying file of it's parent object.

    Parameters
    ----------
    name : str
        The name of the ``InitCon`` object as it is initialized by its ``parent`` object.
    parent: SimulationLog
        The parent ``SimulationLog`` object corresponding to the ``InitCon`` object.
    raw: dict
        The raw data, which should typically be just ``self.parent["name"]`` in this case.

    Notes
    -----
    The formatting for the simulation management objects is dictated by the ``/bin/bin/lib/struct/simlog_struct.json`` file,
    which has constraints on the formatting of each of the logging objects. The format is determined as follows:

    .. include:: ../../PyHPC/bin/lib/struct/simlog_struct.json
        :code:

    """

    def __init__(self, name: str, raw: dict, parent=None):
        #: ``self.parent`` is a reference to the parent object.
        self.parent = parent
        #: ``self.name`` contains the key value of the entry in the ``SimulationLog`` object.
        self.name = name

        #: ``self.raw`` is the core information in the ``InitCon`` object.
        self.raw = raw

    # ---------------------------------------------------------------------------------------------------------------- #
    # Managing Properties   ========================================================================================== #
    # ---------------------------------------------------------------------------------------------------------------- #
    @property
    def sims(self):
        """``self.sims`` contains all the ``SimRec`` objects in the simulation."""
        try:
            return {k: SimRec(k, data, parent=self) for k, data in self.raw["simulations"].items()}
        except KeyError:
            return None

    @property
    def listed(self) -> dict:
        """Corresponds to ``self.raw["simulations"]``. Base utility to standardize entrance procedures across objects."""
        return self.raw["simulations"]

    @property
    def core(self):
        """``self.core``  contains all the core information for this entry."""
        try:
            return self.raw["core"]
        except KeyError:
            return None

    @property
    def inf(self):
        """``self.inf`` contains all the description information for this entry."""
        try:
            return self.raw["information"]
        except KeyError:
            return None

    @property
    def meta(self):
        """``self.meta`` contains all the meta information for this entry."""
        try:
            return self.raw["meta"]
        except KeyError:
            return None

    # ---------------------------------------------------------------------------------------------------------------- #
    #  Dunder Methods ================================================================================================ #
    # ---------------------------------------------------------------------------------------------------------------- #
    def __repr__(self):
        """
        Defines the representation string for the ``SimulationLog`` object.

        Returns
        -------
        The string representation.
        """
        return "InitCon @ %(name)s; len=%(len)s" % {"name": self.name, "len": len(self.sims)}

    def __str__(self):
        """
        Defines ths string representation of the ``InitCon`` object.

        Returns
        -------
        The string representation.
        """
        return "InitCon @ %(name)s" % {"name": self.name}

    def __getitem__(self, item_map: list):
        """
        Defines the capacity to get items from the ``self.raw`` variable.
        Parameters
        ----------
        item_map : list
            The item position to pull from.

        Returns
        -------
        dict
            The dict
        """
        if not isinstance(item_map, list):
            item_map = [item_map]
        try:
            return reduce(operator.getitem, item_map, self.sims)
        except KeyError:
            modlog.exception(
                "Failed to find key path %s in self.raw for InitCon object %s." % (item_map, self.__repr__()))
            self.__missing__(item_map)

    def __setitem__(self, keys: list, value):
        if not isinstance(keys, list):
            keys = [keys]
        self.__getitem__(keys[:-1])[keys[-1]] = value

    def __len__(self):
        return len(self.sims)

    def __contains__(self, item):
        return item in self.sims

    def __delitem__(self, key_list):
        if not isinstance(key_list, list):
            key_list = [key_list]
        del self.__getitem__(key_list[:-1])[key_list[-1]]

    def __iter__(self):
        return iter(self.raw)

    def __missing__(self, key):
        return None

    def add(self, entries, auto_save=True, force=False):
        """
        adds the entry contained in ``**kwargs`` to the ``SimulationLog`` object. The ``entries`` may contain any number
        of individual entries to add.

        Parameters
        ----------
        auto_save : bool
            ``auto_save=True`` will immediately write the simulation log to file once alterations are made.
        entries : dict
            The entries to add to the ``SimulationLog``. Each entry should have the standard format for ``InitCon``:

            .. include:: ../../PyHPC/bin/lib/struct/simlog_struct.json
                :code:

        force : bool
            Forces the Simulation log to accommodate the structure used regardless of if it meets the standard format

            .. warning::
                This could have catastrophic consequences and should be used only if sure of the result.

        Returns
        -------
        None
        """
        #  Debugging
        # ------------------------------------------------------------------------------------------------------------ #
        modlog.debug("Adding %s to %s" % (entries, repr(self)))

        #  Checking structure
        # ------------------------------------------------------------------------------------------------------------ #
        if not force:

            # - Loading the structure information -#
            try:
                with open(_structure_file, "r") as struc_file:
                    _struct = json.load(struc_file)
            except FileNotFoundError:
                modlog.exception(
                    "Failed to locate the simulation log structure file at %s. Check installation." % _structure_file)
                raise PyHPC_Error(
                    "Failed to locate the simulation log structure file at %s. Check installation." % _structure_file)
            except json.JSONDecoder:
                modlog.exception(
                    "Failed to parse the simulation log structure file at %s. Check installation." % _structure_file)
                raise PyHPC_Error(
                    "Failed to parse the simulation log structure file at %s. Check installation." % _structure_file)

            #  Cleaning up the structure
            # -------------------------------------------------------------------------------------------------------- #
            ##- Trying to add any issues -##
            generation_time = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
            new_entries = {}
            for item, data in entries.items():
                new = data.copy()

                # - Adding necessary headers -#
                for header, obj in zip(["information", "meta", "action_log", "core", "outputs", "components"],
                                       ["", {}, {}, {}, {}, {}]):
                    if header not in data:
                        new[header] = obj

                # - Dealing with specialized items -#
                if "dateCreated" not in new["meta"]:
                    new["meta"]["dateCreated"] = generation_time
                if "lastEdited" not in new["meta"]:
                    new["meta"]["lastEdited"] = generation_time
                if "software" not in new["meta"]:
                    new["meta"]["software"] = "NA"

                new_entries[item] = new
            entries = new_entries

            for item, data in entries.items():
                if not check_dictionary_structure(_struct["InitCon"]["format"], data):
                    raise SyntaxError(
                        "InitCon %s failed to add entry %s due to item %s which failed to match structure." % (
                            repr(self), entries, item))

        else:
            modlog.warning("parameter ``force`` was specified in execution of InitCon.add on %s." % (repr(self)))

        #  Adding
        # ------------------------------------------------------------------------------------------------------------ #
        self.raw["simulations"] = {**self.raw["simulations"], **entries}

        #  Managing Saves
        # ------------------------------------------------------------------------------------------------------------ #
        if auto_save:
            self.parent.save()

    def save(self):
        """
        Saves the info contained in ``InitCon`` to file.

        Returns
        -------
        None

        Notes
        -----
        .. attention::
            This function is implemented by calling ``self.parent.save()``, which will cause the **entire** ``parent`` instance
            to save all the changes in the ``SimulationLog``, not just those relevant to this instance of ``InitCon``.
        """
        self.parent.save()

    def delete(self, force=False):
        """
        Deletes the ``InitCon`` object.

        Parameters
        ----------
        force : bool
            ``True`` will force the deletion of the object in question.
        Returns
        -------
        None
        """
        #  debugging
        # ----------------------------------------------------------------------------------------------------------------- #
        modlog.debug("Attempting to delete %s." % self)

        #  Getting Confirmation
        # ----------------------------------------------------------------------------------------------------------------- #
        prefix_text = "[\u001b[32mSimulation Management\u001b[0m]: "
        if not force:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(prefix_text + "User requests to DELETE object %s..." % self)
            yn = input(prefix_text + "Confirm DELETE? [y,N]: ")

            if yn not in ["y", "Y"]:
                print(prefix_text + "DELETE cancelled.")
                return None

            print(prefix_text + "DELETE confirmed.")

            print("+---------------------------------+")
            for item in self.sims:
                print(prefix_text + "Found %s as subobject." % item)
            print("+---------------------------------+")
            yn = input(prefix_text + "DELETE all materials and sub-objects? [y,N]: ")
            if yn in ["y", "Y"]:
                print(prefix_text + "DELETE sub-objects...")
                for item in self.sims:
                    try:
                        item.delete(force=True)
                    except Exception:
                        modlog.exception("Failed to delete %s while deleting %s." % (item, self))
                        print(prefix_text + "DELETE FAILED for %s." % item)

                print(prefix_text + "DELETE %s..." % self)

                try:
                    os.remove(self.name)
                except FileNotFoundError:
                    print(prefix_text + "The file %s corresponding to %s doesn't exist." % (self.name, self))
        else:
            for item in self.sims:
                try:
                    item.delete(force=True)
                except Exception:
                    modlog.exception("Failed to delete %s while deleting %s." % (item, self))
                    print(prefix_text + "DELETE FAILED for %s." % item)
            print(prefix_text + "DELETE %s..." % self)

            try:
                os.remove(self.name)
            except FileNotFoundError:
                print(prefix_text + "The file %s corresponding to %s doesn't exist." % (self.name, self))

        del self.parent.raw[self.name]
        self.parent.save()

    def log(self, message, action, auto_save=True, **kwargs):
        """
        logs the ``message`` to the ``self.raw.action_log``. Additional entries in the record are specified with ``**kwargs``.

        Parameters
        ----------
        message : str
            The message to log with the entry.
        action : str
            The specific action being under-taken. These actions can be arbitrary, but should be consistent for
            best impact.
        auto_save : bool
            ``True`` to automatically write all the data to file.
        kwargs : optional
            Additional attributes to log with the message. All entries should be ``key="string"``. If entries overlap
            with required log elements ``[msg,lineno,file,act,time]``, then they are overridden by the values given.

        Returns
        -------
        None

        """
        #  Managing the required kwargs
        # ------------------------------------------------------------------------------------------------------------ #
        caller = getframeinfo(stack()[1][0])  # -> grabbing frame info
        req_entries = {  # These are the required keys that are always present in the entry.
            "msg"   : message,
            "act"   : action,
            "lineno": caller.lineno,
            "file"  : caller.filename,
            "time"  : datetime.now().strftime('%m-%d-%Y_%H-%M-%S')

        }

        #  Managing additional entries
        # ------------------------------------------------------------------------------------------------------------ #
        entries = {**req_entries, **kwargs}

        #  Logging
        # ------------------------------------------------------------------------------------------------------------ #
        log_time = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')

        self.raw["action_log"][log_time] = entries

        if auto_save:
            self.parent.save()


class SimRec:
    """
    The ``SimRec`` class contains all the information for a single simulation record in the ``SimulationLog`` system.
    This is the most granular view available in the ``SimulationLog`` hierarchy.

    **Formatting**:

    ---
    ```
    {
        "simulations": {
            "<.nml file (or equivalent for other software>": {
              "information": "Filled by the user to record important simulation notes.",
              "action_log": {
                "action": "information"
              },
              "meta": {
              },
              "core": {
              },
              "outputs": {
              }
            }
        }
    }
    ```
    """

    def __init__(self, name, data, parent=None):
        #  Initializing the core variables.
        # ------------------------------------------------------------------------------------------------------------ #
        #: ``self.parent`` is a reference to the parent object.
        self.parent = parent
        #: ``self.name`` contains the <u>absolute path</u> to the ``.nml`` file or equivalent init file for runtime use.
        self.name = name

        #: ``self.raw`` contains all the raw data provided in the ``SimRec`` object.
        self.raw = data

    # ---------------------------------------------------------------------------------------------------------------- #
    # Managing Properties   ========================================================================================== #
    # ---------------------------------------------------------------------------------------------------------------- #
    @property
    def outputs(self):
        """``self.outputs`` Contains all the outputs for the ``SimRec`` object."""
        try:
            return self.raw["outputs"]
        except KeyError:
            return None

    @property
    def listed(self) -> dict:
        return self.raw["outputs"]

    @property
    def core(self):
        """``self.core``  contains all the core information for this entry."""
        try:
            return self.raw["core"]
        except KeyError:
            return None

    @property
    def inf(self):
        """``self.inf`` contains all the description information for this entry."""
        try:
            return self.raw["information"]
        except KeyError:
            return None

    @property
    def meta(self):
        """``self.meta`` contains all the meta information for this entry."""
        try:
            return self.raw["meta"]
        except KeyError:
            return None

    # ---------------------------------------------------------------------------------------------------------------- #
    #  Dunder Methods ================================================================================================ #
    # ---------------------------------------------------------------------------------------------------------------- #
    def __repr__(self):
        """
        Defines the representation string for the ``SimulationLog`` object.

        Returns
        -------
        The string representation.
        """
        return "SimRec @ %(name)s; len=%(len)s" % {"name": self.name, "len": len(self.outputs)}

    def __str__(self):
        """
        Defines ths string representation of the ``InitCon`` object.

        Returns
        -------
        The string representation.
        """
        return "SimRec @ %(name)s" % {"name": self.name}

    def __getitem__(self, item: list):
        """
        Defines the capacity to get items from the ``self.raw`` variable.
        Parameters
        ----------
        item : list
            The item position to pull from.

        Returns
        -------
        dict
            The dict
        """
        if not isinstance(item, list):
            item = [item]
        try:
            return reduce(operator.getitem, item, self.raw)
        except KeyError:
            modlog.exception(
                "Failed to find key path %s in self.raw for SimRec object %s." % (item, self.__repr__()))
            self.__missing__(item)

    def __setitem__(self, keys: list, value):
        if not isinstance(keys, list):
            keys = [keys]
        self.__getitem__(keys[:-1])[keys[-1]] = value

    def __len__(self):
        return len(self.outputs)

    def __contains__(self, path):
        """
        Determines if the ``SimRec`` includes an output record which matches the ``path``.

        Parameters
        ----------
        path: (``str`` or ``pathlib.Path``) the path to the output directory to be checked.

        Returns
        -------
        ``bool``

        """
        return path in self.outputs

    def __delitem__(self, key_list):
        if not isinstance(key_list, list):
            key_list = [key_list]
        del self.__getitem__(key_list[:-1])[key_list[-1]]

    def __iter__(self):
        return iter(self.raw)

    def __missing__(self, key):
        return None

    def log(self, message, action, auto_save=True, object_rec = None,**kwargs):
        """
        logs the ``message`` to the ``self.raw.action_log``. Additional entries in the record are specified with ``**kwargs``.

        Parameters
        ----------
        message : str
            The message to log with the entry.
        action : str
            The specific action being under-taken. These actions can be arbitrary, but should be consistent for
            best impact.
        auto_save : bool
            ``True`` to automatically write all the data to file.
        object_rec : str or None, default=None
            The object record to log too. If ``None``, then it isn't logged elsewhere.
        kwargs : optional
            Additional attributes to log with the message. All entries should be ``key="string"``. If entries overlap
            with required log elements ``[msg,lineno,file,act,time]``, then they are overridden by the values given.

        Returns
        -------
        None

        """
        #  Managing the required kwargs
        # ------------------------------------------------------------------------------------------------------------ #
        caller = getframeinfo(stack()[1][0])  # -> grabbing frame info
        req_entries = {  # These are the required keys that are always present in the entry.
            "msg"   : message,
            "act"   : action,
            "lineno": caller.lineno,
            "file"  : caller.filename,
            "time"  : datetime.now().strftime('%m-%d-%Y_%H-%M-%S'),
            "object": str(object_rec) if object_rec else "Self"

        }

        #  Managing additional entries
        # ------------------------------------------------------------------------------------------------------------ #
        entries = {**req_entries, **kwargs}

        #  Logging
        # ------------------------------------------------------------------------------------------------------------ #
        log_time = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')

        self.raw["action_log"][log_time] = entries

        if object_rec:
            self.raw["outputs"][object_rec]["action_log"][log_time] = entries

        self.parent.log(message,action,object_rec = self.name,**kwargs,level="SimRec")
        if auto_save:
            self.parent.parent.save()

    def save(self):
        self.parent.parent.save()

    def delete(self, force=False):
        """
        Deletes the ``InitCon`` object.

        Parameters
        ----------
        force : bool
            ``True`` will force the deletion of the object in question.
        Returns
        -------
        None
        """
        #  debugging
        # ----------------------------------------------------------------------------------------------------------------- #
        modlog.debug("Attempting to delete %s." % self)

        #  Getting Confirmation
        # ----------------------------------------------------------------------------------------------------------------- #
        prefix_text = "[\u001b[32mSimulation Management\u001b[0m]: "
        if not force:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(prefix_text + "User requests to DELETE object %s..." % self)
            yn = input(prefix_text + "Confirm DELETE? [y,N]: ")

            if yn not in ["y", "Y"]:
                print(prefix_text + "DELETE cancelled.")
                return None

            print(prefix_text + "DELETE confirmed.")

            print("+---------------------------------+")
            for item in self.outputs:
                print(prefix_text + "Found %s as subobject." % item)
            print("+---------------------------------+")
            yn = input(prefix_text + "DELETE all materials and sub-objects? [y,N]: ")
            if yn in ["y", "Y"]:
                print(prefix_text + "DELETE sub-objects...")
                for item in self.outputs:
                    try:
                        shutil.rmtree(item)
                    except Exception:
                        modlog.exception("Failed to delete %s while deleting %s." % (item, self))
                        print(prefix_text + "DELETE FAILED for %s." % item)
                print(prefix_text + "DELETE %s..." % self)

                try:
                    os.remove(self.name)
                except FileNotFoundError:
                    print(prefix_text + "The file %s corresponding to %s doesn't exist." % (self.name, self))
        else:
            for item in self.outputs:
                try:
                    shutil.rmtree(item)
                except Exception:
                    modlog.exception("Failed to delete %s while deleting %s." % (item, self))
                    print(prefix_text + "DELETE FAILED for %s." % item)
            print(prefix_text + "DELETE %s..." % self)

            try:
                os.remove(self.name)
            except FileNotFoundError:
                print(prefix_text + "The file %s corresponding to %s doesn't exist." % (self.name, self))

        del self.parent.raw[self.name]
        self.parent.parent.save()

    def add(self, entries, auto_save=True, force=False):
        """
        Adds the data contained in ``entries`` to the ``SimRec`` object's ``outputs`` dictionary.

        Parameters
        ----------
        entries : dict of {str : dict}
            The entries to add to the ``SimRec``. These should have the following format:

            .. code-block:: json
                {
                "<Output Directory 1> : {
                    "information": "<some information>",
                    "meta": {
                        "dateCreated" : "",
                        "hasRun" : true,
                        }
                    }
                }
        
        auto_save : bool
            ``True`` will cause the object to autosave.
        force : bool
            If ``True``, will force the addition even if it comes back with an addition structure failure.
            
        Returns
        -------
        None
        """
        #  Debugging
        # ------------------------------------------------------------------------------------------------------------ #
        modlog.debug("Adding %s to %s" % (entries, repr(self)))

        #  Checking structure
        # ------------------------------------------------------------------------------------------------------------ #
        if not force:

            # - Loading the structure information -#
            try:
                with open(_structure_file, "r") as struc_file:
                    _struct = json.load(struc_file)
            except FileNotFoundError:
                modlog.exception(
                    "Failed to locate the simulation log structure file at %s. Check installation." % _structure_file)
                raise PyHPC_Error(
                    "Failed to locate the simulation log structure file at %s. Check installation." % _structure_file)
            except json.JSONDecoder:
                modlog.exception(
                    "Failed to parse the simulation log structure file at %s. Check installation." % _structure_file)
                raise PyHPC_Error(
                    "Failed to parse the simulation log structure file at %s. Check installation." % _structure_file)

            #  Cleaning up the structure
            # -------------------------------------------------------------------------------------------------------- #
            ##- Trying to add any issues -##
            generation_time = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
            new_entries = {}
            for item, data in entries.items():
                new = data.copy()

                # - Adding necessary headers -#
                for header, obj in zip(["information", "meta", "action_log"], ["", {}, {}]):
                    if header not in data:
                        new[header] = obj

                # - Dealing with specialized items -#
                if "dateCreated" not in new["meta"]:
                    new["meta"]["dateCreated"] = generation_time
                if "isRun" not in new["meta"]:
                    new["meta"]["isRun"] = False
                if "slurm_path" not in new["meta"]:
                    new["meta"]["slurm_path"] = "None"

                new_entries[item] = new
            entries = new_entries

            for item, data in entries.items():
                if not check_dictionary_structure(_struct["SimRec"]["format"], data):
                    raise SyntaxError(
                        "InitCon %s failed to add entry %s due to item %s which failed to match structure." % (
                            repr(self), entries, item))

        else:
            modlog.warning("parameter ``force`` was specified in execution of InitCon.add on %s." % (repr(self)))

        #  Adding
        # ------------------------------------------------------------------------------------------------------------ #
        self.raw["outputs"] = {**self.raw["outputs"], **entries}

        #  Managing Saves
        # ------------------------------------------------------------------------------------------------------------ #
        if auto_save:
            self.parent.parent.save()


# -------------------------------------------------------------------------------------------------------------------- #
# Sub Functions ====================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def check_dictionary_structure(master: dict, base: dict) -> bool:
    """
    checks the dictionary structure of ``base`` against the ``master`` copy and returns ``True`` if the structure
    matches and ``False`` if the structure fails to correctly match.

    Parameters
    ----------
    master: dict
        The master dictionary containing the structure. The structure is checked as follows:

        1. For each ``key:value`` pair in the dictionary
            - If ``value`` is an <u>empty</u> ``dict``, then ``key`` must be in ``base``, but no further checks are made.
            - If ``value`` is <u>non-empty</u>, then the algorithm proceeds recursively to each ``key:value`` pair.
            - If ``value`` is a ``str``, then ``value`` should represent a ``type`` and is checked against the type.

    base: dict
        The base dictionary to check against the master dictionary.

    Returns
    -------
    value : bool
        The output value of the check. If ``True``, the structures match.
    """
    result = True  # -> this is used to check for the match throughout.
    for key, value in master.items():
        if key not in base:
            modlog.debug("key %s not in base (%s), result = False" % (key, base))
            result = False
        else:
            if isinstance(value, dict) and len(value):
                result = result and check_dictionary_structure(value, base[key])
            elif isinstance(value, str):
                result = result and isinstance(base[key], getattr(builtins, value))

                if not isinstance(base[key], getattr(builtins, value)):
                    modlog.debug("key %s of base %s failed to match type %s, result = %s." % (key, base, value, result))
            else:
                pass
    return result


if __name__ == '__main__':
    simlog = SimulationLog()
