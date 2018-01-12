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
from .lib.logic.equalheight import equalHeightBlob

class Walk(object):
    def __init__(self, summits, saddles, datamap):
        """
        :param summits: summits container
        :param saddles: saddles container
        :param datamap: :class:`Datamap`
        """
        self.logger = logging.getLogger('{}'.format(__name__))
        self.logger.info("Initiating Walk Object")
        self.summits = summits
        self.saddles = saddles
        self.datamap = datamap
        self.linkers = list()

        self.logger.info("Create Fast Lookup Hash for Summit Objects.")
        self.summitHash = self._to_hash(self.summits)

    def _to_hash(self, container):
        """
        Generates a lookup hash for whatever container is passed in.
        :param container:
        :return:
        """
        lookupHash = defaultdict(dict)
        for point in container.points:
            if point.multiPoint:
                for mp in point.multiPoint.points:
                    lookupHash[mp.x][mp.y] = point
            else:
                x, y = self.datamap.latlong_to_xy(point.latitude,
                                                  point.longitude)
                lookupHash[x][y] = point
        return lookupHash

    def run(self):
        """
        Helper for iterating through self.saddles.
        """
        self.logger.info("Initiating Walk")
        for saddle in self.saddles.points:
            if not saddle.disqualified:
                self.walk(saddle)

    def walk(self, saddle):
        # check our high shores
        if not saddle.highShores:
            return
        # Perform walk for the highest point in each highShore.
        # In case of tie, use first one.
        for highShore in saddle.highShores:
            # Sort High Shores from high to low
            highShore.points.sort(key=lambda x: x.elevation, reverse=True)
            explored = defaultdict(dict)
            summits = set()
            toBeAnalyzed = [highShore.points[0]]
            # loop through pool of GridPoints to be analyzied.
            while toBeAnalyzed:
                pointUnderAnalysis = toBeAnalyzed.pop()
                # Already explored these? move along.
                if explored[pointUnderAnalysis.x].get(pointUnderAnalysis.y,
                                                      False):
                    continue
                explored[pointUnderAnalysis.x][pointUnderAnalysis.y] = True
                # call the climb up function and see what
                # we got for out next Candidate
                newCandidate, summit, explored =\
                    self._climb_up(pointUnderAnalysis, explored)
                if newCandidate:
                    toBeAnalyzed.append(newCandidate)
                # If we got a summit as a result add it to the summits list.
                if summit:
                    summits.add(summit)
            # Done walking, stash these summits away.
            highShoreSummits = list(summits)

            # Produce a Linker which links this Saddle to the discovered
            # Summit
            # add that linker to the saddles list of the :class:`Summit`
            # and the summit list of the :class:`Saddle`
            for hs in highShoreSummits:
                linker = Linker(hs, saddle, [])
                hs.saddles.append(linker)
                saddle.summits.append(linker)
                self.linkers.append(linker)

    def _climb_up(self, point, explored):
        """
        _climb_up finds the next higher neighbor to walk up to.
        :param point: Gridpoint to climb up from.
        :param explored: lookup hash of GridPoints that have already
        been explored and are therefore not to be explored again.
        :return: GridPoint (Next candidate), Summit (If found), dict()
         (explored points)
        """
        # Is it a summit? Good job! return that Summit!
        if self.summitHash[point.x].get(point.y, None):
            return None, self.summitHash[point.x][point.y], explored

        startingElevation = point.elevation
        lastElevation = point.elevation
        currentHigh = lastElevation
        candidates = None

        neighbors = self.datamap.iterateDiagonal(point.x, point.y)
        for x, y, elevation in neighbors:

            # Oh fuck no, we've got an equalHeightBlob. Better check that out.
            if elevation == startingElevation:
                multipoint = equalHeightBlob(self.datamap, x, y, elevation)
                # Find all inverse Edgepoints higher than
                # the multiPointBlob elevation
                highNeighbors =\
                    multipoint.inverseEdgePoints.findHighInverseEdgePoints(
                        multipoint.elevation)
                highNeighbors.points.sort(key=lambda x: x.elevation,
                                          reverse=True)
                # Mark multipoint components as explored.
                for mp in multipoint.points:
                    explored[mp.x][mp.y] = True
                return highNeighbors.points[0], None, explored
            # Higher than current highest neighbor? Then this is
            # the new candidate.
            if elevation > currentHigh:
                candidates = GridPoint(x, y, elevation)
        return candidates, None, explored

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
        count = 0
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
                    count += 1
        self.logger.info("Linkers Disqualified: {}".format(count))

    def mark_redundant_linkers(self):
        """
        Disqualifies Linkers and Saddles for Single Summit Saddles.
                  /-----\
        Summit 1000    995 Saddle  <-Disqualify
                  \-----/
        """
        count = 0
        for saddle in self.saddles.points:
            uniqueSummits = set(saddle.summits)

            # More than one summit to begin with, but only one unique?
            # Thats not really a Saddle now is it? Why check if there is more
            # than one when by definition a Saddle has two or more linked
            # summits? Becasue EdgeEffect Saddles can technically have just
            # one.
            if len(saddle.summits) > 1 and len(uniqueSummits) == 1:
                saddle.singleSummit = True
                count += 1
                for linker in saddle.summits:
                    linker.disqualified = True
        self.logger.info("Saddles with disqualified Linkers: {}".format(count))


