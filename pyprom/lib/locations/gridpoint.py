"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base class for x,y oriented objects.
"""
from __future__ import annotations

from .base_gridpoint import BaseGridPoint

from typing import TYPE_CHECKING, Dict, Self
if TYPE_CHECKING:
    from pyprom._typing.type_hints import (
        Numpy_X, Numpy_Y, 
        XY_Elevation,
        Elevation,
    )
    from pyprom.lib.locations.spot_elevation import SpotElevation
class GridPoint(BaseGridPoint):
    """
    A GridPoint Object. This is a Child of
    :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
    In essence, this is an x,y coordinate which also includes elevation.
    """

    __slots__ = ['elevation']

    def __init__(self, x: Numpy_X, y: Numpy_Y, elevation: Elevation):
        """
        :param int x: x coordinate
        :param int y: y coordinate
        :param elevation: elevation in meters
        :type elevation: float, int
        """
        super(GridPoint, self).__init__(x, y)
        self.elevation = elevation

    @classmethod
    def from_dict(self, gridPointDict: Dict[str, int | float]) -> Self:
        """
        Create this object from dictionary representation

        :param dict gridPointDict: dict() representation of this object.
        :return: GridPoint from dict()
        :rtype: :class:`GridPoint`
        """
        return self(gridPointDict['x'],
                    gridPointDict['y'],
                    gridPointDict['elevation'])

    @classmethod
    def from_tuple(self, tup: XY_Elevation) -> Self:
        """
        Create this object from tuple representation
        :param tup:
        :return: GridPoint from tuple()
        :rtype: :class:`GridPoint`
        """
        return self(tup[0], tup[1], tup[2])

    def to_dict(self) -> Dict:
        """
        :return: dict() representation of :class:`GridPoint`
        """
        return {'x': self.x,
                'y': self.y,
                'elevation': self.elevation}

    def to_tuple(self) -> XY_Elevation:
        """
        :return: tuple() representation of :class:`GridPoint`
        """
        return (self.x, self.y, self.elevation)

    def toSpotElevation(self, datamap) -> SpotElevation:
        """
        Converts this GridPoint into a SpotElevation using a datamap.

        :param datamap: Datamap object
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: GridPoint as a SpotElevation object.
        :rtype: :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        """
        from .spot_elevation import SpotElevation
        lat, long = datamap.xy_to_latlon(self.x, self.y)
        return SpotElevation(lat, long, self.elevation)

    def __eq__(self, other: Self) -> bool:
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

    def __ne__(self, other: Self) -> bool:
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

    def __lt__(self, other: Self) -> bool:
        """
        :param other: object which we compare against.
        :type other: :class:`GridPoint`
        :return: bool of if self is of lower elevation than other.
        :rtype: bool
        :raises: TypeError if other not of :class:`GridPoint`
        """
        isGridPoint(other)
        return self.elevation < other.elevation

    def __hash__(self) -> int:
        """
        :return: hash representation of this object.
        :rtype: str
        """
        return hash((self.x, self.y, self.elevation))

    def __repr__(self) -> str:
        """
        :return: String representation of this object
        """
        return "<GridPoint> x: {}, y: {}, elevation(m): {}".\
               format(self.x,
                      self.y,
                      self.elevation)

    __unicode__ = __str__ = __repr__


def isGridPoint(gridPoint: Self) -> None:
    """
    Check if passed in object is a :class:`GridPoint`

    :param gridPoint: object under scrutiny
    :raises: TypeError if other not of :class:`GridPoint`
    """
    if not isinstance(gridPoint, GridPoint):
        raise TypeError("Expected GridPoint Object.")
