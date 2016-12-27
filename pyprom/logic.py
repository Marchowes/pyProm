"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from __future__ import division

import numpy
import logging

from collections import defaultdict
from lib.locations.gridpoint import GridPoint
from lib.locations.saddle import Saddle
from lib.locations.summit import Summit
from lib.locations.inverse_edgepoint import InverseEdgePoint
from lib.locations.edgepoint import EdgePoint
from lib.containers.spot_elevation import SpotElevationContainer
from lib.containers.multipoint import MultiPoint
from lib.containers.edgepoint import EdgePointContainer
from lib.containers.inverse_edgepoint import InverseEdgePointContainer
from lib.containers.high_edge import HighEdgeContainer
from lib.containers.gridpoint import GridPointContainer
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

    def analyze(self):
        """
        Analyze Routine.
        Looks for :class:`Summit`s, and :class:`Saddle`s
        return: (:class:`SpotElevationContainer`,SpotElevationContainer)
        """
        self.logger.info("Initiating Analysis")
        iterator = numpy.nditer(self.data, flags=['multi_index'])
        index = 0
        # Iterate through numpy grid, and keep track of gridpoint coordinates.
        while not iterator.finished:
            x, y = iterator.multi_index
            self.elevation = float(iterator[0])

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
            pseudoShores = self.blob.inverseEdgePoints.findLinear()
            summitLike = False

            # Go find the shore of each blob, and assign a "H"
            # for points higher than the equalHeightBlob, and "L"
            # for points lower.
            for shoreSet in pseudoShores:
                shoreProfile = ""
                for shorePoint in shoreSet.points:
                    if not shorePoint.elevation:
                        continue
                    if shorePoint.elevation > ptElevation:
                        shoreProfile += "H"
                    if shorePoint.elevation < ptElevation:
                        shoreProfile += "L"
                reducedNeighborProfile = compressRepetetiveChars(shoreProfile)

                if any(x in reducedNeighborProfile for x in saddleProfile)\
                        and not summitLike:
                    for exemptPoint in self.blob.points:
                        self.skipSummitAnalysis[exemptPoint.x] \
                            .append(exemptPoint.y)
                    shores = HighEdgeContainer(shoreSet, ptElevation)
                    saddle = Saddle(self.datamap.x_position_latitude(x),
                                    self.datamap.y_position_longitude(y),
                                    self.elevation,
                                    edge=self.edge,
                                    multiPoint=self.blob,
                                    highShores=shores)
                    self.saddleObjects.points.append(saddle)
                    return
                elif reducedNeighborProfile == summitProfile:
                    summitLike = True
                else:
                    summitLike = False
                    break

            if summitLike:
                for exemptPoint in self.blob.points:
                    self.skipSummitAnalysis[exemptPoint.x] \
                        .append(exemptPoint.y)
                summit = Summit(self.datamap.x_position_latitude(x),
                                self.datamap.y_position_longitude(y),
                                self.elevation,
                                edge=self.edge,
                                multiPoint=self.blob
                                )
                self.summitObjects.points.append(summit)
                return
            else:
                for exemptPoint in self.blob.points:
                    self.skipSummitAnalysis[exemptPoint.x] \
                        .append(exemptPoint.y)
                return

        # Label this as an mapEdge under the following condition
        if x in (self.max_x, 0) or y in (self.max_y, 0):
            self.edge = True

        # Begin the ardous task of analyzing points and multipoints
        neighbor = self.datamap.iterateDiagonal(x, y)
        shoreSet = GridPointContainer([])
        neighborProfile = ""
        for _x, _y, elevation in neighbor:

            # If we have equal neighbors, we need to kick off analysis to
            # a special MultiPoint analysis function.
            if not elevation:
                continue
            if elevation == self.elevation and _y not in\
                            self.skipSummitAnalysis[_x]:
                _analyze_multipoint(_x, _y, elevation)
                return
            if elevation > self.elevation:
                neighborProfile += "H"
            if elevation < self.elevation:
                neighborProfile += "L"
            shoreSet.points.append(GridPoint(_x, _y, elevation))

        reducedNeighborProfile = compressRepetetiveChars(neighborProfile)
        if reducedNeighborProfile == summitProfile:
            summit = Summit(self.datamap.x_position_latitude(x),
                            self.datamap.y_position_longitude(y),
                            self.elevation,
                            edge=self.edge)
            self.summitObjects.points.append(summit)

        elif any(x in reducedNeighborProfile for x in saddleProfile):
            shores = HighEdgeContainer(shoreSet, self.elevation)
            saddle = Saddle(self.datamap.x_position_latitude(x),
                            self.datamap.y_position_longitude(y),
                            self.elevation,
                            edge=self.edge,
                            highShores=shores)
            self.saddleObjects.points.append(saddle)
        return

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
            neighbors = self.datamap.iterateDiagonal(gridPoint.x, gridPoint.y)
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
                          masterGridPoint.elevation, self.datamap,
                          edgePoints=EdgePointContainer(
                              edgePointIndex=edgeHash),
                          inverseEdgePoints=InverseEdgePointContainer(
                              inverseEdgePointIndex=inverseEdgeHash,
                              datamap=self.datamap, mapEdge=self.edge)
                          )


class EqualHeightBlob(object):
    """
    I'm really just keeping this around for testing.
    """
    def __init__(self, x, y, elevation, datamap):
        self.datamap = datamap
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
            neighbors = self.datamap.iterateDiagonal(gridPoint.x, gridPoint.y)
            for _x, _y, elevation in neighbors:
                branch = GridPoint(_x, _y, elevation)
                if elevation == self.gridPoint.elevation and _y not in\
                                    self.equalHeightHash[_x]:
                    self.equalHeightHash[_x].append(_y)
                    toBeAnalyzed.append(branch)
                    if _x in (self.datamap.max_x, 0) or _y in\
                            (self.datamap.max_y, 0):
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
                       self.datamap,
                       edgePoints=
                       EdgePointContainer(edgePointIndex=self.edgeHash),
                       inverseEdgePoints=
                       InverseEdgePointContainer(inverseEdgePointIndex=
                                                 self.inverseEdgeHash,
                                                 datamap=self.datamap,
                                                 mapEdge=self.edge)
                       )
