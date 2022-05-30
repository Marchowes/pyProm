"""self.domain.summits
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.domain_map import DomainMap
from lib.logic.parentage import ProminenceIslandParentFinder


class DivideTreeTests(unittest.TestCase):
    """Test Divide Tree."""

    def setUp(self):
        """
        Set Up Tests.
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')

        self.domain = DomainMap.read("/home/mhowes/Elements_TEMP/pyprom_results/080/N44W072_full_run_edge_cycle2.dom", datafile.datamap)


        # datamap = datafile.datamap
        # self.someslice = datamap.subset(2494, 2240, 700, 800)  # this is
        # #  the one we want in the end...
        # # self.someslice = datamap.subset(2594, 2340, 500, 500)
        # # this is fine too apparently... (or not)
        # # self.someslice = datamap.subset(2694, 2440, 400, 400)
        # self.domain = DomainMap(self.someslice)
        # self.domain.run(sparse=True)
        # # self.domain.run()

    # def testDivideTreeInitial(self):
    #     """
    #     Test divide tree initial
    #     """
    #     # self.domain.disqualify_lower_linkers()
    #     # self.domain.mark_redundant_linkers()
    #     import logging
    #     logging.basicConfig(level=logging.DEBUG)
    #     self.domain.detect_basin_saddles()
    #     dt = ProminenceIsland(domain=self.domain)
    #     w = self.domain.summits.highest[0]
    #     dt.localProminentRegion(w)
    #     print(w.lprBoundary)
    #
    # def testDivideTreeOther(self):
    #     """
    #     Test divide tree initial
    #     """
    #     # self.domain.disqualify_lower_linkers()
    #     # self.domain.mark_redundant_linkers()
    #     import logging
    #     logging.basicConfig(level=logging.DEBUG)
    #     self.domain.detect_basin_saddles()
    #     dt = ProminenceIsland(domain=self.domain)
    #     lpr = dt.run()
    #     # w = self.domain.summits.highest[0]
    #     # dt.localProminentRegion(w)
    #     print(lpr)

    # def testDivideTreeOther(self):
    #     """
    #     Test divide tree initial
    #     """
    #     # x = ProminenceIslandFinder(self.domain.summits.highest[0])
    #     # foo = x.find_prominence_island_and_sub_islands()
    #     # print("hi")
    #     #sumsum = [x for x in self.domain.summits if x.id == 'su:FpzutWlK3EBA'][0]
    #
    #     #sumsum = self.domain.summits.elevationRange(5685,5686)[0] # jefferson
    #     sumsum = [x for x in self.domain.summits if x.id == 'su:kAiZHl2Utprc'][0] #lafayette
    #     x = ProminenceIslandParentFinder(sumsum)
    #     a,b =x.find_parent2()
    #     print (a,b)


    def testDivideTreeOther(self):
        """
        Test divide tree initial
        """
        # x = ProminenceIslandFinder(self.domain.summits.highest[0])
        # foo = x.find_prominence_island_and_sub_islands()
        # print("hi")
        #sumsum = [x for x in self.domain.summits if x.id == 'su:FpzutWlK3EBA'][0] #near clay
        #sumsum = self.domain.summits.elevationRange(5685,5686)[0] # jefferson
        #sumsum = [x for x in self.domain.summits if x.id == 'su:kAiZHl2Utprc'][0] #lafayette
        #sumsum = [x for x in self.domain.summits if x.id == 'su:QrdGWnTKqeFw'][0]# sableshoulder
        sumsum = [x for x in self.domain.summits if x.id == 'su:usnWYNyeYf9d'][0] #washington
        x = ProminenceIslandParentFinder(sumsum)
        a,b,c,d =x.find_parent()
        print (a,b,c)