Module PyHPC.setup
==================
Setup script for the PyHPC code system

Written by: Eliza Diggins

Functions
---------

    
`generate_directories(location, overwrite=False)`
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