"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for x,y oriented objects.
"""

from math import hypot

from typing import TYPE_CHECKING, Self, Dict
if TYPE_CHECKING:
    from pyprom._typing.type_hints import Numpy_X, Numpy_Y, XY


class BaseGridPoint:
    """
    Base Object for GridPoints. These are simple x, y coordinates
    with no association to a :class:`pyprom.lib.datamap.DataMap` This
    is a Base class intended to be inherited from in most situations.
    """

    __slots__ = ['x', 'y']

    def __init__(self, x: Numpy_X, y: Numpy_Y):
        """
        A basic x,y GridPoint.

        :param int x: x coordinate
        :param int y: y coordinate
        """
        self.x = x
        self.y = y

    @classmethod
    def from_dict(self, baseGridPointDict: Dict[str, int]) -> Self:
        """
        Create this object from dictionary representation

        :param dict baseGridPointDict: dict() representation of this object.
        :return: BaseGridPoint from dict()
        :rtype: :class:`BaseGridPoint`
        """
        return self(baseGridPointDict['x'],
                    baseGridPointDict['y'])

    @classmethod
    def from_tuple(self, tup: XY) -> Self:
        """
        Create this object from tuple representation
        :param tup:
        :return: BaseGridPoint from tuple()
        :rtype: :class:`BaseGridPoint`
        """
        return self(tup[0], tup[1])

    def to_dict(self) -> dict:
        """
        Create the dictionary representation of this object.

        :return: dict() representation of :class:`BaseGridPoint`
        :rtype: dict()
        """
        return {'x': self.x,
                'y': self.y}

    def to_tuple(self) -> XY:
        """
        Create the tuple representation of this object.

        :return: tuple() representation of :class:`BaseGridPoint`
        :rtype: tuple()
        """
        return (self.x, self.y)


    def distance(self, other: Self) -> float:
        """
        Returns the distance between this :class:`BaseGridPoint` and
        another (in points)

        :param other: :class:`BaseGridPoint` to compare for
         calculating distance.
        :type other: :class:`BaseGridPoint`
        :return: distance.
        :rtype: float
        :raises: TypeError if other not of :class:`BaseGridPoint`
        """
        isBaseGridPoint(other)
        return hypot((self.x - other.x), (self.y - other.y))

    def __hash__(self) -> int:
        """
        Produces the hash representation of this object.

        :return: Hash representation of this object
        :rtype: int
        """
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        """
        :return: String representation of this object
        """
        return "<BaseGridPoint> x: {}, y: {}".format(self.x, self.y)

    def __lt__(self, other: Self) -> bool:
        """
        Determines if this object's elevation is less than another.

        :param other: object which we compare against.
        :type other: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :return: bool of if self is arbitrarily regarded as
         lower than the other
        :raises: TypeError if other not of
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        """
        isBaseGridPoint(other)
        # we only do this to satisfy set requirements. There is no meaningful
        # way to determine if a GridPoint is gt/lt another.
        return self.x + self.y < other.x + other.y

    def __eq__(self, other: Self) -> bool:
        """
        Determines if this object is equal to another.

        :param other: object which we compare against.
        :type other: :class:`BaseGridPoint`
        :return: equality
        :rtype: bool
        :raises: TypeError if other not of :class:`BaseGridPoint`
        """
        isBaseGridPoint(other)
        return [self.x, self.y] ==\
               [other.x, other.y]

    __str__ = __repr__


def isBaseGridPoint(gridPoint) -> None:
    """
    Check if passed in object is a :class:`BaseGridPoint`

    :param gridPoint: object under scrutiny
    :raises: TypeError if other not of :class:`BaseGridPoint`
    """
    if not isinstance(gridPoint, BaseGridPoint):
        raise TypeError("Expected BaseGridPoint Object.")
