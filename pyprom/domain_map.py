"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for creating a pyProm DomainMap.
"""


import os
import time
import logging
import gzip
import cbor


from .feature_discovery import AnalyzeData
from .lib.datamap import DataMap
from .dataload import Loader
from .lib.containers.spot_elevation import SpotElevationContainer
from .lib.containers.summits import SummitsContainer
from .lib.containers.runoffs import RunoffsContainer
from .lib.containers.saddles import SaddlesContainer
from .lib.containers.linker import Linker
from .lib.containers.summit_domain import SummitDomain
from .lib.logic.basin_saddle_finder import BasinSaddleFinder
from .lib.logic.summit_domain_walk import Walk
from .lib.constants import DOMAIN_EXTENSION
from . import version_info

class DomainMap:
    """
    DomainMap object, This object contains the
    :class:`pyprom.lib.containers.saddles.SaddlesContainer`,
    :class:`pyprom.lib.containers.summits.SummitsContainer`,
    :class:`pyprom.lib.containers.runoffs.RunoffsContainer`,
    :class:`pyprom.lib.containers.linker.Linker`,
    required to calculate the surface network.
    """

    def __init__(self, data,
                 summits=SummitsContainer([]),
                 saddles=SaddlesContainer([]),
                 runoffs=RunoffsContainer([]),
                 summit_domains=[],
                 linkers=[]):
        """
        A DomainMap consumes either a :class:`pyprom.lib.datamap.DataMap` object or
        a :class:`pyprom.dataload.Loader` child object.

        :param data: Datamap to be used with this :class:`DomainMap`
        :type data: :class:`pyprom.lib.datamap.DataMap` or
         :class:`pyprom.dataload.Loader`
        :param summits: Summits Container
        :type summits: :class:`pyprom.lib.containers.summits.SummitsContainer`
        :param saddles: Saddles Container
        :type saddles: :class:`pyprom.lib.containers.saddles.SaddlesContainer`
        :param runoffs: RunOffs Container
        :type runoffs: :class:`pyprom.lib.containers.runoffs.RunoffsContainer`
        :param linkers: List of Linkers
        :type linkers: :class:`pyprom.lib.containers.linker.Linker`
        """
        if isinstance(data, DataMap):
            self.datamap = data
        elif isinstance(data, Loader):
            self.datamap = data.datamap
        else:
            raise TypeError('DomainMap Object consumes DataMap object,'
                            ' or Loader type object')
        self.saddles = saddles
        self.summits = summits
        self.runoffs = runoffs
        self.linkers = linkers
        self.summit_domains = summit_domains
        self.extent = 'LL: {}\n LR: {}\n UL: {}\n UR: {}\n'.format(
            self.datamap.lower_left,
            self.datamap.lower_right,
            self.datamap.upper_left,
            self.datamap.upper_right)
        self.logger = logging.getLogger('{}'.format(__name__))
        self.logger.info("DomainMap Object Created: \n{}".format(self.extent))

    def run(self, sparse=False, superSparse=False, rebuildSaddles=False):
        """
        Performs discovery of :class:`pyprom.lib.locations.saddle.Saddle`,
        :class:`pyprom.lib.locations.summit.Summit`,
        :class:`pyprom.lib.locations.runoff.Runoff`,
        and :class:`pyprom.lib.containers.linker.Linker`.
        Runs walk() and disqualifies Basin Saddles.

        :param bool sparse: just do feature discovery, and walk()
        :param bool superSparse: just do feature discovery
        :param bool rebuildSaddles: command AnalyzeData to rebuild saddles
        """
        # Expunge any existing saddles, runoffs, summits, and linkers
        self.saddles = SaddlesContainer([])
        self.summits = SummitsContainer([])
        self.runoffs = RunoffsContainer([])
        self.linkers = list()
        # Find Features
        self.summits, self.saddles, self.runoffs =\
            AnalyzeData(self.datamap).run(rebuildSaddles)
        self.logger.info("DomainMap contains {} Summits,"
                         " {} Saddles, {} Runoffs".format(
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
        Class Method for reading a DomainMap saved to file into a :class:`DomainMap`.

        :param str filename: name of file (including path) to read
        :param datamap: Datamap for this DomainMap
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        """
        # Expunge any existing saddles, summits, and linkers
        filename = os.path.expanduser(filename)
        incoming = gzip.open(filename, 'r')
        domain = cls.from_cbor(incoming.read(), datamap)
        domain.logger.info("Loaded DomainMap Dataset from {}.".format(filename))
        incoming.close()
        return domain

    def write(self, filename):
        """
        Writes the contents of the :class:`DomainMap` to a file.

        :param str filename: name of file (including path) to write this
         :class:`DomainMap` to
        """
        filename = os.path.expanduser(filename)
        if not filename.endswith(DOMAIN_EXTENSION):
            filename += DOMAIN_EXTENSION

        self.logger.info("Writing DomainMap Dataset to {}.".format(filename))
        outgoing = gzip.open(filename, 'wb', 5)
        # ^^ ('filename', 'read/write mode', compression level)
        outgoing.write(self.to_cbor())
        outgoing.close()

    @classmethod
    def from_cbor(cls, cborBinary, datamap):
        """
        Loads a cbor binary into a DomainMap. This also requires
        a :class:`pyprom.lib.datamap.DataMap`

        :param bin cborBinary: cbor of :class:`DomainMap` data
        :param datamap: datamap for this DomainMap
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: :class:`DomainMap`
        """
        domainDict = cbor.loads(cborBinary)
        return cls.from_dict(domainDict, datamap)

    def to_cbor(self):
        """
        Returns compressed cbor binary representation of this :class:`DomainMap`

        :return: cbor binary of :class:`DomainMap`
        """
        return cbor.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, domainDict, datamap):
        """
        Loads dictionary representation into :class:`Domain`

        :param dict domainDict: dict() representation of :class:`Domain`
        :param datamap: datamap for this Domain
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: a new Domain
        :rtype: :class:`DomainMap`
        """
        if domainDict['file_md5'] != datamap.md5:
            raise Exception("Datamap file does not match Datamap "
                            "file used to create DomainMap.")
        saddlesContainer = SaddlesContainer.from_dict(domainDict['saddles'],
                                                      datamap=datamap)
        summitsContainer = SummitsContainer.from_dict(domainDict['summits'],
                                                      datamap=datamap)
        runoffsContainer = RunoffsContainer.from_dict(domainDict['runoffs'],
                                                      datamap=datamap)

        # basinSaddleAlternatives must be populated outside
        # of the dict representation.

        # Since Saddles and Runoffs are all saddles.
        combined = SpotElevationContainer(saddlesContainer.points +
                                          runoffsContainer.points)
        linkers = [
            Linker.from_dict(linkerDict,
                             combined,
                             summitsContainer)
            for linkerDict in domainDict['linkers']]

        summit_domains = set(
            SummitDomain.from_dict(summitDomainDict,
                                   combined,
                                   summitsContainer,
                                   datamap)
            for summitDomainDict in domainDict['summit_domains'])

        return cls(datamap, summitsContainer,
                   saddlesContainer, runoffsContainer,
                   summit_domains, linkers)

    def to_dict(self):
        """
        Returns dict representation of this :class:`DomainMap`

        :param bool noWalkPath: exclude
         :class:`pyprom.lib.containers.walkpath.WalkPath` from member
         :class:`pyprom.lib.containers.linker.Linker`
        :return: dict() representation of :class:`DomainMap`
        :rtype: dict()
        """
        domain_dict = dict()
        domain_dict['domain'] = self.extent,
        domain_dict['datamap'] = self.datamap.filename
        domain_dict['file_md5'] = self.datamap.md5
        domain_dict['date'] = time.strftime("%m-%d-%Y %H:%M:%S")
        domain_dict['version'] = version_info

        # Our main event...
        domain_dict['summits'] = self.summits.to_dict()
        domain_dict['saddles'] = self.saddles.to_dict()
        domain_dict['runoffs'] = self.runoffs.to_dict()

        # Linkers if this domain has been walked.
        domain_dict['linkers'] = [x.to_dict() for x in self.linkers]
        domain_dict['summit_domains'] = [x.to_dict() for x in self.summit_domains]

        return domain_dict

    def purge_saddles(self, singleSummit = True, basinSaddle = True,
                      allBasinSaddles = False):
        """
        Purges Non-redundant Basin Saddles and/or Single Summit linked Saddles

        :param bool singleSummit: Purge singleSummit
         :class:`pyprom.lib.locations.saddle.Saddle` from Saddles Container
        :param bool basinSaddle: Purge basinSaddle
         :class:`pyprom.lib.locations.saddle.Saddle` from Saddles Container
         which do not have an alternativeBasinSaddle
        :param bool allBasinSaddles: Purge all
         :class:`pyprom.lib.locations.saddle.Saddle` from Saddles Container
         regardless of whether they have an alternativeBasinSaddle
        """
        toRemoveSaddles = []
        toKeepSaddles = []
        toKeepLinkers = []
        for saddle in self.saddles:
            # Are we a basin saddle and are we removing basin saddles
            # and are there no alternate basin saddles?
            if saddle.basinSaddle and (basinSaddle or allBasinSaddles):
                # If were culling all Basin Saddles do this.
                if allBasinSaddles:
                    toRemoveSaddles.append(saddle)
                    continue
                # If not, just cull Basin Saddles without alternatives.
                elif not saddle.basinSaddleAlternatives:
                    toRemoveSaddles.append(saddle)
                    continue
            # is this a singleSummit saddle and are we removing those?
            if saddle.singleSummit and singleSummit:
                toRemoveSaddles.append(saddle)
                continue
            toKeepSaddles.append(saddle)
            toKeepLinkers.extend(saddle.summits)

        # Remove parent-child associations for deleted saddles,
        # basin Saddle alternatives, and SummitDomain membership
        # also disqualify Linkers

        for culled in toRemoveSaddles:
            culled.soft_delete()
            for sd in culled.domains:
                sd.remove_saddle(culled)

        self.linkers = toKeepLinkers
        self.saddles = SaddlesContainer(toKeepSaddles)
        self.logger.info("Culled {} Saddles".format(len(toRemoveSaddles)))
        self.logger.info("Kept {} Saddles".format(len(toKeepSaddles)))

    def walk(self, saddles=[]):
        """
        Perform Walk from Saddles contained in this DomainMap

        If saddles are passed in, dont modify the DomainMap.
        Instead, return Saddles returned from the walk.
        """
        walk = Walk(self)
        if not saddles:
            self.saddles, self.runoffs, self.linkers, self.summit_domains =\
                walk.climb_from_saddles()
        else:
            outsaddles, outrunoffs, self.linkers, self.summit_domains =\
                walk.climb_from_saddles(saddles)
            return outsaddles, outrunoffs

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<DomainMap> Lat/Long Extent {} Saddles " \
            "{} Summits {} Runoffs {} Linkers {}".format(
                self.extent,
                len(self.saddles),
                len(self.summits),
                len(self.runoffs),
                len(self.linkers))

    __unicode__ = __str__ = __repr__

    def detect_basin_saddles(self):
        """
        This function identifies Basin Saddles, and Single Summit Saddles
        and disqualifies them.
        """
        bsf = BasinSaddleFinder(self.saddles)
        bsf.disqualify_basin_saddles()
