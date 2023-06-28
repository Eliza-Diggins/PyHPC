import os
import pathlib as pt
import sys

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
import json
import logging
from PyHPC.PyHPC_Core.configuration import read_config
import threading as t
import warnings
import toml
from PyHPC.PyHPC_Utils.text_display_utilities import get_options
from datetime import datetime

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
# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')


# -------------------------------------------------------------------------------------------------------------------- #
#  Command Management ================================================================================================ #
# -------------------------------------------------------------------------------------------------------------------- #
def write_command_string(command: str, *args, **kwargs) -> str:
    """
    Writes the command string corresponding to the specified command in a format which can be used to
    pass through the command line terminal.

    Parameters
    ----------
    command: str
        The command to use.
    args: list of any
        The arguments that need to be passed. These might be things like ``-h``, or ``--help`` as well as non-flag items
        like file-paths.
    kwargs: dict of any
        These are keyword arguments to pass. They are formatted as ``--key value`` in order.

    Returns
    -------
    str:
        The string corresponding to the command.

    Examples
    --------
    >>> print(write_command_string("python3","example.py",o="output_file",r=True))
    python3 'example.py' -o 'output_file' -r 'True'

    An example of using the ``write_command_string`` function to produce a ``python3`` execution.

    >>> print(write_command_string("/path/ramses_3d","path/to/nml.nml",l="False"))
    /path/ramses_3d 'path/to/nml.nml' -l 'False'

    """
    modlog.debug("Writing command %s with args %s and kwargs %s." % (command, args, kwargs))
    command_string = command

    # - Adding the arguments -#
    for arg in args:
        command_string += " '%s'" % str(arg)

    # - Adding the kwargs -#
    for k, v in kwargs.items():
        command_string += " -%s '%s'" % (str(k), str(v))

    return command_string


# -------------------------------------------------------------------------------------------------------------------- #
#  Batch Management ================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def write_slurm_file(command_string, slurm_config=None, name=None, **kwargs):

    #  Intro Debugging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Writing slurm file with name parameter %s." % name)

    #  Setup and Management
    # ----------------------------------------------------------------------------------------------------------------- #
    if not name:  # We specify a name - generic
        modlog.debug("Name parameter was not specified. setting name to generic.")
        name = 'generic'

    if not slurm_config:  # We need to grab it from the user.
        modlog.debug("slurm configuration was not specified, fetching from file and querying the user.")

        # - loading the configuration -#
        try:
            slurm_config_default = toml.load(
                os.path.join(CONFIG["System"]["Directories"]["bin"], "configs", "SLURM.config"))
        except FileNotFoundError:
            modlog.exception(
                "Failed to find the default slurm config at %s." % os.path.join(CONFIG["System"]["Directories"]["bin"],
                                                                                "configs", "SLURM.config"))
            return False
        except toml.TomlDecodeError:
            modlog.exception("The file at %s was corrupted or otherwise unusable." % os.path.join(
                CONFIG["System"]["Directories"]["bin"], "configs", "SLURM.config"))
            return False

        # - grabbing settings -#
        modlog.debug("Grabbing slurm settings from user.")
        slurm_config = get_options(slurm_config_default, "Slurm Batch Settings")
        modlog.debug("Successfully obtained user settings.")

    #  Writing the slurm file
    # ----------------------------------------------------------------------------------------------------------------- #
    date = datetime.now().strftime('%m-%d_%H-%M')
    filename = "%s.SLURM" % (name)
    slurm_script = ""
    # - Adding the batch settings -#
    for setting, value in slurm_config["Settings"].items():
        slurm_script += "#SBATCH -%s %s\n" % (setting, value["v"])

    # - Adding the output -#
    path = os.path.join(CONFIG["System"]["Directories"]["SLURM_output_directory"], pt.Path(filename).stem,
                        slurm_config["files"]["format"]["v"] % {"name": name,
                                                                "date": date})
    slurm_script += "#SBATCH -o %s.out\n" % path
    slurm_script += "#SBATCH -e %s.err" % path

    command = command_string % {**kwargs, **{"batch_options": slurm_script}}

    modlog.debug("Successfully wrote the slurm script to a memory string.")

    #  Generating necessary files / folders
    # ----------------------------------------------------------------------------------------------------------------- #
    if not os.path.exists(
            os.path.join(CONFIG["System"]["Directories"]["SLURM_output_directory"], pt.Path(filename).stem)):
        pt.Path(os.path.join(CONFIG["System"]["Directories"]["SLURM_output_directory"], pt.Path(filename).stem)).mkdir(
            parents=True)
        modlog.debug("Generated the output file at %s" % (
            os.path.join(CONFIG["System"]["Directories"]["SLURM_output_directory"], pt.Path(filename).stem)))
    else:
        pass

    #  Writing the file
    # ----------------------------------------------------------------------------------------------------------------- #
    with open(os.path.join(CONFIG["System"]["Directories"]["slurm_directory"], filename), "w+") as f:
        f.write(command)

    modlog.debug(
        "Completed writing slurm output to %s." % os.path.join(CONFIG["System"]["Directories"]["slurm_directory"]))

    return None


