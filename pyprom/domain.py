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

from .feature_discovery import AnalyzeData
from .lib.datamap import DataMap
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
from .lib.locations.gridpoint import GridPoint


class Domain:
    """
    Domain object, This Object contains all the features required to calculate
    the Surface Network.
    """

    def __init__(self, data):
        """
        A Domain consumes either a :class:`Datamap` object or
        a :class:`Loader` child object.
        :param datamap:
        """
        if isinstance(data, DataMap):
            self.datamap = data
        elif isinstance(data, Loader):
            self.datamap = data.datamap
        else:
            raise TypeError('Domain Object consumes DataMap object,'
                            ' or Loader type object')
        self.saddles = None
        self.summits = None
        self.runoffs = None
        self.linkers = None
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
