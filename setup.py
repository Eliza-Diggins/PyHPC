"""
Setup script for the PyHPC code system

Written by: Eliza Diggins
"""
import argparse
import json
import os
import pathlib as pt
import shutil
from types import SimpleNamespace
from colorama import Fore, Style
from PyHPC_Utils.text_display_utilities import print_title, print_verbose
from PyHPC_Core.utils import get_system_info
import tomlkit as t
from datetime import datetime

# -------------------------------------------------------------------------------------------------------------------- #
#  Setup  ============================================================================================================ #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "PyHPC"
_filename = pt.Path(__file__).name.replace(".py", "")

# - Strings -#
_dbg_string = "%s:%s:" % (_location, _filename)
fdbg_string = _dbg_string + " [" + Fore.LIGHTGREEN_EX + Style.BRIGHT + "INSTALL WIZARD" + Style.RESET_ALL + "]: "
done_string = "[" + Fore.CYAN + Style.BRIGHT + "DONE" + Style.RESET_ALL + "]"
fail_string = "[" + Fore.RED + Style.BRIGHT + "FAILED" + Style.RESET_ALL + "]"

# HARD CODED: the relative location of the install config file from which to generate the correct installation.
__root_path = os.path.join(pt.Path(__file__).parents[0])


# -------------------------------------------------------------------------------------------------------------------- #
#  Sub Functions ===================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def generate_directories(location, overwrite=False):
    ### Generates the necessary directories for install from lib/struct/fstruct.json ###

    # - Checking if location exists -#
    if not os.path.exists(location):
        print_verbose("\t%sGenerating %s..." % (fdbg_string, location), args.verbose, end="")
        try:
            pt.Path(location).mkdir(parents=True)
            print_verbose(done_string, args.verbose)
        except Exception:
            print_verbose(fail_string, args.verbose)
            print("%sLocation %s could not be found or created." % (fdbg_string, location))
            exit()

    else:
        pass

    # - Generating the necessary files -#
    print_verbose("\t%sAttempting to load structure files..." % fdbg_string, args.verbose, end="")
    try:
        with open(os.path.join(__root_path, "bin", "lib", "struct", "fstruct.json"), "r") as file:
            file_structure = json.load(file)
    except FileNotFoundError:
        print_verbose(fail_string, args.verbose)
        print("%sFailed to find %s. Rebuild from github." % (
            fdbg_string, os.path.join(__root_path, "bin", "lib", "struct", "fstruct.json")))
        exit()
    except Exception:
        print_verbose(fail_string, args.verbose)
        print("%sFile %s had incorrect structure. Rebuild from github." % (
            fdbg_string, os.path.join(__root_path, "bin", "lib", "struct", "fstruct.json")))
        exit()

    print_verbose(done_string, args.verbose)

    # - Creating the files -#
    print("\t%sGenerating files..." % fdbg_string, end=("" if not args.verbose else "\n"))
    rec_gen_dirs(location, file_structure, overwrite)
    print("\t" + done_string)


def rec_gen_dirs(loc, dic, ovr):
    if isinstance(dic["files"], dict):
        for k, v in dic["files"].items():
            if isinstance(v, dict):
                # - This is another layer -#
                rec_gen_dirs(os.path.join(loc, v["path"]), v, ovr)
    elif dic["files"] == "":
        print_verbose("\t\t%sGenerating %s..." % (fdbg_string, os.path.join(loc)), args.verbose, end="")
        try:
            pt.Path(os.path.join(loc)).mkdir(parents=True)
        except FileExistsError:
            if ovr:
                shutil.rmtree(loc)
            else:
                pass
            pt.Path(os.path.join(loc)).mkdir(parents=True, exist_ok=True)
        except Exception:
            print_verbose(fail_string, args.verbose)
            print("%sFailed to generate %s." % (fail_string, os.path.join(loc)))
            exit()
        print_verbose(done_string, args.verbose)


def set_directories_in_config(location, cnfg):
    # - Generating the necessary files -#
    print_verbose("\t\t%sAttempting to re-load structure files..." % fdbg_string, args.verbose, end="")
    try:
        with open(os.path.join(__root_path, "bin", "lib", "struct", "fstruct.json"), "r") as file:
            file_structure = json.load(file)
    except FileNotFoundError:
        print_verbose(fail_string, args.verbose)
        print("\t\t%sFailed to find %s. Rebuild from github." % (
            fdbg_string, os.path.join(__root_path, "bin", "lib", "struct", "fstruct.json")))
        exit()
    except Exception:
        print_verbose(fail_string, args.verbose)
        print("\t\t%sFile %s had incorrect structure. Rebuild from github." % (
            fdbg_string, os.path.join(__root_path, "bin", "lib", "struct", "fstruct.json")))
        exit()

    print_verbose(done_string, args.verbose)

    return set_directories_config_recur(cnfg, file_structure, location)


def set_directories_config_recur(cnfg, data, location):
    try:
        for k, v in data["files"].items():
            if isinstance(v, dict):
                if v["link"] != "":
                    cnfg["System"]["Directories"][v["link"]] = os.path.join(location, v["path"])
                else:
                    pass

                if isinstance(v["files"], dict):
                    cnfg = set_directories_config_recur(cnfg, v, os.path.join(location, v["path"]))
                else:
                    pass
            else:
                pass
    except KeyError as err:
        print("\t\t\t%sFailed to set directories at %s. Message = %s." % (fdbg_string, location, repr(err)))
        exit()

    return cnfg


# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------- Main ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
if __name__ == '__main__':
    # - Printing the title -#
    print_title()
    print("%sRunning setup.py..." % fdbg_string)
    # -------------------------------------------------------------------------------------------------------------------- #
    # Arg-parsing ======================================================================================================== #
    # -------------------------------------------------------------------------------------------------------------------- #
    argument_parser = argparse.ArgumentParser()

    # - Adding the necessary arguments -#
    argument_parser.add_argument("-ri", "--reinstall", help="Flag to force a complete reinstallation.",
                                 action="store_true")
    argument_parser.add_argument("-l", "--location", help="The location for the installation.", default=None)
    argument_parser.add_argument("-v", "--verbose", help="Enable verbose mode", action="store_true")

    # - Parsing -#
    args = argument_parser.parse_args()
    # ---------------------------------------------------------------------------------------------------------------- #
    # Checking for an existing installation ========================================================================== #
    # ------------------------------------------------------------------------------------------------------------------#
    new_install = False
    if not args.reinstall:
        print("%sSearching for a valid installation history..." % fdbg_string, end="")

        # - looking for an installation ticket -#
        __local_ticket = os.path.join(__root_path, "bin", "local", "install.tkc")

        if not os.path.exists(__local_ticket):
            new_install = True
            print(fail_string)
            print("\t%sFound no prior installations. Attempting to produce a fresh installation..." % fdbg_string)
        else:
            # Read the data #
            try:
                with open(__local_ticket, "r") as ticket_file:
                    ticket_info = SimpleNamespace(**json.load(ticket_file))
            except Exception:
                print(fail_string)
                print("\t%sThe ticket is not correctly formatted or is corrupted." % fdbg_string)
                new_install = True
        print(done_string)
    else:
        pass

    # ---------------------------------------------------------------------------------------------------------------- #
    #  Installing     ================================================================================================ #
    # ---------------------------------------------------------------------------------------------------------------- #
    if new_install:
        # - checking for validity
        if not args.location:
            print("%s %s -l flag necessary for new installation..." % (fdbg_string, fail_string))
            exit()

        yn = input("%sCreate a new installation? This will wipe existing data. (Y/n): " % fdbg_string)

        if yn in ["y", "Y"]:
            print("%sCreating a new installation instance..." % fdbg_string)
        else:
            print("%sExiting..." % fdbg_string)
            exit()

        # - Managing directories -#
        print("%sGenerating the core directories..." % fdbg_string, end=("" if not args.verbose else "\n"))
        generate_directories(args.location, overwrite=True)
        print(done_string)

        # - Creating configuration file -#
        print("%sGenerating the configuration files..." % fdbg_string, end=("" if not args.verbose else "\n"))

        print_verbose("\t%sGenerating the base config..." % fdbg_string, args.verbose)
        with open(os.path.join(__root_path, "bin", "inst", "cnfg", "install_CONFIG.config"), "r") as file:
            base_config = t.load(file)

        # - Changing necessary directories -#
        base_config = set_directories_in_config(args.location, base_config)

        with open(os.path.join(args.location, "bin", "configs", "CONFIG.config"), "w+") as file:
            t.dump(base_config, file)
        print_verbose("\t" + done_string, args.verbose)

        print_verbose("\t%sCopying remaining configuration files to path..." % fdbg_string, args.verbose)

        for file in os.listdir(os.path.join(__root_path, "bin", "inst", "cnfg")):
            # - is the file a file or a directory -#
            if os.path.isfile(os.path.join(__root_path, "bin", "inst", "cnfg",
                                           file)) and ".config" in file and file != "install_CONFIG.config":
                print_verbose("\t\t%sLocated configuration file %s. Transferring data..." % (fdbg_string, file),
                              args.verbose, end="")
                shutil.copyfile(os.path.join(__root_path, "bin", "inst", "cnfg", file),
                                os.path.join(args.location, "bin", "configs", file.replace("install_", "")))
                print_verbose("\t\t" + done_string, args.verbose)

        print(done_string)

        # - Generating the ticket -#
        print("%sGenerating ticket..." % fdbg_string, end="")
        ticket_info = {
            "version"              : get_system_info().version,
            "stable"               : get_system_info().stable,
            "installation_date"    : datetime.now().strftime('%m-%d-%Y_%H-%M-%S'),
            "installation_location": args.location
        }

        with open(os.path.join(__root_path, "bin", "local", "install.tkc"), "w") as file:
            json.dump(ticket_info, file)
        print(done_string)

        print("%sInstallation Succeeded." % fdbg_string)
        exit()

    else:
        # ------------------------------------------------------------------------------------------------------------ #
        #  Updating     ============================================================================================== #
        # ------------------------------------------------------------------------------------------------------------ #
        print("%sUpdating installation..." % fdbg_string, end=("" if not args.verbose else "\n"))
        print_verbose("\t%sFetching update from git." % fdbg_string,args.verbose,end="")
        os.system("git fetch --all")  # Fetch all the updates.
        os.system("git reset --hard origin/master")  # Resetting the system
        print_verbose(done_string,args.verbose)

        print("%sGenerating directories..."%fdbg_string,end=("" if not args.verbose else "\n"))
        generate_directories(ticket_info.installation_location, overwrite=False)
        print_verbose(done_string,args.verbose)


        print(done_string)
