"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for Coordinate oriented objects.
"""

import utm
from ...lib.util import dottedDecimaltoDegrees


class BaseCoordinate:
    """
    Base Coordinate, intended to be inherited from. This contains
    basic latitude and longitude
    """

    def __init__(self, latitude, longitude, *args, **kwargs):
        """
        :param latitude: latitude in dotted decimal
        :type latitude: int, float
        :param longitude: longitude in dotted decimal
        :type longitude: int, float
        """
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        """
        Returns dict representation of this :class:`BaseCoordinate`

        :return: dict of :class:`BaseCoordinate`
        """
        return {'latitude': self.latitude,
                'longitude': self.longitude}

    @property
    def utm(self):
        """
        Returns Tuple of utm coordinate for this :class:`BaseCoordinate`.

        :return: utm coordinate
        :rtype: str
        """
        return utm.from_latlon(self.latitude, self.longitude)

    @property
    def dms(self):
        """
        Returns the coordinate of this :class:`BaseCoordinate`
        in degrees minutes seconds format

        :return: ((d, m, s), (d, m, s) Tuple of lat/long in dms.
        :rtype: tuple
        """
        return ((dottedDecimaltoDegrees(self.latitude)),
                (dottedDecimaltoDegrees(self.longitude)))

    def __eq__(self, other):
        """
        Determines if this :class:`BaseCoordinate` is equal to another.

        :param other: :class:`BaseCoordinate` to be compared against
        :type other: :class:`BaseCoordinate`
        :return: equality
        :rtype: bool
        """
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
        """
        Determines if this :class:`BaseCoordinate` is not equal to another.

        :param other: :class:`BaseCoordinate` to be compared against
        :type other: :class:`BaseCoordinate`
        :return: inequality
        :rtype: bool
        """
        return [round(self.latitude, 6), round(self.longitude, 6)] != \
               [round(other.latitude, 6), round(other.longitude, 6)]

    def __hash__(self):
        """
        :return: Hash representation of this object
        :rtype: str
        """
        return hash((round(self.latitude, 6), round(self.longitude, 6)))

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<BaseCoordinate> lat {} long {}".format(self.latitude,
                                                        self.longitude)

    __unicode__ = __str__ = __repr__


def isBaseCoordinate(baseCoordinate):
    """
    Check if passed in object is a :class:`BaseCoordinate`

    :param baseCoordinate: object under scrutiny
    :raises: TypeError if other not of :class:`BaseCoordinate`
    """
    if not isinstance(baseCoordinate, BaseCoordinate):
        raise TypeError("Expected BaseCoordinate Object.")