# -------------------------------------------------------------------------------------------------------------------- #
# Configuration Management =========================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def write_ramses_nml(settings: dict, output_location: str) -> bool:

    #  Debugging and setup
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Generating ramses nml file at %s." % output_location)

    # Managing the software details.
    # ----------------------------------------------------------------------------------------------------------------- #
    software, ic_file, mem_mode = settings["META"]["software"]["v"], settings["META"]["ic_file"]["v"], \
                                  settings["META"]["Memory"]["mode"]["v"]
    print(ic_file)
    modlog.debug("software=%s, ic_file=%s, mem_mode=%s." % (software, ic_file, mem_mode))

    with open(os.path.join(pt.Path(__file__).parents[1], "bin", "lib", "imp", "types.json"), "r") as type_file:
        types = json.load(type_file)

    #  Software system work
    # ----------------------------------------------------------------------------------------------------------------- #
    if software not in types["software"]["RAMSES"]:
        raise ValueError("The software %s does not match any of the implemented softwares!" % software)

    # - Managing locations
    for k, v in types["software"]["RAMSES"][software]["header_control"].items():
        settings[k]["enabled"]["v"] = v
        modlog.debug("Enabled %s" % k if v else "Disabled %s" % k)

    # - managing the IC location -#
    exec(types["software"]["RAMSES"][software]["ic_exec"])

    # - managing the memory type -#
    for setting in ["ngrid", "npart"]:
        settings["AMR_PARAMS"][setting + str(mem_mode)] = {
            "v": settings["AMR_PARAMS"][setting]["v"],
            "d": "",
            "i": ""
        }
        del settings["AMR_PARAMS"][setting]

    ramses_nml_string = ""
    #  Writing
    # ----------------------------------------------------------------------------------------------------------------- #
    for k, v in settings.items():  # -> cycle through all of the values seeking headers.
        if k != "META":  # -> We should actually be doing something with this
            # - Checking -#
            check = (len(v) > 0 if "enabled" not in v else (len(v) > 1 and v["enabled"]["v"]))
            if check:
                ramses_nml_string += "&%s\n" % k
                for k_sub, v_sub in v.items():  # -> iterate through the sub set.
                    if k_sub != "enabled":
                        ramses_nml_string += "%s = %s\n" % (k_sub, v_sub["v"])
                    else:
                        pass
                ramses_nml_string += "/\n\n"
        else:
            pass

    with open(output_location, "w+") as nml_file:
        nml_file.write(ramses_nml_string)

    return None

if __name__ == '__main__':
    print(write_command_string.__doc__)
    print(write_command_string("sdfs"))
