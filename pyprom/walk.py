"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This file contains a class for walking from Saddles to Summits.
"""
import logging
from collections import defaultdict
from .lib.locations.gridpoint import GridPoint
from .lib.locations.summit import Summit
from .lib.containers.linker import Linker


class Walk(object):
    def __init__(self, summits, saddles, datamap):

        self.logger = logging.getLogger('{}'.format(__name__))
        self.logger.info("Initiating Walk")
        self.summits = summits
        self.saddles = saddles
        self.datamap = datamap
        self.linkers = list()

        self.logger.info("Create Fast Lookup Hash for Summit Objects.")
        self.summitHash = self._to_hash(self.summits)

    def _to_hash(self, container):
        """
        :param container:
        :return:
        """
        nesteddict = lambda: defaultdict(nesteddict)
        hash = nesteddict()
        for point in container.points:
            if point.multiPoint:
                for mp in point.multiPoint.points:
                    hash[mp.x][mp.y] = point
            else:
                xy = self.datamap.latlong_to_xy(point.latitude, point.longitude)
                hash[xy[0]][xy[1]] = point
        return hash

    def run(self):
        # iterate through saddles
        for saddle in self.saddles.points:
            self.linkers += self.walk(saddle)

    def walk(self, saddle):
        # iterate through high Shores
        linkers = list()
        for highEdge in saddle.highShores:
            # Sort High Shores from high to low
            highEdge.points.sort(key=lambda x: x.elevation, reverse=True)
            lookback = 1
            point = highEdge.points[0]
            path = list([point])
            exemptHash = defaultdict(list)

            while True:
                ####
                if len(path) > 5000:
                    self.logger.info("BORK! stuck at {}".format(point))
                    return path
                ####
                point = self._climb_up(point, exemptHash)
                if isinstance(point, Summit):
                    link = Linker(point, saddle, path)
                    linkers.append(link)
                    saddle.summits.append(link)
                    point.saddles.append(link)
                    break
                if point:
                    exemptHash[point.x].append(point.y)
                    lookback = 1
                    path.append(point)
                else:
                    lookback += 1
                    point = path[-lookback]
        return linkers

    def _climb_up(self, point, exemptHash):

        if self.summitHash[point.x][point.y]:
            return self.summitHash[point.x][point.y]

        lastElevation = point.elevation
        currentHigh = lastElevation
        candidates = list()

        neighbors = self.datamap.iterateDiagonal(point.x, point.y)
        for x, y, elevation in neighbors:
            if y in exemptHash[x]:
                continue
            if elevation > currentHigh and elevation > lastElevation:
                currentHigh = elevation
                candidates = list()
                candidates.append(GridPoint(x, y, elevation))
            if elevation == currentHigh:
                candidates.append(GridPoint(x, y, elevation))
        if candidates:
            winner = candidates[0]
        else:
            winner = None
        return winner





    def disqualify_lower_linkers(self):
        """
        Disqualifies Linkers and Saddles if these conditions are met:
        - Saddle connects to two or less Summits
        - (Summit, Summit) Pair contains another Saddle which is higher
                    OK
                 /--995--\
        Summit 1000     1001 Summit
                 \--990--/
                  tooLow
        """
        for summit in self.summits.points:
            found = list()
            for linker in summit.saddles:
                if len(linker.saddle.summits) > 2:
                    # More than 2? Bail!
                    continue
                found += [x for x in linker.saddle_summits if x != summit]
            redundants = set([x for x in found if found.count(x) > 1])
            highest = -32768
            # figure out what the highest Saddle is.
            for redundant in redundants:
                for linker in summit.saddles:
                    if redundant in [x for x in linker.saddle_summits]:
                        if linker.saddle.elevation > highest:
                            highest = linker.saddle.elevation
            # Disqualify Saddle and Linkers if not the highest.
            for linker in summit.saddles:
                if linker.saddle.elevation < highest:
                    for link in linker.saddle.summits:
                        link.disqualified = True
                    linker.saddle.tooLow = True

    def mark_redundant_linkers(self):
        """
        Disqualifies Linkers and Saddles for Single Summit Saddles.
                  /-----\
        Summit 1000    995 Saddle  <-Disqualify
                  \-----/
        """
        for saddle in self.saddles.points:
            uniqueSummits = set(saddle.summits)

            # More than one summit to begin with, but only one unique?
            # Thats not really a Saddle now is it? Why check if there is more
            # than one when by definition a Saddle has two or more linked
            # summits? Becasue EdgeEffect Saddles can technically have just
            # one.
            if len(saddle.summits) > 1 and len(uniqueSummits) == 1:
                saddle.singleSummit = True
                for linker in saddle.summits:
                    linker.disqualified = True
