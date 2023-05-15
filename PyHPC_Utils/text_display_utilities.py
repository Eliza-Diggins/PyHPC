"""
Text display utilities
"""
import os
import pathlib as pt
import sys

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))

from colorama import Fore, Back, Style
import re
from PyHPC_Core.utils import get_system_info
from PyHPC_Utils.standard_utils import getFromDict, setInDict
from PyHPC_Core.log import get_module_logger
from PyHPC_Core.configuration import read_config
from PyHPC_Utils.remote_utils import rclone_listdir, rclone_isdir
import json
import shutil
from sshkeyboard import listen_keyboard, stop_listening
from copy import deepcopy

# -------------------------------------------------------------------------------------------------------------------- #
#  Setup  ============================================================================================================ #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "PyHPC:PyHPC_Utils"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
_text_file_directory = os.path.join(pt.Path(__file__).parents[1], "bin", "str")
modlog = get_module_logger(_location, _filename)
CONFIG = read_config()
_GSV = {}  # -> This global variable allows for communication between the listener and the function
strip_ANSI_escape_sequences_sub = re.compile(r"\x1b\[[;\d]*[A-Za-z]", re.VERBOSE).sub  # Function to remove color.


# -------------------------------------------------------------------------------------------------------------------- #
# Strings Class ====================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def lenwc(string: str) -> int:
    """
    Returns the length of the string without counting the color bytes.
    :param string: The string to analyze.
    :return:
    """
    return len(strip_ANSI_escape_sequences_sub("", string))


class TerminalString:
    """
    Defines a TerminalString class which contains all of the important information about printing.
    """

    def __init__(self):
        global _text_file_directory
        # Attempting to load
        # ------------------------------------------------------------------------------------------------------------ #
        try:
            with open(os.path.join(_text_file_directory, "cnfg", "print_cnfg.json"), "r") as print_f:
                print_info = json.load(print_f)
        except Exception:
            modlog.exception("Failed to load the TerminalString object.")
            raise OSError("Failed to load the Terminal String object.")

        #  Loading the data
        # ----------------------------------------------------------------------------------------------------------------- #
        self.span_h = print_info["Settings"]["Components"]["span_string"]["value"]
        self.span_v = print_info["Settings"]["Components"]["vertical_span_string"]["value"]
        self.corner = print_info["Settings"]["Components"]["corner_string"]["value"]
        self.opt_format = print_info["Settings"]["Formats"]["dict_entry"]["value"]
        self.pi = print_info
        # Creating Spans
        # ----------------------------------------------------------------------------------------------------------------- #
        self.dim_true = (shutil.get_terminal_size().columns - 2, shutil.get_terminal_size().lines)
        self.dim_alt = (self.dim_true[0] - (self.dim_true[0] % len(self.span_h)),
                        self.dim_true[1] - (self.dim_true[1] % len(self.span_v)))

        self.h = self.corner + (self.span_h * (int(self.dim_alt[0] / len(self.span_h)))) + self.corner

    def get_color(self, val, obj):
        return getattr(obj, getFromDict(self.pi["Settings"]["Colors"], val))

    def str_in_grid(self, value: str, alignment: str = "left") -> str:
        """
        prints the value as it is correctly aligned in the grid
        :param alignment: The alignment to create. (center,left,right)
        :param value: The string to print.
        :return: Str of the value
        """
        #  Grabbing necessary sizing information
        # ----------------------------------------------------------------------------------------------------------------- #
        value = " " + str(value) + " "
        l = lenwc(str(value))
        diff = self.dim_alt[0] - (l)

        if diff < 0:
            diff = 0
            value = str(value)[:self.dim_alt[0] - 3] + Style.RESET_ALL + "..."

        #  Generating the printable
        # ----------------------------------------------------------------------------------------------------------------- #
        if alignment == "right":
            string = self.span_v + (diff * " ") + str(value) + Style.RESET_ALL + self.span_v
        elif alignment == "left":
            string = self.span_v + str(value) + (diff * " ") + Style.RESET_ALL + self.span_v
        elif alignment == "center":
            string = self.span_v + ((diff - int(diff / 2)) * " ") + str(value) + (
                    int(diff / 2) * " ") + Style.RESET_ALL + self.span_v
        else:
            raise ValueError("alignment must be center,left, or right. Not %s." % alignment)

        return string

    def print_option_string(self, k, v, selected=False):
        if any(d not in ["v", "d", "i"] for d in list(v.keys())):
            # This is not a final value
            if not selected:
                out_string = self.pi["Settings"]["Formats"]["dict_entry"]["value_empty"] % (
                        getattr(Fore, self.pi["Settings"]["Colors"]["Dictionary"]["key"]) + str(k) + Style.RESET_ALL)
            else:
                out_string = self.pi["Settings"]["Formats"]["dict_entry"]["value_empty"] % (
                        Fore.BLACK + Back.WHITE + str(k) + Style.RESET_ALL)
            return self.str_in_grid(out_string)
        else:
            if not selected:
                out_string = self.opt_format % (
                    getattr(Fore, self.pi["Settings"]["Colors"]["Dictionary"]["key"]) + str(k) + Style.RESET_ALL,
                    getattr(Fore, self.pi["Settings"]["Colors"]["Dictionary"]["value"]) + str(v["v"]) + Style.RESET_ALL,
                    getattr(Fore, self.pi["Settings"]["Colors"]["Dictionary"]["default"]) + str(
                        v["d"]) + Style.RESET_ALL,
                    getattr(Fore, self.pi["Settings"]["Colors"]["Dictionary"]["info"]) + str(v["i"]) + Style.RESET_ALL)
            else:
                out_string = self.opt_format % (
                    Fore.BLACK + Back.WHITE + str(k),
                    Fore.BLACK + Back.WHITE + str(v["v"]),
                    Fore.BLACK + Back.WHITE + str(v["d"]),
                    Fore.BLACK + Back.WHITE + str(v["i"]) + Style.RESET_ALL)
            return self.str_in_grid(out_string)

    def print_title(self, title):
        """
        Prints a title
        :param title: The title to print.
        :return:
        """
        str = self.h + "\n" + self.str_in_grid("") + "\n" + self.str_in_grid(title,
                                                                             alignment="center") + "\n" + self.str_in_grid(
            "") + "\n" + self.h
        print(str)

    def print_directory_string(self, path, selected=False, maxl=None):
        if not maxl:
            maxl = len(str(path.name))

        space = maxl + 2 - len(str(path.name))

        if not selected:
            out_string = self.get_color(["Directories", ("name_file" if os.path.isfile(path) else "name_directory")],
                                        Fore) + str(path.name) + Style.RESET_ALL + (" " * space) + self.get_color(
                ["Directories", "path"], Fore) + str(path) + Style.RESET_ALL
        else:
            out_string = Fore.BLACK + Back.WHITE + path.name + (" " * space) + str(path)

        return self.str_in_grid(out_string)


