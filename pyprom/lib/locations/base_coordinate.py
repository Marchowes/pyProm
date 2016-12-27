"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for Coordinate oriented objects.
"""

import json


class BaseCoordinate(object):
    """
    Base Coordinate, intended to be inherited from. This contains
    basic lat/long
    """
    def __init__(self, latitude, longitude, *args, **kwargs):
        """
        :param latitude: latitude in dotted decimal
        :param longitude: longitude in dotted decimal
        """
        super(BaseCoordinate, self).__init__()
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        """
        :return: dict of :class:`BaseCoordinate`
        """
        return {'latitude': self.latitude,
                'longitude': self.longitude}

    def to_json(self):
        """
        :return: json string of :class:`BaseCoordinate`
        """
        return json.dumps(self.to_dict())

    def __eq__(self, other):
        latitude = longitude = olatitude = olongitude = None
        if self.latitude:
            latitude = round(self.latitude, 6)
        if self.longitude:
            longitude = round(self.longitude, 6)
        if other.latitude:
            olatitude = round(other.latitude, 6)
        if other.longitude:
            olongitude = round(other.longitude, 6)
        return [latitude, longitude] ==\
               [olatitude, olongitude]

    def __ne__(self, other):
        return [round(self.latitude, 6), round(self.longitude, 6)] != \
               [round(other.latitude, 6), round(other.longitude, 6)]

    def __hash__(self):
        return hash((round(self.latitude, 6), round(self.longitude, 6)))

    def __repr__(self):
        return "<BaseCoordinate> lat {} long {}".format(self.latitude,
                                                        self.longitude)

    __unicode__ = __str__ = __repr__
