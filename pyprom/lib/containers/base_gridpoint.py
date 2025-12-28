"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""
from __future__ import annotations

from pyprom.lib.locations.base_gridpoint import isBaseGridPoint
from typing import TYPE_CHECKING, List, Self
    from pyprom.lib.locations.base_gridpoint import BaseGridPoint

class BaseGridPointContainer:
    """
    Base Grid Point Container. Storage and functions for
    :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
    """

    __slots__ = ['points']

    def __init__(self, 
                 gridPointList: List[BaseGridPoint]
        ):
        """
        :param gridPointList: list of BaseGridPoints
        :type gridPointList:
         list(:class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`)
        """
        self.points: List[BaseGridPoint] = gridPointList

    def append(self, 
            gridPoint: BaseGridPoint
        ):
        """
        Append a BaseGridPoint to the container.

        :param gridPoint: object to append to container.
        :type gridPoint:
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :raises: TypeError if gridPoint not of
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        """
        isBaseGridPoint(gridPoint)
        self.points.append(gridPoint)

    def sort(self, **kwargs) -> List[BaseGridPoint]:
        """
        Sort points using kwargs passed in

        :param kwargs: common sort args
        """
        self.points.sort(**kwargs)

    def index(self, gridPoint: BaseGridPoint) -> int:
        """
        Returns the index that this
        :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint` or child
        object occurs. If none, return None

        :param gridPoint: BaseGridPoint or child object to find index of
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

    def __len__(self) -> int:
        """
        :return: number of items in `self.points`
        :rtype: int
        """
        return len(self.points)

    def __setitem__(self, idx: int, gridPoint: BaseGridPoint):
        """
        Gives this BaseGridPointContainer list like set capabilities

        :param int idx: index value
        :param gridPoint: BaseGridPoint or child object to add.
        :type gridPoint:
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :raises: TypeError if gridPoint not of
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        """
        isBaseGridPoint(gridPoint)
        self.points[idx] = gridPoint

    def __getitem__(self, idx: int):
        """
        Gives this BaseGridPointContainer container list like get capabilities

        :param int idx: index value
        :return: BaseGridPoint from self.point at idx
        :rtype: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        """
        return self.points[idx]

    def __hash__(self) -> int:
        """
        Produces the hash representation of this object.

        :return: Hash representation of this object
        :rtype: str
        """
        return hash(tuple(sorted(self.points)))

    def __eq__(self, other: Self) -> bool:
        """
        Determines if this object is equal to another.

        :param other: object to be compared against
        :type other: :class:`BaseGridPointContainer`
        :return: equality
        :rtype: bool
        :raises: TypeError if other not of :class:`BaseGridPointContainer`
        """
        _isBaseGridPointContainer(other)
        return sorted([x for x in self.points]) == \
            sorted([x for x in other.points])

    def __ne__(self, other: Self) -> bool:
        """
        Determines if this object is not equal to another.

        :param other: object to be compared against
        :type other: :class:`BaseGridPointContainer`
        :return: inequality
        :rtype: bool
        :raises: TypeError if other not of :class:`BaseGridPointContainer`
        """
        _isBaseGridPointContainer(other)
        return sorted([x for x in self.points]) != \
            sorted([x for x in other.points])

    def __repr__(self) -> str:
        """
        :return: String representation of this object
        """
        return "<BaseGridPointContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__


def _isBaseGridPointContainer(gridPointContainer: BaseGridPointContainer) -> None:
    """
    Check if passed in object is a :class:`BaseGridPointContainer`

    :param gridPointContainer: object under scrutiny
    :raises: TypeError if other not of :class:`BaseGridPointContainer`
    """
    if not isinstance(gridPointContainer, BaseGridPointContainer):
        raise TypeError("BaseGridPointContainer expected")
