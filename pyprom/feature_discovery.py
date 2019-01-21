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
    Analyze Data is responsible for discovering the following features:
    :class:`pyprom.lib.locations.saddle.Saddle`,
    :class:`pyprom.lib.locations.summit.Summit`,
    :class:`pyprom.lib.locations.runoff.Runoff`
    """

    def __init__(self, datamap):
        """
        :param datamap: datamap to discover features on.
        :type: :class:`pyprom.lib.datamap.DataMap` object.
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
        Shortcut for running analysis. This will find all features on
        the datamap, as well as rebuild all
        :class:`pyprom.lib.locations.saddle.Saddle` into a more digestible
        format with accurate midpoints and only 2 high edges a piece.

        :return: Containers with features
        :rtype: :class:`pyprom.lib.containers.saddles.SaddlesContainer`
         :class:`pyprom.lib.containers.summits.SummitsContainer`
         :class:`pyprom.lib.containers.runoffs.RunoffsContainer`
        """
        _, _, _ = self.analyze()
        self.logger.info("Rebuilding Saddles")
        self.saddleObjects = self.saddleObjects.rebuildSaddles(self.datamap)
        return self.summitObjects, self.saddleObjects, self.runoffObjects

    def analyze(self):
        """
        Analyze Routine.
        Looks for :class:`pyprom.lib.locations.summit.Summit`,
        :class:`pyprom.lib.locations.saddle.Saddle` and
        :class:`pyprom.lib.locations.runoff.Runoff` features

        :return: Containers
        :rtype: :class:`pyprom.lib.containers.saddles.SaddlesContainer`,
         :class:`pyprom.lib.containers.summits.SummitsContainer`,
         :class:`pyprom.lib.containers.runoffs.RunoffsContainer`,
        """
        self.logger.info("Initiating Saddle, Summit, Runoff Identification")
        self.summitObjects = SummitsContainer([])
        self.saddleObjects = SaddlesContainer([])
        self.runoffObjects = RunoffsContainer([])
        iterator = numpy.nditer(self.data, flags=['multi_index'])
        index = 0
        start = default_timer()
        then = start
        # Iterate through numpy grid, and keep track of GridPoint coordinates.
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

    def analyze_multipoint(self, x, y, ptElevation):
        """
        Logic for analyzing a feature which fits the definition of a
        multipoint.

        :param int x: x coordinate in raster data.
        :param int y: y coordinate in raster data.
        :param ptElevation: Elevation of Multipoint Blob
        :type ptElevation: int, float
        :return: Discovered feature or None
        :rtype: :class:`pyprom.lib.locations.saddle.Saddle`,
         :class:`pyprom.lib.locations.summit.Summit`, or None.
        """
        blob, edgePoints = equalHeightBlob(self.datamap, x, y, ptElevation)
        edge = blob.perimeter.mapEdge
        for exemptPoint in blob:
            self.explored[exemptPoint.x][exemptPoint.y] = True

        return self.consolidatedFeatureLogic(x, y, blob.perimeter,
                                             blob, edge, edgePoints)

    def summit_and_saddle(self, x, y):
        """
        summit_and_saddle does that actual discovery of
        :class:`pyprom.lib.locations.saddle.Saddle`,
        or :class:`pyprom.lib.locations.summit.Summit`

        :param int x: x coordinate in raster data.
        :param int y: y coordinate in raster data.
        :return: Disocvered Feature, or None
        :rtype: :class:`pyprom.lib.locations.saddle.Saddle`
         :class:`pyprom.lib.locations.summit.Summit` or
         :class:`pyprom.lib.locations.runoff.Runoff`, or None.
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
                return self.analyze_multipoint(_x, _y, elevation)

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
        :class:`pyprom.lib.locations.saddle.Saddle`,
        :class:`pyprom.lib.locations.summit.Summit` or
        :class:`pyprom.lib.locations.runoff.Runoff`

        :param int x: x coordinate in raster data.
        :param int y: y coordinate in raster data.
        :param perimeter: Perimeter container
        :type perimeter: :class:`pyprom.lib.containers.perimeter.Perimeter`
        :param multipoint: MultiPoint container
        :type multipoint: :class:`pyprom.lib.containers.multipoint.MultiPoint`
        :param bool edge: is this feature on the map edge?
        :return: List of Container Objects.
        :rtype: :class:`pyprom.lib.containers.spot_elevation.SpotElevationContainer`
         child objects.
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
                runoff = Runoff(lat,
                                long,
                                self.elevation,
                                multiPoint=multipoint,
                                edge=edge,
                                highShores=highPerimeter,
                                edgePoints=edgePoints)
                returnableLocations.append(runoff)
            return returnableLocations

        elif (len(highPerimeter) > 1):
            lat, long = self.datamap.xy_to_latlong(x, y)

            # if we're an edge and all edgepoints are lower than our point.
            if edge and len([a for a in perimeter.mapEdgePoints
                             if a.elevation < self.elevation]) ==\
                    len(perimeter.mapEdgePoints):
                runoff = Runoff(lat,
                                long,
                                self.elevation,
                                multiPoint=multipoint,
                                highShores=highPerimeter,
                                edgePoints=edgePoints)
                returnableLocations.append(runoff)
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
            runoff = Runoff(lat,
                            long,
                            self.elevation,
                            multiPoint=multipoint,
                            highShores=highPerimeter,
                            edgePoints=edgePoints)
            returnableLocations.append(runoff)
        return returnableLocations
