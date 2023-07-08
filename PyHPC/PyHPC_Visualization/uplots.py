"""
User Defined plotting mechanisms.
"""
import logging
import os
import pathlib as pt
import sys
import warnings
import numpy as np
sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[2]))
import yt
from itertools import cycle, islice
from PyHPC.PyHPC_Core.configuration import read_config
import yaml
import matplotlib.pyplot as plt
from PyHPC.PyHPC_Visualization.utils import assert_kwargs,build_transfer_function
import inspect
from mpl_toolkits.axes_grid1 import AxesGrid

_location = "PyHPC_Visualization"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = logging.getLogger(__name__)

# - managing warnings -#
if not CONFIG["System"]["Logging"]["warnings"]:
    warnings.filterwarnings('ignore')
with open(os.path.join(pt.Path(__file__).parents[1], "bin", "lib", "img", "master_directive.yaml")) as file:
    _mdir = yaml.load(file, yaml.FullLoader)


# -------------------------------------------------------------------------------------------------------------------- #
# Functions ========================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
def plot(x, y, **kwargs):
    """
    Standard wrapper for ``plt.plot``.

    Parameters
    ----------
    x: np.ndarray
        The ``x`` coordinates.
    y: np.ndarray
        The ``y`` coordinates.
    **kwargs:
        parameters for the ``plt.plot`` function. (See the `documentation <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html>`_).

    Returns
    -------
    list of plt.Line2D
        The resulting plots.

    """
    if len(kwargs["special"]["figure"].get_axes()):
        ax = kwargs["special"]["figure"].get_axes()[0]
    else:
        ax = kwargs["special"]["figure"].add_subplot(111)

    return ax.plot(x, y, **kwargs["main"])


def projection_plot(path, axis, field,geo, **kwargs):
    """
    Produces a ``yt.ProjectionPlot`` of the dataset in question.

    Parameters
    ----------
    path: str
        The path to the output file to read into ``yt``.
    axis: str or list of float
        The axis along which to project.
    field: tuple of str
        The field to use in the projection.
    geo: tuple
        The geometry of the output plot.
    **kwargs:
        Available ``kwarg`` sections:
        - ProjectionPlot: ``kwargs`` to be passed directly to the ProjectionPlot.


    Returns
    -------
    None

    Examples
    --------
    >>> figure = plt.figure()
    >>> projection_plot(os.path.join(pt.Path(__file__).parents[2],"tests","test_core","output_00001"),"z",
    ...                [("gas","density"),("gas","temperature")],(2,1),
    ...                main={},special={"figure":figure})
    >>> pt.Path(os.path.join(pt.Path(__file__).parents[2],"tests","outputs")).mkdir(parents=True,exist_ok=True)
    >>> figure.savefig(os.path.join(pt.Path(__file__).parents[2],"tests","outputs","projection_plot_ex1.png"))

    """
    #  Logging and Debugging.
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Generating projection_plot of %s with field %s." % (path, field))
    kwargs = assert_kwargs("uplots." + inspect.stack()[0][3], kwargs)
    modlog.debug(kwargs)

    #  Loading the dataset from yt loader
    # ----------------------------------------------------------------------------------------------------------------- #
    ds = yt.load(path, *kwargs["yt_ds"]["args"], **kwargs["yt_ds"]["kwargs"])

    # Loading the commands being passed through.
    for command, values in kwargs["yt_ds"]["commands"].items():
        try:
            getattr(ds, command)(*values["args"], **values["kwargs"])
        except AttributeError:
            modlog.exception("Failed to find command %s for yt data object." % command)

    #  Creating the projection plot
    # ----------------------------------------------------------------------------------------------------------------- #
    px = yt.ProjectionPlot(ds, axis, field, **{k: v for k, v in kwargs["main"].items() if v is not None})

    #  methods
    # ----------------------------------------------------------------------------------------------------------------- #
    # We are now going to adjust our approach. If we have more than one field, each method needs to be applied several
    # times.
    #
    # - sanitizing - #
    if isinstance(field, tuple):  # The field is only of length 1.
        field = [field]
    else:
        pass

    for field_id, minor_field in enumerate(field):  # Iterate through all of the available fields
        for method, values in kwargs["commands"].items():
            # - Checking if we are actually using the given plot -#
            if list(islice(cycle(values["use"]), len(field)))[field_id]:
                try:
                    getattr(px, method)(minor_field,*[i[field_id] for i in values["args"]],
                                        **{k: v[field_id] for k, v in values["kwargs"].items()})
                except IndexError:
                    modlog.warning(
                        f"Failed to implement {method} because the args / kwargs did not have correct length / format.")
            else:
                pass

    for annotation, info in kwargs["annotations"].items():
        if info["enabled"]:
            getattr(px, info["command"])(*info["args"], **info["kwargs"])

    #- Enforcing style ------------------------------------------------- #
    for field_id,minor_field in enumerate(field):
        px.set_cmap(minor_field,list(islice(cycle(kwargs["style"]["cmaps"]),len(field)))[field_id])
        px.set_background_color(minor_field,list(islice(cycle(kwargs["style"]["background_colors"]),len(field)))[field_id])

    #  Moving the object to the correct axes object.
    # ----------------------------------------------------------------------------------------------------------------- #
    grid = AxesGrid(
        kwargs["special"]["figure"],
        *kwargs["grid"]["args"],
        nrows_ncols=geo,
        **kwargs["grid"]["kwargs"])

    for i, f in enumerate(field):
        plot = px.plots[f]
        plot.figure = kwargs["special"]["figure"]
        plot.axes = grid[i].axes
        plot.cax = grid.cbar_axes[i]
    px.render()



