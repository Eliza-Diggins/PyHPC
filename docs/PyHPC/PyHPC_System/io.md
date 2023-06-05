Module PyHPC.PyHPC_System.io
============================
Core IO operations for passing objects to slurm, running commands, etc.

Functions
---------

    
`write_command_string(command: str, *args, **kwargs) ‑> str`
:   Returns the corresponding command string in the format ''command arg[0] arg[...] -k[0] v[0] ... -k[n] v[n].
    :param command: The command to run.
    :param args: Unflagged arguments to pass through the shell.
    :param kwargs: Flagged arguments to pass through the shell with corresponding <b>QUICK</b> keys.
    :return: String.

    
`write_ramses_nml(settings: dict, output_location: str) ‑> bool`
:   Writes a RAMSES nml file at the output_location using the settings specified in ``settings``.
    
    **Processes:**
    
    1. Removes the meta key from the settings.
    2. Converts the memory type to the correct form.
    3. Removes disabled keys
    4. Removes software non compatible headers.
    5. Manages the initial condition file's location.
    
    
    :param settings: The settings
    :param output_location: The output location
    :return: True if pass, Fail if not.

    
`write_slurm_file(command_string, slurm_config=None, name=None, **kwargs)`
:   Writes a ``.slurm`` file corresponding to the provided ``command_string``.
    
    Parameters
    ----------
    command_string : str
        The command string to run from. This should be a string representation of one of the ``.template`` files at
        ``/bin/lib/templates`` or can be hand built. These should be ``csh`` files with ``%(option)s`` inserts for
        string formatting.
    
        ..info::
            The options left in the ``.template`` file or string must correspond to key-words in ``kwargs``.
    
    slurm_config : dict
        The ``slurm_config`` option should specify the settings corresponding to the ``slurm_settings``. If ``None``, then
        the ``slurm_config`` will be obtained from the user.
    name : str
        The name of the ``.slurm`` file.
    
    kwargs :
        additional entry options to be passed through the ``command_string``.
    
    Returns
    -------
    None