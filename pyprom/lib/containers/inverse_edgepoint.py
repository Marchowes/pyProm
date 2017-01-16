"""
pyProm: Copyright 2016

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
        if inverseEdgePointIndex:
            self.inverseEdgePointIndex = inverseEdgePointIndex
            self.points = [v[1] for x, y in self.inverseEdgePointIndex.items()
                           for v in y.items()]
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
            if self.inverseEdgePointIndex[x][y]:
                if -1 <= x <= self.datamap.max_x + 1\
                        and -1 <= y <= self.datamap.max_y + 1:
                    yield self.inverseEdgePointIndex[x][y]
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
            if self.inverseEdgePointIndex[x][y]:
                if -1 <= x <= self.datamap.max_x + 1 \
                        and -1 <= y <= self.datamap.max_y + 1:
                    yield self.inverseEdgePointIndex[x][y]
            else:
                continue

    def findHighEdges(self, elevation):
        """
        Hopefully a way more efficient way of finding high edges.
        :return:
        """
        purgedIndex = defaultdict(list)
        highLists = list()
        for point in self.points:
            if point.y in purgedIndex[point.x]:
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
                    if gridPoint.y not in purgedIndex[gridPoint.x]:
                        highList.append(gridPoint)
                        neighbors = [x for x in
                                     self.iterNeighborDiagonal(gridPoint)
                                     if x.elevation > elevation and
                                     x.y not in purgedIndex[x.x]]
                        toBeAnalyzed += neighbors
                        purgedIndex[gridPoint.x].append(gridPoint.y)
            else:
                purgedIndex[point.x].append(point.y)
        return [GridPointContainer(x) for x in highLists]

    def __repr__(self):
        return "<InverseEdgePointContainer>" \
               " {} Objects".format(len(self.points))

    def __iter__(self):
        for inverseEdgePoint in self.points:
            yield inverseEdgePoint

    __unicode__ = __str__ = __repr__
