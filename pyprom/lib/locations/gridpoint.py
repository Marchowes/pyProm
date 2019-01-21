"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for x,y oriented objects.
"""

from .base_gridpoint import BaseGridPoint


class GridPoint(BaseGridPoint):
    """
    A GridPoint Object. This is a Child of
    :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
    In essence, this is an x,y coordinate which also includes elevation.
    """

    def __init__(self, x, y, elevation):
        """
        :param int x: x coordinate
        :param int y: y coordinate
        :param elevation: elevation in meters
        :type elevation: float, int
        """
        super(GridPoint, self).__init__(x, y)
        self.elevation = elevation

    def to_dict(self):
        """
        :return: dict() representation of :class:`GridPoint`
        """
        return {'x': self.x,
                'y': self.y,
                'elevation': self.elevation}

    @classmethod
    def from_dict(self, gridPointDict):
        """
        Create this object from dictionary representation

        :param dict gridPointDict: dict() representation of this object.
        :return: GridPoint from dict()
        :rtype: :class:`GridPoint`
        """
        return self(gridPointDict['x'],
                    gridPointDict['y'],
                    gridPointDict['elevation'])

    def toSpotElevation(self, datamap):
        """
        Converts this GridPoint into a SpotElevation using a datamap.

        :param datamap: Datamap object
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: GridPoint as a SpotElevation object.
        :rtype: :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        """
        from .spot_elevation import SpotElevation
        lat, long = datamap.xy_to_latlong(self.x, self.y)
        return SpotElevation(lat, long, self.elevation)

    def __eq__(self, other):
        """
        :param other: object which we compare against.
        :type other: :class:`GridPoint`
        :return: equality
        :rtype: bool
        :raises: TypeError if other not of :class:`GridPoint`
        """
        isGridPoint(other)
        return [self.x, self.y, self.elevation] ==\
               [other.x, other.y, other.elevation]

    def __ne__(self, other):
        """
        :param other: object which we compare against.
        :type other: :class:`GridPoint`
        :return: inequality
        :rtype: bool
        :raises: TypeError if other not of :class:`GridPoint`
        """
        isGridPoint(other)
        return [self.x, self.y, self.elevation] !=\
               [other.x, other.y, other.elevation]

    def __lt__(self, other):
        """
        :param other: object which we compare against.
        :type other: :class:`GridPoint`
        :return: bool of if self is of lower elevation than other.
        :rtype: bool
        :raises: TypeError if other not of :class:`GridPoint`
        """
        isGridPoint(other)
        return self.elevation < other.elevation

    def __hash__(self):
        """
        :return: hash representation of this object.
        :rtype: str
        """
        return hash((self.x, self.y, self.elevation))

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<GridPoint> x: {}, y: {}, elevation(m): {}".\
               format(self.x,
                      self.y,
                      self.elevation)

    __unicode__ = __str__ = __repr__


def isGridPoint(gridPoint):
    """
    Check if passed in object is a :class:`GridPoint`

    :param gridPoint: object under scrutiny
    :raises: TypeError if other not of :class:`GridPoint`
    """
    if not isinstance(gridPoint, GridPoint):
        raise TypeError("Expected GridPoint Object.")
