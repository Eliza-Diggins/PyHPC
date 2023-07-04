"""
User Defined plotting mechanisms.
"""
# -------------------------------------------------------------------------------------------------------------------- #
# Functions ========================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
import matplotlib.pyplot as plt

def plot(x,y,**kwargs):
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
    return kwargs["axes"].plot(x,y,**kwargs)