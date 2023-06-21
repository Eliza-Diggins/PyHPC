"""
Text display utilities
"""
import os
import pathlib as pt
import sys

sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[2]))

from colorama import Fore, Back, Style
import re
from PyHPC.PyHPC_Core.utils import get_system_info
from PyHPC.PyHPC_Utils.standard_utils import getFromDict, setInDict
import logging
from PyHPC.PyHPC_Core.configuration import read_config
from PyHPC.PyHPC_Utils.remote_utils import rclone_listdir, rclone_isdir
import json
import shutil
from sshkeyboard import listen_keyboard, stop_listening
from copy import deepcopy
import re

# -------------------------------------------------------------------------------------------------------------------- #
#  Setup  ============================================================================================================ #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "PyHPC:PyHPC_Utils"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
_text_file_directory = os.path.join(pt.Path(__file__).parents[1], "bin", "str")
modlog = logging.getLogger(__name__)
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

    def print_frame(self,dataframe, columns=None,selected=None,location=None):
        """
        Prints the input dataframe to the terminal in a correctly outputted table format.
        Parameters
        ----------
        dataframe: pd.DataFrame
            The dataframe to display.
        columns: list of str
            The columns of the table to show in the table.

        Returns
        -------
        None

        """
        #  Generating the regex
        # ----------------------------------------------------------------------------------------------------------------- #
        _non_span_v_re = re.compile("[^%s]" % self.span_v)
        _no_color_re = re.compile("\\u001b[[0-9]*m")
        #  Configuring the columns of the printing process
        # ----------------------------------------------------------------------------------------------------------------- #
        if not columns:
            columns = dataframe.columns

        col_width_base = int((self.dim_alt[0]-(len(columns)-1))/len(columns)) #: This is the natural length we want
        col_width_offset = (self.dim_alt[0]-(len(columns)-1)) % len(columns) #: This is the remainer on the outsides.

        column_widths = [col_width_base for i in range(len(columns))] + [col_width_offset+col_width_base]

        #- Configuring the columns for the printing process -#
        column_names = [column+(" "*(column_width-2-len(column))) if len(column)<column_width-2 else column[:column_width-5]+"..." for column_width,column in zip(column_widths,columns)]

        #- generating the print header -#
        return_string = "" #: This is the string that is eventually returned from the function.
        header_string = self.span_v #: This is the header specific string.

        for column in column_names:
            header_string += (" %s %s" % (Fore.RED + Style.BRIGHT + column + Style.RESET_ALL,self.span_v))

        return_string += self.h+"\n"
        return_string += header_string + "\n"
        return_string += _non_span_v_re.subn("-",_no_color_re.subn("",header_string)[0])[0] + '\n'

        #  Managing rows
        # ----------------------------------------------------------------------------------------------------------------- #
        if not selected:
            selected = []
        if location == None:
            location = None

        for row_id in range(len(dataframe)):
            #- Grabbing the color precursor -#
            if row_id == location:
                prec = Back.BLUE
            elif row_id in selected:
                prec = Fore.BLACK+Back.WHITE
            else:
                prec = ""

            return_string+= prec+self.span_v
            values = [str(i)  for i in list(dataframe.iloc[row_id,:][columns])]
            values = [
                value + (" " * (column_width - 2 - lenwc(value))) if lenwc(value) < column_width - 2 else value[
                                                                                                         :column_width - 5] + "..."
                for column_width, value in zip(column_widths, values)]
            for v in values:
                return_string += (" %s %s" % (v, self.span_v))

            return_string += Style.RESET_ALL+"\n"
        return_string += self.h + "\n"
        print(return_string)


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

    def nav_build_keylog(self, key):
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
            if key == "a":
                self.command = "add"
                stop_listening()
            if key == "r":
                self.command = "remove"
                stop_listening()
        except AttributeError as ex:
            pass
    def sim_manager_keylog(self,key):
        try:
            if key == "enter":
                self.command = "enter"
                stop_listening()
            if key == "down":
                self.position = (self.position + 1 if self.position != len(self.object.raw) - 1 else 0)
                stop_listening()
            if key == "up":
                self.position = (self.position - 1 if self.position != 0 else len(self.object.raw) - 1)
                stop_listening()
            if key == "backspace":
                self.command = "back"
                stop_listening()
            if key == "l":
                self.command = "log"
                stop_listening()
            if key == "d":
                self.command = "default"
                stop_listening()
            if key == "s":
                self.command = "select"
                stop_listening()
            if key == "d":
                self.command = "delete"
                stop_listening()
            if key == "e":
                self.command = "edit"
                stop_listening()
            if key == "a":
                self.command = "add"
                stop_listening()
        except AttributeError as ex:
            pass
    def edit_dict_keylog(self,key):
        try:
            if key == "enter":
                self.command = "enter"
                stop_listening()
            if key == "down":
                self.position = (self.position + 1 if self.position != len(self.object.raw) - 1 else 0)
                stop_listening()
            if key == "up":
                self.position = (self.position - 1 if self.position != 0 else len(self.object.raw) - 1)
                stop_listening()
            if key == "backspace":
                self.command = "back"
                stop_listening()
            if key == "l":
                self.command = "log"
                stop_listening()
            if key == "d":
                self.command = "default"
                stop_listening()
            if key == "s":
                self.command = "select"
                stop_listening()
            if key == "d":
                self.command = "delete"
                stop_listening()
        except AttributeError as ex:
            pass
    def build_dict_keylog(self,key):
        try:
            if key == "enter":
                self.command = "enter"
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
                stop_listening()
            if key == "a":
                self.command = "add"
                stop_listening()

            if key == "d":
                self.command = "delete"
                stop_listening()
        except AttributeError as ex:
            pass
    def menu_keylog(self, key):
        # Key logger for the options navigation #
        try:
            if key == "enter":
                self.command = "enter"
                stop_listening()
            if key == "down":
                self.location = (self.location + 1 if self.location != len(self.sub_dict) - 1 else 0)
                stop_listening()
            if key == "up":
                self.location = (self.location - 1 if self.location != 0 else len(self.sub_dict) - 1)
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


