from __future__ import division

from collections import defaultdict
from lib.locations import (SpotElevationContainer,
                           Summit,
                           GridPoint,
                           MultiPoint)
from lib.util import coordinateHashToGridPointList
import numpy


class AnalyzeData(object):
    def __init__(self, datamap):
        """
        :param datamap: `DataMap` object.
        """
        self.datamap = datamap
        self.data = self.datamap.numpy_map
        self.edge = False
        self.span_longitude = self.datamap.span_longitude
        self.span_latitude = self.datamap.span_latitude
        self.cardinalGrid = dict()
        self.skipSummitAnalysis = defaultdict(list)
        # Relative Grid Hash -- in case we ever want to use this feature...
        for cardinality in ['N', 'S', 'E', 'W']:
            self.cardinalGrid[cardinality] = candidateGridHash(cardinality, 3)

    def analyze(self):
        """
        Analyze Routine.
        Looks for summits, and returns a list of summits
        FUTURE: Analysis for Cols, as well as capability of chasing equal
        height neighbors.
        """
        iterator = numpy.nditer(self.data, flags=['multi_index'])
        featureObjects = SpotElevationContainer([])
        index = 0
        # Iterate through numpy grid, and keep track of gridpoint coordinates.
        while not iterator.finished:
            x, y = iterator.multi_index
            self.elevation = iterator[0]

            # Quick Progress Meter. Needs refinement,
            index += 1
            if not index % 100000:
                print("{}/{} - {}%".format(index, self.data.size,
                                           (index/self.data.size)*100))

            # Check for summit
            feature = self._summit(x, y)
            # Add summit object to list if it exists
            if feature:
                featureObjects.points.append(feature)
            # Reset variables, and go to next gridpoint.
            self.edge = False
            self.blob = None
            iterator.iternext()
        return featureObjects

    def _summit(self, x, y):
        """
        Summit Scanning Function. Determines if point is a summit.
        :param x: x coordinate
        :param y: y coordinate
        :return: Summit Object
        """

        def analyze_summit():
            """
            Negative analysis for summit. Returns False
            if not a summit, True if it is.
            """
            neighbor = self.iterateDiagonal(x, y)
            for _x, _y, elevation in neighbor:
                if elevation > self.elevation:
                    return False  # Higher Neighbor? Not a summit.

                # If the elevation of a neighbor is equal, Determine
                #  entire blob of equal height neighbors.
                elif elevation == self.elevation and _y not in\
                 self.skipSummitAnalysis[_x]:
                    self.blob = self.equalHeightBlob(_x, _y, elevation)

                    # Iterate through all the points in the equalHeight Blob.
                    for point in self.blob.points:
                        pointNeighbor = self.iterateDiagonal(point.x, point.y)

                        # iterate through all point neighbors, if a neighbor
                        # is higher, then we know this is not a summit
                        for px, py, ele in pointNeighbor:
                            if ele > self.elevation:

                                # Blob not a summit? well, exempt all points
                                # from further analysis.
                                for exemptPoint in self.blob.points:
                                    self.skipSummitAnalysis[exemptPoint.x]\
                                        .append(exemptPoint.y)
                                return False

                    # No higher neighbors? Implicitly a summit. Exempt points
                    # from further analysis.
                    for exemptPoint in self.blob.points:
                        self.skipSummitAnalysis[exemptPoint.x].\
                            append(exemptPoint.y)

                # equal neighbor and exempt? not a summit.
                elif elevation == self.elevation and _y in\
                        self.skipSummitAnalysis[_x]:
                    return False

            # None of the above? Must be a summit.
            return True

        # Returns nothing if the summit analysis is negative.
        if not analyze_summit():
            return

        # Made it this far? Must be a summit. Return Object
        return Summit(self.datamap.x_position_latitude(x),
                      self.datamap.y_position_longitude(y),
                      self.elevation,
                      edge=self.edge,
                      multiPoint=self.blob)

    def iterateDiagonal(self, x, y):
        """
        Generator returns 8 closest neighbors to a raster grid location,
        that is, all points touching including the diagonals.
        """
        degreeMap = {'_0': [0, -1],
                     '_45': [1, -1],
                     '_90': [1, 0],
                     '_135': [1, 1],
                     '_180': [0, 1],
                     '_225': [-1, 1],
                     '_270': [-1, 0],
                     '_315': [-1, -1]}
        for degree, shift in degreeMap.items():
            _x = x+shift[0]
            _y = y+shift[1]
            if 0 <= _x < self.span_latitude-1 and \
               0 <= _y < self.span_longitude-1:
                yield _x, _y, self.data[_x, _y]
            else:
                yield _x, _y, None

    def iterateOrthogonal(self, x, y):
        """
        generator returns 4 closest neighbors to a raster grid location,
        that is, all points touching excluding the diagonals.
        """
        degreeMap = {'_0': [0, -1],
                     '_90': [1, 0],
                     '_180': [0, 1],
                     '_270': [-1, 0]}
        for degree, shift in degreeMap.items():
            _x = x+shift[0]
            _y = y+shift[1]
            if 0 <= _x < self.span_latitude-1 and\
               0 <= _y < self.span_longitude-1:
                yield _x, _y, self.data[_x, _y]
            else:
                yield _x, _y, None

    def equalHeightBlob(self, x, y, elevation):
        """
        This function generates a list of coordinates that involve equal height
        :param x: x coordinate
        :param y: y coordinate
        :param elevation: elevation
        :return: Multipoint Object containing all x,y coordinates and elevation
        """

        masterGridPoint = GridPoint(x, y, elevation)
        equalHeightHash = defaultdict(list)
        equalHeightHash[x].append(y)
        toBeAnalyzed = [masterGridPoint]

        # Loop until pool of equalheight neighbors has been exhausted.
        while toBeAnalyzed:
            gridPoint = toBeAnalyzed.pop()
            neighbors = self.iterateDiagonal(gridPoint.x, gridPoint.y)
            for _x, _y, elevation in neighbors:
                if elevation == masterGridPoint.elevation and\
                                _y not in equalHeightHash[_x]:
                    branch = GridPoint(_x, _y, elevation)
                    equalHeightHash[_x].append(_y)
                    toBeAnalyzed.append(branch)
        return MultiPoint(coordinateHashToGridPointList(equalHeightHash),
                          masterGridPoint.elevation, self)


