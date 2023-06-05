Module PyHPC.PyHPC_System.simulation_management
===============================================
Simulation management tools for the PyHPC system. The core object ``SimulationLog`` is used by the backend to
store and manage simulations throughout the generation pipeline.

Functions
---------

    
`check_dictionary_structure(master: dict, base: dict) ‑> bool`
:   checks the dictionary structure of ``base`` against the ``master`` copy and returns ``True`` if the structure
    matches and ``False`` if the structure fails to correctly match.
    
    Parameters
    ----------
    master: dict
        The master dictionary containing the structure. The structure is checked as follows:
    
        1. For each ``key:value`` pair in the dictionary
            - If ``value`` is an <u>empty</u> ``dict``, then ``key`` must be in ``base``, but no further checks are made.
            - If ``value`` is <u>non-empty</u>, then the algorithm proceeds recursively to each ``key:value`` pair.
            - If ``value`` is a ``str``, then ``value`` should represent a ``type`` and is checked against the type.
    
    base: dict
        The base dictionary to check against the master dictionary.
    
    Returns
    -------
    value : bool
        The output value of the check. If ``True``, the structures match.

Classes
-------

`InitCon(name: str, raw: dict, parent=None)`
:   The ``InitCon`` object is a container for an initial condition file (typically a ``.dat`` or ``.g2`` file). These form
    the individual sub-units of the ``SimulationLog`` object and can be accessed using the ``SimulationLog.ics`` method.
    
    ---
    
    **Formatting**:
    
    ```json
    '<initial_condition_file_path>': {
        "information": "<user input information>",
        "meta": {
          "dateCreated": "",
          "lastEdited": "",
          "<further meta data>": ""
        },
        "simulations": {
          "<simulation 1>": {
            "keys": "values"
          }
        },
        "core": {
        }
      }
    ```

    ### Instance variables

    `core`
    :   ``self.core``  contains all of the core information for this entry.

    `inf`
    :   ``self.inf`` contains all of the description information for this entry.

    `meta`
    :   ``self.meta`` contains all of the meta information for this entry.

    `name`
    :   ``self.name`` contains the key value of the entry in the ``SimulationLog`` object.

    `parent`
    :   ``self.parent`` is a reference to the parent object.

    `raw`
    :   ``self.raw`` is the core information in the ``InitCon`` object.

    `sims`
    :   ``self.sims`` contains all of the ``SimRec`` objects in the simulation.

    ### Methods

    `add(self, entries, auto_save=True, force=False)`
    :   adds the entry contained in ``**kwargs`` to the ``InitCon`` object. The ``entries`` may contain any number
        of individual (<u>correctly formatted</u>) entries to add.
        
        Parameters
        ----------
        auto_save : bool
            ``auto_save=True`` will immediately write the simulation log to file once alterations are made.
        entries : dict
            The entries to add to the ``InitCon``. Each entry should have the standard format:
        
            ```
             "format": {
              "information": "str",
              "action_log": {
              },
              "meta": {
              },
              "core": {
              },
              "outputs": {
              }
            }
            ```
        force : bool
            Forces the Simulation log to accommodate the structure used regardless of if it meets the standard format
            ..warning:: This could have catastrophic consequences and should be used only if sure of the result.
        
        Returns
        -------
        None

    `save(self)`
    :

    `to_html(self, output)`
    :   Writes the init_log to a system of ``html`` files at the ``output`` location.
        
        Parameters
        ----------
        output: The ``path`` to the output directory.
        
        Returns
        -------
        None

`SimRec(name, data, parent=None)`
:   The ``SimRec`` class contains all of the information for a single simulation record in the ``SimulationLog`` system.
    This is the most granular view available in the ``SimulationLog`` hierarchy.
    
    **Formatting**:
    
    ---
    ```
    {
        "simulations": {
            "<.nml file (or equivalent for other software>": {
              "information": "Filled by the user to record important simulation notes.",
              "action_log": {
                "action": "information"
              },
              "meta": {
              },
              "core": {
              },
              "outputs": {
              }
            }
        }
    }
    ```

    ### Instance variables

    `core`
    :   ``self.core``  contains all of the core information for this entry.

    `inf`
    :   ``self.inf`` contains all of the description information for this entry.

    `meta`
    :   ``self.meta`` contains all of the meta information for this entry.

    `name`
    :   ``self.name`` contains the <u>absolute path</u> to the ``.nml`` file or equivalent init file for runtime use.

    `outputs`
    :   ``self.outputs`` Contains all of the outputs for the ``SimRec`` object.

    `parent`
    :   ``self.parent`` is a reference to the parent object.

    `raw`
    :   ``self.raw`` contains all of the raw data provided in the ``SimRec`` object.

    ### Methods

    `log(self, message, action, auto_save=True, **kwargs)`
    :   logs the ``message`` to the ``self.raw.action_log``. Additional entries in the record are specified with ``**kwargs``.
        
        Parameters
        ----------
        message : str
            The message to log with the entry.
        action : str
            The specific action being under-taken. These actions can be arbitrary, but should be consistent for
            best impact.
        auto_save : bool
            ``True`` to automatically write all of the data to file.
        kwargs : optional
            Additional attributes to log with the message. All entries should be ``key="string"``. If entries overlap
            with required log elements ``[msg,lineno,file,act,time]``, then they are overridden by the values given.
        
        Returns
        -------
        None

    `save(self)`
    :

