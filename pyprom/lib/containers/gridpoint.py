"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing GridPoint
type location objects.
"""
import math
import sys

from .base_gridpoint import BaseGridPointContainer
from pyprom.lib.locations.gridpoint import GridPoint
from collections import defaultdict


class GridPointContainer(BaseGridPointContainer):
    """
    Container for GridPoint type lists.
    Allows for various list transformations and functions.
    """
    def __init__(self, gridPointList):
        super(GridPointContainer, self).__init__(gridPointList)
        self.fastLookup = defaultdict(dict)
        # Generate a fast lookup table.
        self.genFastLookup()

    def genFastLookup(self):
        """
        Generates a fast lookup hash of all gridpoints
        :return:
        """
        for gp in self.points:
            self.fastLookup[gp.x][gp.y] = gp

    def iterNeighborDiagonal(self, point):
        """
        Iterate through existing diagonal :class:`GridPoint`
        neighbors.
        :param GridPoint
        """
        if not len(self.fastLookup):
            self.genFastLookup()
        shiftList = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1],
                     [0, -1], [-1, -1]]
        for shift in shiftList:
            x = point.x+shift[0]
            y = point.y+shift[1]
            if self.fastLookup[x].get(y, False):
                yield self.fastLookup[x][y]
            else:
                continue

    def iterNeighborOrthogonal(self, point):
        """
        Iterate through existing orthogonal :class:`GridPoint`
        neighbors.
        :param GridPoint
        """
        if not len(self.fastLookup):
            self.genFastLookup()
        shiftList = [[-1, 0], [0, 1], [1, 0],  [0, -1]]
        for shift in shiftList:
            x = point.x+shift[0]
            y = point.y+shift[1]
            if self.fastLookup[x].get(y, False):
                yield self.fastLookup[x][y]
            else:
                continue

    def findPseudoSummits(self):
        """ Similiar in concept to finding summits and multipoint blobs,
         but smaller in scope.

        Essentially this returns locally scoped Summit points, that is,
        anything that meets the effective definition of a summit with all
        the available data in a GridPoint container.
        This is intended for use for finding high portions along an edge like:
        [1][2][3][2][2][3][4][4][3][2]
               ^           ^^^^
                PSEUDO SUMMITS (simple 1D example)
        No distinction is made between the pseudo summits. This is becasue
        these points are used as a jumping off point for Saddle -> Summit
        walks.
        """
        exploredGridPoints = defaultdict(dict)
        pseudoSummits = list()

        def equalHeightBlob(point):
            """
            Find pseudosummits which contain more than a single point.
            :param point:
            :return:
            """
            toBeAnalyzed = [point]
            analyzed = list()
            while toBeAnalyzed:
                gridPoint = toBeAnalyzed.pop()
                # officially declare that we're looking at this point.
                exploredGridPoints[gridPoint.x][gridPoint.y] = True
                analyzed.append(gridPoint)
                neighbors = self.iterNeighborDiagonal(gridPoint)
                for neighbor in neighbors:
                    if exploredGridPoints[neighbor.x].get(neighbor.y, None):
                        continue
                    # if the neighbor has the same elevation, explore it later
                    if neighbor.elevation == gridPoint.elevation and\
                            not exploredGridPoints[neighbor.x].get(
                                neighbor.y, None):
                        toBeAnalyzed.append(neighbor)
                    # if the neighbor is higher,
                    # the whole party is ruined, bail.
                    if neighbor.elevation > gridPoint.elevation:
                        return None
                # Didnt bail? must be a pseudoSummit
            return analyzed

        # Main Loop. Run through all points.
        for point in self.points:
            # already looked at it? move on.
            if exploredGridPoints[point.x].get(point.y, None):
                continue
            # officially declare that we're looking at this point.
            exploredGridPoints[point.x][point.y] = True
            skip = False
            for neighbor in self.iterNeighborDiagonal(point):
                # do we have equal height neighbors?
                if neighbor.elevation == point.elevation:
                    pseudos = equalHeightBlob(point)
                    if pseudos:
                        pseudoSummits += pseudos
                        skip = True
                        break
                # can't be a high point, bail.
                if neighbor.elevation > point.elevation:
                    skip = True
                    break
            if not skip:
                # Made it this far? must be a pseudosummit.
                pseudoSummits.append(point)
        return pseudoSummits

    def findClosestPoints(self, otherGridpointContainer):
        """
        Calculates and returns The the two closest GridPoints from `self`
        and `otherGridpointContainer` and their distance.
        :param otherGridpointContainer: GridPointContainer
        :return: GridPoint, GridPoint, distance
        """
        myClosest = None
        theirClosest = None
        closest_distance = sys.maxsize
        # Loop through all points in `self`
        for myPoint in self.points:
            # Loop through all points in `otherGridpointContainer`
            for theirPoint in otherGridpointContainer.points:
                # Calculate hypotenuse
                distance = math.sqrt((abs(myPoint.x - theirPoint.x) ** 2) +
                                     (abs(myPoint.y - theirPoint.y) ** 2))
                # if this is the shortest, set it as such.
                if distance < closest_distance:
                    myClosest = myPoint
                    theirClosest = theirPoint
                    closest_distance = distance
        return myClosest, theirClosest, closest_distance

    def __repr__(self):
        return "<GridPointContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__
