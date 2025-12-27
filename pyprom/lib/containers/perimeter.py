"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a Perimeter container class for storing GridPoints
type location objects. and various transforms.
"""
from collections import defaultdict
from .base_self_iterable import BaseSelfIterable
from ..logic.contiguous_neighbors import contiguous_neighbors
from ..locations.gridpoint import GridPoint
from typing import TYPE_CHECKING, Dict, List, Self
if TYPE_CHECKING:
    from pyprom import DataMap
    from pyprom._typing.type_hints import (
        XY_Elevation,
        Elevation,
        XY_Elevation_Fast_Dict,
        XY_Elevation_Generator,
    )


class Perimeter(BaseSelfIterable):
    """
    Container for :class:`Perimeter` type lists. A Perimeter
    is all points Diagonally or Orthogonally neighboring a
    member of a :class:`pyprom.lib.containers.multipoint.MultiPoint`
    """

    __slots__ = ['datamap', 'mapEdge', 'mapEdgePoints']

    def __init__(self, 
        pointList: List[XY_Elevation] | None = None,
        pointIndex:XY_Elevation_Fast_Dict | None = None,
        datamap: DataMap | None = None,
        mapEdge: bool = False,
        mapEdgePoints: List[XY_Elevation] | None = None
    ):
        """
        :param pointList: tuple(x, y, elevation) which make up the Perimeter.
        :type pointList:
            list(tuple(x, y, elevation))
        :param pointIndex: Members as a dict().
        :type pointIndex:
            dict({X: { Y: tuple(x, y, elevation)}}
        :param datamap: datamap which this :class:`Perimeter` uses.
        :type datamap: :class:`pyprom.lib.datamap.DataMap` object.
        :param bool mapEdge: is this a map edge?
        :param mapEdgePoints: list of Points (tuple) on the map edge.
        :type mapEdgePoints: list(tuple(x, y, ele))
        """

        super().__init__(
            pointList=pointList,
            pointIndex=pointIndex
        )

        self.datamap = datamap
        self.mapEdge = mapEdge
        self.mapEdgePoints = mapEdgePoints

    def to_dict(self) -> Dict:
        """
        Create the dictionary representation of this object.

        :return: dict() representation of :class:`Perimeter`
        :rtype: dict()
        """
        perimeterDict = dict()
        perimeterDict['points'] = self.points
        perimeterDict['mapEdge'] = self.mapEdge
        perimeterDict['mapEdgePoints'] = self.mapEdgePoints
        return perimeterDict

    @classmethod
    def from_dict(cls, 
            perimeterDict: dict, 
            datamap: DataMap | None = None
        ) -> Self:
        """
        Create this object from dictionary representation

        :param dict perimeterDict: dict() representation of this object.
        :param datamap: datamap which this Perimeter uses.
        :type datamap: :class:`pyprom.lib.datamap.DataMap` object.
        :return: a new Perimeter object.
        :rtype: :class:`Perimeter`
        """
        perimeterPointHash = defaultdict(dict)
        for pt in perimeterDict['points']:
            perimeterPointHash[pt[0]][pt[1]] = tuple(pt)
        mapEdge = perimeterDict['mapEdge']
        mapEdgePoints = [tuple(x) for x in perimeterDict['mapEdgePoints']]
        return cls(
            pointIndex=perimeterPointHash,
            datamap=datamap,
            mapEdge=mapEdge,
            mapEdgePoints=mapEdgePoints
        )

    def findHighPerimeterNeighborhoods(self, 
            elevation: Elevation
        ) -> List[List[XY_Elevation]]:
        """
        Finds all points that are higher than passed in elevation and returns
        them as a list of contiguous point lists

        :return: list of lists of points containing perimeter member points
            higher than elevation
        :rtype: list(list(tuples)))
        """
        return contiguous_neighbors(self.findHighPerimeter(elevation))

    def findHighPerimeter(self, 
            elevation: Elevation
        ) -> XY_Elevation:
        """
        This function returns all points higher than the passed in
        elevation and returns them in a list of tuples

        :param elevation:
        :type elevation: int, float
        :return: List of points as tuples
        :rtype: list(tuple(x, y, elevation))
        """
        return [x for x in self.points if x[2] > elevation]

    def append(self, point: GridPoint) -> None:
        """
        Add a :class:`pyprom.lib.locations.gridpoint.GridPoint` or tuple(x, y, elevation)
        to this container.

        :param point: GridPoint or tuple to append.
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :type point: tuple(x, y, elevation)
        """
        incoming = self._check_and_return_incoming_point_type(point)
        self.points.append(incoming)

    def __len__(self) -> int:
        """
        :return: number of items in `self.points`
        :rtype: int
        """
        return len(self.points)

    def __setitem__(self, idx: int, point) -> None:
        """
        Gives Perimeter list like set capabilities

        :param int idx: index value
        :param point: GridPoint or tuple for setitem.
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :type point: tuple(x, y, elevation)
        """
        incoming = self._check_and_return_incoming_point_type(point)
        self.points[idx] = incoming

    def __getitem__(self, idx: int) -> XY_Elevation:
        """
        Gives Perimeter list like get capabilities

        :param int idx: index value
        :return: :class:`pyprom.lib.locations.gridpoint.GridPoint`
            self.point at idx
        """
        return self.points[idx]

    def __eq__(self, other: Perimeter) -> bool:
        """
        Determines if this object is equal to another.

        :param other: other :class:`Perimeter` to check.
        :type: :class:`Perimeter`
        :return: equality
        :rtype: bool
        :raises: TypeError if other not of :class:`Perimeter`
        """
        _isPerimeter(other)
        return (
            sorted([x for x in self.points]) == 
            sorted([x for x in other.points])
        )

    def __ne__(self, other: Perimeter) -> bool:
        """
        Determines if this object is not equal to another.

        :param other: other :class:`Perimeter` to check.
        :type: :class:`Perimeter`
        :return: inequality
        :rtype: bool
        :raises: TypeError if other not of :class:`Perimeter`
        """
        _isPerimeter(other)
        return sorted([x for x in self.points]) != \
            sorted([x for x in other.points])

    def __iter__(self) -> XY_Elevation_Generator:
        """
        :return: `self.points` as iterator
        """
        for point in self.points:
            yield point

    def __repr__(self) -> str:
        """
        :return: String representation of this object
        """
        return "<Perimeter>" \
               " {} Objects".format(len(self.points))

    def _check_and_return_incoming_point_type(self, point: GridPoint | tuple) -> XY_Elevation:
        """
        Make sure incoming point type is a tuple with length 3, or explicitly a
        :class:`pyprom.lib.locations.gridpoint.GridPoint`

        :param point: tuple, or
         :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :raises: TypeError if point not of
         :class:`pyprom.lib.locations.gridpoint.GridPoint` or tuple
        :raises: Exception if tuple length != 3
        :return: tuple(x, y, elevation)
        """
        if isinstance(point, GridPoint):
            incoming = point.to_tuple()
        elif isinstance(point, tuple):
            incoming = point
        else:
            raise TypeError("point must be tuple, or GridPoint. Got: {}".format(type(point)))
        if len(incoming) != 3:
            raise Exception("tuple must have length of 3, or object must be GridPoint")
        return incoming

    __unicode__ = __str__ = __repr__


def _isPerimeter(perimeter) -> bool:
    """
    Check if passed in object is a :class:`Perimeter`

    :param perimeter: object under scrutiny
    :raises: TypeError if other not of :class:`Perimeter`
    """
    if not isinstance(perimeter, Perimeter):
        raise TypeError("Perimeter expected")
