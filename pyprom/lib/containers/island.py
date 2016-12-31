"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for creating Islands.
"""

from collections import defaultdict
from .base_gridpoint import BaseGridPointContainer
from ..locations.gridpoint import GridPoint


class Island(BaseGridPointContainer):
    """
    Island Object accepts a list of shore points, and a MultiPoint object
    which is a Pond-type object. points are calculated in fillIn()
    """
    def __init__(self, shoreGridPointList, datamap, pondElevation):
        super(Island, self).__init__(shoreGridPointList)
        self.shoreGridPointList = self.points[:]
        self.pondElevation = pondElevation
        self.datamap = datamap
        self.fillIn()
        self.mapEdge = self.findMapEdge()

    def findMapEdge(self):
        """
        :return: list of SpotElevation Points along the map Edge.
        """
        mapEdge = list()
        for point in self.points:
            if point.x == 0 or point.x == \
                    self.datamap.max_x:
                mapEdge.append(point.toSpotElevation(self.datamap))
            if point.y == 0 or point.y ==\
                    self.datamap.max_y:
                mapEdge.append(point.toSpotElevation(self.datamap))
        return mapEdge

    def fillIn(self):
        """
        Function uses shore GridPoints and water body elevation to find all
        points on island. Object "points" are then replaced with GridPoints
        found.
        """

        # Grabs first point (which is a shore) and prefills in hashes
        toBeAnalyzed = [self.points[0]]
        islandHash = defaultdict(list)
        islandHash[toBeAnalyzed[0].x].append(toBeAnalyzed[0].x)
        islandGridPoints = toBeAnalyzed[:]

        # Find all points not at pond-level.
        while toBeAnalyzed:
            gridPoint = toBeAnalyzed.pop()
            neighbors = self.datamap.iterateDiagonal(gridPoint.x,
                                                     gridPoint.y)
            for _x, _y, elevation in neighbors:

                if elevation != self.pondElevation and _y not in\
                                islandHash[_x]:
                    branch = GridPoint(_x, _y, elevation)
                    islandHash[_x].append(_y)
                    toBeAnalyzed.append(branch)
                    islandGridPoints.append(branch)
        self.points = islandGridPoints

    def __repr__(self):
        return "<Island> {} Point Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__