class PrintRetainer:
    """
    Designed for retained printing.
    """

    def __init__(self):
        self.string = ""
        self.end = ""

    def print(self, msg, end="\n"):
        self.string += msg + end
        print(msg, end=end)
        self.end = end

    def reprint(self, end="\n"):
        msg = self.string
        self.string = ""
        self.print(msg[:-len(self.end)], end=end)


# -------------------------------------------------------------------------------------------------------------------- #
#  Printings    ====================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def print_title(func=print):
    # - Prints the title of the project -#
    with open(os.path.join(_text_file_directory, "general", "title.txt"), "r") as file:
        string = file.read().encode("utf-8").decode("unicode_escape") % tuple(get_system_info().__dict__.values())

    term_string = TerminalString()
    func(term_string.h)
    for line in string.split("\n"):
        func(term_string.str_in_grid(line, alignment="center"))

    func(term_string.h)


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

def print_dictionary(dictionary, location):
    """
    Prints an options dictionary in corrected format.
    :param dict: The dictionary containing the correct structure.
    :param location: The location inside of the dictionary if desired.
    :param header: The header (if desired)
    :return: None
    """
    # - loading the terminal string -#
    text_t = TerminalString()

    for k,v in dictionary.items():
        if location != str(k):
            if not isinstance(v,dict):
                print(text_t.print_option_string(str(k),{"v":str(v),"d":"","i":""},selected=False))
            else:
                print(text_t.str_in_grid("%s"%(Fore.CYAN+str(k))))
        else:
            if not isinstance(v,dict):
                print(text_t.print_option_string(str(k),{"v":str(v),"d":"","i":""},selected=True))
            else:
                print(Fore.BLACK+Back.WHITE+text_t.str_in_grid("%s"%(str(k)))+Style.RESET_ALL)

    print(text_t.h)


