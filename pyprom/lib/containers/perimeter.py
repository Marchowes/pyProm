"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a Perimeter container class for storing GridPoints
type location objects. and various transforms.
"""
from collections import defaultdict
from .gridpoint import GridPointContainer
from ..locations.gridpoint import isGridPoint, GridPoint

DIAGONAL_SHIFT_LIST = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                       (0, -1), (-1, -1))
ORTHOGONAL_SHIFT_LIST = ((-1, 0), (0, 1), (1, 0), (0, -1))


class Perimeter:
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
        :param pointList: GridPoints which make up the Perimeter.
        :type pointList:
         list(:class:`pyprom.lib.locations.gridpoint.GridPoint`)
        :param pointIndex: Members as a dict().
        :type pointIndex:
         dict({X: { Y: :class:`pyprom.lib.locations.gridpoint.GridPoint`}}
        :param datamap: datamap which this :class:`Perimeter` uses.
        :type datamap: :class:`pyprom.lib.datamap.DataMap` object.
        :param bool mapEdge: is this a map edge?
        :param mapEdgePoints: list of Points on the map edge.
        :type mapEdgePoints:
         list(:class:`pyprom.lib.locations.gridpoint.GridPoint`)
        """
        super(Perimeter, self).__init__()
        self.points = list()
        if pointIndex:
            self.pointIndex = pointIndex
            self.points = [iep for x, _y in self.pointIndex.items()
                           for y, iep in _y.items()]

        if pointList:
            self.points = pointList
        self.datamap = datamap
        self.mapEdge = mapEdge
        self.mapEdgePoints = mapEdgePoints

    def iterNeighborDiagonal(self, point):
        """
        Iterate through diagonally and orthogonally neighboring
        :class:`pyprom.lib.locations.gridpoint.GridPoint` which are
        also members of this :class:`Perimeter`

        :param point: Gridpoint to find neighbors of
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        for shift in DIAGONAL_SHIFT_LIST:
            x = point.x + shift[0]
            y = point.y + shift[1]
            if self.pointIndex[x].get(y, False):
                yield self.pointIndex[x].get(y, False)
            else:
                continue

    def iterNeighborOrthogonal(self, point):
        """
        Iterate through orthogonally neighboring
        :class:`pyprom.lib.locations.gridpoint.GridPoint` which are
        also members of this :class:`Perimeter`

        :param point: Gridpoint to find neighbors of
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        for shift in ORTHOGONAL_SHIFT_LIST:
            x = point.x + shift[0]
            y = point.y + shift[1]
            if self.pointIndex[x].get(y, False):
                yield self.pointIndex[x].get(y, False)
            else:
                continue

    def to_dict(self):
        """
        Create the dictionary representation of this object.

        :return: dict() representation of :class:`Perimeter`
        :rtype: dict()
        """
        perimeterDict = dict()
        perimeterDict['points'] = [x.to_dict() for x in self.points]
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
            perimeterPointHash[pt['x']][pt['y']] =\
                GridPoint(pt['x'], pt['y'], pt['elevation'])
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
            if explored[point.x].get(point.y, False):
                continue
            if point.elevation > elevation:
                toBeAnalyzed = [point]
                highList = list()
                while True:
                    if not toBeAnalyzed:
                        highLists.append(highList)
                        break
                    else:
                        gridPoint = toBeAnalyzed.pop()
                    if not explored[gridPoint.x].get(gridPoint.y, False):
                        highList.append(gridPoint)
                        neighbors = [x for x in
                                     self.iterNeighborDiagonal(gridPoint)
                                     if x.elevation > elevation and
                                     not explored[x.x].get(x.y, False)]
                        toBeAnalyzed += neighbors
                        explored[gridPoint.x][gridPoint.y] = True
            else:
                explored[point.x][point.y] = True
        return [GridPointContainer(x) for x in highLists]

    def findHighPerimeter(self, elevation):
        """
        This function returns all points higher than the passed in
        elevation and returns them in a GridPointContainer.

        :param elevation:
        :type elevation: int, float
        :return: GridPointContainer containing high perimeter points.
        :rtype: :class:`pyprom.lib.containers.gridpoint.GridPointContainer`
        """
        higherPoints = [x for x in self.points if x.elevation > elevation]
        return GridPointContainer(higherPoints)

    def append(self, point):
        """
        Add a :class:`pyprom.lib.locations.gridpoint.GridPoint` to
        this container.

        :param point: GridPoint to append.
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :raises: TypeError if point not of
         :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        isGridPoint(point)
        self.points.append(point)

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
        :param point: GridPoint for setitem.
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :raises: TypeError if point not of
         :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        isGridPoint(point)
        self.points[idx] = point

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

    __unicode__ = __str__ = __repr__


def _isPerimeter(perimeter):
    """
    Check if passed in object is a :class:`Perimeter`

    :param perimeter: object under scrutiny
    :raises: TypeError if other not of :class:`Perimeter`
    """
    if not isinstance(perimeter, Perimeter):
        raise TypeError("Perimeter expected")
