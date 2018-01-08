"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""
from collections import defaultdict
from .gridpoint import GridPointContainer


class InverseEdgePointContainer(object):
    """
    Container for :class:`InverseEdgePoint` type lists.
    Allows for various list transformations.
    :param inverseEdgePointList: list of :class:`InverseEdgePoint` to
     self.points
    :param inverseEdgePointIndex: {X: { Y: :class:`InverseEdgePoint`}} passing
    this will automatically generate self.points
    """
    def __init__(self, inverseEdgePointList=None,
                 inverseEdgePointIndex=None,
                 datamap=None, mapEdge=False):
        super(InverseEdgePointContainer, self).__init__()
        self.points = list()
        if inverseEdgePointIndex:
            self.inverseEdgePointIndex = inverseEdgePointIndex
            self.points = [iep for x, _y in self.inverseEdgePointIndex.items()
                           for y, iep in _y.items()]
        if inverseEdgePointList:
            self.points = inverseEdgePointList
        self.datamap = datamap
        self.mapEdge = mapEdge

    def iterNeighborDiagonal(self, inverseEdgePoint):
        """
        Iterate through existing diagonal :class:`InverseEdgePoint`
        neighbors.
        :param inverseEdgePoint:
        """
        shiftList = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1],
                     [0, -1], [-1, -1]]
        for shift in shiftList:
            x = inverseEdgePoint.x+shift[0]
            y = inverseEdgePoint.y+shift[1]
            if self.inverseEdgePointIndex[x].get(y, False):
                if -1 <= x <= self.datamap.max_x + 1\
                        and -1 <= y <= self.datamap.max_y + 1:
                    yield self.inverseEdgePointIndex[x].get(y, False)
            else:
                continue

    def iterNeighborOrthogonal(self, inverseEdgePoint):
        """
        Iterate through existing orthogonal :class:`InverseEdgePoint`
        neighbors.
        :param inverseEdgePoint:
        """

        shiftList = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        for shift in shiftList:
            x = inverseEdgePoint.x + shift[0]
            y = inverseEdgePoint.y + shift[1]
            if self.inverseEdgePointIndex[x].get(y, False):
                if -1 <= x <= self.datamap.max_x + 1 \
                        and -1 <= y <= self.datamap.max_y + 1:
                    yield self.inverseEdgePointIndex[x].get(y, False)
            else:
                continue

    def findHighEdges(self, elevation):
        """
        Hopefully a way more efficient way of finding high edges.
        :return:
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

    def findHighInverseEdgePoints(self, elevation):
        """
        This function returns all inverseEdgePoints higher than the passed in
        elevation and returns them in a GridPointContainer.
        :param elevation:
        :return: GridPointContainer
        """

        higherPoints = [x for x in self.points if x.elevation > elevation]
        return GridPointContainer(higherPoints)



    def __repr__(self):
        return "<InverseEdgePointContainer>" \
               " {} Objects".format(len(self.points))

    def __iter__(self):
        for inverseEdgePoint in self.points:
            yield inverseEdgePoint

    __unicode__ = __str__ = __repr__