class BetaWalk(object):
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
        lookupHash = defaultdict(dict)
        for point in container.points:
            if point.multiPoint:
                for mp in point.multiPoint.points:
                    lookupHash[mp.x][mp.y] = point
            else:
                x,y = self.datamap.latlong_to_xy(point.latitude, point.longitude)
                lookupHash[x][y] = point
        return lookupHash

    def run(self):
        # iterate through saddles
        for saddle in self.saddles.points:
            if not saddle.disqualified:
                self.walk(saddle)

    def walk(self, saddle):
        # iterate through high Shores
        linkers = list()
        for highEdge in saddle.highShores:
            # Sort High Shores from high to low
            highEdge.points.sort(key=lambda x: x.elevation, reverse=True)
            lookback = 1
            point = highEdge.points[0]
            path = list([point])
            explored = defaultdict(dict)

            while True:
                ####
                if len(path) > 5000:
                    self.logger.info("BORK! stuck at {}".format(point))
                    return path
                ####
                point = self._climb_up(point, explored)
                if isinstance(point, Summit):
                    link = Linker(point, saddle, path)
                    linkers.append(link)
                    saddle.summits.append(link)
                    point.saddles.append(link)
                    break
                if point:
                    explored[point.x][point.y] = True
                    lookback = 1
                    path.append(point)
                else:
                    lookback += 1
                    point = path[-lookback]
        return linkers

    def _climb_up(self, point, explored):

        if self.summitHash[point.x].get(point.y, None):
            return self.summitHash[point.x][point.y]

        lastElevation = point.elevation
        currentHigh = lastElevation
        candidates = list()

        neighbors = self.datamap.iterateDiagonal(point.x, point.y)
        for x, y, elevation in neighbors:
            if explored[x].get(y, False):
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
        count = 0
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
                    count += 1
        self.logger.info("Linkers Disqualified: {}".format(count))


    def mark_redundant_linkers(self):
        """
        Disqualifies Linkers and Saddles for Single Summit Saddles.
                  /-----\
        Summit 1000    995 Saddle  <-Disqualify
                  \-----/
        """
        count = 0
        for saddle in self.saddles.points:
            uniqueSummits = set(saddle.summits)

            # More than one summit to begin with, but only one unique?
            # Thats not really a Saddle now is it? Why check if there is more
            # than one when by definition a Saddle has two or more linked
            # summits? Becasue EdgeEffect Saddles can technically have just
            # one.
            if len(saddle.summits) > 1 and len(uniqueSummits) == 1:
                saddle.singleSummit = True
                count += 1
                for linker in saddle.summits:
                    linker.disqualified = True
        self.logger.info("Saddles with disqualified Linkers: {}".format(count))