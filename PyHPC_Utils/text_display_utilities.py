"""
Text display utilities
"""
import pathlib as pt
from colorama import Fore,Back,Style
import os
from PyHPC_Core.utils import get_system_info
# -------------------------------------------------------------------------------------------------------------------- #
#  Setup  ============================================================================================================ #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "PyHPC:PyHPC_Utils"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
__text_file_directory = os.path.join(pt.Path(__file__).parents[1],"bin","str")
# -------------------------------------------------------------------------------------------------------------------- #
#  Printings    ====================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def print_title():
    #- Prints the title of the project -#
    with open(os.path.join(__text_file_directory,"general","title.txt"),"r") as file:
        print(file.read().encode("utf-8").decode("unicode_escape")%tuple(get_system_info().__dict__.values()))

def print_verbose(msg,verbose,**kwargs):
    if verbose:
        print(msg,**kwargs)
    else:
        pass
    return None

if __name__ == '__main__':
    print_title()