`SimulationLog(path=None)`
:   ``SimulationLog`` class to manage the simulations stored on the drive.
    
    :param path: The filepath at which to locate the simulation log file (``.json``)
    
    ---
    
    ## Formatting ``SimulationLog`` Objects
    
    The purpose of the simulation logging module is to keep track of active simulations in the research
    stream in as seamless a way as possible. The following are of core importance for use of the system
    
    - The <b>root</b> of any entry in the simulation log is the <u>initial condition file</u>
        - The intention here is that for any given physical setup, there may be many simulations
          of interest which need to all be tracked and which may have different ``.nml`` and ``.slurm`` files.
    - The simulation log pertinent to your installation is located at ``/bin/simLog.json`` and prescribes to <u>all</u> of
      the formatting restrictions of ``.json`` type files.
    
    ## Formatting
    
    The format of a single entry is as follows:
    
    ```json
    {
      '<initial_condition_file_path>': {
        "information": "<user input information>",
        "meta": {
          "dateCreated": "",
          "lastEdited": "",
          "<further meta data>": ""
        },
        "simulations": {
          "<simulation 1>": {
            "keys": "values"
          }
        },
        "core": {
        }
      }
    }
    ```
    
    meta data can be added to the entry as needed as the system <u>never enforces a key list</u>. If the user is
    benefitted by adding additional information, then they may do so without issue. There are a few required pieces
    of information required for every entry:
    
    ```json
    {
      "<initial_condition_file_path>": {
        "information": "(Can be blank, but must be present)",
        "meta": {
          "dateCreated": "the timestap for creation",
          "software": "the software used to generate the .nml file"
        },
        "simulations": {
        },
        "core": {
          "npart": {
            "dm": "---",
            "gas": "---"
          }
        }
      }
    }
    ```
    
    The user <b>must specify: ``information``,``meta``,``simulations``,and``core``</b>.
    
    ## Simulations
    
    Simulations are logged as subsets of the ``initial_condition_file`` objects in the database. This means that they hold a
    format
    of there own. Like the initial conditions, the <b>root</b> of any ``simulation`` in the log is the ``.nml`` file. The
    simulation takes the
    following format
    
    ```json
    {
      "simulations": {
        "<.nml file (or equivalent for other software>": {
          "information": "Filled by the user to record important simulation notes.",
          "action_log": {
            "action": "information"
          },
          "meta": {
          },
          "core": {
          },
          "outputs": {
          }
        }
      }
    }
    ```
    
    Again, there is no hard enforcement of the format. There are a few required keys for adding a simulation; an example of
    a very basic simulation
    being added to the simulation log might look like
    
    ```json
    {
      "simulations": {
        "example.nml": {
          "information": "A dummy simulation for use as an example.",
          "action_log": {
          },
          "meta": {
            "fileCreated": "01-01-1000"
          },
          "core": {
          },
          "outputs": {
          }
        }
      }
    }
    ```

    ### Instance variables

    `ics: dict`
    :   Contains the dictionary of ``InitCon`` objects to use during execution.
        
        Returns
        -------
        val : ``dict``
            The dictionary of ``InitCon`` objects.

    ### Methods

    `add(self, entries, auto_save=True, force=False)`
    :   adds the entry contained in ``**kwargs`` to the ``SimulationLog`` object. The ``entries`` may contain any number
        of individual (<u>correctly formatted</u>) entries to add.
        
        Parameters
        ----------
        auto_save : bool
            ``auto_save=True`` will immediately write the simulation log to file once alterations are made.
        entries : dict
            The entries to add to the ``SimulationLog``. Each entry should have the standard format:
        
            ```
            {
              '<initial_condition_file_path>': {
                "information": "<user input information>",
                "meta": {
                  "dateCreated": "",
                  "lastEdited": "",
                  "<further meta data>": ""
                },
                "simulations": {
                  "<simulation 1>": {
                    "keys": "values"
                  }
                },
                "core": {
                }
              }
            }
            ```
        force : bool
            Forces the Simulation log to accommodate the structure used regardless of if it meets the standard format
            ..warning:: This could have catastrophic consequences and should be used only if sure of the result.
        
        Returns
        -------
        None

    `get_simulation_records(self) ‑> dict`
    :   Fetches all of the ``SimRec`` objects in the ``SimulationLog``.
        
        Returns
        -------
        dict
            Dictionary of all of the ``SimRec`` objects in the format ``{name:SimRec}``.

    `save(self)`
    :   Saves the current simulation log.
        
        Returns
        -------
        None

    `search(self, search_kwargs: dict, search_for: str = 'sim', return_by: str = 'sim') ‑> list`
    :   Searches the ``SimulationLog`` object for entries with data matching those stated in the ``search_kwargs``.
        The ``search_for`` and ``return_by`` parameters can be used to control the granularity of the search.
        
        Parameters
        ----------
        search_kwargs : ``dict``
            The ``kwargs`` to use for the search. Should be a set of ``{k:v,...}``.
            All objects matching the level of granularity specified by ``search_for`` will be queried to see if ``obj.raw`` includes the given kwargs.
            If the ``kwargs`` dictionary has ``list`` type entries, the search will be done based on an ``OR`` boolean search approach.
            Individual entries in the ``kwargs`` are searched based on ``AND`` booleans.
        search_for : ``str``
            The level of granularity to use in the search. can be ``sim`` or ``ic``.
        return_by : ``str``
            The level of granularity to return by. Can be ``sim`` or ``ic``.
        
        Returns
        -------
        Returns a list of matching objects.

    `to_html(self, output)`
    :   Writes the simulation log to a system of ``html`` files at the ``output`` location.
        
        .. warning::
            Incomplete
        
        .. todo::
            Finish this.
        Parameters
        ----------
        output: The ``path`` to the output directory.
        
        Returns
        -------
        None