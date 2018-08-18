"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for x,y oriented objects.
"""

import json


class BaseGridPoint:
    """
    Base Object for GridPoints
    """

    def __init__(self, x, y):
        """
        Basic Gridpoint.
        :param x: x coordinate
        :param y: y coordinate
        """
        super(BaseGridPoint, self).__init__()
        self.x = x
        self.y = y

    def to_dict(self):
        """
        :return: dict() representation of :class:`BaseGridPoint`
        """
        return {'x': self.x,
                'y': self.y}

    def to_json(self, prettyprint=True):
        """
        :param prettyprint: human readable,
        :return: json string of :class:`BaseGridPoint`
        """
        to_json = self.to_dict()
        if prettyprint:
            return json.dumps(to_json, sort_keys=True,
                              indent=4, separators=(',', ': '))
        else:
            return json.dumps(to_json)

    def __hash__(self):
        """
        :return: Hash representation of this object
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
        :return: bool of if self is arbitrarily regarded as lower than the other
        :raises: TypeError if other not of :class:`GridPoint`
        """
        isBaseGridPoint(other)
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
    :param gridPoint: object under scrutiny
    :raises: TypeError if other not of :class:`BaseGridPoint`
    """
    if not isinstance(gridPoint, BaseGridPoint):
        raise TypeError("Expected BaseGridPoint Object.")
