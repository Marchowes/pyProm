"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for x,y oriented objects.
"""

import json
from .base_gridpoint import BaseGridPoint


class GridPoint(BaseGridPoint):
    def __init__(self, x, y, elevation):
        """
        A basic grid point. This maps an elevation to an X,Y coordinate.
        :param x: x coordinate
        :param y: y coordinate
        :param elevation: elevation in meters
        """
        super(GridPoint, self).__init__(x, y)
        self.elevation = elevation

    def to_dict(self):
        """
        :return: dict of :class:`GridPoint`
        """
        return {'x': self.x,
                'y': self.y,
                'elevation': self.elevation}

    def to_json(self, prettyprint=True):
        """
        :param prettyprint: human readable,
        :return: json string of :class:`GridPoint`
        """
        to_json = self.to_dict()
        if prettyprint:
            return json.dumps(to_json, sort_keys=True,
                              indent=4, separators=(',', ': '))
        else:
            return json.dumps(to_json)

    def toSpotElevation(self, datamap):
        """
        :param datamap: :class:`Datamap` object
        :return: SpotElevation object
        """
        from .spot_elevation import SpotElevation
        latlong = datamap.xy_to_latlong(self.x, self.y)
        return SpotElevation(latlong[0], latlong[1], self.elevation)

    def __eq__(self, other):
        return [self.x, self.y, self.elevation] ==\
               [other.x, other.y, other.elevation]

    def __ne__(self, other):
        return [self.x, self.y, self.elevation] !=\
               [other.x, other.y, other.elevation]

    def __repr__(self):
        return "<GridPoint> x: {}, y: {}, elevation(m); {}".\
               format(self.x,
                      self.y,
                      self.elevation)

    __unicode__ = __str__ = __repr__
