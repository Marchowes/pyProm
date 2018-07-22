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
from .lib.containers.saddles import SaddlesContainer
from .lib.containers.summits import SummitsContainer
from .lib.containers.high_edge import HighEdgeContainer
from .lib.containers.gridpoint import GridPointContainer
from .lib.util import compressRepetetiveChars
from .lib.logic.equalheight import equalHeightBlob


class AnalyzeData(object):
    def __init__(self, datamap):
        """
        :param datamap: `DataMap` object.
        """
        self.logger = logging.getLogger('{}'.format(__name__))
        self.datamap = datamap
        self.data = self.datamap.numpy_map
        self.edge = False
        self.max_y = self.datamap.max_y
        self.max_x = self.datamap.max_x
        self.explored = defaultdict(dict)

    def run(self):
        _, _ = self.analyze()
        self.logger.info("Rebuilding Saddles")
        self.saddleObjects = self.saddleObjects.rebuildSaddles(self.datamap)
        return self.summitObjects, self.saddleObjects

    def analyze(self):
        """
        Analyze Routine.
        Looks for :class:`Summit`s, and :class:`Saddle`s
        return: (:class:`SpotElevationContainer`,SpotElevationContainer)
        """
        self.start = default_timer()
        self.lasttime = self.start
        self.logger.info("Initiating Saddle and Summit Identification")
        self.summitObjects = SummitsContainer([])
        self.saddleObjects = SaddlesContainer([])
        iterator = numpy.nditer(self.data, flags=['multi_index'])
        index = 0
        # Iterate through numpy grid, and keep track of gridpoint coordinates.
        while not iterator.finished:
            x, y = iterator.multi_index
            # core storage is always in metric.
            if self.datamap.unit == "FEET":
                self.elevation = float(.3048*iterator[0])
            else:
                self.elevation = float(iterator[0])

            # Quick Progress Meter. Needs refinement,
            index += 1
            if not index % 100000:

                thisTime = default_timer()
                split = round(thisTime - self.lasttime, 2)
                self.lasttime = default_timer()
                rt = self.lasttime - self.start
                pointsPerSec = round(index/rt, 2)
                self.logger.info(
                    "Points per second: {} - {}%"
                    " runtime: {}, split: {}".format(
                        pointsPerSec,
                        round(index/self.data.size * 100, 2),
                        (str(timedelta(seconds=round(rt, 2)))),
                        split
                    ))

            # skip if this is a nodata point.
            if self.elevation == self.datamap.nodata:
                iterator.iternext()
                continue
            # Check for summit or saddle
            result = self.summit_and_saddle(x, y)
            if result:
                if isinstance(result, Saddle):
                    self.saddleObjects.append(result)
                if isinstance(result, Summit):
                    self.summitObjects.append(result)
            # Reset variables, and go to next gridpoint.
            self.edge = False
            self.blob = None
            iterator.iternext()
        # Free some memory.
        del(self.explored)
        return self.summitObjects, self.saddleObjects

    def analyze_multipoint(self, x, y, ptElevation):
        """
        :param x:
        :param y:
        :param ptElevation: Elevation of Multipoint Blob
        :return: Summit, Saddle, or None
        """
        self.blob = equalHeightBlob(self.datamap, x, y, ptElevation)
        self.edge = self.blob.perimeter.mapEdge

        highPerimeter = self.blob.perimeter.findHighEdges(
            self.elevation)

        for exemptPoint in self.blob:
            self.explored[exemptPoint.x][exemptPoint.y] = True
        if not len(highPerimeter):
            lat, long = self.datamap.xy_to_latlong(x, y)
            summit = Summit(lat,
                            long,
                            self.elevation,
                            edge=self.edge,
                            multiPoint=self.blob
                            )
            return summit
        if (len(highPerimeter) > 1) or\
                (len(highPerimeter) == 1 and self.edge):
            lat, long = self.datamap.xy_to_latlong(x, y)
            saddle = Saddle(lat,
                            long,
                            self.elevation,
                            edge=self.edge,
                            multiPoint=self.blob,
                            highShores=highPerimeter)
            return saddle
        return None

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

        saddleProfile = ["HLHL", "LHLH"]
        summitProfile = "L"

        # Label this as an mapEdge under the following condition
        if not self.edge:
            if x in (self.max_x, 0) or y in (self.max_y, 0):
                self.edge = True

        # Begin the ardous task of analyzing points and multipoints
        neighbor = self.datamap.iterateDiagonal(x, y)
        shoreSet = GridPointContainer([])
        neighborProfile = ""
        for _x, _y, elevation in neighbor:

            # Nothing there? move along.
            if not elevation:
                continue
            # If we have equal neighbors, we need to kick off analysis to
            # a special MultiPoint analysis function and return the result.
            if elevation == self.elevation and\
                    not self.explored[_x].get(_y, False):
                return self.analyze_multipoint(_x, _y, elevation)

            if elevation > self.elevation:
                neighborProfile += "H"
            if elevation < self.elevation:
                neighborProfile += "L"
            shoreSet.append(GridPoint(_x, _y, elevation))

        reducedNeighborProfile = compressRepetetiveChars(neighborProfile)
        # Did the profile match "L" aka a Summit?
        if reducedNeighborProfile == summitProfile:
            lat, long = self.datamap.xy_to_latlong(x, y)
            summit = Summit(lat,
                            long,
                            self.elevation,
                            edge=self.edge)
            return summit

        # Did the profile match HLHL or LHLH?
        elif any(x in reducedNeighborProfile for x in saddleProfile):
            shores = HighEdgeContainer(shoreSet, self.elevation)
            lat, long = self.datamap.xy_to_latlong(x, y)
            saddle = Saddle(lat,
                            long,
                            self.elevation,
                            edge=self.edge,
                            highShores=[GridPointContainer(g)
                                        for g in shores.highPoints])
            return saddle
        return None
