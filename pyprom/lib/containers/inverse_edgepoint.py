"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""

from collections import defaultdict
from .base import _Base
from .shore import ShoreContainer


class InverseEdgePointContainer(_Base):
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
        self.exemptPoints = defaultdict(list)
        self.mapEdge = mapEdge
        self.branchMapEdge = False

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

    def findLinear(self):
        """
        :return: list of GridPoint containers representing individual edges
        """

        shoreContainers = list()
        self.exemptPoints = defaultdict(list)

        rounds = 0
        self.edge = list()
        one = list()

        # Find points with exactly one neighbor. These are edgepoints.
        # Subdivide these into two groups, edges and stubs.

        for point in (pt for pt in self.points):
            neighbors = [x for x in self.iterNeighborOrthogonal(point)]
            if len(neighbors) == 1:
                if point.x in [self.datamap.max_x, 0] or\
                                point.y in [self.datamap.max_y, 0]:
                    self.edge.append(point)
            if len(neighbors) == 1:
                one.append(point)

        # order the points
        scanOrder = self.edge + one + self.points

        while True:
            rounds += 1
            for point in (pt for pt in scanOrder
                          if pt.y not in self.exemptPoints[pt.x]):
                neighbors = [x for x in self.iterNeighborOrthogonal(point)]
                masterPoint = point

                if not len(neighbors):
                    self.exemptPoints[point.x].append(point.y)
                    if point.x in (0, self.datamap.max_x) or \
                       point.y in (0, self.datamap.max_y):
                        shoreContainers.append(ShoreContainer([point], True))
                    else:
                        shoreContainers.append(ShoreContainer([point]))
                    break

                firstPoint = neighbors[0]
                shoreContainers.append(ShoreContainer(
                    self.branchChaser(masterPoint,
                                      masterPoint,
                                      firstPoint), self.branchMapEdge))
                self.branchMapEdge = False
                break

            if not len([pt for pt in self.points if pt.y not in
                        self.exemptPoints[pt.x]]):
                return shoreContainers
            if rounds > 100:
                self.logger.info('Something broke in {}'.format(self))
                return shoreContainers

    def branchChaser(self, masterPoint, originalPoint, firstPoint):
        """
        Recursive function for chasing down inverse edge Branches
        :param masterPoint: Master point for this segment. This is
         passed all the way through.
        :param originalPoint: Original Point Branch under analysis.
        :param firstPoint: First point, this is a neighbor of the
         OriginalPoint and determines the direction of analysis travel.
        :return: ordered List of points.
        """

        lookbackPoint = originalPoint
        currentPoint = firstPoint

        orderedList = [originalPoint]

        while True:
            # First, we find all neighbors who are not the original point,
            # a lookback point, the master point, or an already analyzed point.

            neighbors = [pt for pt in self.iterNeighborOrthogonal(currentPoint)
                         if pt not in [lookbackPoint,
                                       originalPoint,
                                       masterPoint]]
            neighbors = [pt for pt in neighbors
                         if pt.y not in self.exemptPoints[pt.x]]

            # More than one neighbor? We'll need to look back at the last
            # point and find how common neighbors we have.
            commonEdgeHash = defaultdict(list)
            if currentPoint.x in (0, self.datamap.max_x) or\
               currentPoint.y in (0, self.datamap.max_y):
                self.branchMapEdge = True
            if len(neighbors) > 1:
                for neighbor in neighbors:
                    commonEdgePoints =\
                        len(set(neighbor.edgePoints).
                            intersection(lookbackPoint.edgePoints))
                    commonEdgeHash[commonEdgePoints].append(neighbor)

                # Look for the neighbors with the most EdgePoints in common
                if len(commonEdgeHash[max(commonEdgeHash.keys())]) != 1:
                    level1CommonEdgeHash = defaultdict(list)
                    # a bunch of neighbors with no common EdgePoints? Lets
                    # look for common edges with the neighbors
                    if max(commonEdgeHash.keys()) == 0:
                        for nei in commonEdgeHash[0]:
                            level1CommonEdgePoints = len(nei.edgePoints)
                            level1CommonEdgeHash[level1CommonEdgePoints].\
                                append(nei)

                        if len(level1CommonEdgeHash[max(
                                level1CommonEdgeHash.keys())]) != 1:
                            # Fucking hell, they're equal. Guess we'll just
                            # choose the first one anyways.
                            self.logger.debug("Highly unusual Branch "
                                              "Exception! on {}".format(self))
                            self.logger.debug(
                                "TroubleMakers {}".format(currentPoint))

                        orderedList +=\
                            self.branchChaser(
                                masterPoint,
                                currentPoint,
                                level1CommonEdgeHash[max(
                                    level1CommonEdgeHash.keys())][0])
                        continue
                else:
                    # Follow the branch with the most common neighbors.
                    orderedList +=\
                        self.branchChaser(
                            masterPoint,
                            currentPoint,
                            commonEdgeHash[max(commonEdgeHash.keys())][0])
                    continue

            # Not exempt? Add to the ordered list.
            if currentPoint.y not in self.exemptPoints[currentPoint.x]:
                # Last modification in PR, delete this comment someday.
                self.exemptPoints[currentPoint.x].append(currentPoint.y)
                orderedList.append(currentPoint)

            if len(neighbors) == 0:
                # End of the line? return the ordered list.
                for point in orderedList:
                    self.exemptPoints[point.x].append(point.y)
                return orderedList

            # Just one neighbor? Okay, do this...
            lookbackPoint = currentPoint
            currentPoint = neighbors[0]

    def __repr__(self):
        return "<InverseEdgePointContainer>" \
               " {} Objects".format(len(self.points))

    def __iter__(self):
        for inverseEdgePoint in self.points:
            yield inverseEdgePoint

    __unicode__ = __str__ = __repr__
