"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

Base object for containers which are have member points of (x,y) tuples
which are self iterable.
"""

FULL_SHIFT_LIST = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                       (0, -1), (-1, -1))
ORTHOGONAL_SHIFT_LIST = ((-1, 0), (0, 1), (1, 0), (0, -1))
DIAGONAL_SHIFT_LIST = ((-1, 1), (1, 1), (1, -1), (-1, -1))
FULL_SHIFT_ORTHOGONAL_DIAGONAL_LIST = ORTHOGONAL_SHIFT_LIST + DIAGONAL_SHIFT_LIST

class BaseSelfIterable:
    def __init__(self):
        pass

    def iterNeighborFull(self, point):
        """
        Iterate through diagonally and orthogonally neighboring
        :class:`pyprom.lib.locations.gridpoint.GridPoint` which are
        also members of this :class:`BaseSelfIterable`

        :param point: Gridpoint to find neighbors of
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        for shift in FULL_SHIFT_LIST:
            x = point[0] + shift[0]
            y = point[1] + shift[1]
            if self.pointIndex[x].get(y, False):
                yield self.pointIndex[x].get(y, False)
            else:
                continue

    def iterNeighborOrthogonal(self, point):
        """
        Iterate through orthogonally neighboring
        :class:`pyprom.lib.locations.gridpoint.GridPoint` which are
        also members of this :class:`BaseSelfIterable`

        :param point: Gridpoint to find neighbors of
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        for shift in ORTHOGONAL_SHIFT_LIST:
            x = point[0] + shift[0]
            y = point[1] + shift[1]
            if self.pointIndex[x].get(y, False):
                yield self.pointIndex[x].get(y, False)
            else:
                continue

    def iterNeighborOrthogonalDiagonal(self, point):
        """
        Iterate through orthogonally, then diagonally neighboring
        :class:`pyprom.lib.locations.gridpoint.GridPoint` which are
        also members of this :class:`Perimeter`

        :param point: Gridpoint to find neighbors of
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        for shift in ORTHOGONAL_SHIFT_LIST:
            x = point[0] + shift[0]
            y = point[1] + shift[1]
            if self.pointIndex[x].get(y, False):
                yield self.pointIndex[x].get(y, False)
            else:
                continue