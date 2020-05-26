"""
pyProm: Copyright 2019.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict
from ..locations.gridpoint import GridPoint
from ..locations.saddle import Saddle
from ..locations.runoff import Runoff
from ..containers.summit_domain import SummitDomain
from .equalheight import equalHeightBlob
from ..containers.linker import Linker
from ..containers.saddles import SaddlesContainer
from ..containers.runoffs import RunoffsContainer
from ..containers.spot_elevation import SpotElevationContainer
from ..logic.internal_saddle_network import InternalSaddleNetwork
from ..logic.tuple_funcs import highest
from ..logic.shortest_path_by_points import find_closest_point_by_distance_map

from timeit import default_timer
from datetime import timedelta
import logging

class Walk:
    """
    This class discovers Summit Domains by performing a walk from
    each Saddle high edge to whatever Summit is found by a direct
    ascending walk
    """

    def __init__(self, domainmap):
        self.domainmap = domainmap
        # all points found to be members of a Summit_Domain
        self.summit_domain_points = defaultdict(dict)
        self.logger = logging.getLogger('{}'.format(__name__))

        self._prepopulate_summit_domain_points()

    def _prepopulate_summit_domain_points(self):
        """
        Finds all summit member points, creates SummitDomain objects,
        and prepopulates those objects with those member points.
        This also populates the summit_domain_points which allows us to quickly
        loop of which SummitDomain if any an X, Y coordinate is a member of.
        """
        for summit in self.domainmap.summits:
            # Already got one? move along.
            if summit.domain:
                continue
            sd = SummitDomain(self.domainmap.datamap, summit, [], [])
            summit.domain = sd
            if summit.multipoint:
                sd.extend(summit.multipoint.points, self.summit_domain_points)
            else:
                x, y = self.domainmap.datamap.latlong_to_xy(summit.latitude,
                                                  summit.longitude)
                sd.append((x, y), self.summit_domain_points)


    def climb(self, point):
        """
        Climb climbs from a single point and add it and all points along a
        path to a SummitDomain. This path is comprised of whatever neighbor
        was the steepest neighbor. If an equalheight neighbor is found,
        then that equalheight blob is analyzed as a whole and the closest
        high shore climb is selected.

        :param point: (x, y)
        :return: :class:`SummitDomain` for which it was determined that this
         point climbed to.
        """
        climbed_points = [point]
        current_point = point
        # are we a summit right off the bat?
        if self.summit_domain_points[point[0]].get(point[1], None):
            return self.summit_domain_points[point[0]][point[1]]
        while True:
            sn = self.domainmap.datamap.steepestNeighbor(current_point[0], current_point[1])

            if not sn:
                self.logger.info(f"Strip Went Nowhere! Ends at {current_point} climbed points: {climbed_points}")
                return None

            # If the steepest neighbor is already a member of a SummitDomain,
            # add all climbed points to that Summit domain, and return that SummitDomain
            if self.summit_domain_points[sn[0]].get(sn[1], None):
                self.summit_domain_points[sn[0]][sn[1]].extend(climbed_points,
                                                               self.summit_domain_points)
                return self.summit_domain_points[sn[0]][sn[1]]
            # equal height? (idx 2 is elevation)
            if sn[2] == current_point[2]:
                summit_domain = self.climb_points([], sn)
                summit_domain.extend(climbed_points, self.summit_domain_points)
                return summit_domain
            climbed_points.append(sn)
            current_point = sn

    def climb_points(self, points, entryPoint=None):
        """
        Climb_points works in two ways:

        In the case of analysis of the high shore of a Saddle, this function
        accepts a list of points, and climbs from all of them. leveraging the
        climb() function to determine which Saddle Domain the point belongs to.f

        This function is also used an an intermediary to analyze multipoints
        along a domain walk path. This is done by passing an entryPoint and no
        points. We can determine if the possible path to a summit has already
        been established.

        :param points: list[(x, y)]
        :param entryPoint: (x, y, ele)
        :return: :class:`SummitDomain` if points
        :return: list(:class:`SummitDomain`) if entryPoint
        """
        summit_domains = set()
        # Entrypoint means we know this is an equalheight
        if entryPoint:
            mp, _ = equalHeightBlob(self.domainmap.datamap, entryPoint[0], entryPoint[1], entryPoint[2])
            points = mp.perimeter.findHighPerimeter(entryPoint[2])  # needs better logic, this currently blindly overwrites points
        # Loop and climb!
        for point in points:
            sd = self.climb(point)
            if sd:
                summit_domains.add(sd)
            else:
                self.logger.info("point {} didn't climb anywhere!".format(point))

        if entryPoint:
            closest = find_closest_point_by_distance_map(mp.points, mp.perimeter.findHighPerimeter(mp.elevation))
            for internal_pt, highShore in closest.items():
                # assign all internal members of the multipoint to the summit domain of the closest highShore
                self.summit_domain_points[internal_pt[0]][internal_pt[1]] = self.summit_domain_points[highShore[0]][highShore[1]]
            return self.summit_domain_points[entryPoint[0]][entryPoint[1]]
        else:
            return summit_domains

    def climb_from_saddles(self, saddles=[]):
        """
        Climbs from all saddles contained in self.domainmap.saddles
        :return: walkedSaddles, walkedRunOffs, linkers, summitDomains
        """
        if not saddles:
            saddles = SpotElevationContainer(self.domainmap.saddles.points + self.domainmap.runoffs.points)
        walkedFeatures = list()
        linkers = list()
        summitDomains = set()
        start = default_timer()
        then = start
        for idx, basesaddle in enumerate(saddles):
            # Dumb counter logic
            if not idx % 2000:
                now = default_timer()
                pointsPerSec = round(idx / (now - start), 2)
                self.logger.info(
                    "Saddles per second: {} - {}%"
                    " runtime: {}, split: {}".format(
                        pointsPerSec,
                        round(idx / len(saddles) * 100, 2),
                        (str(timedelta(seconds=round(now - start, 2)))),
                        round(now - then, 2)
                    ))
                then = now

            # If this saddle is not an edgeEffect, we can build a Synthetic Saddle
            # and just walk up from the highShore points closest to other high shores.
            saddlesUnderTest = [basesaddle]
            synthetic = False
            if not basesaddle.edgeEffect:
                saddlesUnderTest = self.generate_synthetic_saddles(basesaddle)
                synthetic = True
            # loop through synthetic/non synthetic saddles.
            # non synthetic saddles will have their full highEdges explored.
            # synthetic ones do not.
            for saddle in saddlesUnderTest:
                for highEdge in saddle.highShores:
                    domains = self.climb_points(highEdge)
                    dd = list(domains) # debug
                    if len(domains) > 1:
                        if not saddle.edgeEffect:
                            self.logger.info("Found {} which is more than 1 dom in high edge. Reconcile later. Edge? {}".format(len(domains), saddle.edgeEffect))
                            print(saddle.id)
                    if len(domains) == 0:
                        self.logger.info("no dom in high edge. That's not good.")

                # will need to check all highEdge-domains,
                # if we find any saddles with a domain which shows up in > 1 high edge we will need to rectify that.
                # To rectify, we need to find ..?


                # this means it's an edge effect
                if not synthetic:
                    edge_saddles = []
                    # don't mess with runoffs.
                    if isinstance(saddle, Runoff):
                        # No high Shores, means this is a Summit-Like Runoff, look for matching summit domain at runoff point.
                        if not saddle.highShores:
                            point = saddle.toXYTuple(self.domainmap.datamap)
                            sd = self.summit_domain_points[point[0]].get(point[1], None)
                            # nothing there? continue.
                            if not sd:
                                self.logger.info("Failed to find SummitDomain for summit-like Runoff {}".format(saddle))
                                walkedFeatures.append(saddle)
                                continue
                            summitDomains.add(sd)
                            sd.saddles.append(saddle)
                            summit = sd.summit
                            linker = Linker(summit, saddle)
                            linker.add_to_remote_saddle_and_summit()
                            linkers.append(linker)
                        else:
                            # if we are a Runoff and there is a high edge, treat like any old Saddle
                            # becasue we walk from all high shore points, this should be OK.
                            edge_saddles = [saddle]
                    edge_saddles = self.generate_synthetic_saddles(saddle) if not edge_saddles else edge_saddles
                    for edge_saddle in edge_saddles:
                        for highEdge in edge_saddle.highShores:
                            h0 = highEdge[0]
                            sd = self.summit_domain_points[h0[0]].get(h0[1], None)
                            # nothing there? continue.
                            if not sd:
                                self.logger.info("highEdge {} in NON-synthetic saddle {} was not a summit domain member.".format(h0, edge_saddle))
                                continue
                            summitDomains.add(sd)
                            sd.saddles.append(edge_saddle)
                            summit = sd.summit
                            linker = Linker(summit, edge_saddle)
                            linker.add_to_remote_saddle_and_summit()
                            linkers.append(linker)
                        # mark the synthetic saddle as a child of the old saddle
                        edge_saddle.parent = saddle
                        # and vice versa
                        saddle.children.append(edge_saddle)
                        saddle.disqualified = True
                        walkedFeatures.append(edge_saddle)
                    # keep the old saddle, but make sure to disqualify
                    basesaddle.disqualified = True
                    walkedFeatures.append(basesaddle)
                else:
                    # synthetic saddles only have 1 point in each HS, so we know they'll be a domain member.
                    for highEdge in saddle.highShores:
                        h0 = highEdge[0]
                        sd = self.summit_domain_points[h0[0]].get(h0[1], None)
                        if not sd:
                            self.logger.info("highEdge {} in synthetic saddle {} was not a summit domain member.".format(h0, saddle))
                            continue
                        summitDomains.add(sd)
                        sd.saddles.append(saddle)
                        summit = sd.summit
                        linker = Linker(summit, saddle)
                        linker.add_to_remote_saddle_and_summit(ignoreDuplicates=False)
                        linkers.append(linker)
                    walkedFeatures.append(saddle)

        walkedSaddles = SaddlesContainer([])
        walkedRunOffs = RunoffsContainer([])
        for walkedFeature in walkedFeatures:
            if isinstance(walkedFeature, Runoff):
                walkedRunOffs.append(walkedFeature)
            elif isinstance(walkedFeature, Saddle):
                walkedSaddles.append(walkedFeature)

        return walkedSaddles, walkedRunOffs, linkers, summitDomains

    def generate_synthetic_saddles(self, saddle):

        # This should not be, just return it.
        if len(saddle.highShores) < 2:
            return [saddle]

        # More than 2 high shores? build the network, and return the result.
        if len(saddle.highShores) > 2:
            nw = InternalSaddleNetwork(saddle, self.domainmap.datamap)
            return nw.generate_child_saddles()
        #Just 2

        if saddle.multipoint:
            hs0, hs1, midpoint = saddle.high_shore_shortest_path(
                self.domainmap.datamap)

            middleSpotElevation = GridPoint(midpoint[0],
                                            midpoint[1],
                                            saddle.elevation).\
                toSpotElevation(self.domainmap.datamap)

            newSaddle = Saddle(middleSpotElevation.latitude,
                               middleSpotElevation.longitude,
                               saddle.elevation)

            highShores = [[hs0], [hs1]]
        else:
            newSaddle = Saddle(saddle.latitude,
                               saddle.longitude,
                               saddle.elevation)

            # todo: closest highShore, not just first one.
            highShores = []
            for highShore in saddle.highShores:
                highShores.append(highest(highShore))

        # assign our slimmed down high shores.
        newSaddle.highShores = highShores
        return [newSaddle]