def print_directories_dict(directories, selected, location=None, smax=None):
    text_t = TerminalString()
    text_t.print_title("File Selector")
    if max:
        print(text_t.str_in_grid("Select A Directory: %s" % (
            "(%s/%s Selected)" % (len(selected), smax) if len(selected) != smax else "(%s/%s Selected)" % (
                Fore.RED + str(len(selected)), str(smax) + Style.RESET_ALL))) + "\n" + text_t.str_in_grid(""))
    else:
        print(text_t.str_in_grid("Select A Directory: "))
        print(text_t.str_in_grid(""))
    max_dir_length = max([0] + [len(str(i.name)) for i in directories])
    for id, dir in enumerate(directories):
        print(text_t.print_directory_string(pt.Path(dir), selected=(id == location), maxl=max_dir_length))

    print(text_t.h)
    print(text_t.str_in_grid("Selected Directories:"))
    print(text_t.str_in_grid(""))
    max_select_length = max([0] + [len(str(i.name)) for i in directories])
    for id, select in enumerate(selected):
        print(text_t.print_directory_string(pt.Path(select), selected=(id + len(directories) == location),
                                            maxl=max_select_length))
    print(text_t.h)


# -------------------------------------------------------------------------------------------------------------------- #
# Conversions ======================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def dict_to_html(dictionary: dict, headers=None) -> str:
    """
    Converts a ``dict`` object to ``html``.

    Parameters
    ----------
    dictionary : dict
        The dictionary to convert.

    headers : list, default=None
        The columns to include in the table. If ``None``, simply includes all headers.

    Returns
    -------
    str
        The converted table in html code.

    """
    #  Managing headers
    # ----------------------------------------------------------------------------------------------------------------- #
    if not headers:
        all_headers = [list(entry.keys()) for entry in dictionary.values()]
        headers = []
        for val in all_headers:
            headers += val

        headers = list(set(list(headers)))
        headers = [" "] + headers

    #  Writing
    # ----------------------------------------------------------------------------------------------------------------- #
    html_string = "<table>\n"

    # - Writing the header -#
    html_string += "\t<tr>\n"

    for head in headers:
        html_string += "\t\t<th>%s</th>\n" % head
    html_string += "\t</tr>\n"

    # - Writing the table -#
    for entry, value in dictionary.items():
        html_string += "\t<tr>\n"

        html_string += "\t\t<td>%s</td>\n" % entry
        for head in headers[1:]:
            html_string += "\t\t<td>%s</td>\n" % value[head]
        html_string += "\t</tr>\n"
    html_string += "</table>"

    return html_string


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


