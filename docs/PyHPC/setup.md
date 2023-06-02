Module PyHPC.setup
==================
Installation script for the PyHPC system. This script will install the necessary configuration files and
other critical resources for execution to the output location of your choice. If a ticket exists for your current
installation, then an update will occur unless the ```-ri``` or ``--reinstall`` flag is used in the command line, in
which case a full reinstallation will occur.

**Usage:**

```commandline
  _/_/_/_/_/_/                 _/          _/   _/_/_/_/_/_/       _/_/_/_/_/
  _/         _/                _/          _/   _/         _/    _/
  _/         _/  _/      _/    _/          _/   _/         _/   _/
  _/_/_/_/_/_/   _/      _/    _/_/_/_/_/_/_/   _/_/_/_/_/_/    _/
  _/              _/_/_/_/     _/          _/   _/              _/
  _/                  _/       _/          _/   _/               _/
  _/             _/_/_/        _/          _/   _/                 _/_/_/_/_/
#-------------------------------------------------------------------------------#
Written by Eliza C. Diggins, University of Utah Department of Physics and Astronomy

Version = 0.2-Alpha
#-----------#

Stable = False
#------------#

PyHPC:setup: [INSTALL WIZARD]: Running setup.py...
usage: setup.py [-h] [-ri] [-l LOCATION] [-v] [-g]

optional arguments:
  -h, --help            show this help message and exit
  -ri, --reinstall      Flag to force a complete reinstallation.
  -l LOCATION, --location LOCATION
                        The location for the installation.
  -v, --verbose         Enable verbose mode
  -g, --git             Update from github.
```

Functions
---------

    
`generate_directories(location, overwrite=False)`
:   

    
`print_title()`
:   

    
`print_verbose(msg, verbose, **kwargs)`
:   

    
`rec_gen_dirs(loc, dic, ovr)`
:   

    
`set_directories_config_recur(cnfg, data, location)`
:   

    
`set_directories_in_config(location, cnfg)`
:   

    
`update_dict(master: dict, local: dict) ‑> dict`
:   Searches for updates to the local dictionary in master and applies them without lossing user entries in the local dict.
    :param master: The master dict from which to find updates
    :param local: The local dict with user settings.
    :return: dict.