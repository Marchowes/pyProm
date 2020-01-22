"""
pyProm: Copyright 2019.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict
from ..locations.gridpoint import GridPoint
from ..locations.saddle import Saddle
from ..containers.summit_domain import SummitDomain
from .equalheight import equalHeightBlob
from ..containers.disposable_multipoint import DisposableMultipoint
from ..containers.linker import Linker
from ..containers.saddles import SaddlesContainer
from ..logic.internal_saddle_network import InternalSaddleNetwork
from ..containers.gridpoint import GridPointContainer

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
        # all points found to be members of a Disposable Multipoint
        self.disposable_multipoints = defaultdict(dict)
        self.disposable_multipoints_list = list()
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
            if summit.multiPoint:
                sd.extend(summit.multiPoint.points, self.summit_domain_points)
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
                self.logger.info("Strip Went Nowhere! {}".format(climbed_points))
                return None

            # If the steepest neighbor is already a member of a SummitDomain,
            # add all climbed points to that Summit domain, and return that SummitDomain
            if self.summit_domain_points[sn[0]].get(sn[1], None):
                self.summit_domain_points[sn[0]][sn[1]].extend(climbed_points,
                                                               self.summit_domain_points)
                return self.summit_domain_points[sn[0]][sn[1]]
            # equal height? (idx 2 is elevation)
            if sn[2] == current_point[2]:
                # already calculated?
                dm = self.disposable_multipoints[current_point[0]].get(current_point[1], None)
                if dm:
                    hpp = dm.multiPoint.closestHighPerimeterPoint(GridPoint.from_tuple(current_point)) # comes back as GridPoint
                    self.summit_domain_points[hpp.x][hpp.y].extend(climbed_points,
                                                                   self.summit_domain_points)
                    return self.summit_domain_points[hpp.x][hpp.y]
                # nope? add climb it, add out points to the found Summit_Domain and return said SummitDomain
                summit_domain = self.climb_points([], current_point)
                summit_domain.extend(climbed_points, self.summit_domain_points)
                return summit_domain
            climbed_points.append(sn)
            current_point = sn



    def climb_points(self, points, entryPoint=None):
        """
        Climb_points works in two ways:

        In the case of analysis of the high shore of a Saddle, this function
        accepts a list of points, and climbs from all of them. leveraging the
        climb() function to determine which Saddle Domain the point belongs to.

        This function is also used an an intermediary to analyze multipoints
        along a domain walk path. This is done by passing an entryPoint and no
        points. We can determine if the possible path to a summit has already
        been established, and if not, we can create a disposable Multipoint
        object used for finding all paths from the multipoint.

        :param points: list[(x, y)]
        :param entryPoint: (x, y, ele)
        :return: :class:`SummitDomain` if points
        :return: list(:class:`SummitDomain`) if entryPoint
        """
        disposableMultipoint = None
        summit_domains = set()
        # Entrypoint means we know this is an equalheight, so find that
        # and build our disposableMultipoint
        if entryPoint:
            mp = equalHeightBlob(self.domainmap.datamap, entryPoint[0], entryPoint[1], entryPoint[2])[0]
            points = mp.perimeter.findHighPerimeter(entryPoint[2],
                                                    as_tuples=True)  # needs better logic, this currently blindly overwrites points
        # Loop and climb!
        for point in points:
            sd = self.climb(point)
            if sd:
                summit_domains.add(sd)
            else:
                self.logger.info("point {} didn't climb anywhere!".format(point))
        if entryPoint:
            # todo: This logic is where the inside MP path needs to be calculated.
            # If more than 1 summit_domains were found we need to create a disposable_mp. and return the closest high shore's SummitDomain
            if len(summit_domains) > 1:
                disposableMultipoint = DisposableMultipoint(entryPoint, mp, self.disposable_multipoints)
                self.disposable_multipoints_list.append(disposableMultipoint)
                closestHPP = disposableMultipoint.multiPoint.closestHighPerimeterPoint(GridPoint.from_tuple(entryPoint))
                # dont populate the summit doing with an points yet, save that for post processing.
                return self.summit_domain_points[closestHPP.x][closestHPP.y]
            if len(summit_domains) == 1:
                sd = summit_domains.pop()
                for point in points:
                    self.summit_domain_points[point[0]][point[1]] = sd
                return sd
        else:
            return summit_domains

    def climb_from_saddles(self):
        """
        Climbs from all saddles contained in self.domainmap.saddles
        :return: walkedSaddles, linkers, summitDomains
        """
        walkedSaddles = SaddlesContainer([])
        linkers = list()
        summitDomains = set()
        start = default_timer()
        then = start
        for idx, basesaddle in enumerate(self.domainmap.saddles):
            # Dumb counter logic
            if not idx % 2000:
                now = default_timer()
                pointsPerSec = round(idx / (now - start), 2)
                self.logger.info(
                    "Saddles per second: {} - {}%"
                    " runtime: {}, split: {}".format(
                        pointsPerSec,
                        round(idx / len(self.domainmap.saddles) * 100, 2),
                        (str(timedelta(seconds=round(now - start, 2)))),
                        round(now - then, 2)
                    ))
                then = now

            # If this saddle is not an edgeEffect, we can build a Synthetic Saddle
            # and just walk up from the highShore points closest to other high shores.
            saddles = [basesaddle]
            synthetic = False
            if not basesaddle.edgeEffect:
                saddles = self.generate_synthetic_saddles(basesaddle)
                synthetic = True
            # loop through synthetic/non synthetic saddles.
            # non synthetic saddles will have their full highEdges explored.
            # synthetic ones do not.
            for saddle in saddles:
                domainsInSaddle = list()
                highEdgeDomains = list()
                for highEdge in saddle.highShores:
                    domainsInHighEdge = list()
                    domains = self.climb_points([point.to_tuple() for point in highEdge.points])
                    domainsInHighEdge.append(domains)
                    domainsInSaddle.extend(domains)
                    if len(domainsInHighEdge) > 1:
                        self.logger.info("Found {} which is more than 1 dom in high edge. Reconcile later.".format(len(domainsInHighEdge)))
                    if len(domainsInHighEdge) == 0:
                        self.logger.info("no dom in high edge. That's not good.")
                    highEdgeDomains.append(domainsInHighEdge)

                # will need to check all highEdge-domains,
                # if we find any saddles with a domain which shows up in > 1 high edge we will need to rectify that.
                # To rectify, we need to find ..?


                # this means it's an edge effect
                if not synthetic:
                    edge_saddles = self.generate_synthetic_saddles(saddle)

                    # if len(edge_saddle.highshores) < 2:
                    #     continue
                    for edge_saddle in edge_saddles:
                        for highEdge in edge_saddle.highShores:
                            h0 = highEdge[0]
                            sd = self.summit_domain_points[h0.x].get(h0.y, None)
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
                        walkedSaddles.append(edge_saddle)
                    # keep the old saddle, but make sure to disqualify
                    basesaddle.disqualified = True
                    walkedSaddles.append(basesaddle)
                else:
                    # synthetic saddles only have 1 point in each HS, so we know they'll be a domain member.
                    for highEdge in saddle.highShores:
                        h0 = highEdge[0]
                        sd = self.summit_domain_points[h0.x].get(h0.y, None)
                        if not sd:
                            self.logger.info("highEdge {} in synthetic saddle {} was not a summit domain member.".format(h0, saddle))
                            continue
                        summitDomains.add(sd)
                        sd.saddles.append(saddle)
                        summit = sd.summit
                        linker = Linker(summit, saddle)
                        linker.add_to_remote_saddle_and_summit()
                        linkers.append(linker)
                    walkedSaddles.append(saddle)

        return walkedSaddles, linkers, summitDomains

    def generate_synthetic_saddles(self, saddle):

        # This should not be, just return it.
        if len(saddle.highShores) < 2:
            return [saddle]

        # More than 2 high shores? build the network, and return the result.
        if len(saddle.highShores) > 2:
            nw = InternalSaddleNetwork(saddle, self.domainmap.datamap)
            return nw.generate_child_saddles()

        # if we've just got 2 high shores, find all the highest points in
        # the highShores, and find the midpoint between the first two if
        # it's a multipoint
        if len(saddle.highShores) == 2:
            highShores = []
            for highShore in saddle.highShores:
                highShores.append(GridPointContainer(highShore.highest))

            # if multipoint use first of each of the highest high shores
            # and find the mid point for both. Then find the point within
            # the multipoint that is closest to that midpoint. Disregard
            # high shores.
            if saddle.multiPoint:
                hs0, hs1, distance = \
                    saddle.highShores[0].findClosestPoints(
                        saddle.highShores[1])
                # find the middle GP for the 2 closest opposing shore
                # points.
                # Note, in some cases this might be outside the multipoint
                middleGP = GridPoint(int((hs0.x +
                                          hs1.x) / 2),
                                     int((hs0.y +
                                          hs1.y) / 2),
                                     saddle.elevation)
                # reconcile any points which might be outside the
                # multipoint by finding the closest point inside the
                # multipoint.
                middleSpotElevation = \
                    saddle.multiPoint.closestPoint(middleGP,
                                                   asSpotElevation=True)
                newSaddle = Saddle(middleSpotElevation.latitude,
                                   middleSpotElevation.longitude,
                                   middleSpotElevation.elevation)
            # if not multipoint, just use that point.
            else:
                newSaddle = Saddle(saddle.latitude,
                                   saddle.longitude,
                                   saddle.elevation)

            newSaddle.highShores = [GridPointContainer(highShores[0]),
                                    GridPointContainer(highShores[1])]
            return [newSaddle]