def build_options(option_dict, title):
    """
    ``build_options`` is similar to ``PyHPC.PyHPC_Utils.text_display_utilities.get_options``; however, in this case,
    the user can add and remove components from the dictionary as well.

    Parameters
    ----------
    option_dict : dict
        The base / default component settings.
    title : str
        The title to display

    Returns
    -------
    dict
        Selected options in a dictionary format.
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

    # startup copy and setting #
    settings = {"Component 1":deepcopy(option_dict)}  # create the copy we are going to use for the setting storage.


    klog = KeyLogger(position=["Component 1"],
                     location=0,
                     selected_key=None,
                     sub_dict=settings,
                     command=None,
                     reset=True,
                     reset_location=True)

    #  Main Cycle
    # ----------------------------------------------------------------------------------------------------------------- #
    CHECK_DONE = False  # whole scope check for finish.

    while not CHECK_DONE:  # we are still cycling'

        ## Setting the title ##
        text_t.print_title(title)

        #  Locating
        # ----------------------------------------------------------------------------------------------------------------- #

        # -------------------------------------------------------------------------------------------------------------------- #
        # Printing the options dictionary ==================================================================================== #
        # -------------------------------------------------------------------------------------------------------------------- #
        print_option_dict(klog.sub_dict, klog.position[-1], header=header)
        print("'backspace': move up level\n'enter': move down level / edit\n'+': add component\n'-': remove component\n'd': reset")
        # -------------------------------------------------------------------------------------------------------------------- #
        #  Navigation ======================================================================================================== #
        # -------------------------------------------------------------------------------------------------------------------- #
        listen_keyboard(on_press=klog.nav_build_keylog)
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

                    if not yn:
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
                if len(klog.position) != 1:
                    setInDict(settings, klog.position + ["v"], getFromDict(settings, klog.position + ["d"]))
                    klog.sub_dict = getFromDict(settings, klog.position[:-1])
                else:
                    pass

            elif klog.command == "add":
                if len(klog.position) > 1:
                    pass
                else:
                    comps = [int(k.split(" ")[1]) for k in settings]
                    settings = {**settings,"Component %s"%str(max(comps)+1):deepcopy(option_dict)}
                    klog.sub_dict = getFromDict(settings, klog.position[:-1])

            elif klog.command == "remove":
                if len(klog.position) > 1 or len(settings) <=1:
                    pass
                else:
                    settings ={k:v for k,v in settings.items() if k!=klog.position[-1]}
                    klog.position = ["Component 1"]
                    klog.sub_dict = getFromDict(settings, klog.position[:-1])
            klog.command = None
        os.system('cls' if os.name == 'nt' else 'clear')
    return settings


def select_files(root_directories, max=None, condition=lambda x: True):
    """
    Allows the user to select up to ``max`` files satisfying the condition ``condition`` from the ``root_directories`` listed.

    Parameters
    ----------
    root_directories: list of str
        The list of paths to include in the searchable part of the selection.
    max : int, default=None
        The maximal number of selected items. By default there is no limit.
    condition: callable
        The ``condition`` can be used to sort for certain items in the nested lists. This should be a function which
        takes a single argument, ``path`` and returns either ``True`` or ``False`` to indicate whether or not the
        item should be included.

    Returns
    -------
    list
        The list of selected directories.

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
                if os.path.isdir(klog.position) and klog.position not in selected_items:
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


def option_menu(options, desc=True, title=None):
    """
    Select from any of the options in the  ``options`` list.

    Parameters
    ----------
    options : dict
        ``dict`` of options (``dict``) of the form ``{"name 1":"desc"}``.
    desc : bool
        ``True`` to show descriptions in the selection process

    title : str
        The title to print at the head of the execution area.

    Returns
    -------
    str
        The selected option name from the list.

    """
    #  Logging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Selecting options from %s." % options)

    #  Managing structure
    # ----------------------------------------------------------------------------------------------------------------- #
    logger = KeyLogger(options=options, location=0, exit=False, command=None)

    # - Generating the options dict - #
    if desc:
        options_dictionary = {
            name: {
                "v": "",
                "d": "",
                "i": value
            }
            for name, value in options.items()

        }
    else:
        options_dictionary = {
            name: {
                "v": "",
                "d": "",
                "i": ""
            }
            for name, value in options.items()

        }

    # - Fetching terminal - #
    keys = list(options_dictionary.keys())
    terminal_string = TerminalString()

    while not logger.exit:
        #  Managing title printing
        # ----------------------------------------------------------------------------------------------------------------- #
        if title:
            terminal_string.print_title(title)
        else:
            terminal_string.print_title(title)

        print_option_dict(options_dictionary, location=keys[logger.location])

        listen_keyboard(on_press=logger.menu_keylog)

        #  Managing the commands
        # ----------------------------------------------------------------------------------------------------------------- #
        if logger.command:  # we have a command to execute
            if logger.command == "enter":
                return keys[logger.location]
            logger.command = None

        os.system('cls' if os.name == 'nt' else 'clear')