class EqualHeightBlob(object):
    """
    I'm really just keeping this around for testing.
    """
    def __init__(self, x, y, elevation, analysis):
        self.analysis = analysis
        self.gridPoint = GridPoint(x, y, elevation)
        self.equalHeightBlob = list()  # [[x,y]]
        self.equalHeightHash = defaultdict(list)
        self.equalHeightHash[x].append(y)
        self.buildBlob([self.gridPoint])

    def buildBlob(self, toBeAnalyzed):
        while toBeAnalyzed:
            gridPoint = toBeAnalyzed.pop()
            neighbors = self.analysis.iterateDiagonal(gridPoint.x, gridPoint.y)
            for _x, _y, elevation in neighbors:
                if elevation == self.gridPoint.elevation and _y not in\
                                self.equalHeightHash[_x]:
                    branch = GridPoint(_x, _y, elevation)
                    self.equalHeightHash[_x].append(_y)
                    toBeAnalyzed.append(branch)
        self.equalHeightBlob = MultiPoint(coordinateHashToGridPointList(
                                          self.equalHeightHash),
                                          self.gridPoint.elevation,
                                          self.analysis)


def candidateGridHash(cardinality, resolution=1):
    """
    :param cardinality: [N,S,E,W]
    :param resolution: size of cardinal grid (resolution x resolution)
    :return: Returns a resolution x resolution relative grid
     based on cardinality.
    """
    if not resolution % 2:
        resolution += 1  # has to be odd.
    offset = int(numpy.median(range(resolution)))
    if cardinality.upper() == "N":
        return [[x, y] for x in range(-offset, offset+1)
                for y in range(-resolution, 0)]
    if cardinality.upper() == "E":
        return [[x, y] for x in range(1, resolution+1)
                for y in range(-offset, offset+1)]
    if cardinality.upper() == "S":
        return [[x, y] for x in range(-offset, offset+1)
                for y in range(1, resolution+1)]
    if cardinality.upper() == "W":
        return [[x, y] for x in range(-resolution, 0)
                for y in range(-offset, offset+1)]
