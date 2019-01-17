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

    This is intended to be inherited from, namely for:
    :class:`pyprom.lib.containers.saddles.SaddlesContainer`,
    :class:`pyprom.lib.containers.summits.SummitsContainer`,
    and :class:`pyprom.lib.containers.runoffs.RunOffsContainer`
    """

    def __init__(self, spotElevationList):
        """
        :param spotElevationList: list of SpotElevation objects
         which will reside in this container.
        :type spotElevationList:
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        """
        super(SpotElevationContainer, self).__init__()
        self.points = spotElevationList
        self.fast_lookup = {point.id: point for point in self.points}

    @property
    def lowest(self):
        """
        :return: list of lowest
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation` object(s)
         found in this container
        :rtype:
         list(:class:`pyprom.lib.locations.spot_elevation.SpotElevation`)
        """
        low = self.points[0].elevation
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
        :return: list of highest
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation` object(s)
         found in this container
        :rtype:
         list(:class:`pyprom.lib.locations.spot_elevation.SpotElevation`)
        """
        high = self.points[0].elevation
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
        Returns all members of this container within a certain radius.

        :param lat: latitude of center in dotted decimal
        :type lat: float, int
        :param long: longitude of center in dotted decimal
        :type long: float, int
        :param value: number of units of distance
        :type value: float, int
        :param str unit: type of unit (m, km, mi, ft)
        :return: SpotElevationContainer loaded with results.
        :rtype: :class:`SpotElevationContainer`
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
        Returns all members of this container in a rectangle of
        (lat1, long1) - (lat2, long2)

        :param lat1:  latitude of point 1
        :type lat1: float, int
        :param long1: longitude of point 1
        :type long1: float, int
        :param lat2:  latitude of point 2
        :type lat2: float, int
        :param long2: longitude of point 2
        :type long2: float, int
        :return: SpotElevationContainer loaded with all points within
         (inclusive) the specified rectangle.
        :rtype: :class:`SpotElevationContainer`
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
        Returns all members of this container within a certain elevation
        range in feet

        :param lower: lower limit in feet
        :type lower: int, float
        :param upper: upper limit in feet
        :type upper: int, float
        :return: all points in range between lower and upper (exclusive)
        :rtype: :class:`SpotElevationContainer`
        """
        return self.__class__([x for x in self.points if
                               x.feet > lower and x.feet < upper])

    def elevationRangeMetric(self, lower=-100000, upper=100000):
        """
        Returns all members of this container within a certain elevation range
        using meters

        :param lower: lower limit in meters
        :type lower: int, float
        :param upper: upper limit in meters
        :type upper: int, float
        :return: all points in range between lower and upper (exclusive)
        :rtype: :class:`SpotElevationContainer`
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

        :param dict spotElevationContainerDict: dict() representation of
         :class:`SpotElevationContainer`.
        :param datamap: datamap which MultiPoint style SpotElevations use.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: :class:`SpotElevationContainer`
        """
        spotelevations = []
        for spotelevation in spotElevationContainerDict['spotelevations']:
            spotelevations.append(Summit.from_dict(spotelevation, datamap))
        spotElevationContainer = cls(spotelevations)

        return spotElevationContainer

    def append(self, spotElevation):
        """
        Append a :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        to this container.

        :param spotElevation: SpotElevation to append.
        :type spotElevation:
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        :raises: TypeError if point not of
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        """
        isSpotElevation(spotElevation)
        self.points.append(spotElevation)
        self.fast_lookup[spotElevation.id] = spotElevation

    def index(self, spotElevation):
        """
        Returns the index that this
        :class:`pyprom.lib.locations.spot_elevation.SpotElevation` or child
        object occurs.
        if none, return None

        :param gridPoint: Gridpoint to find index of.
        :type gridPoint:
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        :return: index in points list where this spotElevation exists
        :rtype: int, None
        """
        try:
            return self.points.index(spotElevation)
        except:
            return None

    def __len__(self):
        """
        :return: number of items in `self.points`
        :rtype: int
        """
        return len(self.points)

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<SpotElevationContainer> {} Objects".format(self.__len__())

    def __setitem__(self, idx, spotElevation):
        """
        Gives :class:`SpotElevationContainer` list like set capabilities

        :param int idx: index value
        :param spotElevation: Spot Elevation object to set.
        :type spotElevation:
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        :raises: TypeError if spotElevation not of
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        """
        isSpotElevation(spotElevation)
        self.points[idx] = spotElevation

    def __getitem__(self, idx):
        """
        Gives :class:`SpotElevationContainer` list like get capabilities

        :param int idx: index value
        :return: :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
         self.point at idx
        """
        return self.points[idx]

    def __eq__(self, other):
        """
        Determines if :class:`SpotElevationContainer` is equal to another.

        :param other: other :class:`SpotElevationContainer` to check.
        :type: :class:`SpotElevationContainer`
        :return: equality
        :rtype: bool
        :raises: TypeError if other not of :class:`SpotElevationContainer`
        """
        _isSpotElevationContainer(other)
        return sorted([x for x in self.points]) == \
            sorted([x for x in other.points])

    def __ne__(self, other):
        """
        Determines if :class:`SpotElevationContainer` is not equal to another.

        :param other: other :class:`SpotElevationContainer` to check.
        :type: :class:`SpotElevationContainer`
        :return: equality
        :rtype: bool
        :raises: TypeError if other not of :class:`SpotElevationContainer`
        """
        _isSpotElevationContainer(other)
        return sorted([x for x in self.points]) != \
            sorted([x for x in other.points])

    __unicode__ = __str__ = __repr__


def _isSpotElevationContainer(spotElevationContainer):
    """
    Check if passed in object is a :class:`SpotElevationContainer`


    :param spotElevationContainer: object under scrutiny
    :raises: TypeError if other not of :class:`SpotElevationContainer`
    """
    if not isinstance(spotElevationContainer, SpotElevationContainer):
        raise TypeError("SpotElevationContainer expected")