def slice_plot(path, axis, field,geo, **kwargs):
    """
    Produces a ``yt.SlicePlot`` of the dataset in question.

    Parameters
    ----------
    path: str
        The path to the output file to read into ``yt``.
    axis: str or list of float
        The axis along which to project.
    field: tuple of str
        The field to use in the projection.
    geo: tuple
        The geometry of the output plot.
    **kwargs:
        Available ``kwarg`` sections:
        - ProjectionPlot: ``kwargs`` to be passed directly to the ProjectionPlot.


    Returns
    -------
    None

    Examples
    --------
    >>> figure = plt.figure()
    >>> slice_plot(os.path.join(pt.Path(__file__).parents[2],"tests","test_core","output_00001"),"z",
    ...                [("gas","density"),("gas","temperature")],(2,1),
    ...                main={},special={"figure":figure})
    >>> pt.Path(os.path.join(pt.Path(__file__).parents[2],"tests","outputs")).mkdir(parents=True,exist_ok=True)
    >>> figure.savefig(os.path.join(pt.Path(__file__).parents[2],"tests","outputs","slice_plot_ex1.png"))

    """
    #  Logging and Debugging.
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Generating projection_plot of %s with field %s." % (path, field))
    kwargs = assert_kwargs("uplots." + inspect.stack()[0][3], kwargs)
    modlog.debug(kwargs)

    #  Loading the dataset from yt loader
    # ----------------------------------------------------------------------------------------------------------------- #
    ds = yt.load(path, *kwargs["yt_ds"]["args"], **kwargs["yt_ds"]["kwargs"])

    # Loading the commands being passed through.
    for command, values in kwargs["yt_ds"]["commands"].items():
        try:
            getattr(ds, command)(*values["args"], **values["kwargs"])
        except AttributeError:
            modlog.exception("Failed to find command %s for yt data object." % command)

    #  Creating the projection plot
    # ----------------------------------------------------------------------------------------------------------------- #
    px = yt.SlicePlot(ds, axis, field, **{k: v for k, v in kwargs["main"].items() if v is not None})

    #  methods
    # ----------------------------------------------------------------------------------------------------------------- #
    # We are now going to adjust our approach. If we have more than one field, each method needs to be applied several
    # times.
    #
    # - sanitizing - #
    if isinstance(field, tuple):  # The field is only of length 1.
        field = [field]
    else:
        pass

    for field_id, minor_field in enumerate(field):  # Iterate through all of the available fields
        for method, values in kwargs["commands"].items():
            # - Checking if we are actually using the given plot -#
            if list(islice(cycle(values["use"]), len(field)))[field_id]:
                try:
                    getattr(px, method)(minor_field,*[i[field_id] for i in values["args"]],
                                        **{k: v[field_id] for k, v in values["kwargs"].items()})
                except IndexError:
                    modlog.warning(
                        f"Failed to implement {method} because the args / kwargs did not have correct length / format.")
            else:
                pass

    for annotation, info in kwargs["annotations"].items():
        if info["enabled"]:
            getattr(px, info["command"])(*info["args"], **info["kwargs"])

    #- Enforcing style ------------------------------------------------- #
    for field_id,minor_field in enumerate(field):
        px.set_cmap(minor_field,list(islice(cycle(kwargs["style"]["cmaps"]),len(field)))[field_id])
        px.set_background_color(minor_field,list(islice(cycle(kwargs["style"]["background_colors"]),len(field)))[field_id])

    #  Moving the object to the correct axes object.
    # ----------------------------------------------------------------------------------------------------------------- #
    grid = AxesGrid(
        kwargs["special"]["figure"],
        *kwargs["grid"]["args"],
        nrows_ncols=geo,
        **kwargs["grid"]["kwargs"])

    for i, f in enumerate(field):
        plot = px.plots[f]
        plot.figure = kwargs["special"]["figure"]
        plot.axes = grid[i].axes
        plot.cax = grid.cbar_axes[i]
    px.render()

def volume_render(path,field,**kwargs):
    modlog.debug("Generating projection_plot of %s with field." % (path))
    kwargs = assert_kwargs("uplots." + inspect.stack()[0][3], kwargs)
    modlog.debug(kwargs)

    #  Loading the dataset from yt loader
    # ----------------------------------------------------------------------------------------------------------------- #
    ds = yt.load(path, *kwargs["yt_ds"]["args"], **kwargs["yt_ds"]["kwargs"])

    # Loading the commands being passed through.
    for command, values in kwargs["yt_ds"]["commands"].items():
        try:
            getattr(ds, command)(*values["args"], **values["kwargs"])
        except AttributeError:
            modlog.exception("Failed to find command %s for yt data object." % command)

    #  generating the scene
    # ----------------------------------------------------------------------------------------------------------------- #
    sc = yt.create_scene(ds,lens_type=kwargs["camera"]["kwargs"]["lens"],profile_field=field)

    #  Managing Sources
    # ----------------------------------------------------------------------------------------------------------------- #
    source = sc[0]

    source.tfh.tf = build_transfer_function(kwargs["transfer_function"])
    source.tfh.grey_opacity = False

    return sc


if __name__ == '__main__':
    volume_render(os.path.join(pt.Path(__file__).parents[2],"tests","test_core","output_00001"))
