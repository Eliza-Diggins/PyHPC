"""

    Tools for remote file management using RClone or single transfer.
-- Last Check: 12/16 --
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
from time import perf_counter
import numpy as np
from colorama import Fore, Style

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

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# -------------------------------------------------- Fixed Variables ----------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#

# - Grabbing core necessary datasets for the remote management -#
with open(os.path.join(pt.Path(__file__).parents[1], "bin", "lib", "struct", "file_struct.json"),
          "r") as file_setup_json:
    file_struct = json.load(file_setup_json)


# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# --------------------------------------------------- Sub-Functions -----------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#

#  IO Operations - basic
# ----------------------------------------------------------------------------------------------------------------- #
@time_function
def get_all_files(directory, top_directory=None):
    """
    Finds all of the files within ``directory`` and returns as a formatted list with relative and absolute paths.
    Parameters
    ----------
    directory: the directory from which to search.
    top_directory: The directory from which to construct the relative paths.
    Returns: Returns a list of tuples [(path,rel-path,file)].
    -------

    """
    #  Setup
    # ----------------------------------------------------------------------------------------------------------------- #
    # - Managing the top directory -#
    if top_directory == None:
        top_directory = directory

    #  Main
    # ----------------------------------------------------------------------------------------------------------------- #
    files = []  # this is the list we will eventually return.

    if not os.path.isdir(directory):  # -> This is a file, so we return
        return [(directory, str(pt.Path(directory).relative_to(top_directory)), "")]

    for file in os.listdir(directory):  # cycle through each directory.
        if os.path.isfile(os.path.join(directory, file)):  # this is a file, we add it.
            files.append((os.path.join(directory, file),
                          str(pt.Path(os.path.join(directory, file)).relative_to(top_directory)),
                          file))
        else:  # its a directory
            files += get_all_files(os.path.join(directory, file), top_directory=top_directory)

    return files


@time_function
def get_all_remote_files(directory, top_directory=None):
    """
    Grabs all of the files within the directory and returns as a list with (path, rel-path, file). [BOX]
    Parameters
    ----------
    directory: the directory from which to search.

    Returns: Returns a list of tuples [(path,rel-path,file)].
    -------

    """
    #  Setup
    # ----------------------------------------------------------------------------------------------------------------- #
    if top_directory == None:
        top_directory = directory

    files = []  # this is the list we will eventually return.

    if pt.Path(directory).suffix != "":  # This is a file
        return [(directory, str(directory).replace(top_directory, ""), "")]

    #  Core Runtime loop
    # ----------------------------------------------------------------------------------------------------------------- #
    for file in rclone_listdir(directory):  # cycle through each directory.

        if pt.Path(file).suffix != "":  # this is a file, we add it.
            files.append((os.path.join(directory, file),
                          str(pt.Path(os.path.join(directory, file)).relative_to(top_directory)),
                          file))

        else:  # its a directory
            files += get_all_remote_files(os.path.join(directory, file), top_directory=top_directory)

    return files


@time_function
def get_remote_location(local_path, move_to_unfiled=CONFIG["System"]["Directories"]["Remote"]["send_to_unfiled"]):
    """
    Determines the correct path to use for rclone on the box side of file transfer.

    Parameters
    ----------
    local_path: The local path on the disk.
    move_to_unfiled: If True, then we will move items without a reasonable path to an unfiled location.

    Returns: The correct path to copy to for that file.
    -------

    """
    # Introduction Debug
    # ------------------------------------------------------------------------------------------------------------------#
    modlog.debug("Attempting to locate correct remote location of %s." % local_path)

    #  Categorizing the local file.
    # ----------------------------------------------------------------------------------------------------------------- #
    # - Identifying matched paths -#
    matched_paths = [header for header in
                     [
                         (k, v) for k, v in
                         list(file_struct["location_config_links"]["values"].items())
                     ]
                     if header[1] in local_path
                     ]

    if not len(matched_paths):
        # - We failed to find a matched path for this directory so we need to figure out what to do.
        modlog.warning("Failed to find a local header for the file path %s. Filing under unfiled." % local_path)

        if move_to_unfiled:
            # - We are going to transfer to the unfiled directory.
            return file_struct["rclone_paths"]["values"]["unfiled"]

        else:
            return None  # -> indicator sentinel

    else:
        # We did find a matching header.
        if len(matched_paths) > 1:
            modlog.warning("The length of matched paths is %s for local path %s. Selected %s." % (
                len(matched_paths), local_path, matched_paths[0]))
            match = matched_paths[0]
        else:
            match = matched_paths[0]

    #  Manipulating the match correctly
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Found match %s for local path %s." % (match, local_path))

    proper_path = str(local_path).replace(match[1], file_struct["rclone_paths"]["values"][match[0]])

    modlog.debug("Found proper path for %s to be %s in rclone." % (local_path, proper_path))
    return proper_path


@time_function
def get_local_location(remote_path, move_to_unfiled=CONFIG["System"]["Directories"]["Remote"]["send_to_unfiled"]):
    """
    Determines the correct path to use for rclone on the box side of file transfer.
    Parameters
    ----------
    local_path: The local path on the disk.
    move_to_unfiled: If True, then we will move items without a reasonable path to an unfiled location.

    Returns: The correct path to copy to for that file.
    -------

    """
    #  Intro Debugging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Seeking correct local equivalent for remote path %s." % remote_path)

    #  Managing matches
    # ----------------------------------------------------------------------------------------------------------------- #
    matched_paths = [
        header for header in [
            (k, v) for k, v in file_struct["rclone_paths"]["values"].items()
        ]
        if header[1] in remote_path
    ]

    if not len(matched_paths):
        # - We failed to find a matched path for this directory so we need to figure out what to do.
        modlog.warning("Failed to find a remote header for the file path %s. Filing under unfiled." % remote_path)

        if move_to_unfiled:
            # - We are going to transfer to the unfiled directory.
            return CONFIG["System"]["Directories"]["unfiled_directory"]

        else:
            return None  # -> indicator sentinel
    else:
        # There are matches
        if len(matched_paths) > 1:
            modlog.warning("The matched paths (%s) are not of length 1. Selecting %s as match to %s." % (
            matched_paths, matched_paths[0], remote_path))

        match = matched_paths[0]

    #  Constructing the proper path
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Found match %s for remote path %s." % (match, remote_path))

    proper_path = str(remote_path).replace(match[1], CONFIG["System"]["Directories"][match[0]])

    modlog.debug("Found proper path for %s to be %s in local." % (remote_path, proper_path))
    return proper_path


#  Remote Management IO - Complex
# ----------------------------------------------------------------------------------------------------------------- #
def send_item_to_rclone(location_path, move_to_unfiled=CONFIG["System"]["Directories"]["Remote"]["send_to_unfiled"]):
    """
    Sends the specified item to the correct rclone directory.
    Parameters
    ----------
    location_path: The path to the correct directory.

    Returns: None.
    -------

    """
    #  Logging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Sending file at %s to remote." % location_path)

    #  Getting the remote path
    # ----------------------------------------------------------------------------------------------------------------- #
    path = get_remote_location(location_path, move_to_unfiled=move_to_unfiled)

    modlog.debug("Remote path corresponding to %s was found to be %s." % (location_path, path))

    if path != False:
        # We actually found a path.
        try:
            os.system("rclone copy '%s' '%s'" % (location_path, path))
        except Exception:
            modlog.exception("Transfer %s -> %s Failed." % (location_path, path)
                             )
    else:
        modlog.warning("Failed to find a reasonable path for %s. Not transfering." % (location_path))

    return None


def mt_send_item_to_rclone(location_path, move_to_unfiled=CONFIG["System"]["Directories"]["Remote"]["send_to_unfiled"]):
    """
    Sends the specified item to the correct rclone directory. (MULTI-Threaded)
    Parameters
    ----------
    location_path: The path to the correct directory.

    Returns: None.
    -------

    """
    #  Intro debugging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Transferring %s to remote..." % location_path)

    t_s = perf_counter()
    path = get_remote_location(location_path, move_to_unfiled=move_to_unfiled)

    if path != False:
        # We actually found a path.
        try:
            os.system("rclone copy '%s' '%s'" % (location_path, path))
        except Exception:
            modlog.exception("Transfer %s -> %s Failed." % (location_path, path)
                             )
    else:
        modlog.warning("Failed to find a reasonable path for %s. Not transfering." % (location_path))

    t_f = str(np.round(perf_counter() - t_s, decimals=2))

    screen_lock.acquire()
    print(
        "%supload_files:" % _dbg_string + " [" + Fore.LIGHTGREEN_EX + Style.BRIGHT + "FILE WIZARD" + Style.RESET_ALL + "]: " + "Uploading %s..." % location_path + "  [%s|%s]" % (
            Fore.CYAN + Style.BRIGHT + "DONE" + Style.RESET_ALL,
            Fore.GREEN + Style.BRIGHT + "%s s" % t_f + Style.RESET_ALL
        ))
    screen_lock.release()


def get_item_from_rclone(location_path, move_to_unfiled=CONFIG["System"]["Directories"]["Remote"]["send_to_unfiled"]):
    """
    Downloads an item from box using rclone
    Parameters
    ----------
    location_path: The path to the correct directory.

    Returns: None.
    -------

        """
    #  Logging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Getting file at %s to remote." % location_path)

    #  Getting the remote path
    # ----------------------------------------------------------------------------------------------------------------- #
    path = get_local_location(location_path, move_to_unfiled=move_to_unfiled)

    modlog.debug("Remote path corresponding to %s was found to be %s." % (location_path, path))

    if path != False:
        # We actually found a path.
        try:
            os.system("rclone copy '%s' '%s'" % (location_path, path))
        except Exception:
            modlog.exception("Transfer %s -> %s Failed." % (location_path, path)
                             )
    else:
        modlog.warning("Failed to find a reasonable path for %s. Not transfering." % (location_path))

    return None


def mt_get_item_from_rclone(location_path,
                            move_to_unfiled=CONFIG["System"]["Directories"]["Remote"]["send_to_unfiled"]):
    """
        Downloads an item from box using rclone. (MULTI-Threaded)
    Parameters
    ----------
    location_path: The path to the correct directory.

    Returns: None.
    -------

    """
    t_s = perf_counter()
    #  Logging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Getting file at %s to remote." % location_path)

    #  Getting the remote path
    # ----------------------------------------------------------------------------------------------------------------- #
    path = get_local_location(location_path, move_to_unfiled=move_to_unfiled)

    modlog.debug("Remote path corresponding to %s was found to be %s." % (location_path, path))

    if path != False:
        # We actually found a path.
        try:
            os.system("rclone copy '%s' '%s'" % (location_path, path))
        except Exception:
            modlog.exception("Transfer %s -> %s Failed." % (location_path, path)
                             )
    else:
        modlog.warning("Failed to find a reasonable path for %s. Not transfering." % (location_path))

    t_f = str(np.round(perf_counter() - t_s, decimals=2))

    screen_lock.acquire()
    print(
        "%sdownload_files:" % _dbg_string + " [" + Fore.LIGHTGREEN_EX + Style.BRIGHT + "FILE WIZARD" + Style.RESET_ALL + "]: " + "Downloading %s..." % location_path + "  [%s|%s]" % (
            Fore.CYAN + Style.BRIGHT + "DONE" + Style.RESET_ALL,
            Fore.GREEN + Style.BRIGHT + "%s s" % t_f + Style.RESET_ALL
        ))
    screen_lock.release()


if __name__ == '__main__':
    print(get_remote_location(os.path.join(CONFIG["System"]["Directories"]["figures_directory"], "Fig1")))
    print(get_local_location("PyHPC/Analyses/Figures/Fig1.png"))
