Module PyHPC.PyHPC_System.file_management
=========================================
Tools for remote file management using RClone or single transfer.
-- Last Check: 12/16 --

Functions
---------

    
`get_all_files(directory, top_directory=None)`
:   Finds all of the files within ``directory`` and returns as a formatted list with relative and absolute paths.
    Parameters
    ----------
    directory: the directory from which to search.
    top_directory: The directory from which to construct the relative paths.
    Returns: Returns a list of tuples [(path,rel-path,file)].
    -------

    
`get_all_remote_files(directory, top_directory=None)`
:   Grabs all of the files within the directory and returns as a list with (path, rel-path, file). [BOX]
    Parameters
    ----------
    directory: the directory from which to search.
    
    Returns: Returns a list of tuples [(path,rel-path,file)].
    -------

    
`get_item_from_rclone(location_path, move_to_unfiled=True)`
:   Downloads an item from box using rclone
    Parameters
    ----------
    location_path: The path to the correct directory.
    
    Returns: None.
    -------

    
`get_local_location(remote_path, move_to_unfiled=True)`
:   Determines the correct path to use for rclone on the box side of file transfer.
    Parameters
    ----------
    local_path: The local path on the disk.
    move_to_unfiled: If True, then we will move items without a reasonable path to an unfiled location.
    
    Returns: The correct path to copy to for that file.
    -------

    
`get_remote_location(local_path, move_to_unfiled=True)`
:   Determines the correct path to use for rclone on the box side of file transfer.
    
    Parameters
    ----------
    local_path: The local path on the disk.
    move_to_unfiled: If True, then we will move items without a reasonable path to an unfiled location.
    
    Returns: The correct path to copy to for that file.
    -------

    
`mt_get_item_from_rclone(location_path, move_to_unfiled=True)`
:   Downloads an item from box using rclone. (MULTI-Threaded)
    Parameters
    ----------
    location_path: The path to the correct directory.
    
    Returns: None.
    -------

    
`mt_send_item_to_rclone(location_path, move_to_unfiled=True)`
:   Sends the specified item to the correct rclone directory. (MULTI-Threaded)
    Parameters
    ----------
    location_path: The path to the correct directory.
    
    Returns: None.
    -------

    
`send_item_to_rclone(location_path, move_to_unfiled=True)`
:   Sends the specified item to the correct rclone directory.
    Parameters
    ----------
    location_path: The path to the correct directory.
    
    Returns: None.
    -------