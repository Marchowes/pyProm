"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""
from collections import defaultdict
from .gridpoint import GridPointContainer
from ..locations.gridpoint import isGridPoint


class Perimeter(object):
    """
    Container for :class:`Perimeter` type lists.
    Allows for various list transformations.
    :param pointList: list of :class:`PerimeterPoint` to
     self.points
    :param pointIndex: {X: { Y: :class:`PerimeterPoint`}} passing
    this will automatically generate self.points
    """
    def __init__(self, pointList=None,
                 pointIndex=None,
                 datamap=None, mapEdge=False):
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

    def iterNeighborDiagonal(self, point):
        """
        Iterate through existing diagonal :class:`PerimeterPoint`
        neighbors.
        :param point:
        """
        shiftList = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1],
                     [0, -1], [-1, -1]]
        for shift in shiftList:
            x = point.x+shift[0]
            y = point.y+shift[1]
            if self.pointIndex[x].get(y, False):
                if -1 <= x <= self.datamap.max_x + 1\
                        and -1 <= y <= self.datamap.max_y + 1:
                    yield self.pointIndex[x].get(y, False)
            else:
                continue

    def iterNeighborOrthogonal(self, point):
        """
        Iterate through existing orthogonal :class:`PerimeterPoint`
        neighbors.
        :param point:
        """

        shiftList = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        for shift in shiftList:
            x = point.x + shift[0]
            y = point.y + shift[1]
            if self.pointIndex[x].get(y, False):
                if -1 <= x <= self.datamap.max_x + 1 \
                        and -1 <= y <= self.datamap.max_y + 1:
                    yield self.pointIndex[x].get(y, False)
            else:
                continue

    def findHighEdges(self, elevation):
        """
        This function returns a list of GridpointContainers. Each container
        holds a list of perimeterPoints which are discontigous so far as
        the other container is concerned. This is used to identify discontigous
        sets of perimeterPoints for determining if this is a Saddle or not.
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
    `   Gives Perimeter list like get capabilities
        :param idx: index value
        :return: :class:`SpotElevation` self.point at idx
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

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<Perimeter>" \
               " {} Objects".format(len(self.points))

    def __iter__(self):
        for point in self.points:
            yield point

    __unicode__ = __str__ = __repr__


def _isPerimeter(perimeter):
    """
    :param perimeter: object under scrutiny
    :raises: TypeError if other not of :class:`Perimeter`
    """
    if not isinstance(perimeter, Perimeter):
        raise TypeError("Perimeter expected")