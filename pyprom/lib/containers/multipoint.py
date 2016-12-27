"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Multipoint
type location objects as well as a number of functions.
"""
import json
from collections import (defaultdict,
                         Counter)
from .gridpoint import GridPointContainer
from .island import Island
from ..locations.base_coordinate import BaseCoordinate
from ..locations.gridpoint import GridPoint
from ..location_util import findExtremities


class MultiPoint(object):
    """
    This is an "equal height" Multipoint storage container that
    provides a number of functions for analysis of these blob like
    locations. An Example of this would be a pond. This object in
    contains a list of all the points of this pond.
    :param points: list of BaseGridPoint objects
    :param elevation: elevation in meters
    :param datamap: :class:`Datamap` object.
    :param edgePoints: :class:`EdgePointContainer` object
    :param inverseEdgePoints: :class:`InverseEdgePointContainer` object
    """
    def __init__(self, points, elevation, datamap,
                 edgePoints=None, inverseEdgePoints=None):
        super(MultiPoint, self).__init__()
        self.points = points  # BaseGridPoint Object.
        self.elevation = elevation
        self.datamap = datamap  # data analysis object.
        self.edgePoints = edgePoints
        self.inverseEdgePoints = inverseEdgePoints
        self.mapEdge = []

    def to_dict(self, verbose=True):
        """
        :param verbose: returns extra data like `InverseEdgePoint`
        and `EdgePoint` (future)
        :return: list of dicts.
        """
        plist = list()
        for point in self.points:
            pdict = dict()
            pdict['gridpoint'] = point.to_dict()
            pdict['coordinate'] = \
                BaseCoordinate(self.datamap.x_position_latitude(point.x),
                               self.datamap.y_position_longitude(point.y)
                               ).to_dict()
            plist.append(pdict)
        return plist

    def to_json(self, verbose=False):
        """
        :param verbose: returns extra data like `InverseEdgePoint`
        and `EdgePoint` (future)
        :return: json data
        """
        return json.dumps(self.to_dict(verbose=verbose))

    def findExtremities(self):
        """
        Function will find all the points furthest N, S, E, W and
        return their X or Y values.
        :return: dict: {'N': x, 'S': x, 'E': y, 'W': y}
        """
        return findExtremities(self.findShores().points)

    def findMapEdge(self):
        """
        :return: list of :class:`SpotElevation` Points along the map Edge.
        That is, the edge of the dataset map.
        """
        mapEdge = list()
        for point in self.points:
            if point.x == 0 or point.x == self.datamap.max_x:
                newPoint = GridPoint(point.x, point.y, self.elevation)
                mapEdge.append(newPoint.toSpotElevation(self.datamap))
            if point.y == 0 or point.y == self.datamap.max_y:
                newPoint = GridPoint(point.x, point.y, self.elevation)
                mapEdge.append(newPoint.toSpotElevation(self.datamap))
        return mapEdge

    def findEdge(self):
        """
        Finds all points in a Equal Height Multipoint that have non-equal
        neighbors. Using the pond example, these are all the water points
        that border the shore
        :return: list of EdgePoint objects.
        """
        return self.edgePoints

    # Obsolete. Kept for debugging.
    def findShores(self, edge=None):
        """
        Function will find all shores along pond-like multipoint. and add all
        discontiguous shore points as lists within the returned list.
        This is needed for finding "Islands".
        :param: edge - A list of edges (can reduce redundant edge finds
         in certain cases.)
        :return: List of lists of `GridPoint` representing a Shore
        """
        if not edge:
            edge = self.findEdge()

        # Flatten list and find unique members.
        shorePoints = list(set([val for sublist in
                           [x.nonEqualNeighbors for x in edge.points]
                           for val in sublist]))

        # For Optimized Lookups on larger lists.
        shoreIndex = defaultdict(list)
        for shorePoint in shorePoints:
            shoreIndex[shorePoint.x].append(shorePoint.y)
        purgedIndex = defaultdict(list)

        # initialize the shoreList and its index.
        shoreList = list()
        shoreList.append(list())
        listIndex = 0

        # Grab some shorePoint to start with.
        masterGridPoint = shorePoints[0]
        toBeAnalyzed = [masterGridPoint]

        # toBeAnalyzed preloaded with the first point in the shorePoints list.
        # First act is to pop a point from toBeAnalyzed, and analyze it's
        # orthogonal neighbors for shorePoint members and add them to the
        # toBeAnalyzed list. These points are also added to a purgedIndex,
        # as well as dropped from shoreIndex.
        # Once neighbors are depleted, a new point is pulled from the
        # shorePoints list the list index is incremented and its neighbors are
        # analyzed until shorePoints is depleted.

        while True:
            if not toBeAnalyzed:
                if shorePoints:
                    listIndex += 1
                    shoreList.append(list())
                    toBeAnalyzed = [shorePoints[0]]
            if not toBeAnalyzed:
                break
            try:
                gridPoint = toBeAnalyzed.pop()
            except:
                return shoreList

            if gridPoint.y not in purgedIndex[gridPoint.x]:
                shorePoints.remove(gridPoint)
                shoreIndex[gridPoint.x].remove(gridPoint.y)
                purgedIndex[gridPoint.x].append(gridPoint.y)
                shoreList[listIndex].append(gridPoint)
            else:
                continue
            neighbors = self.datamap.iterateOrthogonal(gridPoint.x,
                                                       gridPoint.y)
            for _x, _y, elevation in neighbors:
                candidate = GridPoint(_x, _y, elevation)
                if candidate.y in shoreIndex[candidate.x]:
                    toBeAnalyzed.append(candidate)
        return [GridPointContainer(x) for x in shoreList]

    def findIslands(self):
        """
        findIslands runs through a list of shore lists and finds the
        extremities of each shorelist. The list with the most maximum
        relative extremity is considered the main pond shore. Everything
        else is implicity an Island .
        :return: List of Islands.
        """

        # First lets find the shores.
        shoreList = self.findShores()

        # Initialize Blank Values.
        N, S, E, W = (None for i in range(4))

        # Next, we find all the furthest extremities among all shore lists.
        # In theory, the only extremities that can occur for shorelines that
        # Don't belong to the main pond body are along the map edge.
        for index, shore in enumerate(shoreList):
            extremityHash = shore.findExtremities()
            if index == 0:
                N, S, E, W = ([shore] for i in range(4))
                continue
            if extremityHash['N'][0].x < N[0].findExtremities()['N'][0].x:
                N = [shore]
            elif extremityHash['N'][0].x == N[0].findExtremities()['N'][0].x:
                N.append(shore)
            if extremityHash['S'][0].x > S[0].findExtremities()['S'][0].x:
                S = [shore]
            elif extremityHash['S'][0].x == S[0].findExtremities()['S'][0].x:
                S.append(shore)
            if extremityHash['E'][0].y > E[0].findExtremities()['E'][0].y:
                E = [shore]
            elif extremityHash['E'][0].y == E[0].findExtremities()['E'][0].y:
                E.append(shore)
            if extremityHash['W'][0].y < W[0].findExtremities()['W'][0].y:
                W = [shore]
            elif extremityHash['W'][0].y == W[0].findExtremities()['W'][0].y:
                W.append(shore)

        # Now, lets flatten the list of cardinal extremities
        flatList = [val for sublist in [N, S, E, W] for val in sublist]
        counter = Counter(flatList)

        # In theory, the main pond shore should have the most extremities
        pondLike = counter.most_common(1)

        # Wow, what a piece of crap. I feel ashamed of the next 6 lines.
        if pondLike[0][0] < 4:
            raise Exception("Largest Pond does not have 4 max points."
                            " Something is horribly Wrong.")
        if len(pondLike) != 1:
            raise Exception("Equal number of extremities in pond?"
                            " How can that be?")

            pondLike = pondLike[0][0]

        # Find any map edges and add them to the Plain Blob Object mapEdge.
        self.mapEdge = self.findMapEdge()

        # Well, this probably isn't an island, so drop it from the list.
        shoreList.remove(pondLike)

        # Find any map edges for the island, and create Island Objects.
        islands = list()
        for island in shoreList:
            islands.append(Island(island.points,
                                  self.datamap,
                                  self.elevation))
        return islands

    @property
    def pointsLatLong(self):
        """
        :return: List of All blob points with lat/long instead of x/y
        """
        return [BaseCoordinate(
                self.datamap.x_position_latitude(coord.x),
                self.datamap.y_position_longitude(coord.y))
                for coord in self.points]

    def __repr__(self):
        return "<Multipoint> elevation(m): {}, points {}". \
            format(self.elevation,
                   len(self.points))

    __unicode__ = __str__ = __repr__
