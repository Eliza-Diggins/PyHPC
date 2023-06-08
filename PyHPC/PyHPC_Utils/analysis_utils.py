"""
Analysis utilities for use in various mathematical / analytic situations throughout the ``PyHPC`` framework.

..author::
    Eliza Diggins
"""
import numpy as np


def recenter(positions, masses):
    r"""
    Recenters the list of positions on the correct sequence of locations.


    **Theory**:

    Consider a set of systems with positions \(\textbf{x}_0,\dots,\textbf{x}_n\) and each system must be located in
    order relative to the COM. The first system \(S_0\) is centered at \((0,0,0)\) to start. This is reasonable because
    we end up centered on COM anyways. Thus
    <ul>
    <li> $$\textbf{x}_0 \to 0 $$</li>
    <li> \(\textbf{x}_1 \to \textbf{x}_1 \) because \(\textbf{R} = 0 \).
    </ul>

    From here on out, things begin to change: each position needs to be written relative to the COM of the state
    prior. As such, letting \(\textbf{x}_0 = \textbf{0}\), then relative to the \(j\)th COM, the positions of the particles
    are

    $$ \textbf{x}^j_i = \textbf{x}^0_i - \sum_{k=1}^{j-1} \frac{\sum_{l=0}^k \textbf{x}_l^k m_l}{\sum_{l=0}^k m_l} $$




    Parameters
    ----------
    positions : list of list
        The positions ``[x,y,z]`` of each of the systems in the simulation.

    Returns
    -------
    np.ndarray
        The positions relative to the COM of the previous set of particles.

    """
    # - Centering -#

    positions = np.array([np.array(position) - np.array(positions[0]) for position in positions]).transpose()
    positions_movable = positions.copy()

    masses = np.array(masses).ravel()
    coms = np.zeros(positions.shape)

    for column in range(1, coms.shape[1]):
        coms[:, column] = np.matmul(positions_movable[:, :column], masses[:column].transpose()) / np.sum(
            masses[:column])
        positions_movable = positions_movable - np.hstack(
            tuple([coms[:, column].reshape((3, 1)) for i in range(coms.shape[1])]))
        positions[:, column] = positions_movable[:, column]

    return positions
