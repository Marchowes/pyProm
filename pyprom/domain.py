"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for creating a pyProm Domain.
"""


import os
import time
import logging
import gzip
import cbor

from timeit import default_timer
from datetime import timedelta
from collections import defaultdict

from .feature_discovery import AnalyzeData
from .lib.datamap import DataMap
from .lib.logic.equalheight import equalHeightBlob
from .dataload import Loader
from .lib.containers.spot_elevation import SpotElevationContainer
from .lib.containers.summits import SummitsContainer
from .lib.containers.runoffs import RunoffsContainer
from .lib.containers.saddles import SaddlesContainer
from .lib.containers.linker import Linker
from .lib.containers.walkpath import WalkPath
from .lib.locations.gridpoint import GridPoint
from .lib.logic.basin_saddle_finder import BasinSaddleFinder


class Domain:
    """
    Domain object, This Object contains all the features required to calculate
    the Surface Network.
    """

    def __init__(self, data,
                 summits=SummitsContainer([]),
                 saddles=SaddlesContainer([]),
                 runoffs=RunoffsContainer([]),
                 linkers=[]):
        """
        A Domain consumes either a :class:`Datamap` object or
        a :class:`Loader` child object.
        :param data: :class:`Datamap` or :class:`Loader`
        :param summits: :class:`SummitsContainer`
        :param saddles: :class:`SaddlesContainer`
        :param runoffs: :class:`RunoffsContainer`
        :param linkers: list of :class:`Linker`
        """
        if isinstance(data, DataMap):
            self.datamap = data
        elif isinstance(data, Loader):
            self.datamap = data.datamap
        else:
            raise TypeError('Domain Object consumes DataMap object,'
                            ' or Loader type object')
        self.saddles = saddles
        self.summits = summits
        self.runoffs = runoffs
        self.linkers = linkers
        self.extent = 'LL: {}\n LR: {}\n UL: {}\n UR: {}\n'.format(
            self.datamap.lower_left,
            self.datamap.lower_right,
            self.datamap.upper_left,
            self.datamap.upper_right)
        self.logger = logging.getLogger('{}'.format(__name__))
        self.logger.info("Domain Object Created: \n{}".format(self.extent))

    def run(self, sparse=False, superSparse=False):
        """
        Performs discovery of :class:`Saddle`, :class:`Summits`
        and :class:`Linkers`.
        Runs walk() and disqualifies known problem linkers.
        :param sparse: just do feature discovery, skip walk() and linker logic.
        """
        # Expunge any existing saddles, runoffs, summits, and linkers
        self.saddles = SaddlesContainer([])
        self.summits = SummitsContainer([])
        self.runoffs = RunoffsContainer([])
        self.linkers = list()
        # Find Features
        self.summits, self.saddles, self.runoffs =\
            AnalyzeData(self.datamap).run()
        self.logger.info("Domain contains {} Summits, {} Saddles, {} Runoffs".format(
            len(self.summits),
            len(self.saddles),
            len(self.runoffs)))
        # If we're in superSparse mode, bail.
        if superSparse:
            return

        # Perform Walk
        self.walk()

        # If we're in sparse mode, don't bother with the Basin Saddles.
        if sparse:
            return

        self.detect_basin_saddles()

    @classmethod
    def read(cls, filename, datamap):
        """
        :param filename: name of file (including path) to read
        """
        # Expunge any existing saddles, summits, and linkers
        filename = os.path.expanduser(filename)
        incoming = gzip.open(filename, 'r')
        domain = cls.from_cbor(incoming.read(), datamap)
        domain.logger.info("Loaded Domain Dataset from {}.".format(filename))
        incoming.close()
        return domain

    def write(self, filename, noWalkPath=True):
        """
        :param filename: name of file (including path) to write cbor data to
        compressed cbor data from
        """
        filename = os.path.expanduser(filename)
        self.logger.info("Writing Domain Dataset to {}.".format(filename))
        outgoing = gzip.open(filename, 'wb', 5)
        # ^^ ('filename', 'read/write mode', compression level)
        outgoing.write(self.to_cbor(noWalkPath=noWalkPath))
        outgoing.close()

    @classmethod
    def from_cbor(cls, cborBinary, datamap):
        """
        :param cborBinary: cbor of :class:`Domain` data
        :param datamap: :class:`Datamap`
        :return: :class:`Domain`
        """
        domainDict = cbor.loads(cborBinary)
        return cls.from_dict(domainDict, datamap)

    def to_cbor(self, noWalkPath=True):
        """
        :return: cbor binary of :class:`Domain`
        """
        return cbor.dumps(self.to_dict(noWalkPath=noWalkPath))

    @classmethod
    def from_dict(cls, domainDict, datamap):
        """
        :param domainDict: dict() representation of :class:`Domain`
        :param datamap: :class:`Datamap`
        :return: :class:`Domain`
        """
        saddlesContainer = SaddlesContainer.from_dict(domainDict['saddles'],
                                                      datamap=datamap)
        summitsContainer = SummitsContainer.from_dict(domainDict['summits'],
                                                      datamap=datamap)
        runoffsContainer = RunoffsContainer.from_dict(domainDict['runoffs'],
                                                      datamap=datamap)

        combined = SpotElevationContainer(saddlesContainer.points +
                                          runoffsContainer.points)
        linkers = [
            Linker.from_dict(linkerDict,
                             combined,
                             summitsContainer)
            for linkerDict in domainDict['linkers']]
        return cls(datamap, summitsContainer,
                   saddlesContainer, runoffsContainer, linkers)

    def to_dict(self, noWalkPath=True):
        """
        :return: dict() representation of :class:`Domain`
        """
        domain_dict = dict()
        domain_dict['domain'] = self.extent,
        domain_dict['datamap'] = self.datamap.filename
        domain_dict['date'] = time.strftime("%m-%d-%Y %H:%M:%S")

        # Our main event...
        domain_dict['summits'] = self.summits.to_dict()
        domain_dict['saddles'] = self.saddles.to_dict()
        domain_dict['runoffs'] = self.runoffs.to_dict()

        # Linkers if this domain has been walked.
        domain_dict['linkers'] = [x.to_dict(noWalkPath=noWalkPath)
                                  for x in self.linkers]
        return domain_dict

    def purge_saddles(self, singleSummit = True, basinSaddle = True):
        """
        Purges Non-redundant Basin Saddles and/or Single Summit linked Saddles
        :param singleSummit: Bool, purge singleSummit :class:`Saddle`s
        :param basinSaddle:  Bool, purge basinSaddle :class:`Saddle`s
        """
        toRemoveSaddles = []
        toKeepSaddles = []
        toKeepLinkers = []
        for saddle in self.saddles:
            # Are we a basin saddle and are we removing basin saddles
            # and are there no alternate basin saddles?
            if saddle.basinSaddle and basinSaddle and\
                    not saddle.basinSaddleAlternatives:
                toRemoveSaddles.append(saddle)
                continue
            # is this a singleSummit saddle and are we removing those?
            if saddle.singleSummit and singleSummit:
                toRemoveSaddles.append(saddle)
                continue
            toKeepSaddles.append(saddle)
            toKeepLinkers.extend(saddle.summits)
        self.linkers = toKeepLinkers
        self.saddles = SaddlesContainer(toKeepSaddles)
        self.logger.info("Culled {} Saddles".format(len(toRemoveSaddles)))
        self.logger.info("Kept {} Saddles".format(len(toKeepSaddles)))

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<Domain> Lat/Long Extent {} Saddles " \
            "{} Summits {} Runoffs {} Linkers {}".format(
                self.extent,
                len(self.saddles),
                len(self.summits),
                len(self.runoffs),
                len(self.linkers))

    __unicode__ = __str__ = __repr__

    def walk(self):
        """
        Helper for iterating through self.saddles.
        """
        summitHash = defaultdict(dict)
        for point in self.summits.points:
            if point.multiPoint:
                for mp in point.multiPoint.points:
                    summitHash[mp.x][mp.y] = point
            else:
                x, y = self.datamap.latlong_to_xy(point.latitude,
                                                  point.longitude)
                summitHash[x][y] = point

        self.logger.info("Initiating Walk")
        start = default_timer()
        then = start
        for idx, saddle in enumerate(
                self.saddles.points + self.runoffs.points):
            if not idx % 2000:
                now = default_timer()
                pointsPerSec = round(idx / (now - start), 2)
                self.logger.info(
                    "Saddles per second: {} - {}%"
                    " runtime: {}, split: {}".format(
                        pointsPerSec,
                        round(idx / len(self.saddles) * 100, 2),
                        (str(timedelta(seconds=round(now - start, 2)))),
                        round(now - then, 2)
                    ))
                then = now
            if not saddle.disqualified:
                self._walk(saddle, summitHash)

    def walkSingleSaddle(self, saddle):
        """
        Perform a walk on a single saddle
        This still modifies internal attributes in this :class:`Domain` object
        :param saddle: :class:`Saddle`
        """
        summitHash = defaultdict(dict)
        for point in self.summits.points:
            if point.multiPoint:
                for mp in point.multiPoint.points:
                    summitHash[mp.x][mp.y] = point
            else:
                x, y = self.datamap.latlong_to_xy(point.latitude,
                                                  point.longitude)
                summitHash[x][y] = point

        self._walk(saddle, summitHash)

    def _walk(self, saddle, summitHash):
        """
        Walk from HighEdge. Appends to self.linkers
        :param saddle:
        """
        if not saddle.highShores:
            return
        # Perform walk for the highest point in each highShore.
        # In case of tie, use first one.
        for highShore in saddle.highShores:
            # Sort High Shores from high to low
            highShore.points.sort(key=lambda x: x.elevation, reverse=True)
            explored = defaultdict(dict)
            orderedExploredPoints = []
            orderedOrderedExploredPoints = []
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
                orderedExploredPoints.append(self.datamap.xy_to_latlong(
                    pointUnderAnalysis.x,
                    pointUnderAnalysis.y))
                # call the climb up function and see what
                # we got for out next Candidate
                newCandidate, summit, explored, orderedExploredPoints =\
                    self._climb_up(pointUnderAnalysis, summitHash, explored,
                                   orderedExploredPoints)
                if newCandidate:
                    toBeAnalyzed.append(newCandidate)
                # If we got a summit as a result add it to the summits list.
                if summit:
                    orderedOrderedExploredPoints.append(orderedExploredPoints)
                    orderedExploredPoints = []
                    summits.add(summit)
            # Done walking, stash these summits away.
            highShoreSummits = list(summits)

            # Produce a Linker which links this Saddle to the discovered
            # Summit
            # add that linker to the saddles list of the :class:`Summit`
            # and the summit list of the :class:`Saddle`
            for idx, hs in enumerate(highShoreSummits):
                walkpath = WalkPath(orderedOrderedExploredPoints[idx])
                linker = Linker(hs, saddle, walkpath)
                linker.add_to_remote_saddle_and_summit()
                # remove this?
                self.linkers.append(linker)

    def _climb_up(self, point, summitHash, explored, orderedExploredPoints):
        """
        _climb_up finds the next higher neighbor to walk up to.
        :param point: Gridpoint to climb up from.
        :param explored: lookup hash of GridPoints that have already
        been explored and are therefore not to be explored again.
        :return: GridPoint (Next candidate), Summit (If found), dict()
         (explored points)
        """
        # Is it a summit? Good job! return that Summit!
        if summitHash[point.x].get(point.y, None):
            return None, summitHash[point.x][point.y],\
                explored, orderedExploredPoints

        startingElevation = point.elevation
        lastElevation = point.elevation
        currentHigh = lastElevation
        candidates = None

        neighbors = self.datamap.iterateDiagonal(point.x, point.y)
        for x, y, elevation in neighbors:

            # Oh fuck no, we've got an equalHeightBlob. Better check that out.
            if elevation == startingElevation:
                multipoint, _ = equalHeightBlob(self.datamap, x, y, elevation)
                # Find all perimeter points higher than
                # the multiPointBlob elevation
                highNeighbors =\
                    multipoint.perimeter.findHighPerimeter(
                        multipoint.elevation)
                highNeighbors.sort(key=lambda x: x.elevation, reverse=True)
                # Mark multipoint components as explored.
                for mp in multipoint:
                    explored[mp.x][mp.y] = True
                    orderedExploredPoints.append(
                        self.datamap.xy_to_latlong(mp.x, mp.y))
                return highNeighbors.points[0], None,\
                    explored, orderedExploredPoints
            # Higher than current highest neighbor? Then this is
            # the new candidate.
            if elevation > currentHigh:
                candidates = GridPoint(x, y, elevation)
                currentHigh = elevation
        return candidates, None, explored, orderedExploredPoints

    def detect_basin_saddles(self):
        """
        Helper for discovering Basin Saddles
        """
        bsf = BasinSaddleFinder(self.saddles)
        bsf.disqualify_basin_saddles()
