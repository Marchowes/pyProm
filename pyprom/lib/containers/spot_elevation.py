"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing SpotElevation
type location objects.
"""

from ..locations.summit import Summit
from ..locations.spot_elevation import isSpotElevation
from .base import _Base
from geopy.distance import vincenty


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
        self.fast_lookup = {point.id: point for point in self.points}

    @property
    def lowest(self):
        """
        :return: list of lowest spot_elevation object(s)
        """
        low = 10000
        lowest = list()
        for spot_elevation in self.points:
            if spot_elevation.elevation < low:
                low = spot_elevation.elevation
                lowest = list()
                lowest.append(spot_elevation)
            elif spot_elevation.elevation == low:
                lowest.append(spot_elevation)
        return lowest

    @property
    def highest(self):
        """
        :return: list of highest spot_elevation object(s)
        """
        high = -32768
        highest = list()
        for spot_elevation in self.points:
            if spot_elevation.elevation > high:
                high = spot_elevation.elevation
                highest = list()
                highest.append(spot_elevation)
            elif spot_elevation.elevation == high:
                highest.append(spot_elevation)
        return highest

    def radius(self, lat, long, value, unit='m'):
        """
        :param lat: latitude of center in dotted decimal
        :param long: longitude of center in dotted decimal
        :param value: number of units of distance
        :param unit: type of unit (m, km, mi, ft)
        :return: SpotElevationContainer loaded with results.
        """
        unit = unit.lower()
        # convert our units to meters so we only have to deal with one unit
        #  type.
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
        # iterate through points and collect only points within the specified
        # distance using the vincenty algorithm.
        for point in self.points:
            distance = vincenty((lat, long),
                                (point.latitude, point.longitude)).meters
            if distance < convertedDist:
                positive.append(point)
        return self.__class__(positive)

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
        return self.__class__(
            [x for x in self.points if lowerlat < x.latitude < upperlat and
                lowerlong < x.longitude < upperlong])

    def elevationRange(self, lower=-100000, upper=100000):
        """
        :param lower: lower limit in feet
        :param upper: upper limit in feet
        :return: list of all points in range between lower and upper
        """
        return self.__class__([x for x in self.points if
                               x.feet > lower and x.feet < upper])

    def elevationRangeMetric(self, lower=-100000, upper=100000):
        """
        :param lower: lower limit in Meters
        :param upper: upper limit in Meters
        :return: list of all points in range between lower and upper
        """
        return self.__class__([x for x in self.points if
                              upper > x.elevation > lower])

    def to_dict(self):
        """
        :return: dict() representation of :class:`SpotElevationContainer`
        """
        return {"spotelevations": [x for x in self.points.to_dict()]}

    @classmethod
    def from_dict(cls, spotElevationContainerDict, datamap=None):
        """
        Load this object and child objects from a dict.
        :param spotElevationContainerDict: dict() representation of
            :class:`SpotElevation`.
        :param datamap: :class:`Datamap`
        :return: :class:`SpotElevation`
        """
        spotelevations = []
        for spotelevation in spotElevationContainerDict['spotelevations']:
            spotelevations.append(Summit.from_dict(spotelevation, datamap))
        spotElevationContainer = cls(spotelevations)

        return spotElevationContainer

    def append(self, spotElevation):
        """
        Add a SpotElevation to the container.
        :param spotElevation: :class:`SpotElevation`
        :raises: TypeError if point not of :class:`SpotElevation`
        """
        isSpotElevation(spotElevation)
        self.points.append(spotElevation)
        self.fast_lookup[spotElevation.id] = spotElevation

    def __len__(self):
        """
        :return: integer - number of items in self.points
        """
        return len(self.points)

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<SpotElevationContainer> {} Objects".format(self.__len__())

    def __setitem__(self, idx, spotElevation):
        """
        Gives SpotElevationContainer list like set capabilities
        :param idx: index value
        :param spotElevation: :class:`SpotElevation`
        :raises: TypeError if spotElevation not of :class:`SpotElevation`
        """
        isSpotElevation(spotElevation)
        self.points[idx] = spotElevation

    def __getitem__(self, idx):
        """
        Gives SpotElevationContainer list like get capabilities
        :param idx: index value
        :return: :class:`SpotElevation` self.point at idx
        """
        return self.points[idx]

    def __eq__(self, other):
        """
        Determines if SpotElevationContainer is equal to another.
        :param other: :class:`SpotElevationContainer`
        :return: bool of equality
        :raises: TypeError if other not of :class:`SpotElevation`
        """
        _isSpotElevationContainer(other)
        return sorted([x for x in self.points]) == \
            sorted([x for x in other.points])

    def __ne__(self, other):
        """
        :param other: :class:`SpotElevationContainer`
        :return: bool of inequality
        :raises: TypeError if other not of :class:`SpotElevationContainer`
        """
        _isSpotElevationContainer(other)
        return sorted([x for x in self.points]) != \
            sorted([x for x in other.points])

    __unicode__ = __str__ = __repr__


def _isSpotElevationContainer(spotElevationContainer):
    """
    :param spotElevationContainer: object under scrutiny
    :raises: TypeError if other not of :class:`SpotElevationContainer`
    """
    if not isinstance(spotElevationContainer, SpotElevationContainer):
        raise TypeError("SpotElevationContainer expected")
