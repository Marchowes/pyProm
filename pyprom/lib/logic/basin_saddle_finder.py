"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains logic for identifying Basin Saddles.
"""
import logging
from ..containers.saddles import SaddlesContainer
from timeit import default_timer
from collections import OrderedDict


class BasinSaddleFinder:
    """
    Class for identifying all basin saddles.
    A Basin Saddle is the lowest member of a cycle.
    """

    def __init__(self, saddles):
        """
        :param saddles: SaddlesContainer containing saddles to be analyzed
        :type saddles: :class:`pyprom.lib.containers.saddles.SaddlesContainer`
        :raises: TypeError if not a
         :class:`pyprom.lib.containers.saddles.SaddlesContainer`
        """
        if not isinstance(saddles, SaddlesContainer):
            raise TypeError("Saddles must be SaddlesContainer")

        self.logger = logging.getLogger('{}'.format(__name__))
        self.saddles = saddles

    def disqualify_basin_saddles(self):
        """
        This function identifies Basin Saddles or single summit (stub)
        saddles, marks them as disqualified, and sets
        basinSaddleAlternatives on the disqualified saddle, and the
        alternate basin saddle.
        """
        # initiation
        start = default_timer()
        purgedStubsCounter = 0
        basinSaddlesCounter = 0
        # features are an ordered dict. We use an ordered dict so we can
        # have deterministic results.
        features = OrderedDict(sorted(
            {saddle.id: saddle for saddle in self.saddles}.items(),
            key=lambda t: t[1].elevation))

        self.logger.info("Identifying Stub Saddles")
        for id, saddle in features.items():
            if not saddle.disqualified:
                purgedStubsCounter +=\
                    self._disqualify_single_source_saddles(saddle)
        self.logger.info("Identifying Stub Saddles Complete"
                         " in {} seconds {} Saddles purged ".format(
                             default_timer() - start, purgedStubsCounter))

        start = default_timer()
        self.logger.info("Detecting Tree Cycles, identifying Basin Saddles")
        cycles = []
        root = None
        while features:  # loop over features
            if root is None:
                _, root = features.popitem()
            if root.disqualified:
                root = None
                continue
            stack = [root]  # stack of features to explore.
            lookback = {root.id: root}  # lookback from each feature
            exploredNbrs = {root.id: dict()}  # hash of explored neighbors.
            cycleMembers = {}
            while stack:
                z = stack.pop()
                if z.disqualified:
                    features.pop(z.id, None)
                    continue
                zEexploredNbrs = exploredNbrs[z.id]
                for nbr in z.feature_neighbors():
                    if nbr.disqualified:
                        features.pop(nbr.id, None)
                        continue
                    if nbr.id not in exploredNbrs:  # new node
                        lookback[nbr.id] = z
                        stack.append(nbr)
                        exploredNbrs[nbr.id] = {z.id: True}
                    elif nbr == z:  # self loops
                        cycles.append([z])
                    elif nbr.id not in zEexploredNbrs:  # found a cycle
                        pn = exploredNbrs[nbr.id]
                        cycle = [nbr, z]
                        cycleMembers = {nbr.id: True, z.id: True}
                        p = lookback[z.id]
                        while p.id not in pn:
                            cycle.append(p)
                            cycleMembers[p.id] = True
                            p = lookback[p.id]
                            if p.id == root.id:
                                break
                        cycle.append(p)
                        lowest = self.find_lowest_cycle_members(cycle)
                        self._disqualify_and_label(lowest)
                        basinSaddlesCounter += 1
                        cycles.append(cycle)
                        exploredNbrs[nbr.id][z.id] = True
            exemptFeatures = lookback.keys() - cycleMembers.keys()
            for toRemove in exemptFeatures:
                features.pop(toRemove, None)
            if cycleMembers:
                features[root.id] = root
            root = None
        self.logger.info("Basin Saddle detection complete in {}"
                         " seconds {} Basin Saddles".format(
                             default_timer() - start, basinSaddlesCounter))

    def _disqualify_and_label(self, lowest):
        """
        Consumes a list of features of the same height, disqualifies
        one, and sets basinSaddleAlternatives for equal height features.

        :param lowest: list of "lowest" features.
        :type lowest:
         list(:class:`pyprom.lib.locations.spot_elevation.SpotElevation`)
        """
        lowest[0].disqualify_self_and_linkers(basinSaddle=True)
        if len(lowest) > 1:
            for saddle in lowest:
                saddle.basinSaddleAlternatives = lowest.copy()
                saddle.basinSaddleAlternatives.remove(saddle)

    def find_lowest_cycle_members(self, cycle):
        """
        Consumes a list of points which make a cycle. Finds lowest points
        and returns a list of features which are the lowest.

        :param cycle: features which make a cycle.
        :type cycle:
         list(:class:`pyprom.lib.locations.spot_elevation.SpotElevation`)
        """
        lowest = []
        lowest.append(cycle[0])
        for node in cycle:
            if node.elevation == lowest[0].elevation and\
                    node.id != lowest[0].id:
                lowest.append(node)
                continue
            if node.elevation < lowest[0].elevation:
                lowest = [node]
                continue
        return lowest

    def _disqualify_single_source_saddles(self, saddle):
        """
        |Disqualifies Linkers and Saddles for Single Summit Saddles.
        |          ``v-----v``
        |``Summit 1000    995 Saddle  <-Disqualify``
        |          ``^-----^``
        |
        |          and
        |
        | Summit 1000 ----- 995 Saddle <- Disqualify

        :return: 0 = no disqualified. 1 = disqualified.
        :rtype: int
        """
        uniqueSummits = set([x.summit for x in saddle.summits])
        if len(uniqueSummits) <= 1:
            saddle.disqualify_self_and_linkers(singleSummit=True)
            return 1
        return 0
