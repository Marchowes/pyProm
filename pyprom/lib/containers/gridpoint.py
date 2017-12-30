"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing GridPoint
type location objects.
"""

from .base_gridpoint import BaseGridPointContainer
from collections import defaultdict


class GridPointContainer(BaseGridPointContainer):
    """
    Container for GridPoint type lists.
    Allows for various list transformations and functions.
    """
    def __init__(self, gridPointList):
        super(GridPointContainer, self).__init__(gridPointList)
        self.fastLookup = defaultdict(dict)
        # Generate a fast lookup table.
        self.genFastLookup()

    def genFastLookup(self):
        """
        Generates a fast lookup hash of all gridpoints
        :return:
        """
        for gp in self.points:
            self.fastLookup[gp.x][gp.y] = gp

    def iterNeighborDiagonal(self, point):
        """
        Iterate through existing diagonal :class:`GridPoint`
        neighbors.
        :param GridPoint
        """
        if not len(self.fastLookup):
            self.genFastLookup()
        shiftList = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1],
                     [0, -1], [-1, -1]]
        for shift in shiftList:
            x = point.x+shift[0]
            y = point.y+shift[1]
            if self.fastLookup[x].get(y, False):
                yield self.fastLookup[x][y]
            else:
                continue

    def iterNeighborOrthogonal(self, point):
        """
        Iterate through existing orthogonal :class:`GridPoint`
        neighbors.
        :param GridPoint
        """
        if not len(self.fastLookup):
            self.genFastLookup()
        shiftList = [[-1, 0], [0, 1], [1, 0],  [0, -1]]
        for shift in shiftList:
            x = point.x+shift[0]
            y = point.y+shift[1]
            if self.fastLookup[x].get(y, False):
                yield self.fastLookup[x][y]
            else:
                continue


    def __repr__(self):
        return "<GridPointContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__
