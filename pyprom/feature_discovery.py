"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from __future__ import division

import numpy
import logging

from collections import defaultdict
from timeit import default_timer
from datetime import timedelta
from .lib.locations.gridpoint import GridPoint
from .lib.locations.saddle import Saddle
from .lib.locations.summit import Summit
from .lib.locations.runoff import Runoff
from .lib.locations.base_gridpoint import BaseGridPoint
from .lib.containers.saddles import SaddlesContainer
from .lib.containers.summits import SummitsContainer
from .lib.containers.runoffs import RunoffsContainer
from .lib.containers.perimeter import Perimeter
from .lib.logic.equalheight import equalHeightBlob


class AnalyzeData:
    """
    Object responsible for discovering features
    """

    def __init__(self, datamap):
        """
        :param datamap: `DataMap` object.
        """
        self.logger = logging.getLogger('{}'.format(__name__))
        self.datamap = datamap
        self.data = self.datamap.numpy_map
        self.max_y = self.datamap.max_y
        self.max_x = self.datamap.max_x
        self.x_mapEdge = {0: True, self.max_x: True}
        self.y_mapEdge = {0: True, self.max_y: True}
        self.explored = defaultdict(dict)

    def run(self):
        """
        Shortcut for running analysis
        :return: :class:`Summit`s, :class:`Saddle`s and :class:`Runoff`s
        """
        _, _, _ = self.analyze()
        self.logger.info("Rebuilding Saddles")
        self.saddleObjects = self.saddleObjects.rebuildSaddles(self.datamap)
        return self.summitObjects, self.saddleObjects, self.runoffObjects

    def analyze(self):
        """
        Analyze Routine.
        Looks for :class:`Summit`s, :class:`Saddle`s and :class:`Runoff`s
        return: (:class:`SummitsContainer`, :class:`SaddlesContainer`,
         :class:`RunoffsContainer`,)
        """
        self.logger.info("Initiating Saddle, Summit, Runoff Identification")
        self.summitObjects = SummitsContainer([])
        self.saddleObjects = SaddlesContainer([])
        self.runoffObjects = RunoffsContainer([])
        iterator = numpy.nditer(self.data, flags=['multi_index'])
        index = 0
        start = default_timer()
        then = start
        # Iterate through numpy grid, and keep track of gridpoint coordinates.
        while not iterator.finished:
            x, y = iterator.multi_index
            # core storage is always in metric.
            if self.datamap.unit == "FEET":
                self.elevation = float(.3048 * iterator[0])
            else:
                self.elevation = float(iterator[0])

            # Quick Progress Meter. Needs refinement,
            index += 1
            if not index % 100000:
                now = default_timer()
                pointsPerSec = round(index / (now - start), 2)
                self.logger.info(
                    "Points per second: {} - {}%"
                    " runtime: {}, split: {}".format(
                        pointsPerSec,
                        round(index / self.data.size * 100, 2),
                        (str(timedelta(seconds=round(now - start, 2)))),
                        round(now - then, 2)
                    ))
                then = now

            # skip if this is a nodata point.
            if self.elevation == self.datamap.nodata:
                iterator.iternext()
                continue
            # Check for summit, saddle, or runoff
            results = self.summit_and_saddle(x, y)
            if results:
                for result in results:
                    if isinstance(result, Summit):
                        self.summitObjects.append(result)
                    if isinstance(result, Runoff):
                        self.runoffObjects.append(result)
                    elif isinstance(result, Saddle):
                        self.saddleObjects.append(result)
            # Reset variables, and go to next gridpoint.
            iterator.iternext()
        # Free some memory.
        del(self.explored)
        return self.summitObjects, self.saddleObjects, self.runoffObjects

    def analyze_multipoint(self, x, y, ptElevation, edge):
        """
        :param x:
        :param y:
        :param ptElevation: Elevation of Multipoint Blob
        :return: Summit, Saddle, or None
        """
        blob, edgePoints = equalHeightBlob(self.datamap, x, y, ptElevation)
        edge = blob.perimeter.mapEdge
        for exemptPoint in blob:
            self.explored[exemptPoint.x][exemptPoint.y] = True

        return self.consolidatedFeatureLogic(x, y, blob.perimeter,
                                             blob, edge, edgePoints)

    def summit_and_saddle(self, x, y):
        """
        summit_and_saddle does that actual discovery of summits and saddles.
        :param x:
        :param y:
        :return: Summit, Saddle, or None
        """
        # Exempt! bail out!
        if self.explored[x].get(y, False):
            return None
        edge = False

        # Label this as an mapEdge under the following condition
        edgePoints = []
        if self.x_mapEdge.get(x) or self.y_mapEdge.get(y):
            edge = True
            edgePoints = [BaseGridPoint(x, y)]

        # Begin the ardous task of analyzing points and multipoints
        neighbor = self.datamap.iterateDiagonal(x, y)
        shoreSetIndex = defaultdict(dict)
        shoreMapEdge = []
        for _x, _y, elevation in neighbor:

            # Nothing there? move along.
            if elevation == self.datamap.nodata:
                continue
            # If we have equal neighbors, we need to kick off analysis to
            # a special MultiPoint analysis function and return the result.
            if elevation == self.elevation and\
                    not self.explored[_x].get(_y, False):
                return self.analyze_multipoint(_x, _y, elevation, edge)

            gp = GridPoint(_x, _y, elevation)
            if elevation > self.elevation:
                shoreSetIndex[_x][_y] = gp
            if self.x_mapEdge.get(_x) or self.y_mapEdge.get(_y):
                shoreMapEdge.append(gp)

        shoreSet = Perimeter(pointIndex=shoreSetIndex,
                             datamap=self.datamap,
                             mapEdge=edge,
                             mapEdgePoints=shoreMapEdge)
        return self.consolidatedFeatureLogic(x, y, shoreSet, None,
                                             edge, edgePoints)

    def consolidatedFeatureLogic(self, x, y, perimeter,
                                 multipoint, edge, edgePoints):
        """
        Consolidated Feature Logic analyzes the highEdges around a point or
        multipoint and determines if the pattern matches a
        :class:`Summit` :class:`Saddle` :class:`Runoff`

        :param x: x coordinate.
        :param y: y coordinate.
        :param perimeter: :class:`Perimeter` container.
        :param multipoint: :class:`Multipoint` container
        :param edge: bool if this is a mapEdge.
        :return: list of :class:`SpotElevationContainer` child objects.
        """
        returnableLocations = []
        highPerimeter = perimeter.findHighEdges(
            self.elevation)

        if not len(highPerimeter):
            lat, long = self.datamap.xy_to_latlong(x, y)
            summit = Summit(lat,
                            long,
                            self.elevation,
                            multiPoint=multipoint,
                            edge=edge,
                            edgePoints=edgePoints
                            )
            returnableLocations.append(summit)
            # edge summits are inherently Runoffs
            if edge:
                runOff = Runoff(lat,
                                long,
                                self.elevation,
                                multiPoint=multipoint,
                                edge=edge,
                                highShores=highPerimeter,
                                edgePoints=edgePoints)
                returnableLocations.append(runOff)
            return returnableLocations

        elif (len(highPerimeter) > 1):
            lat, long = self.datamap.xy_to_latlong(x, y)

            # if we're an edge and all edgepoints are lower than our point.
            if edge and len([a for a in perimeter.mapEdgePoints
                             if a.elevation < self.elevation]) ==\
                    len(perimeter.mapEdgePoints):
                runOff = Runoff(lat,
                                long,
                                self.elevation,
                                multiPoint=multipoint,
                                highShores=highPerimeter,
                                edgePoints=edgePoints)
                returnableLocations.append(runOff)
                return returnableLocations

            saddle = Saddle(lat,
                            long,
                            self.elevation,
                            multiPoint=multipoint,
                            edge=edge,
                            highShores=highPerimeter,
                            edgePoints=edgePoints)
            returnableLocations.append(saddle)

        # if we're an edge and all edgepoints are lower than our point.
        if edge and len([a for a in perimeter.mapEdgePoints
                         if a.elevation < self.elevation]) ==\
                len(perimeter.mapEdgePoints):
            lat, long = self.datamap.xy_to_latlong(x, y)
            runOff = Runoff(lat,
                            long,
                            self.elevation,
                            multiPoint=multipoint,
                            highShores=highPerimeter,
                            edgePoints=edgePoints)
            returnableLocations.append(runOff)
        return returnableLocations
