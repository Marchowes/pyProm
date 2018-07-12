"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""

from pyprom.lib.locations.gridpoint import GridPoint

class BaseGridPointContainer(object):
    """
    Base Grid Point Container.
    """
    def __init__(self, gridPointList):
        """
        :param gridPointList: list of :class:`GridPoints`
        """
        super(BaseGridPointContainer, self).__init__()
        self.points = gridPointList

    def append(self, gridPoint):
        """
        Append a gridpoint to the container.
        :param gridPoint: :class:`GridPoint`
        """
        if not isinstance(gridPoint, GridPoint):
            raise TypeError("GridPointContainer can only contain"
                            " GridPoint objects.")
        self.points.append(gridPoint)

    def __setitem__(self, idx, value):
         self.points[idx] = value

    def __getitem__(self, idx):
        return self.points[idx]

    def __hash__(self):
        return hash(tuple(sorted([x.x for x in self.points])))

    def __eq__(self, other):
        return sorted([x.x for x in self.points]) == \
               sorted([x.x for x in other.points])

    def __ne__(self, other):
        return sorted([x.x for x in self.points]) == \
               sorted([x.x for x in other.points])

    def __repr__(self):
        return "<BaseGridPointContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__
