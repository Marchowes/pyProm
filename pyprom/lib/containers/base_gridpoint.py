"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""

from pyprom.lib.locations.gridpoint import isGridPoint


class BaseGridPointContainer(object):
    """
    Base Grid Point Container.
    """

    def __init__(self, gridPointList):
        """
        :param gridPointList: list of :class:`GridPoints`
        """
        self.points = gridPointList

    def append(self, gridPoint):
        """
        Append a gridPoint to the container.
        :param gridPoint: :class:`GridPoint`
        :raises: TypeError if gridPoint not of :class:`GridPoint`
        """
        isGridPoint(gridPoint)
        self.points.append(gridPoint)

    def sort(self, **kwargs):
        """
        Sort points using kwargs passed in.
        :param kwargs:
        """
        self.points.sort(**kwargs)

    def __len__(self):
        """
        :return: integer - number of items in self.points
        """
        return len(self.points)

    def __setitem__(self, idx, gridPoint):
        """
        Gives BaseGridpoint list like set capabilities
        :param idx: index value
        :param gridPoint: :class:`GridPoint`
        :raises: TypeError if gridPoint not of :class:`GridPoint`
        """
        isGridPoint(gridPoint)
        self.points[idx] = gridPoint

    def __getitem__(self, idx):
        """
        Gives BaseGridpoint list like get capabilities
        :param idx: index value
        :return: :class:`GridPoint` self.point at idx
        """
        return self.points[idx]

    def __hash__(self):
        """
        Generates hash based on points.
        :return: string representation of hash
        """
        return hash(tuple(sorted([x.x for x in self.points])))

    def __eq__(self, other):
        """
        Determines if BaseGridPointContainer is equal to another.
        :param other: :class:`BaseGridPointContainer` to be compared against
        :return: bool of equality
        :raises: TypeError if other not of :class:`BaseGridPointContainer`
        """
        _isBaseGridPointContainer(other)
        return sorted([x for x in self.points]) == \
            sorted([x for x in other.points])

    def __ne__(self, other):
        """
        Determines if BaseGridPointContainer is not equal to another.
        :param other: :class:`BaseGridPointContainer` to be compared against
        :return: bool of inequality
        :raises: TypeError if other not of :class:`BaseGridPointContainer`
        """
        _isBaseGridPointContainer(other)
        return sorted([x for x in self.points]) != \
            sorted([x for x in other.points])

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<BaseGridPointContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__


def _isBaseGridPointContainer(gridPointContainer):
    """
    :param gridPointContainer: object under scrutiny
    :raises: TypeError if other not of :class:`BaseGridPointContainer`
    """
    if not isinstance(gridPointContainer, BaseGridPointContainer):
        raise TypeError("BaseGridPointContainer expected")
