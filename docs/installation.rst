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

>>> python3 setup.py

This will initialize the startup system. You may follow the prompts to successfully complete the setup process.