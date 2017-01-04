"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""
import logging
from collections import defaultdict
from lib.locations.gridpoint import GridPoint
from lib.locations.summit import Summit
from lib.containers.linker import Linker

class Walk(object):
    def __init__(self, summits, saddles, datamap):

        self.logger = logging.getLogger('pyProm.{}'.format(__name__))
        self.logger.info("Initiating Walk")
        self.summits = summits
        self.saddles = saddles
        self.datamap = datamap

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
                hash[self.datamap.relative_position_latitude(
                        point.latitude)]\
                    [self.datamap.relative_position_longitude(
                        point.longitude)]\
                            = point
        return hash


    def run(self):
        #iterate through saddles
        for saddle in self.saddles:
            self.walk(saddle)

    def walk(self, saddle):
        #iterate through high Shores
        links = list()
        for highEdge in saddle.highShores:
            #Sort High Shores from high to low
            highEdge.points.sort(key=lambda x: x.elevation, reverse=True)

            path = list()
            point = highEdge.points[0]
            exemptHash = defaultdict(list)

            while True:
                path.append(point)
                ####
                if len(path) > 5000:
                    self.logger.info("BORK! stuck at {}".format(point))
                    return path
                ####
                point = self._climb_up(point, exemptHash)
                if not point:
                    break
                if isinstance(point, Summit):
                    self.logger.info('Linked {} -> {}'.format(saddle, point))
                    link = Linker(point, saddle, path)
                    links.append(link)
                    saddle.summits.append(link)
                    point.saddles.append(link)

                    break
                exemptHash[point.x].append(point.y)

        if len(set(saddle.summits)) == 1:
            saddle.disqualified = True
        return links


    def _climb_up(self, point, exemptHash):

        #HERE: Logic to ID if we've hit a summit
        if self.summitHash[point.x][point.y]:
            return self.summitHash[point.x][point.y]


        lastElevation = point.elevation
        currentHigh= lastElevation
        candidates = list()

        neighbors = self.datamap.iterateDiagonal(point.x, point.y)
        for x, y, elevation in neighbors:
            if y in exemptHash[x]:
                continue
            if elevation > currentHigh and elevation > lastElevation:
                currentHigh = elevation
                candidates = list()
                candidates.append(GridPoint(x,y,elevation))
            if elevation == currentHigh:
                candidates.append(GridPoint(x, y, elevation))
        # Make smarter?
        # if currentHigh == point.elevation:
        try:
            winner = candidates[0]
        except:
            self.logger.info("BORK! stuck at {}".format(point))
            return None
        return winner









