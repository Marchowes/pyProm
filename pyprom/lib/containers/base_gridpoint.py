"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""

from pyprom.lib.locations.gridpoint import isGridPoint


class BaseGridPointContainer:
    """
    Base Grid Point Container. Storage and functions for
    :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`s
    """

    def __init__(self, gridPointList):
        """
        :param gridPointList: list of
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        """
        self.points = gridPointList

    def append(self, gridPoint):
        """
        Append a gridPoint to the container.

        :param gridPoint: object to append to container.
        :type gridPoint: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :raises: TypeError if gridPoint not of :class:`GridPoint`
        """
        isGridPoint(gridPoint)
        self.points.append(gridPoint)

    def sort(self, **kwargs):
        """
        Sort points using kwargs passed in
        .
        :param kwargs:
        """
        self.points.sort(**kwargs)

    def index(self, gridPoint):
        """
        Returns the index that this
        :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint` or child
        object occurs. If none, return None

        :param gridPoint:
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint` to find
         index of
        :type gridPoint:
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :return: index in points list where this
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint` resides.
        :rtype: int
        """
        try:
            return self.points.index(gridPoint)
        except:
            return None

    def __len__(self):
        """
        :return: number of items in self.points
        :rtype: int
        """
        return len(self.points)

    def __setitem__(self, idx, gridPoint):
        """
        Gives this container list like set capabilities

        :param int idx: index value
        :param gridPoint: gridpoint to add.
        :type gridPoint: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :raises: TypeError if gridPoint not of
         :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        isGridPoint(gridPoint)
        self.points[idx] = gridPoint

    def __getitem__(self, idx):
        """
        Gives this container list like get capabilities

        :param int idx: index value
        :return: :class:`pyprom.lib.locations.gridpoint.GridPoint`
         from self.point at idx
        """
        return self.points[idx]

    def __hash__(self):
        """
        Generates hash based on points.

        :return: string representation of hash
        """
        return hash(tuple(sorted(self.points)))

    def __eq__(self, other):
        """
        Determines if this :class:`BaseGridPointContainer` is equal to another.

        :param other: object to be compared against
        :type other: :class:`BaseGridPointContainer`
        :return: equality
        :rtype: bool
        :raises: TypeError if other not of :class:`BaseGridPointContainer`
        """
        _isBaseGridPointContainer(other)
        return sorted([x for x in self.points]) == \
            sorted([x for x in other.points])

    def __ne__(self, other):
        """
        Determines if :class:`BaseGridPointContainer` is not equal to another.

        :param other: object to be compared against
        :type other: :class:`BaseGridPointContainer`
        :return: inequality
        :rtype: bool
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
    Check if passed in object is a :class:`BaseGridPointContainer`

    :param gridPointContainer: object under scrutiny
    :raises: TypeError if other not of :class:`BaseGridPointContainer`
    """
    if not isinstance(gridPointContainer, BaseGridPointContainer):
        raise TypeError("BaseGridPointContainer expected")
