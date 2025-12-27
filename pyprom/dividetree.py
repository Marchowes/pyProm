"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for manipulating a pyProm Divide Tree.
"""
from __future__ import annotations

import logging

from fastkml import kml
from shapely.geometry import Point, LineString

from timeit import default_timer

from typing import TYPE_CHECKING, List, Dict, Tuple
if TYPE_CHECKING:
    from pyprom import DataMap
    from pyprom.domain_map import DomainMap
    from pyprom.lib.locations.summit import Summit
    from pyprom.lib.locations.saddle import Saddle
    from pyprom.lib.containers.linker import Linker


class DivideTree:
    """Divide Tree"""

    def __init__(self,
            domain: DomainMap | None = None, 
            datamap: DataMap | None = None
        ):
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

    def run(self) -> None:
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



    def localProminentRegion(self, summit: Summit) -> None:
        """Lpr"""
        exempt = {} # hash of locally exempt linkers
        path = list() # list of linkers
        lprPathObj = LPRPaths()

        self.branchChaser(summit, summit, 0, exempt, path, lprPathObj)
        summit.lprPaths = lprPathObj

        #print("done")

    def branchChaser(self, 
            master: Summit, 
            branch: Summit, 
            depth: int, 
            exempt: Dict[str, bool], 
            path: List[Linker],
            lprPathObj: LPRPaths
        ) -> None:
        """Branch chaser
        :param: master :class:`Summit`
        :param: branch :class:`Summit`
        :depth: int
        :exempt: []:class:`Linkers`
        """
        depth += 1
        # self.logger.info("Assessing {} off Master {} depth {}"
        # .format(branch, master, depth))
        if depth > 400:
            self.logger.info(
                "Near Max Recurse! Bail! Master: {}".format(master))
            if master not in self.busted:
                self.busted.append(master)
            return

        #print("DEPTH: {}".format(depth))

        # Main Loop
        for linker in branch.saddles:
            # if depth == 1:
            #     print("top level... bitch")
            if linker.disqualified:
                # if depth == 1:
                #     print("Shit, thats a problem...")
                continue
            if exempt.get(linker.id, False):
                # if depth == 1:
                #     print("wtf, why?")
                continue
            exempt[linker.id] = True

            if linker.saddle.disqualified:
                # print("linker disqualified!")
                continue
            # did we bump up against an edge?
            if linker.saddle.edgeEffect:
                path_terminal = path.copy()
                path_terminal.append(linker)
                lprPathObj.LPRpaths.append(LPRpath(path_terminal, linker.saddle))
                lprPathObj.edge = True
                continue

            # loop through all summits linked to the saddle linked to the linker in the main loop
            for nextSummitLinker in linker.linkers_to_summits_connected_via_saddle():
                # If we've already explored this link, continue.
                if exempt.get(nextSummitLinker.id) or linker.disqualified:
                    continue

                # did we bump up against an edge?
                if nextSummitLinker.summit.elevation <= branch.elevation and nextSummitLinker.summit.edgeEffect:
                    path_terminal = path.copy()
                    path_terminal.append(linker)
                    lprPathObj.LPRpaths.append(LPRpath(path_terminal, linker.saddle))
                    lprPathObj.edge = True
                # Linked Summit Lower or equal? chase it.
                elif nextSummitLinker.summit.elevation <= branch.elevation:
                    path_for_recurse = path.copy()
                    path_for_recurse.append(linker)
                    path_for_recurse.append(nextSummitLinker)
                    # branch.parent = master
                    self.branchChaser(master, nextSummitLinker.summit, depth, exempt, path_for_recurse, lprPathObj)
                # Linked Summit Higher? then this is a LPR Boundary.
                elif nextSummitLinker.summit.elevation > branch.elevation:
                    path_terminal = path.copy()
                    path_terminal.append(linker)
                    saddle = linker.saddle
                    lprPathObj.LPRpaths.append(LPRpath(path_terminal, saddle))
                    #self.logger.info("Boundary At {}".format(linker.saddle))
                    if master not in saddle.lprBoundary:
                        saddle.lprBoundary.append(master)
                    if saddle not in master.lprBoundary:
                        master.lprBoundary.append(saddle)
                #print("terminal point {}".format(nextSummitLinker.summit))



    def parentFinder(self, summit: Summit):
        """Nothing"""
        pass
        # for summit in branch.saddles.summits_connected_via_saddle():
        #     if summit.elevation > branch.elevation:

class LPRPaths:
    def __init__(self):
        self.LPRpaths: List[LPRpath] = list()
        self.edge: bool = False

    def elements_for_kml(self) -> Tuple[Saddle | Summit | Linker]:
        elements = []
        for element in self.LPRpaths:
            elements.extend(element.elements_for_kml())
        return elements

class LPRpath:
    def __init__(self,
            path: List[Linker], 
            saddle: Saddle
        ):
        self.path = path
        self.saddle = saddle
        self.decline = self.path[0].summit.feet - self.saddle.feet

    def elements_for_kml(self) -> Tuple[Saddle | Summit | Linker]:
        saddles = []
        summits = []
        linkers = []
        for linker in self.path:
            saddles.append(linker.saddle)
            summits.append(linker.summit)
            linkers.append(linker)
        return summits + saddles + linkers

    def __repr__(self) -> str:
        return "<LPRPath> Saddle {} Hops {} Decline {}".format(self.saddle, len(self.path), self.decline)
