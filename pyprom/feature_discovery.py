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
from math import floor
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
from .lib.logic.contiguous_neighbors import contiguous_neighbors, touching_neighborhoods
from .lib.logic.shortest_path_by_points import high_shore_shortest_path
from .lib.logic.tuple_funcs import highest

from .lib.constants import METERS_TO_FEET


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
        self.explored = defaultdict(dict)

    def run(self, rebuildSaddles=True):
        """
        Shortcut for running analysis. This will find all features on
        the datamap, as well as rebuild all
        :class:`pyprom.lib.locations.saddle.Saddle` into a more digestible
        format with accurate midpoints and only 2 high edges a piece.

        :param bool rebuildSaddles: run saddle rebuild logic
        :return: Containers with features
        :rtype: :class:`pyprom.lib.containers.saddles.SaddlesContainer`
         :class:`pyprom.lib.containers.summits.SummitsContainer`
         :class:`pyprom.lib.containers.runoffs.RunoffsContainer`
        """
        _, _, _ = self.analyze()
        # Corners also are runoffs.
        self.runoffObjects.extend(make_corner_runoffs(self.datamap))

        if rebuildSaddles:
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
                self.elevation = float(METERS_TO_FEET * iterator[0])
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
            self.explored[exemptPoint[0]][exemptPoint[1]] = True

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
        if self.datamap.is_map_edge(x, y):
            edge = True
            edgePoints = [(x, y, self.elevation)]

        # Begin the ardous task of analyzing points and multipoints
        neighbor = self.datamap.iterateFull(x, y)
        shoreSetIndex = defaultdict(dict)
        shoreList = list()
        shoreMapEdge = set()
        for _x, _y, elevation in neighbor:

            # Nothing there? move along.
            if elevation == self.datamap.nodata:
                continue
            # If we have equal neighbors, we need to kick off analysis to
            # a special MultiPoint analysis function and return the result.
            if elevation == self.elevation and\
                    not self.explored[_x].get(_y, False):
                return self.analyze_multipoint(_x, _y, elevation)

            if elevation > self.elevation:
                shore = (_x, _y, elevation)
                shoreSetIndex[_x][_y] = (_x, _y, elevation)
                shoreList.append(shore)
            if self.datamap.is_map_edge(_x, _y):
                shoreMapEdge.add((_x, _y, elevation))

        shoreSet = Perimeter(pointList=shoreList,
                             pointIndex=shoreSetIndex,
                             datamap=self.datamap,
                             mapEdge=edge,
                             mapEdgePoints=list(shoreMapEdge))
        return self.consolidatedFeatureLogic(x, y, shoreSet, [],
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
        :param list edgePoints: list of edgePoints (x, y, el tuples).
        :return: List of Container Objects.
        :rtype: :class:`pyprom.lib.containers.spot_elevation.SpotElevationContainer`
         child objects.
        """
        returnableLocations = []
        highPerimeter = perimeter.findHighEdges(
            self.elevation)
        lat, long = self.datamap.xy_to_latlong(x, y)

        # if there is no high perimeter
        if not highPerimeter:
            summit = Summit(lat,
                            long,
                            self.elevation,
                            multiPoint=multipoint,
                            edge=edge,
                            edgePoints=edgePoints
                            )
            returnableLocations.append(summit)

        elif (len(highPerimeter) > 1) and not edge:
            saddle = Saddle(lat,
                            long,
                            self.elevation,
                            multiPoint=multipoint,
                            edge=edge,
                            highShores=highPerimeter,
                            edgePoints=edgePoints)
            returnableLocations.append(saddle)

        if edge:
            returnableLocations.extend(self.edge_feature_analysis(x, y, perimeter,
                              multipoint, edge, edgePoints, highPerimeter))



        return returnableLocations



    def edge_feature_analysis(self, x, y, perimeter,
                              multipoint, edge, edgePoints, highPerimeter):
        """
        figure out edge runoffs and saddles.

        :param int x: x coordinate in raster data.
        :param int y: y coordinate in raster data.
        :param perimeter: Perimeter container
        :type perimeter: :class:`pyprom.lib.containers.perimeter.Perimeter`
        :param multipoint: MultiPoint container
        :type multipoint: :class:`pyprom.lib.containers.multipoint.MultiPoint`
        :param bool edge: is this feature on the map edge?
        :param list edgePoints: list of edgePoints (x, y, el tuples).
        :param highPerimeter: list of high perimeter points
        :return: List of Container Objects.
        :rtype: :class:`pyprom.lib.containers.spot_elevation.SpotElevationContainer`
         child objects.
        """

        returnable_features = []
        # not edge? GTFO
        if not edge:
            return returnable_features

        lat, long = self.datamap.xy_to_latlong(x, y)

        # No high perimeter? that makes this a "Summit-like" runoff.
        if not highPerimeter:
            runoff = Runoff(lat,
                            long,
                            self.elevation,
                            multiPoint=multipoint,
                            edge=edge,
                            highShores=highPerimeter,
                            edgePoints=edgePoints)
            returnable_features.append(runoff)
            # No need to further process.
            return returnable_features

        # All points which are technically perimeter points,
        # which are on the edge of our map regardless of elevation
        map_edge_perimeter_neighborhoods = contiguous_neighbors(perimeter.mapEdgePoints)

        # Find all neighborhoods comprising of only points lower than self.elevation
        lower_perimeter_map_edge_neighborhoods = []
        for neighborhood in map_edge_perimeter_neighborhoods:
            if highest(neighborhood)[0][2] < self.elevation:
                lower_perimeter_map_edge_neighborhoods.append(neighborhood)

        # did we find one or fewer perimeter neighborhood lower than our elevation?
        if len(lower_perimeter_map_edge_neighborhoods) <= 1:
            # Do we have more than one high shore?
            # If so, generate a saddle with an edge effect.
            # There is no runoff here.
            if len(highPerimeter) > 1:
                saddle = Saddle(lat,
                                long,
                                self.elevation,
                                multiPoint=multipoint,
                                edge=edge,
                                highShores=highPerimeter,
                                edgePoints=edgePoints)
                returnable_features.append(saddle)
            # No need to further process.
            # If there are no runoff like edges, and just a single high
            # shore, then we'll just return an empty list.
            return returnable_features

        # keep track of all edgepoint neighborhoods which were converted to runoff.
        runoff_edge_neighborhoods = []

        # did we find more than one perimeter neighborhood
        # lower than our elevation, and do we have at least 1 highPerimeter?
        if len(lower_perimeter_map_edge_neighborhoods) > 1 and highPerimeter:
            # okay, damn, lets analyze further!

            # Keep track of edgepoints not converted into runoffs.
            remaining_edgepoints = edgePoints.copy()

            # Find all neighborhoods of edgepoints
            edge_point_neighborhoods = contiguous_neighbors(edgePoints)

            # we're packing these into a big list, so keep track of where edgepoint neighborhoods end in the list
            edges_max_idx = len(edge_point_neighborhoods) - 1

            # combine lower perimeter edges and edgepoints
            all_neighborhoods = edge_point_neighborhoods + lower_perimeter_map_edge_neighborhoods

            # find out what neighborhood neighbors other neighborhoods.
            touching = touching_neighborhoods(all_neighborhoods, self.datamap)


            # this loop identifies Runoffs.
            # This also handles the case where we have one high shore
            for idx, touched in touching.items():
                # unless its a non perimeter edge point, dont bother.
                if idx > edges_max_idx:
                    continue
                # if your edgepoint neighborhood, touches 2 lower perimeter neighborhoods, then this is a Runoff.
                if len(touched) == 2:
                    #todo: make this choose the actual center, not just list middle.
                    mid = edge_point_neighborhoods[idx][floor(len(edge_point_neighborhoods[idx])/2)]
                    _lat, _long = self.datamap.xy_to_latlong(mid[0], mid[1])

                    highShores = []
                    if multipoint:
                        pts = multipoint.points
                        # this gets the closest single highshore point to our midpoint
                        highShores.append([high_shore_shortest_path(mid, pts, highPerimeter, self.datamap)])
                    else:
                        # just use the regular highShores if not a multipoint
                        highShores = highPerimeter

                    runoff = Runoff(_lat,
                                    _long,
                                    self.elevation,
                                    multiPoint=[],
                                    highShores=highShores,
                                    edgePoints=edge_point_neighborhoods[idx])
                    returnable_features.append(runoff)

                    runoff_edge_neighborhoods.append(edge_point_neighborhoods[idx])
                    for pt in edge_point_neighborhoods[idx]:
                        remaining_edgepoints.remove(pt) #todo optimize

            # If we meet the definition of a regular Saddle do the following:
            # - If all high edges were converted into runoffs,
            # then we make this into a regular old non edge saddle,
            # and we remove and edgePoints, as well as the edge flag.
            #
            # - If there are some edgepoints which were not converted into
            # a runoff, then keep those edgepoints (but not any converted to runoffs)
            # and keep this as an edge Saddle.

            if len(highPerimeter) >= 2:
                # did all our edgepoints get converted to runoffs?
                # if not, we need to make an edge saddle.
                # if so, we can just make a regular saddle. and ignore edgepoints
                if len(runoff_edge_neighborhoods) == len(edge_point_neighborhoods):
                    saddle = Saddle(lat, long,
                                    self.elevation,
                                    multiPoint = multipoint,
                                    edge = False,
                                    highShores = highPerimeter,
                                    edgePoints = [])
                    returnable_features.append(saddle)
                else:
                    saddle = Saddle(lat, long,
                                    self.elevation,
                                    multiPoint = multipoint,
                                    edge = edge,
                                    highShores = highPerimeter,
                                    edgePoints = remaining_edgepoints)
                    returnable_features.append(saddle)
        return returnable_features

def make_corner_runoffs(datamap):
    """
    Dumb function for generating single point corner runoffs.

    :param datamap: datamap to generate corner runoffs for.
    :type datamap: :class:`pyprom.lib.datamap.DataMap`
    :return: list(:class:`pyprom.lib.locations.runoff.Runoff`)
    """

    rll = Runoff(*datamap.lower_left,
                 datamap.get(datamap.max_x, 0))
    rll.edgePoints.append((datamap.max_x, 0, datamap.get(datamap.max_x, 0)))
    rlr = Runoff(*datamap.lower_right,
                 datamap.get(datamap.max_x, datamap.max_y))
    rlr.edgePoints.append((datamap.max_x, datamap.max_y, datamap.get(datamap.max_x, datamap.max_y)))
    rul = Runoff(*datamap.upper_left,
                 datamap.get(0, 0))
    rul.edgePoints.append((0, 0, datamap.get(0, 0)))
    rur = Runoff(*datamap.upper_right,
                 datamap.get(0, datamap.max_y))
    rur.edgePoints.append((0, datamap.max_y, datamap.get(0, datamap.max_y)))

    return [rll, rlr, rul, rur]
