"""
User Defined plotting mechanisms.
"""
import logging
import pathlib as pt
import os
import sys
import warnings
sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[2]))
import yt

from PyHPC.PyHPC_Core.configuration import read_config
import yaml
import matplotlib.pyplot as plt

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


def projection_plot(path, field, **kwargs):
    """
    Produces a ``yt.ProjectionPlot`` of the dataset in question.

    Parameters
    ----------
    path: str
        The path to the output file to read into ``yt``.
    field: tuple of str
        The field to use in the projection.
    **kwargs:
        Available ``kwarg`` sections:
        - ProjectionPlot: ``kwargs`` to be passed directly to the ProjectionPlot.


    Returns
    -------
    None

    Examples
    --------
    >>> figure = plt.figure()
    >>> projection_plot(os.path.join(pt.Path(__file__).parents[2],"tests","test_core","output_00001"),
    ...                ("gas","density"),
    ...                main={"axis":"z"},special={
    ...                                           "figure":figure})
    >>> pt.Path(os.path.join(pt.Path(__file__).parents[2],"tests","outputs")).mkdir(parents=True,exist_ok=True)
    >>> figure.savefig(os.path.join(pt.Path(__file__).parents[2],"tests","outputs","projection_plot_ex1.png"))

    """
    #  Logging and Debugging.
    # ----------------------------------------------------------------------------------------------------------------- #
    modlog.debug("Generating projection_plot of %s with field %s."%(path,field))
    ds = yt.load(path)

    #  building kwargs
    # ----------------------------------------------------------------------------------------------------------------- #
    kwargs = {
        k:(kwargs[k] if k in kwargs else {}) for k in _mdir["Functions"]["uplots.projection_plot"]["kwargs"]
    }
    #  Creating the projection plot
    # ----------------------------------------------------------------------------------------------------------------- #
    px = yt.ProjectionPlot(ds,kwargs["main"]["axis"],field)

    if "cmap" in kwargs["style"]:
        px.set_cmap(field,kwargs["style"]["cmap"])


    for annotation,info in kwargs["annotations"].items():
        if info["enabled"]:
            getattr(px,info["command"])(*info["args"],**info["kwargs"])

    #  Moving the object to the correct axes object.
    # ----------------------------------------------------------------------------------------------------------------- #
    plot = px.plots[field]
    plot.figure = kwargs["special"]["figure"]
    plot.axes = kwargs["special"]["figure"].add_subplot(111)
    px.render()

if __name__ == '__main__':
    figure = plt.figure()

    projection_plot(os.path.join(pt.Path(__file__).parents[2],"tests","test_core","output_00001"),
                    ("gas","density"),
                    main={"axis":"z"},special={
                                               "figure":figure})

    plt.show()