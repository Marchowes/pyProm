"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for x,y oriented objects.
"""

from .base_gridpoint import BaseGridPoint


class GridPoint(BaseGridPoint):
    """Grid Point"""

    def __init__(self, x, y, elevation):
        """
        A basic grid point. This maps an elevation to an X,Y coordinate.
        :param x: x coordinate
        :param y: y coordinate
        :param elevation: elevation in meters
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
        :return: dict of :class:`GridPoint`
        """
        return self(gridPointDict['x'],
                    gridPointDict['y'],
                    gridPointDict['elevation'])

    def toSpotElevation(self, datamap):
        """
        :param datamap: :class:`Datamap` object
        :return: SpotElevation object
        """
        from .spot_elevation import SpotElevation
        lat, long = datamap.xy_to_latlong(self.x, self.y)
        return SpotElevation(lat, long, self.elevation)

    def __eq__(self, other):
        """
        :param other: object which we compare against.
        :return: bool if self is equal to other
        :raises: TypeError if other not of :class:`GridPoint`
        """
        isGridPoint(other)
        return [self.x, self.y, self.elevation] ==\
               [other.x, other.y, other.elevation]

    def __ne__(self, other):
        """
        :param other: object which we compare against.
        :return: bool if self is not equal to other
        :raises: TypeError if other not of :class:`GridPoint`
        """
        isGridPoint(other)
        return [self.x, self.y, self.elevation] !=\
               [other.x, other.y, other.elevation]

    def __lt__(self, other):
        """
        :param other: object which we compare against.
        :return: bool of if self is of lower elevation than other.
        :raises: TypeError if other not of :class:`GridPoint`
        """
        isGridPoint(other)
        return self.elevation < other.elevation

    def __hash__(self):
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
    :param gridPoint: object under scrutiny
    :raises: TypeError if other not of :class:`GridPoint`
    """
    if not isinstance(gridPoint, GridPoint):
        raise TypeError("Expected GridPoint Object.")
