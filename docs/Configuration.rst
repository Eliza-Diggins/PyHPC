================
Configuration
================
The configuration settings for the ``PyHPC`` project are somewhat complex.
The following are the core configuration files to be aware of.

System Config
-------------
The system configuration file is found at the user-install directory ``/bin/configs/CONFIG.config``.

.. include:: ../PyHPC/bin/inst/cnfg/install_CONFIG.config
    :code:

RAMSES Config
-------------
These settings are focused on managing the RAMSES runtime environment.

.. include:: ../PyHPC/bin/inst/cnfg/install_RAMSES.config
    :code:

CLUSTEP Config
-------------
These settings are focused on managing the CLUSTEP runtime environment.

.. include:: ../PyHPC/bin/inst/cnfg/install_CLUSTEP.config
    :code:

BATCH Config
-------------
These settings manage the system's interactions with SLURM.

.. include:: ../PyHPC/bin/inst/cnfg/install_SLURM.config
    :code: