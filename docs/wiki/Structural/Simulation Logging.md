# Simulation Logging

---

## Introduction

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