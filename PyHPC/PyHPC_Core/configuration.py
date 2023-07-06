"""
========================
Configuration In PyHPC
========================
The configuration management in PyHPC is housed within the ``PyHPC.PyHPC_Core.configuration`` module. This manages all
of the configuration files located in the ``/bin/configs`` folder of the user installation.

Setup
-----
There are several different configuration files in the ``/bin/configs`` folder each with a different purpose. To read more
about the core configuration systems included in the ``PyHPC`` runtime environment, read `here <../Configuration.html>`_.

"""
import json
import os
import pathlib as pt
from types import SimpleNamespace
import cmocean as cmo
import toml as tml
from colorama import Fore
from matplotlib.pyplot import cm

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Variables ------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
with open(os.path.join(pt.Path(__file__).parents[1], "bin", "local", "install.tkc")) as file:
    ### Reading the CONFIG file from the installation ticket.
    ticket_info = SimpleNamespace(**json.load(file))

# Setting up the debug strings #
_location = "PyHPC_Core"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s" % (_location, _filename)


# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# -------------------------------------------------------FUNCTIONS ------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
def read_config() -> dict:
    """
    Reads the configuration file at ``/bin/configs/CONFIG.config``.

    Returns
    -------
    dict:
        The configuration dictionary.

    Examples:
    ---------
    >>> CONFIG = read_config()
    >>> assert len(CONFIG) != 0
    """
    ### reading the TOML string ###
    config_dict = tml.load(os.path.join(ticket_info.installation_location, "bin", "configs", "CONFIG.config"))

    #
    #       Post Processing...
    #

    ## Manging colormaps ##

    return config_dict


# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# -------------------------------------------------------  MAIN  --------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
if __name__ == '__main__':
    CONFIG = read_config()
    print(CONFIG)
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# -------------------------------------------------------  NOTES  -------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
"""
NOTES:
"""
