"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for manipulating a pyProm Divide Tree.
"""

import logging

from timeit import default_timer

class DivideTree:
    """Divide Tree"""

    def __init__(self, domain=None, datamap=None):
        """
        A divide tree optionally consumes :class:`Domain`
         and/or :class:`datamap`.
        :param domain:
        :param datamap:
        """
        self.logger = logging.getLogger('{}'.format(__name__))
        self.summits = domain.summits
        self.saddles = domain.saddles
        self.linkers = domain.linkers
        if not datamap:
            self.datamap = domain.datamap
        self.datamap = datamap
        self.busted = list()  # Temporary!

    def run(self):
        """Run"""
        localHighest = self.summits.highest[0]
        localHighest.localHighest = True
        localHighest.parent = localHighest
        start = default_timer()
        then = start
        index = 0
        for summit in self.summits:
            index += 1
            if not index % 1000:
                now = default_timer()
                self.logger.info("{}% split: {} duration: {}".format(index/len(self.summits)*100, round(now-then,2), round(now-start,2)))
                then = now
            self.localProminentRegion(summit)



    def localProminentRegion(self, summit):
        """Lpr"""
        exempt = list()  # list of locally exempt linkers
        self.branchChaser(summit, summit, 0, exempt)

    def branchChaser(self, master, branch, depth, exempt):
        """Branch chaser"""
        depth += 1
        # self.logger.info("Assessing {} off Master {} depth {}"
        # .format(branch, master, depth))
        if depth > 400:
            self.logger.info(
                "Near Max Recurse! Bail! Master: {}".format(master))
            if master not in self.busted:
                self.busted.append(master)
            return
        for linker in branch.saddles:
            if linker.disqualified:
                continue
            if linker in exempt:
                continue
            exempt.append(linker)
            # sort summits connected to saddle.
            summits = sorted(
                [x for x in linker.saddle_summits if x != branch],
                key=lambda x: x.elevation)
            for nextSummit in summits:
                if nextSummit.elevation <= branch.elevation:
                    # branch.parent = master
                    self.branchChaser(master, nextSummit, depth, exempt)
                # Neighbor Higher? then this is a LPR Boundary.
                if nextSummit.elevation > branch.elevation:
                    # self.logger.info("Boundary At {}".format(linker.saddle))
                    if master not in linker.saddle.lprBoundary:
                        linker.saddle.lprBoundary.append(master)
                    if linker.saddle not in master.lprBoundary:
                        master.lprBoundary.append(linker.saddle)

    def parentFinder(self, summit):
        """Nothing"""
        pass
        # for summit in branch.saddles.saddle_summits:
        #     if summit.elevation > branch.elevation:


class LPR:
    """
    LPR
    """

    def __init__(self, highPoint=None,
                 subsetSaddles=None,
                 boundarySaddles=None):
        """
        :param highPoint: hp
        :param subsetSaddles: sad
        :param boundarySaddles: bdry
        """
        self.highPoint = highPoint
        self.subsetSaddles = subsetSaddles
        self.boundarySaddles = boundarySaddles
