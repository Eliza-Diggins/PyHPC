"""
==============================
Producing Images in ``PyHPC``
==============================
The ``PyHPC`` system uses the ``yt`` project as its backbone for analysis, and therefore plots through ``yt`` as well.
There are several included plotting systems for various purposes and a catch-all strategy for batches of plots that need
to be generated. In some advanced cases, ``yt`` may need to be used in isolation or in conjunction with ``PyHPC`` because
automated systems are insufficient to meet the user's need.

Automated Plotting
------------------
Because plotting is so important to the analysis system, but is rather tedious, especially on ``CHPC``, we have included
a system for generating relatively simple plots for what are called ``pdirectives``. A ``pdirective`` is a file with
extension ``.pd``, which contains instructions on how the system should plot a given set of data. These can then
be read by ``PyHPC`` and be used either as an animation task or as a single plot.

Pdirectives
^^^^^^^^^^^
the ``.pd`` files should be formatted as follows:

.. code-block:: yaml

    information: |
        This is never read and can include any important information about the plot.

    #Figure is the core of the Pdirective and contains all of the data
    #corresponding to the intended figure including its subplots.

    Figure:
        grid:
            # The grid can be used to specify the gridspec layout desired.
            - [1,1,2,2]
            - [1,1,2,2]
        Subplots:

        #Subplots are the most important part of the Pdirective. Each one
        #contains the function headers that correspond to the necessary functions
        #to actually produce the visual.
        # !Subplots are indexed by number!
        # ! Each subplot must have "Functions" and "Parameters".
        #
            1:
                Functions:
                    # Each function in Function should be named by its correct reference (in the code). To use
                    # yt.ProjectionPlot, you title it yt.ProjectionPlot as the key in the entry.
                    #
                    #    ! If you need to re-use a function in a SINGLE subplot, label it (N)function
                    #    ! where N is the index.
                    #
                    # Each function specified must have entries: args and kwargs. These must correspond to those
                    # recognized in the program itself. See the section below on ease of use for more detailed
                    # information on this.
                    #
                    function1:
                        args: ["x","y","z"]
                        kwargs:
                            "color": "red"
                    function2:
                        args: [":ds",":f"]
                        kwargs:
                            "cmap":"Blues"
                Parameters:
                    # The Parameters are those things which we wish to constrain about the subplot object itself.
                    # Each Parameter must have a command ".something()", its args, and its kwargs. These are
                    # run after each other plotting procedure has been finished and are done in order.
                    .set_xlim:
                        args: [[0,1]]
                        kwargs: {}
            2:
                Functions:
                    function1:
                        args: ["x","y","z"]
                        kwargs:
                            "color": "red"
                Parameters: {}
        Parameters:
            # These parameters are the same as those described above for subplots; however, this time they apply
            # specifically to the figure object instead.
            .set_size_inches:
                args: [[10,10]]
                kwargs: {}
    PostProcessing:
        # The post processing part of the directive can be excluded if unwanted. With this, you can change the default
        # behavior after execution. There are two settings: post process, which is a pure python script to be executed
        # after the course of the computation is completed.
        #
        # !! WARNING: this uses the exec() function. Because there are no security threats, this fault will be
        #             permitted to persist; however, user idiocy could lead to unintended consequences for the
        #              system.
        #
        # The second option in post processing is the output field, which can specify a save location for the finished
        # plot.
        #
        output: None
        script: |
            pass

Advanced User Settings
^^^^^^^^^^^^^^^^^^^^^^
There are a few further details to describe in the ``pdirective`` system. The foremost of these is the use of wildcards.

- A ``wildcard`` variable in a ``.pd`` file is an ``arg, kwarg`` for a function which is denoted ``%{name}%``. When these
  are placed in a ``.pd`` file, the pre-processor will automatically seek out the corresponding ``name`` kwarg in the
  function producing the plot and filter that data in. This is most useful for filtering in the data you wish to plot.
- What if I want to add a colorbar or other secondary structure?
    This is intended as a simple / user-friendly plotting system; however, in ``PyHPC``, any plotting systems will only
    return the corresponding ``PlotDirective``, which can be manipulated further by direct interaction with ``matplotlib``.
- If the system includes argument sorting, look at the documentation below for instruction.

Defaults
^^^^^^^^
The intention behind the ``PlotDirective`` construct is not to allow the user to interact easily with simple functions
like ``plt.plot`` or ``plt.imshow``, but instead to allow a system for interacting with **user defined** plotting systems
which may include many different components.

For example, lets say that ``foo(x,y)`` generates a complex plot which includes a colorbar and some annotations as well as
a legend. The user might not want to have to provide **all** of those ``kwargs`` to their ``pdirective`` file. This is where
the ``master_directive.pd`` file comes to the rescue. This is a special file in the ``PyHPC`` system and can be used to
generate pre-written settings for different components. The format is as follows:

.. code-block:: yaml

    Information: |
        This is the master directive for the PyHPC system (mock up)
    Functions:
        # Functions
        # ---------
        #   These are all of the implemented functions for plotting. Here, we would include an entry for foo(x,y) as
        # discussed above. In this case, the function takes only ``kwargs`` and not args, but the ``kwargs`` can
        # take on a variety of roles.
        foo:
            kwargs:
                color: "red"
                linewidth: 3
    Structures:
        # Structures
        # ----------
        # Not all of the work we want to do while plotting requires interaction with files. In some cases, we have
        # to interact with structures / objects as well. In this case, we specify the structural parameters as follows:
        #
        # 1. (args,kwargs): These are passed to a self-identified ``initialization_function``, where they may be used
        #   to generate the object of importance. Please be aware that the person writing the custom script must dictate
        #   the proper proceedure for different entry types.
        #
        # 2. commands:
        #   Include direct commands with their own ``kwargs`` and ``args`` after the loading process.
        Figure:
            args: []
            kwargs: {}
            commands: {}

In this case, **every time** the structure / function described in the ``master_directive`` is used in a ``.pd`` file,
the defaults will be auto-populated unless overridden.

.. todo::
    There should be an implementation option by which to avoid having persistent defaults if unwanted.

.. attention::
    In the case of a complex function, it is advised that included kwargs are categorized so that the endpoint function
    can easily differentiate those kwargs corresponding to different structures in the plotting system.
"""