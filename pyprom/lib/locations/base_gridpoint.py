"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for x,y oriented objects.
"""

from math import hypot


class BaseGridPoint:
    """
    Base Object for GridPoints. These are simple x, y coordinates
    with no association to a :class:`pyprom.lib.datamap.DataMap` This
    is a Base class intended to be inherited from in most situations.
    """

    def __init__(self, x, y):
        """
        A basic x,y GridPoint.

        :param int x: x coordinate
        :param int y: y coordinate
        """
        self.x = x
        self.y = y

    def to_dict(self):
        """
        Returns dict representation of this :class:`BaseGridPoint`

        :return: dict() representation of :class:`BaseGridPoint`
        """
        return {'x': self.x,
                'y': self.y}

    def distance(self, other):
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

    def __hash__(self):
        """
        :return: Hash representation of this object
        :rtype str:
        """
        return hash((self.x, self.y))

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<BaseGridPoint> x: {}, y: {}".format(self.x, self.y)

    def __lt__(self, other):
        """
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

    def __eq__(self, other):
        """
        :param other: object which we compare against.
        :return: bool if self is equal to other
        :raises: TypeError if other not of :class:`BaseGridPoint`
        """
        isBaseGridPoint(other)
        return [self.x, self.y] ==\
               [other.x, other.y]

    __unicode__ = __str__ = __repr__


def isBaseGridPoint(gridPoint):
    """
    Check if passed in object is a :class:`BaseGridPoint`

    :param gridPoint: object under scrutiny
    :raises: TypeError if other not of :class:`BaseGridPoint`
    """
    if not isinstance(gridPoint, BaseGridPoint):
        raise TypeError("Expected BaseGridPoint Object.")
