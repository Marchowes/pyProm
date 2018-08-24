"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for Coordinate oriented objects with
Elevation data.
"""

from .base_coordinate import BaseCoordinate
from .base_gridpoint import BaseGridPoint
from ..util import randomString


class SpotElevation(BaseCoordinate):
    """
    SpotElevation -- Intended to be inherited from. lat/long/elevation
    """

    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        """
        :param latitude: latitude in dotted decimal
        :param longitude: longitude in dotted decimal
        :param elevation: elevation in meters
        :param edge: (bool) does this :class:`SpotElevation` have an edge
         Effect?
        :param edgePoints: list of :class:`BaseGridPoint` which are on
         the map edge.
        """
        super(SpotElevation, self).__init__(latitude, longitude)
        self.elevation = elevation
        self.edgeEffect = kwargs.get('edge', False)
        self.edgePoints = kwargs.get('edgePoints', [])
        self.id = kwargs.get('id', 'se:' + randomString())

    def to_dict(self):
        """
        :return: dict() representation of :class:`SpotElevation`
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
        :return: :class:`SpotElevation`
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
        Return this :class:`SpotElevation object` as
         a :class:`GridPoint object`
        :param datamap: :class:`Datamap` object
        :return: :class:`GridPoint object`
        """
        from .gridpoint import GridPoint
        x, y = datamap.latlong_to_xy(self.latitude, self.longitude)
        return GridPoint(x, y, self.elevation)

    @property
    def feet(self):
        """
        :return: elevation in feet
        """
        try:
            return self.elevation * 3.2808
        except:
            return None

    def __eq__(self, other):
        """
        Determines if :class:`SpotElevation` is equal to another.
        :param other: :class:`SpotElevation` to be compared against
        :return: bool of inequality
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
        Determines if :class:`SpotElevation` is not equal to another.
        :param other: :class:`SpotElevation` to be compared against
        :return: bool of inequality
        """
        return [round(self.latitude, 6), round(self.longitude, 6),
                self.elevation] != \
               [round(other.latitude, 6), round(other.longitude, 6),
                other.elevation]

    def __lt__(self, other):
        """
        :param other: object which we compare against.
        :return: bool of if self is of lower elevation than other.
        :raises: TypeError if other not of :class:`BaseCoordinate`
        """
        isSpotElevation(other)
        return self.elevation < other.elevation

    def __hash__(self):
        """
        :return: Hash representation of this object
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
    :param spotElevation: object under scrutiny
    :raises: TypeError if other not of :class:`SpotElevation`
    """
    if not isinstance(spotElevation, SpotElevation):
        raise TypeError("Expected SpotElevation or child"
                        " of SpotElevation Object.")
