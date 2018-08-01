"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a Perimeter container class for storing GridPoints
type location objects. and various transforms.
"""
from collections import defaultdict
from .gridpoint import GridPointContainer
from ..locations.gridpoint import isGridPoint

DIAGONAL_SHIFT_LIST = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                       (0, -1), (-1, -1))
ORTHOGONAL_SHIFT_LIST = ((-1, 0), (0, 1), (1, 0), (0, -1))


class Perimeter:
    """
    Container for :class:`Perimeter` type lists.
    Allows for various list transformations.
    """

    def __init__(self, pointList=None,
                 pointIndex=None,
                 datamap=None,
                 mapEdge=False,
                 mapEdgePoints=None):
        """

        :param pointList: pointList: list of :class:`GridPoint` to
        self.points
        :param pointIndex: pointIndex: {X: { Y: :class:`GridPoint`}} passing
        this will automatically generate self.points
        :param datamap: datamap object
        :param mapEdge: (bool) is this a map edge?
        :param mapEdgePoints: :class:`GridPoint` list of Points on
         the map edge.
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
        Iterate through existing diagonal :class:`GridPoint`
        neighbors.
        :param point:
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
        Iterate through existing orthogonal :class:`GridPoint`
        neighbors.
        :param point:
        """
        for shift in ORTHOGONAL_SHIFT_LIST:
            x = point.x + shift[0]
            y = point.y + shift[1]
            if self.pointIndex[x].get(y, False):
                yield self.pointIndex[x].get(y, False)
            else:
                continue

    def findHighEdges(self, elevation):
        """
        This function returns a list of GridpointContainers. Each container
        holds a list of GridPoints which are discontigous so far as
        the other container is concerned. This is used to identify discontigous
        sets of GridPoints for determining if this is a Saddle or not.
        :return: list of GridPointContainers containing HighEdges.
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
        :return: GridPointContainer
        """
        higherPoints = [x for x in self.points if x.elevation > elevation]
        return GridPointContainer(higherPoints)

    def append(self, point):
        """
        Add a GridPoint to the container.
        :param point: :class:`GridPoint`
        :raises: TypeError if point not of :class:`GridPoint`
        """
        isGridPoint(point)
        self.points.append(point)

    def __len__(self):
        """
        :return: integer - number of items in self.points
        """
        return len(self.points)

    def __setitem__(self, idx, point):
        """
        Gives Perimeter list like set capabilities
        :param idx: index value
        :param point: :class:`SpotElevation`
        :raises: TypeError if point not of :class:`GridPoint`
        """
        isGridPoint(point)
        self.points[idx] = point

    def __getitem__(self, idx):
        """
        Gives Perimeter list like get capabilities
        :param idx: index value
        :return: :class:`Gridpoint` self.point at idx
        """
        return self.points[idx]

    def __eq__(self, other):
        """
        Determines if Perimeter is equal to another.
        :param other: :class:`Perimeter`
        :return: bool of equality
        :raises: TypeError if other not of :class:`Perimeter`
        """
        _isPerimeter(other)
        return sorted([x for x in self.points]) == \
            sorted([x for x in other.points])

    def __ne__(self, other):
        """
        :param other: :class:`Perimeter`
        :return: bool of inequality
        :raises: TypeError if other not of :class:`Perimeter`
        """
        _isPerimeter(other)
        return sorted([x for x in self.points]) != \
            sorted([x for x in other.points])

    def __iter__(self):
        """
        :return: iterator for self.points
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
    :param perimeter: object under scrutiny
    :raises: TypeError if other not of :class:`Perimeter`
    """
    if not isinstance(perimeter, Perimeter):
        raise TypeError("Perimeter expected")
