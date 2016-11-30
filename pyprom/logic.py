from __future__ import division

import numpy
import logging

from collections import defaultdict
from lib.locations import (SpotElevationContainer,
                           Summit, Saddle,
                           GridPoint, MultiPoint,
                           GridPoint, MultiPoint,
                           EdgePoint, InverseEdgePoint,
                           EdgePointContainer,
                           InverseEdgePointContainer)
from lib.util import (coordinateHashToGridPointList,
                      compressRepetetiveChars)


class AnalyzeData(object):
    def __init__(self, datamap):
        """
        :param datamap: `DataMap` object.
        """
        self.logger = logging.getLogger('pyProm.{}'.format(__name__))
        self.datamap = datamap
        self.data = self.datamap.numpy_map
        self.edge = False
        self.max_y = self.datamap.max_y
        self.span_longitude = self.datamap.span_longitude
        self.max_x = self.datamap.max_x
        self.span_latitude = self.datamap.span_latitude
        self.cardinalGrid = dict()
        self.skipSummitAnalysis = defaultdict(list)
        self.summitObjects = SpotElevationContainer([])
        self.saddleObjects = SpotElevationContainer([])
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
        self.logger.info("Initiating Analysis")
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
                self.logger.info("{}/{} - {}%".format(index, self.data.size,
                                (index/self.data.size)*100))

            # Check for summit
            self._summit_and_saddle(x, y)
            # Reset variables, and go to next gridpoint.
            self.edge = False
            self.blob = None
            iterator.iternext()
        return self.summitObjects, self.saddleObjects

    def _summit_and_saddle(self, x, y):
        """
        :param x:
        :param y:
        :return: Summit, Saddle, or None
        """

        # Exempt! bail out!
        if y in self.skipSummitAnalysis[x]:
            return

        saddleProfile = ["HLHL", "LHLH"]
        summitProfile = "L"

        def _analyze_multipoint(x, y, ptElevation):
            self.blob = self.equalHeightBlob(x, y, ptElevation)
            pseudoShore = self.blob.inverseEdgePoints.findLinear()
            shoreProfile = ""

            # Go find the shore of each blob, and assign a "H"
            # for points higher than the equalHeightBlob, and "L"
            # for points lower.
            for shoreSet in pseudoShore:
                for shorePoint in shoreSet.points:

                    if shorePoint.elevation > ptElevation:
                        shoreProfile += "H"
                    if shorePoint.elevation < ptElevation:
                        shoreProfile += "L"
                reducedNeighborProfile = compressRepetetiveChars(shoreProfile)

                # Does it reduce to all points lower? Must be a summit!
                if reducedNeighborProfile == summitProfile:
                    for exemptPoint in self.blob.points:
                        self.skipSummitAnalysis[exemptPoint.x] \
                            .append(exemptPoint.y)
                    summit = Summit(self.datamap.x_position_latitude(x),
                                    self.datamap.y_position_longitude(y),
                                    self.elevation,
                                    edge=self.edge,
                                    multiPoint=self.blob)
                    self.summitObjects.points.append(summit)
                    return

                elif any(x in reducedNeighborProfile for x in saddleProfile):
                    for exemptPoint in self.blob.points:
                        self.skipSummitAnalysis[exemptPoint.x] \
                            .append(exemptPoint.y)
                    saddle = Saddle(self.datamap.x_position_latitude(x),
                                    self.datamap.y_position_longitude(y),
                                    self.elevation,
                                    edge=self.edge,
                                    multiPoint=self.blob)
                    self.saddleObjects.points.append(saddle)
                    return

            # Nothing? Exempt points anyways.
            for exemptPoint in self.blob.points:
                self.skipSummitAnalysis[exemptPoint.x] \
                    .append(exemptPoint.y)
            return

        # Label this as an mapEdge under the following condition
        if x in (self.max_x, 0) or y in (self.max_y, 0):
            self.edge = True

        # Begin the ardous task of analyzing points and multipoints
        neighbor = self.iterateDiagonal(x, y)
        neighborProfile = ""
        for _x, _y, elevation in neighbor:

            # If we have equal neighbors, we need to kick off analysis to
            # a special MultiPoint analysis function.
            if elevation == self.elevation and _y not in\
                            self.skipSummitAnalysis[_x]:
                _analyze_multipoint(_x, _y, elevation)
                return
            if elevation > self.elevation:
                neighborProfile += "H"
            if elevation < self.elevation:
                neighborProfile += "L"

        reducedNeighborProfile = compressRepetetiveChars(neighborProfile)
        if reducedNeighborProfile == summitProfile:
            summit = Summit(self.datamap.x_position_latitude(x),
                            self.datamap.y_position_longitude(y),
                            self.elevation,
                            edge=self.edge)
            self.summitObjects.points.append(summit)

        elif any(x in reducedNeighborProfile for x in saddleProfile):
            saddle =  Saddle(self.datamap.x_position_latitude(x),
                             self.datamap.y_position_longitude(y),
                             self.elevation,
                             edge=self.edge)
            self.saddleObjects.points.append(saddle)
        return

    def iterateDiagonal(self, x, y):
        """
        Generator returns 8 closest neighbors to a raster grid location,
        that is, all points touching including the diagonals.
        """
        shiftList = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1],
                     [0, -1], [-1, -1]]
        # 0, 45, 90, 135, 180, 225, 270, 315

        for shift in shiftList:
            _x = x+shift[0]
            _y = y+shift[1]
            if 0 <= _x <= self.max_x and \
               0 <= _y <= self.max_y:
                yield _x, _y, self.data[_x, _y]
            else:
                yield _x, _y, None

    def iterateOrthogonal(self, x, y):
        """
        generator returns 4 closest neighbors to a raster grid location,
        that is, all points touching excluding the diagonals.
        """
        shiftList = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        # 0, 90, 180, 270

        for shift in shiftList:
            _x = x+shift[0]
            _y = y+shift[1]
            if 0 <= _x <= self.max_x and\
               0 <= _y <= self.max_y:
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
        nesteddict = lambda: defaultdict(nesteddict)
        edgeHash = nesteddict()  # {X : { Y : EdgePoint}}
        inverseEdgeHash = nesteddict()  # InverseEdgepoint (shore).
        toBeAnalyzed = [masterGridPoint]

        # Helper function for equal neighbors.
        def addEqual():
            if edgeHash[gridPoint.x][gridPoint.y]:
                    edgeHash[gridPoint.x][gridPoint.y]. \
                         equalNeighbors.append(branch)
            # Does not exist? Create.
            else:
                edgeHash[gridPoint.x][gridPoint.y] = \
                    EdgePoint(gridPoint.x, gridPoint.y,
                              gridPoint.elevation,
                              [], [branch])

        # Loop until pool of equalHeight neighbors has been exhausted.
        while toBeAnalyzed:
            gridPoint = toBeAnalyzed.pop()
            neighbors = self.iterateDiagonal(gridPoint.x, gridPoint.y)
            if gridPoint.x in (self.max_x, 0) or gridPoint.y in\
                    (self.max_y, 0):
                self.edge = True
            for _x, _y, elevation in neighbors:
                if elevation == masterGridPoint.elevation and\
                                _y not in equalHeightHash[_x]:
                    branch = GridPoint(_x, _y, elevation)
                    equalHeightHash[_x].append(_y)
                    toBeAnalyzed.append(branch)
                    addEqual()
                # Equal and exempt? add to equal neighbor list.
                elif elevation == gridPoint.elevation:
                    addEqual()
                elif elevation != gridPoint.elevation:
                    # EdgePoint Object Exists? append nonEqual
                    if edgeHash[gridPoint.x][gridPoint.y]:
                        edgeHash[gridPoint.x][gridPoint.y]. \
                            nonEqualNeighbors.append(GridPoint(
                                 _x, _y, elevation))
                    # Does not exist? Create.
                    else:
                        edgeHash[gridPoint.x][gridPoint.y] = \
                            EdgePoint(gridPoint.x, gridPoint.y,
                                      gridPoint.elevation,
                                      [GridPoint(_x, _y, elevation)], [])

                    # Add inverse EdgePoints (aka shores).
                    if inverseEdgeHash[_x][_y]:
                        inverseEdgeHash[_x][_y].addEdge(
                            edgeHash[gridPoint.x][gridPoint.y])
                    else:
                        inverseEdgeHash[_x][_y] = \
                            InverseEdgePoint(_x, _y, elevation,
                                             [edgeHash[gridPoint.x]
                                              [gridPoint.y]])

        return MultiPoint(coordinateHashToGridPointList(equalHeightHash),
                          masterGridPoint.elevation, self,
                          edgePoints=EdgePointContainer(
                              edgePointIndex=edgeHash),
                          inverseEdgePoints=InverseEdgePointContainer(
                              inverseEdgePointIndex=inverseEdgeHash,
                              analyzeData=self, mapEdge = self.edge)
                          )


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

        nesteddict = lambda: defaultdict(nesteddict)
        self.edgeHash = nesteddict()  # {X : { Y : EdgePoint}}
        self.inverseEdgeHash = nesteddict()  # Inverse Edgepoint (shore).
        self.edge = False
        self.buildBlob([self.gridPoint])

    def buildBlob(self, toBeAnalyzed):

        def addEqual(branch):
            if self.edgeHash[gridPoint.x][gridPoint.y]:
                self.edgeHash[gridPoint.x][gridPoint.y]. \
                    equalNeighbors.append(branch)
            # Does not exist? Create.
            else:
                self.edgeHash[gridPoint.x][gridPoint.y] = \
                    EdgePoint(gridPoint.x, gridPoint.y,
                              gridPoint.elevation,
                              [], [branch])

        while toBeAnalyzed:
            gridPoint = toBeAnalyzed.pop()
            neighbors = self.analysis.iterateDiagonal(gridPoint.x, gridPoint.y)
            for _x, _y, elevation in neighbors:
                branch = GridPoint(_x, _y, elevation)
                if elevation == self.gridPoint.elevation and _y not in\
                                    self.equalHeightHash[_x]:
                    self.equalHeightHash[_x].append(_y)
                    toBeAnalyzed.append(branch)
                    if _x in (self.analysis.max_x,0) or _y in\
                            (self.analysis.max_y,0):
                        self.edge = True
                    addEqual(branch)
                elif elevation == self.gridPoint.elevation:
                    addEqual(branch)
                # Non Equal?
                elif elevation != self.gridPoint.elevation:
                    # EdgePoint Object Exists? append nonEqual
                    if self.edgeHash[gridPoint.x][gridPoint.y]:
                        self.edgeHash[gridPoint.x][gridPoint.y].\
                            nonEqualNeighbors.append(branch)
                    # Does not exist? Create.
                    else:
                        self.edgeHash[gridPoint.x][gridPoint.y] = \
                            EdgePoint(gridPoint.x, gridPoint.y,
                                      gridPoint.elevation,
                                      [branch], [])

                    # Add inverse EdgePoints (aka shores).
                    if self.inverseEdgeHash[_x][_y]:
                        self.inverseEdgeHash[_x][_y].addEdge(
                            self.edgeHash[gridPoint.x][gridPoint.y])
                    else:
                        self.inverseEdgeHash[_x][_y] = \
                            InverseEdgePoint(_x, _y, elevation,
                                  [self.edgeHash[gridPoint.x][gridPoint.y]])

        self.equalHeightBlob =\
            MultiPoint(coordinateHashToGridPointList(
                       self.equalHeightHash),
                       self.gridPoint.elevation,
                       self.analysis,
                       edgePoints=
                       EdgePointContainer(edgePointIndex=
                                          self.edgeHash),
                       inverseEdgePoints=
                       InverseEdgePointContainer(inverseEdgePointIndex=
                                                 self.inverseEdgeHash,
                                                 analyzeData=self.analysis,
                                                 mapEdge = self.edge)
                       )


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
