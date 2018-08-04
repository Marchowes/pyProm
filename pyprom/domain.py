"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for creating a pyProm Domain.
"""


import os
import time
import json
import logging
import gzip

from timeit import default_timer
from datetime import timedelta
from collections import defaultdict

from .feature_discovery import AnalyzeData
from .lib.datamap import DataMap
from .lib.logic.equalheight import equalHeightBlob
from .dataload import Loader
from .lib.containers.spot_elevation import SpotElevationContainer
from .lib.locations.summit import Summit
from .lib.locations.saddle import Saddle
from .lib.locations.base_gridpoint import BaseGridPoint
from .lib.containers.multipoint import MultiPoint
from .lib.containers.summits import SummitsContainer
from .lib.containers.runoffs import RunoffsContainer
from .lib.containers.saddles import SaddlesContainer
from .lib.containers.gridpoint import GridPointContainer
from .lib.containers.linker import Linker
from .lib.containers.walkpath import WalkPath
from .lib.locations.gridpoint import GridPoint


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

    def run(self):
        """
        Performs discovery of :class:`Saddle`, :class:`Summits`
        and :class:`Linkers`.
        """
        # Expunge any existing saddles, summits, and linkers
        self.saddles = SaddlesContainer([])
        self.summits = SummitsContainer([])
        self.runoffs = RunoffsContainer([])
        self.linkers = list()
        self.summits, self.saddles, self.runoffs =\
            AnalyzeData(self.datamap).run()

    def read(self, filename):
        """
        :param filename: name of file (including path) to read
        """
        # Expunge any existing saddles, summits, and linkers
        filename = os.path.expanduser(filename)
        self.logger.info("Loading Domain Dataset from {}.".format(filename))
        incoming = gzip.open(filename, 'r')
        self.saddles = SpotElevationContainer([])
        self.summits = SpotElevationContainer([])
        self.linkers = list()
        self.from_json(incoming.read())
        incoming.close()

    def write(self, filename):
        """
        :param filename: name of file (including path) to write json data to
        compressed json data from
        """
        filename = os.path.expanduser(filename)
        self.logger.info("Writing Domain Dataset to {}.".format(filename))
        outgoing = gzip.open(filename, 'w', 5)
        # ^^ ('filename', 'read/write mode', compression level)
        outgoing.write(self.to_json(prettyprint=False).encode('utf-8'))
        outgoing.close()

    def from_json(self, jsonString):
        """
        :param jsonString: json string of :class:`Domain` data
        """
        hash = json.loads(jsonString.decode("utf-8"))

        def _loader(point, otype):

            if otype == 'Summit':
                feature = Summit(point['latitude'],
                                 point['longitude'],
                                 point['elevation'])
            elif otype == 'Saddle':
                feature = Saddle(point['latitude'],
                                 point['longitude'],
                                 point['elevation'])
            else:
                raise Exception('Cannot import unknown type:'.format(otype))
            mpPoints = list()
            if point.get('multipoint', None):
                for mp in point['multipoint']:
                    mpPoints.append(BaseGridPoint(mp['gridpoint']['x'],
                                                  mp['gridpoint']['y']))
                feature.multiPoint = MultiPoint(mpPoints,
                                                point['elevation'],
                                                self.datamap)
            if point.get('highShores', None):
                feature.highShores = list()
                for hs in point['highShores']:
                    feature.highShores.append(
                        GridPointContainer(
                            [GridPoint(x['x'], x['y'], x['elevation'])
                             for x in hs]))
            feature.edgeEffect = point['edge']
            return feature
        self.summits = SummitsContainer(
            [_loader(x, 'Summit') for x in hash['summits']])
        self.saddles = SaddlesContainer(
            [_loader(x, 'Saddle') for x in hash['saddles']])
        # self.linkers = ????

    def to_json(self, prettyprint=True):
        """
        :param prettyprint: human readable,
         but takes more space when written to a file.
        :return: json string of :class:`Domain` Data.
        """
        if prettyprint:
            return json.dumps(self.to_dict(), sort_keys=True,
                              indent=4, separators=(',', ': '))
        else:
            return json.dumps(self.to_dict())

    def to_dict(self):
        """
        Dictionary of all :class:`Domain` Data.
        """
        domain_dict = {'domain': self.extent,
                       'date': time.strftime("%m-%d-%Y %H:%M:%S")}

        domain_dict['summits'] = [x.to_dict(recurse=True)
                                  for x in self.summits]
        domain_dict['saddles'] = [x.to_dict(recurse=True)
                                  for x in self.saddles]
        # domain_dict['linkers'] = ?TODO

        return domain_dict

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
        lasttime = start
        for idx, saddle in enumerate(
                self.saddles.points + self.runoffs.points):
            if not idx % 2000:
                thisTime = default_timer()
                split = round(thisTime - lasttime, 2)
                self.lasttime = default_timer()
                rt = self.lasttime - start
                pointsPerSec = round(idx / rt, 2)
                self.logger.info(
                    "Saddles per second: {} - {}%"
                    " runtime: {}, split: {}".format(
                        pointsPerSec,
                        round(idx / len(self.saddles) * 100, 2),
                        (str(timedelta(seconds=round(rt, 2)))),
                        split
                    ))
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
                multipoint = equalHeightBlob(self.datamap, x, y, elevation)
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
        return candidates, None, explored, orderedExploredPoints

    def disqualify_lower_linkers(self):
        """
        Disqualifies Linkers and Saddles if these conditions are met:
        - Saddle connects to two or less Summits
        - (Summit, Summit) Pair contains another Saddle which is higher
                    OK
                 /--995--/
        Summit 1000     1001 Summit
                 /--990--/
                  tooLow
        """
        count = 0
        for summit in self.summits:
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
                  /-----/
        Summit 1000    995 Saddle  <-Disqualify
                  /-----/
        """
        count = 0
        for saddle in self.saddles.points + self.runoffs.points:
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
