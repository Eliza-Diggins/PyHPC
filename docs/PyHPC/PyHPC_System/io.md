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

    
`write_slurm_file(command_string, slurm_config=None, name=None)`
:   Writes the ``command_string`` to a SLURM compatible form using the ``slurm_config``
    :param command_string: The command string to add as the executable section of the .slurm file.
    :param slurm_config: the configuration dictionary for slurm. Defaults to calling for a select settings dialog.
    :param name: The name to give to the slurm executable.
    :return: None