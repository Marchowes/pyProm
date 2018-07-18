"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for Coordinate oriented objects.
"""

import json
import utm


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

    def to_json(self, prettyprint=True):
        """
        :param prettyprint: human readable,
        :return: json string of :class:`BaseCoordinate`
        """
        if prettyprint:
            return json.dumps(self.to_dict(), sort_keys=True,
                              indent=4, separators=(',', ': '))
        else:
            return json.dumps(self.to_dict())

    @property
    def utm(self):
        """
        Returns Tuple of utm coordinate for this :class:`BaseCoordinate`.
        :return:
        """
        return utm.from_latlon(self.latitude, self.longitude)

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


def isBaseCoordinate(baseCoordinate):
    """
    :param baseCoordinate: object under scrutiny
    :raises: TypeError if other not of :class:`BaseCoordinate`
    """
    if not isinstance(baseCoordinate, BaseCoordinate):
        raise TypeError("Expected BaseCoordinate Object.")