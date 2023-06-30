"""
==============================
Producing Images in ``PyHPC``
==============================
In the ``PyHPC`` system, you can generate any of a variety of plots of various types. This is done through what is called
a ``plotting_directive``, which is formatted ``json`` indicating to the computer exactly what you want to have plotted.

How It Works
------------
The ``generate_image`` function is the core function in this library. To it, one **must** pass 2 things:

1. The ``plotting_directive``
2. The opened dataset ``ds``.

Additionally, the keyword ``axis`` can be specified to place the plot automatically in a given axis. This
can also be done manually later.

Plotting Directives
^^^^^^^^^^^^^^^^^^^
The Plotting directive is a ``json`` style file / dictionary containing the execution data for given plotting function. The format is as follows:

.. code-block:: yaml

    information: &info |
      This file is an example file.
    gridspec: &gridspec
      - [1,1,2,2]
      - [1,1,2,2]
    functions: &functions
      plt.plot: &plt-plot
        axis: 1
        args: &plt-plot_args
          - :x
          - :y
        kwargs: &plt-plot_kwargs
          color: red
          linewidth: 3
        inherits:

structures: &structures

The first section of the ``plotting_directive`` specifies the gridspec layout. This can generally be overridden (see the documentation for
individual plotting routines), and so is not always necessary. The second part is used to specify the functions to use in the plotting.
``args`` and ``kwargs`` are to be passed by name and will be associated with the correct / necessary plotting functions as specified.

The Master Directive
^^^^^^^^^^^^^^^^^^^^
The ``master directive`` is the file off of which all plotting execution is based. it specifies the allowed combinations of
``kwargs`` and ``args`` which allow for execution of the script to occur. The master directive is included here as a guide for
the available plotting options:

.. include:: ../../PyHPC/bin/lib/img/master_directive.yaml
    :code: yaml

Under the hood, the functionality is relatively simple. Every plot that can be made has an entry in ``functions``. The
entry key can be used to call the function. The ``args`` list contains (in order) the arguments that have to be provided to
said function. Those values in ``<?>`` are special characters indicating that we are plotting specific aspects of the
data provided. In the case of a ``yt`` style plotting system, we would have ``args: ["<ds>","field"]``, which would
then force the user to specify the ``field`` in their directive.

.. attention::
    If a ``arg`` is not specified in the ``plotting_directive`` but doesn't have any special markers, then
    the execution will fail because of the lack of a required value. On the other hand, one need not typically specify
    those values ``<?>`` which are special as they should be inferred from context.

Once the ``args`` have been specified, the ``kwargs`` are also contained in ``kwargs``. These can be overridden by inclusion
in the ``plotting_directive``; however, the execution will fail if an undocumented ``kwarg`` is passed.

.. attention::
    (**Managing Defaults**) Defaults can be managed a number of ways in the ``master_directive``.

    1. The simplest way is to simply include the ``default`` tag in the ``kwarg`` dictionary and specify the value by hand.
    2. If you want to link the default to the config, you need to use ``<key>:"CONFIG:path,to,value"``.
    3. If ``default`` is not specified, then the ``kwarg`` is, by default, simply occluded from the execution.
Finally, the ``structure`` section of the ``master_directive`` is used to specify additional structures which might
be added to the plot. This might include a ``legend`` or ``colorbar``. In cases where these need not always be
present (such as for ``legend`` and ``colorbar``), the first ``kwarg`` (``enabled``) is used to specify whether or not
to include that object in the final plot.
"""
import json
import os
import pathlib as pt
import sys
import warnings

from PyHPC.PyHPC_Core.configuration import read_config
import logging

# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
# ------------------------------------------------------ Setup ----------------------------------------------------------#
# --|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--#
_location = "PyHPC_Visualization"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = logging.getLogger(__name__)

# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')

# -------------------------------------------------------------------------------------------------------------------- #
#  Functions ========================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #

def generate_image(image_directive):
    """
    sdfsdf
    Parameters
    ----------
    image_directive

    Returns
    -------

    """
    pass
