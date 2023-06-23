[![yt-project](https://img.shields.io/static/v1?label="works%20with"&message="yt"&color="blueviolet")](https://yt-project.org)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Coverage Status](https://coveralls.io/repos/github/Eliza-Diggins/PyHPC/badge.svg?branch=master)](https://coveralls.io/github/Eliza-Diggins/PyHPC?branch=master)

Welcome to PyHPC
=================
``PyHPC`` is a toolbox designed to stream line astrophysical simulations on the CHPC architecture at the University of Utah. Further information on installation, usage
and other important aspects of the program can
be found in the documentation below:

---
Quick Links
--------

<a href="https://eliza-diggins.github.io/PyHPC/_build/html/index.html">Documentation</a>

---

PyHPC Installation
=====================

The PyHPC library can be installed on any system, but is best suited for installation on
a user's local drive on the <a href="https://chpc.utah.edu">CHPC</a> arcitecture. The following guide outlines
the necessary process to install the software.

Obtaining the Source Code
-------------------------
The source code can be obtained from Github. First, select an ``installation`` directory. The ``installation``
directory can be somewhat hidden if you like as it won't contain any of your output data.

Once there, the following command will clone the repository onto your local drive.

``` commandline
>>> git clone 'http://www.github.com/Eliza-Diggins/PyHPC'
```

If the clone succeeds, you should see the source code populated in your current directory.

Installation
------------
Once the source code is obtained, setup is quite simple. From within the ``./PyHPC`` directory
of the source code, run the following command:

``` commandline
>>> python3 setup.py -l <user_directory>
```

where ``user_directory`` is the directory in which all of the datasets will be kept.
This will initialize the startup system. You may follow the prompts to successfully complete the setup process.