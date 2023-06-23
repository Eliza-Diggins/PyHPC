=====================
PyHPC Installation
=====================

The PyHPC linbrary can be installed on any system, but is best suited for installation on
a user's local drive on the `CHPC System <https://chpc.utah.edu/>`_. The following guide outlines
the necessary process to install the software.

Obtaining the Source Code
-------------------------
The source code can be obtained from Github. First, select an ``installation`` directory. The ``installation``
directory can be somewhat hidden if you like as it won't contain any of your output data.

Once there, the following command will clone the repository onto your local drive.

>>> git clone 'http://www.github.com/Eliza-Diggins/PyHPC'

If the clone succeeds, you should see the source code populated in your current directory.

Installation
------------
Once the source code is obtained, setup is quite simple. From within the ``./PyHPC`` directory
of the source code, run the following command:

>>> python3 setup.py -l <user_directory>

where ``user_directory`` is the directory in which all of the datasets will be kept.
This will initialize the startup system. You may follow the prompts to successfully complete the setup process.

=========================
PyHPC Basic Configuration
=========================
Once ``PyHPC`` is  installed, there are some significant configuration related issues that need to be managed before
you can fully take advantage of the pipeline and its various options. To modify the configuration files, navigate to
``<user_directory>/bin/configs``. There are several files here, generally speaking, each one controls the default execution behavior
of the software it is named after. The ``Simlog.json`` file is a simulation log file, which you can read more about
in the documentation on project management. At this stage, the most important file is ``CONFIG.CONFIG``, which should
look something like this:

.. include