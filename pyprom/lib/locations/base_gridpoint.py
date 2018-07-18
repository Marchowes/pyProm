"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for x,y oriented objects.
"""

import json


class BaseGridPoint(object):
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
        :return: dict of :class:`BaseGridPoint`)
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
        return hash((self.x, self.y))

    def __repr__(self):
        return "<BaseGridPoint> x: {}, y: {}".format(self.x, self.y)

    __unicode__ = __str__ = __repr__


def isBaseGridPoint(gridPoint):
    """
    :param gridPoint: object under scrutiny
    :raises: TypeError if other not of :class:`BaseGridPoint`
    """
    if not isinstance(gridPoint, BaseGridPoint):
        raise TypeError("Expected BaseGridPoint Object.")