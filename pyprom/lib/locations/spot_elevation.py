"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for Coordinate oriented objects with
Elevation data.
"""

from shapely.geometry import Point

from .base_coordinate import BaseCoordinate
from .base_gridpoint import BaseGridPoint
from ..util import randomString
from ..constants import FEET_TO_METERS


class SpotElevation(BaseCoordinate):
    """
    SpotElevation is intended to be inherited from. Effectively it's a
    Latitude/Longitude coordinate with an elevation
    """
    __slots__ = ['elevation', 'edgeEffect', 'edgePoints', 'id']

    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        """
        :param latitude: latitude in dotted decimal
        :type latitude: int, float
        :param longitude: longitude in dotted decimal
        :type longitude: int, float
        :param elevation: elevation in meters
        :type elevation: int, float
        :param bool edge: does this :class:`SpotElevation` have an edge
         Effect?
        :param list edgePoints: list of BaseGridPoints which are on the map
         edge.
        :type edgePoints:
         list(:class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`)
        """
        super(SpotElevation, self).__init__(latitude, longitude)
        self.elevation = elevation
        self.edgeEffect = kwargs.get('edge', False)
        self.edgePoints = kwargs.get('edgePoints', [])
        self.id = kwargs.get('id', 'se:' + randomString())

    def to_dict(self):
        """
        Create the dictionary representation of this object.

        :return: dict() representation of :class:`SpotElevation`
        :rtype: dict()
        """
        return {'latitude': self.latitude,
                'longitude': self.longitude,
                'elevation': self.elevation,
                'edge': self.edgeEffect,
                'edgepoints': [x.to_dict() for x in self.edgePoints],
                'id': self.id
                }

    @classmethod
    def from_dict(cls, spotElevationDict):
        """
        Create :class:`SpotElevation` from dictionary representation

        :param spotElevationDict: dict representation of this object
        :return: a new SpotElevation
        :rtype: :class:`SpotElevation`
        """
        lat = spotElevationDict['lat']
        long = spotElevationDict['lon']
        elevation = spotElevationDict['ele']
        edge = spotElevationDict['edge']
        edgePoints = [BaseGridPoint(pt['x'], pt['y'])
                      for pt in spotElevationDict['edgepoints']]
        id = spotElevationDict['id']
        return cls(lat, long, elevation,
                   edge=edge,
                   edgePoints=edgePoints,
                   id=id)

    def toGridPoint(self, datamap):
        """
        Return this :class:`SpotElevation` object as
        a :class:`pyprom.lib.locations.gridpoint.GridPoint`
        object based on the :class:`pyprom.lib.datamap.DataMap`
        passed in.

        :param datamap: Datamap object
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: Gridpoint representation of this object
        :rtype: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        from .gridpoint import GridPoint
        x, y = datamap.latlong_to_xy(self.latitude, self.longitude)
        return GridPoint(x, y, self.elevation)

    def toXYTuple(self, datamap):
        """
        Return this :class:`SpotElevation` object as
        an (x, y, ele) tuple
        object based on the :class:`pyprom.lib.datamap.DataMap`
        passed in.

        :param datamap: Datamap object
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: (x, y, ele))
        :rtype: tuple
        """
        x, y = datamap.latlong_to_xy(self.latitude, self.longitude)
        return (x, y, self.elevation)

    @property
    def feet(self):
        """
        :return: elevation in feet
        :rtype: float, None
        """
        try:
            return self.elevation * FEET_TO_METERS
        except:
            return None

    @property
    def shape(self):
        """
        Returns a point representation of this :class:`SpotElevation` as a
         :class:`shapely.geometry.Point`
        :return: :class:`shapely.geometry.Point`
        """
        return Point(self.longitude, self.latitude)

    def __eq__(self, other):
        """
        Determines if this object is equal to another.

        :param other: object to be compared against
        :type other: :class:`SpotElevation`
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
        return [latitude, longitude, self.elevation] ==\
               [olatitude, olongitude, other.elevation]

    def __ne__(self, other):
        """
        Determines if this object is not equal to another.

        :param other: object to be compared against
        :type other: :class:`SpotElevation`
        :return: inequality
        :rtype: bool
        """
        return [round(self.latitude, 6), round(self.longitude, 6),
                self.elevation] != \
               [round(other.latitude, 6), round(other.longitude, 6),
                other.elevation]

    def __lt__(self, other):
        """
        Determines if :class:`SpotElevation` elevation is less than another.

        :param other: object which we compare against.
        :type other: :class:`SpotElevation`
        :return: if self is of lower elevation than other.
        :rtype: bool
        :raises: TypeError if other not of :class:`SpotElevation`
        """
        isSpotElevation(other)
        return self.elevation < other.elevation

    def __hash__(self):
        """
        :return: Hash representation of this object
        :rtype: str
        """
        return hash((round(self.latitude, 6), round(self.longitude, 6),
                     self.elevation))

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<SpotElevation> lat {} long" \
               " {} {}ft, {}m".format(self.latitude,
                                      self.longitude,
                                      self.feet,
                                      self.elevation)

    __unicode__ = __str__ = __repr__


def isSpotElevation(spotElevation):
    """
    Check if passed in object is a :class:`SpotElevation`

    :param spotElevation: object under scrutiny
    :raises: TypeError if other not of :class:`SpotElevation`
    """
    if not isinstance(spotElevation, SpotElevation):
        raise TypeError("Expected SpotElevation or child"
                        " of SpotElevation Object.")
