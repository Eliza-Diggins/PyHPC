"""
Simply, Core utilities for the PyHPC project.
"""
from types import SimpleNamespace
import os
import pathlib as pt
import json
# -------------------------------------------------------------------------------------------------------------------- #
#  setup    ========================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
__proj_directory = os.path.join(pt.Path(__file__).parents[1])
# -------------------------------------------------------------------------------------------------------------------- #
# System Info  ======================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
def get_system_info():
    """
    Fetches all of the system info.
    :return: an object containing all of the desired data.
    """
    #- Finding the version -#
    with open(os.path.join(__proj_directory,"bin","lib","ver.json"),"r") as f:
        project_data = json.load(f)

    return SimpleNamespace(**project_data)

if __name__ == '__main__':
    get_system_info()