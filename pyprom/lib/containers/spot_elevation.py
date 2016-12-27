"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing SpotElevation
type location objects.
"""

from ..location_util import longitudeArcSec
from base import _Base
from math import sqrt


class SpotElevationContainer(_Base):
    """
    Container for Spot Elevation type lists.
    Allows for various list transformations.
    """
    def __init__(self, spotElevationList):
        """
        :param spotElevationList: list of :class:`SpotElevation`s
        """
        super(SpotElevationContainer, self).__init__()
        self.points = spotElevationList

    def radius(self, lat, long, datamap, value, unit='m'):
        """
        :param lat: latitude of center in dotted decimal
        :param long: longitude of center in dotted decimal
        :param datamap: datamap object
        :param value: number of units of distance
        :param unit: type of unit (m, km, mi, ft)
        :return: SpotElevationContainer loaded with results.
        """
        unit = unit.lower()
        if unit in ['meters', 'meter', 'm']:
            convertedDist = value
        elif unit in ['kilometers', 'kilometer', 'km']:
            convertedDist = value * 1000
        elif unit in ['feet', 'foot', 'ft']:
            convertedDist = 0.3048 * value
        elif unit in ['miles', 'mile', 'mi']:
            convertedDist = 0.3048 * value * 5280
        else:
            raise ValueError('No unit value specified')

        positive = list()
        longitudalMetersPerArcSec = longitudeArcSec(lat) *\
            datamap.arcsec_resolution
        lateralMetersPerArcSec = 30.8666
        for point in self.points:
            latDist = (abs(lat - point.latitude) * 3600) *\
                lateralMetersPerArcSec
            longDist = (abs(long - point.longitude) * 3600) *\
                longitudalMetersPerArcSec
            distance = sqrt(longDist**2 + latDist**2)
            if distance <= convertedDist:
                positive.append(point)
        return SpotElevationContainer(positive)

    def rectangle(self, lat1, long1, lat2, long2):
        """
        For the purpose of gathering all points in a rectangle of
        (lat1, long1) - (lat2, long2)
        :param lat1:  latitude of point 1
        :param long1: longitude of point 1
        :param lat2:  latitude of point 2
        :param long2: longitude of point 2
        :return: list of all points in that between
        (lat1, long1) - (lat2, long2)
        """
        upperlat = max(lat1, lat2)
        upperlong = max(long1, long2)
        lowerlat = min(lat1, lat2)
        lowerlong = min(long1, long2)
        return SpotElevationContainer(
            [x for x in self.points if lowerlat < x.latitude < upperlat and
                lowerlong < x.longitude < upperlong])

    def byType(self, string):
        """
        :param string: Object type (as String). ex: Saddle, Summit
        :return: SpotElevationContainer of objects by type.
        """
        name = string.upper()
        return SpotElevationContainer([x for x in self.points
                                       if type(x).__name__.upper() == name])

    def elevationRange(self, lower=None, upper=100000):
        """
        :param lower: lower limit in feet
        :param upper: upper limit in feet
        :return: list of all points in range between lower and upper
        """
        return SpotElevationContainer([x for x in self.points if
                                       x.feet > lower and x.feet < upper])

    def elevationRangeMetric(self, lower=None, upper=100000):
        """
        :param lower: lower limit in Meters
        :param upper: upper limit in Meters
        :return: list of all points in range between lower and upper
        """
        return SpotElevationContainer([x for x in self.points if
                                       x.elevation > lower and
                                       x.elevation < upper])

    def __repr__(self):
        return "<SpotElevationContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__