def edit_dictionary(dictionary,title):
    """
    Allows for editing of the dictionary.
    Parameters
    ----------
    dictionary: dict
        The dictionary to edit.

    Returns
    -------
    dict
        The resulting dictionary after edits.

    """
    #  Logging
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Selecting dictionary from %s." % dictionary)

    #  Managing structure
    # ----------------------------------------------------------------------------------------------------------------- #
    klog = KeyLogger(sub_dict=dictionary, location=0, exit=False, command=None,position=[])


    # - Fetching terminal - #
    terminal_string = TerminalString()

    while not klog.exit:
        #  Managing title printing
        # ----------------------------------------------------------------------------------------------------------------- #
        if title:
            terminal_string.print_title(title)
        else:
            terminal_string.print_title(title)

        if len(klog.sub_dict):
            print_dictionary(klog.sub_dict,location=str(list(klog.sub_dict.keys())[klog.location]))
        else:
            print("-- Nothing Here --")
        listen_keyboard(on_press=klog.build_dict_keylog)

        #  Managing the commands
        # ----------------------------------------------------------------------------------------------------------------- #
        if klog.command:  # we have a command to execute
            if klog.command == "enter":
                if len(klog.sub_dict) and isinstance(klog.sub_dict[list(klog.sub_dict.keys())[klog.location]],dict):
                    klog.position.append(list(klog.sub_dict.keys())[klog.location])
                    klog.sub_dict = klog.sub_dict[list(klog.sub_dict.keys())[klog.location]]
                    klog.location = 0
                else:
                    type = input("[Dict-Manager]: Data type? [L[ist],D[ict],I[nt],F[loat],S[tring]")
                    if type in ["D", "dict", 'DICT']:
                        setInDict(dictionary, klog.position + [list(klog.sub_dict.keys())[klog.location]], {})
                    if type == "L":
                        setInDict(dictionary, klog.position + [list(klog.sub_dict.keys())[klog.location]], input("[Dict-Manager]: Enter the new value: ").split(","))
                    elif type not in { "I": int, "F": float, "S": str}:
                        input(
                            "[Dict-Manager]: The datatype you entered isn't valid. Press any key top return to execution...")
                    else:
                        setInDict(dictionary, klog.position + [list(klog.sub_dict.keys())[klog.location]],
                                  {"I": int, "F": float, "S": str}[type](
                                      input("[Dict-Manager]: Enter the new value: ")))

                    print(dictionary)
                    klog.sub_dict = getFromDict(dictionary, klog.position)

            elif klog.command == "back":
                if len(klog.position)> 0:
                    klog.position = klog.position[:-1]
                    klog.sub_dict = getFromDict(dictionary,klog.position)
                    klog.location = 0
                else:
                    val = get_yes_no("Exit Dictioanry Editor?")

                    if val:
                        return dictionary
            elif klog.command == "add":
                key = input("[Dict-Manager]: Enter the key name:")
                type = input("[Dict-Manager]: Data type? [L[ist],D[ict],I[nt],F[loat],S[tring]")
                if type in ["D","dict",'DICT']:
                    setInDict(dictionary,klog.position+[key],{})
                elif type not in {"L":list,"D":dict,"I":int,"F":float,"S":str}:
                    input("[Dict-Manager]: The datatype you entered isn't valid. Press any key top return to execution...")
                else:
                    setInDict(dictionary,klog.position+[key],{"L":list,"D":dict,"I":int,"F":float,"S":str}[type](input("[Dict-Manager]: Enter the new value: ")))

                print(dictionary)
                klog.sub_dict = getFromDict(dictionary,klog.position)
            elif klog.command == "delete":
                del klog.sub_dict[list(klog.sub_dict.keys())[klog.location]]
                setInDict(dictionary,klog.position,klog.sub_dict.copy())
                klog.location = 0
            klog.command = None

        os.system('cls' if os.name == 'nt' else 'clear')
        print(klog.position)

if __name__ == '__main__':
    stri = {
  "test.g2": {
    "information": "A simple test case to guide development use.",
    "meta": {
      "dateCreated": "01_01_2000-01:00:00",
      "lastEdited": "01_01_2000-01:00:00"
    },
    "simulations": {
      "test.nml": {
        "information": "Simulation example entry.",
        "action_log": {
          "created": "date = something"
        },
        "meta": {},
        "core": {},
        "outputs": {}
      }
    },
    "core": {}
  }
}
    text_t = TerminalString()
    import pandas as pd
    x ={"1":{1:2,2:3,3:4},"2":"hemp","Somethin":"345"}
    t = TerminalString()
    edit_dictionary(stri,"None")
