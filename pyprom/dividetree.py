"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for manipulating a pyProm Divide Tree.
"""

import logging

class DivideTree(object):
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
        self.datamap = datamap
        self.busted = list() # Temporary!

    def run(self):
        localHighest = self.summits.highest[0]
        localHighest.localHighest = True
        localHighest.parent = localHighest


    def localProminentRegion(self, summit):
        exempt = list() #list of locally exempt linkers
        self.branchChaser(summit, summit, 0, exempt)


    def branchChaser(self, master, branch, depth, exempt):
        depth += 1
        #self.logger.info("Assessing {} off Master {} depth {}".format(branch, master, depth))
        if depth > 400:
            self.logger.info("Near Max Recurse! Bail! Master: {}".format(master))
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
                    #branch.parent = master
                    self.branchChaser(master, nextSummit, depth, exempt)
                # Neighbor Higher? then this is a LPR Boundary.
                if nextSummit.elevation > branch.elevation:
                    #self.logger.info("Boundary At {}".format(linker.saddle))
                    if master not in linker.saddle.lprBoundary:
                        linker.saddle.lprBoundary.append(master)

    def parentFinder(self, summit):
        pass









        # for summit in branch.saddles.saddle_summits:
        #     if summit.elevation > branch.elevation:


    class LPR(object):
        def __init__(self, highPoint = None, subsetSaddles = None, boundarySaddles = None):
            self.highPoint = highPoint
            self.subsetSaddles = subsetSaddles
            self.boundarySaddles = boundarySaddles


