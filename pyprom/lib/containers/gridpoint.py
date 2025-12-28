"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing GridPoint
type location objects.
"""
from __future__ import annotations

import sys

from .base_gridpoint import BaseGridPointContainer
from pyprom.lib.locations.gridpoint import GridPoint, isGridPoint
from collections import defaultdict

from typing import TYPE_CHECKING, List, Self, Dict, Generator, Tuple
if TYPE_CHECKING:
    from pyprom._typing.type_hints import XY_Elevation
    from pyprom.lib.locations.gridpoint import GridPoint


class GridPointContainer(BaseGridPointContainer):
    """
    GridPoint Container for GridPoint type lists.
    Storage and functions for :class:`pyprom.lib.locations.gridpoint.GridPoint`
    """

    __slots__ = ['fastLookup']

    def __init__(self, gridPointList: List[GridPoint]):
        """
        :param gridPointList: list of GridPoints
        :type gridPointList:
         list(:class:`pyprom.lib.locations.gridpoint.GridPoint`)
        :raises: TypeError when gridPointList contains non
         :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        super(GridPointContainer, self).__init__(gridPointList)
        if len([x for x in gridPointList if not isinstance(x, GridPoint)]):
            raise TypeError("gridPointList passed to GridPointContainer"
                            " can only contain GridPoint objects.")

        self.fastLookup = defaultdict(dict)
        # Generate a fast lookup table.
        self.genFastLookup()

    def to_dict(self) -> dict:
        """
        Create the dictionary representation of this object.

        :return: dict() representation of :class:`GridPointContainer`
        :rtype: dict()
        """
        gpcDict = {"points": [x.to_dict() for x in self.points]}
        return gpcDict

    @classmethod
    def from_dict(cls, gpcDict: dict) -> Self:
        """
        Create this object from dictionary representation

        :param dict gpcDict: dict representation of :class:`GridPointContainer`
        :return: a new GridPointContainer
        :rtype: :class:`GridPointContainer`
        """
        points = [GridPoint(pt['x'], pt['y'], pt['elevation'])
                  for pt in gpcDict['points']]
        obj = cls(points)
        obj.genFastLookup()
        return obj

    @property
    def lowest(self) -> List[GridPoint]:
        """
        :return: list of lowest GridPoint objects found in this container
        :rtype: list(:class:`pyprom.lib.locations.gridpoint.GridPoint`)
        """
        low = self.points[0].elevation
        lowest = list()
        for gridPoint in self.points:
            if gridPoint.elevation < low:
                low = gridPoint.elevation
                lowest = list()
                lowest.append(gridPoint)
            elif gridPoint.elevation == low:
                lowest.append(gridPoint)
        return lowest

    @property
    def highest(self) -> List[GridPoint]:
        """
        :return: list of highest GridPoint objects found in this container
        :rtype: list(:class:`pyprom.lib.locations.gridpoint.GridPoint`)
        """
        high = self.points[0].elevation
        highest = list()
        for gridPoint in self.points:
            if gridPoint.elevation > high:
                high = gridPoint.elevation
                highest = list()
                highest.append(gridPoint)
            elif gridPoint.elevation == high:
                highest.append(gridPoint)
        return highest

    def genFastLookup(self) -> Dict[int, Dict[int, bool]]:
        """
        Generates a fast lookup hash of all GridPoints in this container
        in the format of:
        {x: {y: :class:`pyprom.lib.locations.gridpoint.GridPoint`}}
        """
        for gp in self.points:
            self.fastLookup[gp.x][gp.y] = gp

    def iterNeighborFull(self, point: GridPoint) -> Generator[GridPoint]:
        """
        Iterate through existing diagonal/orthogonal
        :class:`pyprom.lib.locations.gridpoint.GridPoint`
        neighbors found in this :class:`GridPointContainer`.

        :param point: gridpoint to find neighbors of.
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :rtype: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        if not len(self.fastLookup):
            self.genFastLookup()
        shiftList = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                     (0, -1), (-1, -1))
        for shift in shiftList:
            x = point.x + shift[0]
            y = point.y + shift[1]
            if self.fastLookup[x].get(y, False):
                yield self.fastLookup[x][y]
            else:
                continue

    def iterNeighborOrthogonal(self, point: GridPoint) -> Generator[GridPoint]:
        """
        Iterate through existing orthogonal
        :class:`pyprom.lib.locations.gridpoint.GridPoint`
        neighbors found in this :class:`GridPointContainer`.

        :param point: gridpoint to find neighbors of.
        :type point: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :rtype: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        if not len(self.fastLookup):
            self.genFastLookup()
        shiftList = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        for shift in shiftList:
            x = point.x + shift[0]
            y = point.y + shift[1]
            if self.fastLookup[x].get(y, False):
                yield self.fastLookup[x][y]
            else:
                continue

    def findPseudoSummits(self) -> List[GridPoint]:
        """
        | Similiar in concept to finding summits and multipoint blobs,
        | but smaller in scope.
        |
        | Essentially this returns locally scoped Summit points, that is,
        | anything that meets the effective definition of a summit with all
        | the available data in a :class:`GridPointContainer`.
        | This is intended for use for finding high portions along an edge like:
        | ``[1][2][3][2][2][3][4][4][3][2]``
        | ``       ^           ^^^^``
        | ``       PSEUDO SUMMITS (simple 1D example)``
        | No distinction is made between the pseudo summits. This is becasue
        | these points are used as a jumping off point for Saddle -> Summit
        | walks.
        """
        exploredGridPoints = defaultdict(dict)
        pseudoSummits = list()

        def equalHeightBlob(point: GridPoint) -> List[GridPoint]:
            """
            Find pseudosummits which contain more than a single point.

            :param point: gridpoint for analysis
            :type param: :class:`pyprom.lib.locations.gridpoint.GridPoint`
            :return: list of GridPoints
            :rtype: list(:class:`pyprom.lib.locations.gridpoint.GridPoint`)
            """
            toBeAnalyzed = [point]
            analyzed = list()
            while toBeAnalyzed:
                gridPoint = toBeAnalyzed.pop()
                # officially declare that we're looking at this point.
                exploredGridPoints[gridPoint.x][gridPoint.y] = True
                analyzed.append(gridPoint)
                neighbors = self.iterNeighborFull(gridPoint)
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
            for neighbor in self.iterNeighborFull(point):
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

    def findClosestPoints(self, otherGridpointContainer: Self) -> Tuple[GridPoint, GridPoint, float]:
        """
        Calculates and returns The the two closest
        :class:`pyprom.lib.locations.gridpoint.GridPoint`
        objects from this :class:`GridPointContainer`
        and `otherGridpointContainer` and their distance.

        :param otherGridpointContainer: The other
         :class:`GridPointContainer` to compare against.
        :type otherGridPointContainer: :class:`GridPointContainer`
        :return: This :class:`GridPointContainer` and
         other  :class:`GridPointContainer` closest
         :class:`pyprom.lib.locations.gridpoint.GridPoint`, and
         distance between them.
        :rtype: :class:`pyprom.lib.locations.gridpoint.GridPoint`,
         :class:`pyprom.lib.locations.gridpoint.GridPoint`, float
        """
        myClosest = None
        theirClosest = None
        closest_distance = sys.maxsize
        # Loop through all points in `self`
        for myPoint in self.points:
            # Loop through all points in `otherGridpointContainer`
            for theirPoint in otherGridpointContainer.points:
                distance = myPoint.distance(theirPoint)
                # if this is the shortest, set it as such.
                if distance < closest_distance:
                    myClosest = myPoint
                    theirClosest = theirPoint
                    closest_distance = distance
        return myClosest, theirClosest, closest_distance

    def append(self, gridPoint: GridPoint) -> None:
        """
        Append a :class:`pyprom.lib.locations.gridpoint.GridPoint`
        to the container.

        :param gridPoint: GridPoint to append
        :type gridPoint: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :raises: TypeError if gridPoint not of
         :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        isGridPoint(gridPoint)
        self.points.append(gridPoint)
        self.genFastLookup()

    def to_tuples(self) -> List[XY_Elevation]:
        """
        :return: :class:`GridPointContainer` members as a list of
         (x, y, elevation) tuples.
        """
        return [x.to_tuple() for x in self.points]

    def __repr__(self) -> str:
        """
        :return: String representation of this object
        """
        return "<GridPointContainer> {} Objects".format(len(self.points))

    __str__ = __repr__