class KeyLogger:
    """
    General class of key logger methods
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def yes_no_keylog(self, key):
        # Key logger for the yes no answer dialog #
        try:
            if key == "enter":
                # do something
                self.value = (self.position == 0)
                stop_listening()
            elif key == "left":
                self.position = (self.position - 1) % 2
                stop_listening()
            elif key == "right":
                self.position = (self.position + 1) % 2
                stop_listening()
        except AttributeError as ex:
            pass

    def nav_keylog(self, key):
        # Key logger for the options navigation #
        try:
            if key == "enter":
                self.command = "edit"
                stop_listening()
            if key == "down":
                self.location = (self.location + 1 if self.location != len(self.sub_dict) - 1 else 0)
                stop_listening()
            if key == "up":
                self.location = (self.location - 1 if self.location != 0 else len(self.sub_dict) - 1)
                stop_listening()
            if key == "backspace":
                self.command = "back"
                stop_listening()
            if key == "q":
                self.command = "quit"
                stop_listening()
            if key == "d":
                self.command = "default"
                stop_listening()
        except AttributeError as ex:
            pass

    def file_keylog(self, key):
        "keylogger for managing files."
        try:
            if key == "up":
                self.location = (self.location - 1 if self.location != 0 else self.length)
                stop_listening()
            elif key == "down":
                self.location = (self.location + 1 if self.location < self.length else 0)
                stop_listening()
            elif key == "a":
                self.command = "add"
                stop_listening()
            elif key == "d":
                self.command = "remove"
                stop_listening()
            elif key == "enter":
                self.command = "enter"
                stop_listening()
            elif key == "backspace":
                self.command = "back"
                stop_listening()
        except Exception:
            pass


# -------------------------------------------------------------------------------------------------------------------- #
#  Printings    ====================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def print_title():
    # - Prints the title of the project -#
    with open(os.path.join(_text_file_directory, "general", "title.txt"), "r") as file:
        print(file.read().encode("utf-8").decode("unicode_escape") % tuple(get_system_info().__dict__.values()))


def print_verbose(msg, verbose, **kwargs):
    if verbose:
        print(msg, **kwargs)
    else:
        pass
    return None


def get_dict_str(di, tabs=0):
    str = ""
    for k, v in di.items():
        if isinstance(v, dict):
            str += ("\t" * tabs) + "%s: {\n" % k
            str += get_dict_str(v, tabs=tabs + 1)
            str += ("\t" * tabs) + "}\n"
        else:
            str += ("\t" * tabs + "%s: %s\n" % (k, v))

    return str


def print_option_dict(dict, location, header=None):
    """
    Prints an options dictionary in corrected format.
    :param dict: The dictionary containing the correct structure.
    :param location: The location inside of the dictionary if desired.
    :param header: The header (if desired)
    :return: None
    """
    # - loading the terminal string -#
    text_t = TerminalString()

    # - Generating the tops
    if header:
        print(text_t.str_in_grid(header))
    else:
        pass

    print(text_t.h)

    # Main #
    for k, v in dict.items():
        print(text_t.print_option_string(k, v, selected=(location == k)))

    print(text_t.h)


def print_directories_dict(directories, selected, location=None, smax=None):
    text_t = TerminalString()
    text_t.print_title("File Selector")
    if max:
        print(text_t.str_in_grid("Select A Directory: %s" % (
            "(%s/%s Selected)" % (len(selected), smax) if len(selected) != smax else "(%s/%s Selected)" % (
                Fore.RED + str(len(selected)), str(smax) + Style.RESET_ALL))) + "\n" + text_t.h)
    else:
        print(text_t.str_in_grid("Select A Directory: ") + "\n" + text_t.h)
    max_dir_length = max([len(str(i.name)) for i in directories])
    for id, dir in enumerate(directories):
        print(text_t.print_directory_string(pt.Path(dir), selected=(id == location), maxl=max_dir_length))

    print(text_t.h)
    print(text_t.str_in_grid("Selected Directories:"))
    print(text_t.h)
    max_select_length = max([len(str(i.name)) for i in directories])
    for id, select in enumerate(selected):
        print(text_t.print_directory_string(pt.Path(select), selected=(id + len(directories) == location),
                                            maxl=max_select_length))
    print(text_t.h)


# -------------------------------------------------------------------------------------------------------------------- #
#  Movement Related Behaviors ======================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def get_yes_no(header_message):
    """
    Gets a yes or no response from the user.
    Parameters
    ----------
    header_message: The message to send to the header.

    Returns: True or False
    -------

    """
    # - Defining the two strings to display -#
    yes_string = "%s: [%s|%s]" % (header_message, Fore.BLACK + Back.WHITE + "YES" + Style.RESET_ALL, "NO")
    no_string = "%s: [%s|%s]" % (header_message, "YES", Fore.BLACK + Back.WHITE + "NO" + Style.RESET_ALL)

    # - Creating the key logger -#
    klog = KeyLogger(position=0, value=None)
    while klog.value == None:
        os.system('cls' if os.name == 'nt' else 'clear')
        if klog.position == 0:
            print(yes_string)
        else:
            print(no_string)

        listen_keyboard(on_press=klog.yes_no_keylog)

    return klog.value


def get_options(option_dict, title):
    """
    Selects options from a set of options in a dictionary list.
    :param option_dict: The options to select from.
    :param title: The title to print along with the options.
    :return: The correct option_dict.
    """
    #  Intro debug
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Selecting options with title %s." % title)

    #  Printing the title
    # ----------------------------------------------------------------------------------------------------------------- #
    text_t = TerminalString()

    #  Setup
    # ----------------------------------------------------------------------------------------------------------------- #

    # - Core printing utilities -#
    header = "Select the option to edit..."
    setting_commands = {
        "n": "Exit/Finish - Move down a level.",
        "e": "Edit - Move to.",
        "d": "Reset option to default",
    }

    # startup copy and setting #
    settings = deepcopy(option_dict)  # create the copy we are going to use for the setting storage.

    klog = KeyLogger(position=[list(option_dict.keys())[0]],
                     location=0,
                     selected_key=None,
                     sub_dict=option_dict,
                     command=None,
                     reset=True,
                     reset_location=True)

    #  Main Cycle
    # ----------------------------------------------------------------------------------------------------------------- #
    CHECK_DONE = False  # whole scope check for finish.
    new_calcs = True  # This flag lets us skip calculations if they aren't necessary.

    while not CHECK_DONE:  # we are still cycling'

        ## Setting the title ##
        text_t.print_title(title)

        #  Locating
        # ----------------------------------------------------------------------------------------------------------------- #

        # -------------------------------------------------------------------------------------------------------------------- #
        # Printing the options dictionary ==================================================================================== #
        # -------------------------------------------------------------------------------------------------------------------- #
        print_option_dict(klog.sub_dict, klog.position[-1], header=header)

        # -------------------------------------------------------------------------------------------------------------------- #
        #  Navigation ======================================================================================================== #
        # -------------------------------------------------------------------------------------------------------------------- #
        listen_keyboard(on_press=klog.nav_keylog)
        # - Forcing location parity -#
        klog.position[-1] = list(klog.sub_dict.keys())[klog.location]

        if klog.command:  # we have a command to execute
            if klog.command == "edit":

                #  Editing the dictionary
                # ----------------------------------------------------------------------------------------------------------------- #
                if all(k in ["v", "d", "i"] for k in list(klog.sub_dict[klog.position[-1]].keys())):
                    # This is an explicit value
                    inp = input(
                        "%sPlease enter a new value for %s. ['n' to return]:" % (
                            "[" + Fore.RED + "INPUT" + Style.RESET_ALL + "]: ",
                            klog.position[-1]))
                    if inp != "n":
                        setInDict(settings, klog.position + ["v"], inp)
                        klog.sub_dict = getFromDict(settings, klog.position[:-1])


                else:
                    # We are not editing, we are entering.
                    klog.sub_dict = getFromDict(settings, klog.position)
                    klog.position += [list(klog.sub_dict.keys())[0]]
                    klog.location = 0


            elif klog.command == "back":

                #  Moving backward
                # ----------------------------------------------------------------------------------------------------------------- #
                # We need to reduce a layer
                if len(klog.position) > 1:
                    # - We can actually move back -#
                    klog.position = klog.position[:-1]
                    klog.sub_dict = getFromDict(settings, klog.position[:-1])

                    klog.location = list(klog.sub_dict.keys()).index(klog.position[-1])
                else:
                    yn = get_yes_no("Exit the option selection?")

                    if yn != True:
                        pass
                    else:
                        return settings
            elif klog.command == "quit":
                yn = get_yes_no("Exit the option selection?")

                if yn != True:
                    pass
                else:
                    return settings
            elif klog.command == "default":
                setInDict(settings, klog.position + ["v"], getFromDict(settings, klog.position + ["d"]))
                klog.sub_dict = getFromDict(settings, klog.position[:-1])

            klog.command = None
        os.system('cls' if os.name == 'nt' else 'clear')
    return settings


def select_files(root_directories, max=None, condition=lambda x: True):
    """
    Allows the user to select files from the root directories, selecting a maximum of max subject to conditions.
    :param root_directories: The root directories to search from
    :param max: The maximum number of selectable items
    :param condition: Conditions by which to sort.
    :return:
    """
    #  Debugging and Setup
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Selecting %s files from %s" % (max, root_directories))
    root_directories = [pt.Path(i) for i in root_directories]
    # - Creating the print manager and the key logger -#
    klog = KeyLogger(display_directories=[i for i in root_directories if condition(i)],
                     position="",
                     location=0,
                     command=None)
    text_t = TerminalString()

    # - Selected items -#
    selected_items = []
    exit = False

    while not exit:
        # ------------------------------------------------------------------------------------------------------------- #
        # Printing
        # ------------------------------------------------------------------------------------------------------------ #
        klog.length = len(klog.display_directories) + len(selected_items) - 1
        print_directories_dict(klog.display_directories, selected_items, location=klog.location, smax=max)

        # ------------------------------------------------------------------------------------------------------------- #
        # Listening ================================================================================================== #
        # --------------------------------------------------------------------------------------------------------------#
        listen_keyboard(on_press=klog.file_keylog)

        klog.position = (klog.display_directories + selected_items)[klog.location]
        #  Command management
        # ----------------------------------------------------------------------------------------------------------------- #
        if klog.command:
            if klog.command == "add":
                if klog.position in klog.display_directories:
                    check = True if not max else len(selected_items) < max

                    if check:
                        selected_items.append(klog.position)
                        klog.display_directories.remove(klog.position)
                        klog.position = (klog.display_directories + selected_items)[klog.location]
                    else:
                        print("You have selected the maximal number of objects because max=%s." % max)
                else:
                    pass
            elif klog.command == "remove":
                if klog.position in selected_items:
                    selected_items.remove(klog.position)
                    klog.display_directories.append(klog.position)
                    klog.position = (klog.display_directories + selected_items)[klog.location]
                else:
                    pass
            elif klog.command == "enter":
                if os.path.isdir(klog.position):
                    sub_dirs = [pt.Path(os.path.join(klog.position, i)) for i in
                                os.listdir(klog.position) if condition(pt.Path(os.path.join(klog.position, i)))]
                    if len(sub_dirs):
                        klog.display_directories = sub_dirs
                        klog.location = 0
                        klog.position = (klog.display_directories + selected_items)[klog.location]
                    else:
                        pass

            elif klog.command == "back":
                if klog.position not in root_directories:
                    if klog.position.parents[0] in root_directories:
                        klog.display_directories = [i for i in root_directories if condition(i)]
                    else:
                        klog.display_directories = [pt.Path(os.path.join(klog.position.parents[1], i)) for i in
                                                    os.listdir(klog.position.parents[1]) if
                                                    condition(pt.Path(os.path.join(klog.position.parents[1], i)))]
                    klog.location = 0
                    klog.position = (klog.display_directories + selected_items)[klog.location]
                else:
                    klog.command = "exit"

            #  Exit Command
            # ----------------------------------------------------------------------------------------------------------------- #
            if klog.command == "exit":
                os.system('cls' if os.name == 'nt' else 'clear')
                return selected_items
            klog.command = None
        os.system('cls' if os.name == 'nt' else 'clear')


def select_files_remote(root_directories, max=None, condition=lambda x: True):
    """
    Allows the user to select files from the root directories, selecting a maximum of max subject to conditions.
    :param root_directories: The root directories to search from
    :param max: The maximum number of selectable items
    :param condition: Conditions by which to sort.
    :return:
    """
    #  Debugging and Setup
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Selecting %s files from %s" % (max, root_directories))
    root_directories = [pt.Path(i) for i in root_directories]
    # - Creating the print manager and the key logger -#
    klog = KeyLogger(display_directories=[i for i in root_directories if condition(i)],
                     position="",
                     location=0,
                     command=None)
    text_t = TerminalString()

    # - Selected items -#
    selected_items = []
    exit = False

    while not exit:
        # ------------------------------------------------------------------------------------------------------------- #
        # Printing
        # ------------------------------------------------------------------------------------------------------------ #
        klog.length = len(klog.display_directories) + len(selected_items) - 1
        print_directories_dict(klog.display_directories, selected_items, location=klog.location, smax=max)

        # ------------------------------------------------------------------------------------------------------------- #
        # Listening ================================================================================================== #
        # --------------------------------------------------------------------------------------------------------------#
        listen_keyboard(on_press=klog.file_keylog)

        klog.position = (klog.display_directories + selected_items)[klog.location]
        #  Command management
        # ----------------------------------------------------------------------------------------------------------------- #
        if klog.command:
            if klog.command == "add":
                if klog.position in klog.display_directories:
                    check = True if not max else len(selected_items) < max

                    if check:
                        selected_items.append(klog.position)
                        klog.display_directories.remove(klog.position)
                        klog.position = (klog.display_directories + selected_items)[klog.location]
                    else:
                        print("You have selected the maximal number of objects because max=%s." % max)
                else:
                    pass
            elif klog.command == "remove":
                if klog.position in selected_items:
                    selected_items.remove(klog.position)
                    klog.display_directories.append(klog.position)
                    klog.position = (klog.display_directories + selected_items)[klog.location]
                else:
                    pass
            elif klog.command == "enter":
                if rclone_isdir(klog.position):
                    sub_dirs = [pt.Path(os.path.join(klog.position, i)) for i in
                                rclone_listdir(klog.position) if condition(pt.Path(os.path.join(klog.position, i)))]
                    if len(sub_dirs):
                        klog.display_directories = sub_dirs
                        klog.location = 0
                        klog.position = (klog.display_directories + selected_items)[klog.location]
                    else:
                        pass
            elif klog.command == "back":
                if klog.position not in root_directories:
                    if klog.position.parents[0] in root_directories:
                        klog.display_directories = [i for i in root_directories if condition(i)]
                    else:
                        klog.display_directories = [pt.Path(os.path.join(klog.position.parents[1], i)) for i in
                                                    rclone_listdir(klog.position.parents[1]) if
                                                    condition(pt.Path(os.path.join(klog.position.parents[1], i)))]
                    klog.location = 0
                    klog.position = (klog.display_directories + selected_items)[klog.location]
                else:
                    klog.command = "exit"

            #  Exit Command
            # ----------------------------------------------------------------------------------------------------------------- #
            if klog.command == "exit":
                os.system('cls' if os.name == 'nt' else 'clear')
                return selected_items
            klog.command = None
        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    text_t = TerminalString()
    select_files_remote(["box:/PyCS"], max=3, condition=lambda x: (rclone_isdir(x) or x.suffix == ".mp4"))
