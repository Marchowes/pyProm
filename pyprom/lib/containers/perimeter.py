"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a Perimeter container class for storing GridPoints
type location objects. and various transforms.
"""
from collections import defaultdict
from .gridpoint import GridPointContainer
from .base_self_iterable import BaseSelfIterable
from ..locations.gridpoint import GridPoint


class Perimeter(BaseSelfIterable):
    """
    Container for :class:`Perimeter` type lists. A Perimeter
    is all points Diagonally or Orthogonally neighboring a
    member of a :class:`pyprom.lib.containers.multipoint.MultiPoint`
    """

    def __init__(self, pointList=None,
                 pointIndex=None,
                 datamap=None,
                 mapEdge=False,
                 mapEdgePoints=None):
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
        :param mapEdgePoints: list of Points on the map edge.
        :type mapEdgePoints:
         list(:class:`pyprom.lib.locations.gridpoint.GridPoint`)
        """
        self.points = list()
        if pointList and pointIndex:
            raise Exception("choose one, pointList or PointIndex")
        if pointIndex:
            self.pointIndex = pointIndex
            self.points = [iep for x, _y in self.pointIndex.items()
                           for y, iep in _y.items()]

        if pointList:
            self.points = pointList
            self.pointIndex = defaultdict(dict)
            for point in self.points:
                self.pointIndex[point[0]][point[1]] = point

        self.datamap = datamap
        self.mapEdge = mapEdge
        self.mapEdgePoints = mapEdgePoints

    def to_dict(self):
        """
        Create the dictionary representation of this object.

        :return: dict() representation of :class:`Perimeter`
        :rtype: dict()
        """
        perimeterDict = dict()
        perimeterDict['points'] = self.points
        perimeterDict['mapEdge'] = self.mapEdge
        perimeterDict['mapEdgePoints'] = [x.to_dict()
                                          for x in self.mapEdgePoints]
        return perimeterDict

    @classmethod
    def from_dict(cls, perimeterDict, datamap=None):
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
            perimeterPointHash[pt[0]][pt[1]] =\
                tuple(pt)
        mapEdge = perimeterDict['mapEdge']
        mapEdgePoints = [GridPoint(x['x'], x['y'], x['elevation'])
                         for x in perimeterDict['mapEdgePoints']]
        return cls(pointIndex=perimeterPointHash,
                   datamap=datamap,
                   mapEdge=mapEdge,
                   mapEdgePoints=mapEdgePoints)

    def findHighEdges(self, elevation):
        """
        This function returns a list of
        :class:`pyprom.lib.containers.gridpoint.GridPointContainer`. Each
        container holds a list of
        :class:`pyprom.lib.locations.gridpoint.GridPoint` which are
        discontigous so far as the other container is concerned.
        This is used to identify discontigous sets of
        :class:`pyprom.lib.locations.gridpoint.GridPoint` for determining
        if this is a :class:`pyprom.lib.locations.saddle.Saddle` or not.

        :return: list of GridPointContainers containing HighEdges.
        :rtype:
         list(:class:`pyprom.lib.containers.gridpoint.GridPointContainer`)
        """
        explored = defaultdict(dict)
        highLists = list()
        for point in self.points:
            if explored[point[0]].get(point[1], False):
                continue
            if point[2] > elevation:
                toBeAnalyzed = [point]
                highList = list()
                while True:
                    if not toBeAnalyzed:
                        highLists.append(highList)
                        break
                    else:
                        gridPoint = toBeAnalyzed.pop()
                    if not explored[gridPoint[0]].get(gridPoint[1], False):
                        highList.append(GridPoint.from_tuple(gridPoint))
                        neighbors = [x for x in
                                     self.iterNeighborDiagonal(gridPoint)
                                     if x[2] > elevation and
                                     not explored[x[0]].get(x[1], False)]
                        toBeAnalyzed += neighbors
                        explored[gridPoint[0]][gridPoint[1]] = True
            else:
                explored[point[0]][point[1]] = True
        return [GridPointContainer(x) for x in highLists]

    def findHighPerimeter(self, elevation, as_tuples=False):
        """
        This function returns all points higher than the passed in
        elevation and returns them in a GridPointContainer. Unless
        as_tuples is True, then a list of tuples is returned.

        :param elevation:
        :type elevation: int, float
        :param as_tuples: returns result as list of (x, y, elevation) tuples
        :return: GridPointContainer containing high perimeter points.
        :rtype: :class:`pyprom.lib.containers.gridpoint.GridPointContainer`
        :return: List of points as tuples
        :rtype: list(tuple(x, y, elevation))
        """
        if as_tuples:
            return [x for x in self.points if x[2] > elevation]
        else:
            higherPoints = [GridPoint.from_tuple(x) for x in self.points if x[2] > elevation]
            return GridPointContainer(higherPoints)

    def append(self, point):
        """
        Add a :class:`pyprom.lib.locations.gridpoint.GridPoint` or tuple(x, y, elevation)
        to this container.

        :param point: GridPoint or tuple to append.
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :type point: tuple(x, y, elevation)
        """
        incoming = self._check_and_return_incoming_point_type(point)
        self.points.append(incoming)

    def __len__(self):
        """
        :return: number of items in `self.points`
        :rtype: int
        """
        return len(self.points)

    def __setitem__(self, idx, point):
        """
        Gives Perimeter list like set capabilities

        :param int idx: index value
        :param point: GridPoint or tuple for setitem.
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :type point: tuple(x, y, elevation)
        """
        incoming = self._check_and_return_incoming_point_type(point)
        self.points[idx] = incoming

    def __getitem__(self, idx):
        """
        Gives Perimeter list like get capabilities

        :param int idx: index value
        :return: :class:`pyprom.lib.locations.gridpoint.GridPoint`
         self.point at idx
        """
        return self.points[idx]

    def __eq__(self, other):
        """
        Determines if this object is equal to another.

        :param other: other :class:`Perimeter` to check.
        :type: :class:`Perimeter`
        :return: equality
        :rtype: bool
        :raises: TypeError if other not of :class:`Perimeter`
        """
        _isPerimeter(other)
        return sorted([x for x in self.points]) == \
            sorted([x for x in other.points])

    def __ne__(self, other):
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

    def __iter__(self):
        """
        :return: `self.points` as iterator
        """
        for point in self.points:
            yield point

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<Perimeter>" \
               " {} Objects".format(len(self.points))

    def _check_and_return_incoming_point_type(self, point):
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


def _isPerimeter(perimeter):
    """
    Check if passed in object is a :class:`Perimeter`

    :param perimeter: object under scrutiny
    :raises: TypeError if other not of :class:`Perimeter`
    """
    if not isinstance(perimeter, Perimeter):
        raise TypeError("Perimeter expected")
