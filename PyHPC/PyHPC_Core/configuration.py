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
    Reads the configuration file.
    Returns
    dict
        The configuration data.
    -------

    """
    ### reading the TOML string ###
    config_dict = tml.load(os.path.join(ticket_info.installation_location, "bin", "configs", "CONFIG.config"))

    #
    #       Post Processing...
    #

    ## Manging colormaps ##
    _fdbg_string = _dbg_string + Fore.LIGHTMAGENTA_EX + ":read_config:" + Fore.WHITE
    for key in config_dict["Visualization"]["Colormaps"]:
        try:
            config_dict["Visualization"]["Colormaps"][key] = cm.get_cmap(config_dict["Visualization"]["Colormaps"][key])
        except ValueError:  # The colormap doesn't exist
            raise ValueError("%s Configuration key %s failed. %s is not a colormap." % (
                _fdbg_string, key, config_dict["Visualization"]["Colormaps"][key]))

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
