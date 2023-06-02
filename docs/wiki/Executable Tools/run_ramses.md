# PyHPC_Executables - run_ramses.py

---

## Contents

---

### Base Information

The following help information can be accessed using the ```-h``` tag at the command line.

```commandline
+-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=+
|                                                                                                                                                        |
|                                        _/_/_/_/_/_/                 _/          _/   _/_/_/_/_/_/       _/_/_/_/_/                                     |
|                                        _/         _/                _/          _/   _/         _/    _/                                               |
|                                        _/         _/  _/      _/    _/          _/   _/         _/   _/                                                |
|                                        _/_/_/_/_/_/   _/      _/    _/_/_/_/_/_/_/   _/_/_/_/_/_/    _/                                                |
|                                        _/              _/_/_/_/     _/          _/   _/              _/                                                |
|                                        _/                  _/       _/          _/   _/               _/                                               |
|                                        _/             _/_/_/        _/          _/   _/                 _/_/_/_/_/                                     |
|                                    #-------------------------------------------------------------------------------#                                   |
|                                   Written by Eliza C. Diggins, University of Utah Department of Physics and Astronomy                                  |
|                                                                                                                                                        |
|                                                                   Version = 0.2-Alpha                                                                  |
|                                                                      #-----------#                                                                     |
|                                                                                                                                                        |
|                                                                     Stable = False                                                                     |
|                                                                     #------------#                                                                     |
|                                                                                                                                                        |
+-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=+
|                                                                                                                                                        |
|                                                                RAMSES Pipeline Software                                                                |
|                                                                                                                                                        |
+-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=-=|=+

PyHPC_executables:run_ramses: [Execution Wizard]: Beginning Execution:
PyHPC_executables:run_ramses: [Execution Wizard]: Loading command line arguments...usage: run_ramses.py [-h] [-v] [-i IC] [-n NML] [--nml_output NML_OUTPUT] [--slurm_output SLURM_OUTPUT] [-s]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Toggles verbose mode.
  -i IC, --ic IC        Tag to the initial condition file to initialize.
  -n NML, --nml NML     The nml path to use to pass the settings generation stage.
  --nml_output NML_OUTPUT
                        Use this to hard set the .nml output location.
  --slurm_output SLURM_OUTPUT
                        Use this to hard set the slurm file location.
  -s, --stop            Enable this flag to generate only the slurm file but not execute.
```