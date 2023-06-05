Module PyHPC.PyHPC_Utils.text_display_utilities
===============================================
Text display utilities

Functions
---------

    
`dict_to_html(dictionary: dict, headers=None) ‑> str`
:   Converts a ``dict`` object to ``html``.
    
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

    
`get_dict_str(di, tabs=0)`
:   

    
`get_options(option_dict, title)`
:   Selects options from a set of options in a dictionary list.
    :param option_dict: The options to select from.
    :param title: The title to print along with the options.
    :return: The correct option_dict.

    
`get_yes_no(header_message)`
:   Gets a yes or no response from the user.
    Parameters
    ----------
    header_message: The message to send to the header.
    
    Returns: True or False
    -------

    
`lenwc(string: str) ‑> int`
:   Returns the length of the string without counting the color bytes.
    :param string: The string to analyze.
    :return:

    
`print_directories_dict(directories, selected, location=None, smax=None)`
:   

    
`print_option_dict(dict, location, header=None)`
:   Prints an options dictionary in corrected format.
    :param dict: The dictionary containing the correct structure.
    :param location: The location inside of the dictionary if desired.
    :param header: The header (if desired)
    :return: None

    
`print_title(func=<built-in function print>)`
:   

    
`print_verbose(msg, verbose, **kwargs)`
:   

    
`select_files(root_directories, max=None, condition=<function <lambda>>)`
:   Allows the user to select files from the root directories, selecting a maximum of max subject to conditions.
    :param root_directories: The root directories to search from
    :param max: The maximum number of selectable items
    :param condition: Conditions by which to sort.
    :return:

    
`select_files_remote(root_directories, max=None, condition=<function <lambda>>)`
:   Allows the user to select files from the root directories, selecting a maximum of max subject to conditions.
    :param root_directories: The root directories to search from
    :param max: The maximum number of selectable items
    :param condition: Conditions by which to sort.
    :return:

    
`strip_ANSI_escape_sequences_sub(repl, string, count=0)`
:   Return the string obtained by replacing the leftmost non-overlapping occurrences of pattern in string by the replacement repl.

Classes
-------

`KeyLogger(**kwargs)`
:   General class of key logger methods

    ### Methods

    `file_keylog(self, key)`
    :   keylogger for managing files.

    `nav_keylog(self, key)`
    :

    `yes_no_keylog(self, key)`
    :

`PrintRetainer()`
:   Designed for retained printing.

    ### Methods

    `print(self, msg, end='\n')`
    :

    `reprint(self, end='\n')`
    :

`TerminalString()`
:   Defines a TerminalString class which contains all of the important information about printing.

    ### Methods

    `get_color(self, val, obj)`
    :

    `print_directory_string(self, path, selected=False, maxl=None)`
    :

    `print_option_string(self, k, v, selected=False)`
    :

    `print_title(self, title)`
    :   Prints a title
        :param title: The title to print.
        :return:

    `str_in_grid(self, value: str, alignment: str = 'left') ‑> str`
    :   prints the value as it is correctly aligned in the grid
        :param alignment: The alignment to create. (center,left,right)
        :param value: The string to print.
        :return: Str of the value