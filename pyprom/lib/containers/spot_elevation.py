"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing SpotElevation
type location objects.
"""
import json

from ..location_util import longitudeArcSec
from ..locations.saddle import Saddle
from ..locations.summit import Summit
from ..locations.spot_elevation import SpotElevation
from ..locations.base_gridpoint import BaseGridPoint
from ..locations.gridpoint import GridPoint
from .multipoint import MultiPoint
from .gridpoint import GridPointContainer
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
            distance = vincenty((lat,long),
                                (point.latitude, point.longitude)).meters
            if distance < convertedDist:
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

    def elevationRange(self, lower=-100000, upper=100000):
        """
        :param lower: lower limit in feet
        :param upper: upper limit in feet
        :return: list of all points in range between lower and upper
        """
        return SpotElevationContainer([x for x in self.points if
                                       x.feet > lower and x.feet < upper])

    def elevationRangeMetric(self, lower=-100000, upper=100000):
        """
        :param lower: lower limit in Meters
        :param upper: upper limit in Meters
        :return: list of all points in range between lower and upper
        """
        return SpotElevationContainer([x for x in self.points if
                                       x.elevation > lower and
                                       x.elevation < upper])

    def to_json(self, prettyprint=True):
        """
        :param prettyprint: human readable,
         but takes more space when written to a file.
        :return: json string of all points in this container.
        """
        if prettyprint:
            return json.dumps([x.to_dict(recurse=True) for x in self.points],
                              sort_keys=True, indent=4, separators=(',', ': '))
        else:
            return json.dumps([x.to_dict(recurse=True) for x in self.points])

    def from_json(self, jsonData, datamap):
        """
        :param jsonData: json string of data to be loaded in this container
        :param datamap:
        :return:
        """
        hash = json.loads(jsonData)
        self.points = list()
        for point in hash:
            objType = point.get('type', 'SpotElevation')
            if objType == 'Summit':
                feature = Summit(point['latitude'],
                                 point['longitude'],
                                 point['elevation'])
            elif objType == 'Saddle':
                feature = Saddle(point['latitude'],
                                 point['longitude'],
                                 point['elevation'])
            elif objType == 'SpotElevation':
                feature = SpotElevation(point['latitude'],
                                        point['longitude'],
                                        point['elevation'])
            else:
                raise Exception('Cannot import unknown type:'.format(objType))
            mpPoints = list()
            if point.get('multipoint', None):
                for mp in point['multipoint']:
                    mpPoints.append(BaseGridPoint(mp['gridpoint']['x'],
                                                  mp['gridpoint']['y']))
                feature.multiPoint = MultiPoint(mpPoints,
                                                point['elevation'],
                                                datamap)
            if point.get('highShores', None):
                feature.highShores = list()
                for hs in point['highShores']:
                    feature.highShores.append(
                        GridPointContainer(
                            [GridPoint(x['x'], x['y'], x['elevation'])
                             for x in hs]))
            feature.edgeEffect = point['edge']
            self.points.append(feature)

    def process_saddles_into_dual_linkers_or_less(self):
        """
        Any saddle with more than 2 linkers will be broken down into multiple equal saddles with only 2 linkers.
        EX:
        Saddle (X,Y) with Linkers A,B,C,D becomes:

        Saddle (X,Y): A,B
        Saddle (X,Y): A,C
        Saddle (X,Y): A,D
        Saddle (X,Y): B,C
        Saddle (X,Y): B,D
        Saddle (X,Y): C,D
        """
        pass

    def __len__(self):
        return len(self.points)

    def __repr__(self):
        return "<SpotElevationContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__
