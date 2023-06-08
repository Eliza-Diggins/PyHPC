Module PyHPC.PyHPC_Utils.standard_utils
=======================================
Standard utility functions for wide useage throughout the system.

Functions
---------

    
`getFromDict(dataDict, mapList)`
:   Fetches the values from a nested ``dataDict``.
    Parameters
    ----------
    dataDict: dict
        The nested dictionary from which to pull the data.
    mapList: list of str
        The list of keys at which to locate the value.
    
    Returns
    -------
    any
        The value at ``dataDict[mapList[0]][mapList[...]][mapList[-1]]``.

    
`setInDict(dataDict, mapList, value)`
:   Sets the value of ``dataDict`` at ``mapList`` to ``value``.
    Parameters
    ----------
    dataDict : dict
        The dictionary in which to set the data.
    mapList : list of str
        The sequence of keys to locate the entry to change.
    value : any
        The value to set.
    
    Returns
    -------
    None