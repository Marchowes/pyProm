"""self.domain.summits
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.domain_map import DomainMap
from pyprom.dividetree import DivideTree


class DivideTreeTests(unittest.TestCase):
    """Test Divide Tree."""

    def setUp(self):
        """
        Set Up Tests.
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = datafile.datamap
        self.someslice = datamap.subset(2494, 2240, 700, 800)  # this is
        #  the one we want in the end...
        # self.someslice = datamap.subset(2594, 2340, 500, 500)
        # this is fine too apparently... (or not)
        # self.someslice = datamap.subset(2694, 2440, 400, 400)
        self.domain = DomainMap(self.someslice)
        self.domain.run(sparse=True)
        # self.domain.run()

    def testDivideTreeInitial(self):
        """
        Test divide tree initial
        """
        # self.domain.disqualify_lower_linkers()
        # self.domain.mark_redundant_linkers()
        import logging
        logging.basicConfig(level=logging.DEBUG)
        self.domain.detect_basin_saddles()
        dt = DivideTree(domain=self.domain)
        w = self.domain.summits.highest[0]
        dt.localProminentRegion(w)
        print(w.lprBoundary)

    def testDivideTreeOther(self):
        """
        Test divide tree initial
        """
        # self.domain.disqualify_lower_linkers()
        # self.domain.mark_redundant_linkers()
        import logging
        logging.basicConfig(level=logging.DEBUG)
        self.domain.detect_basin_saddles()
        dt = DivideTree(domain=self.domain)
        lpr = dt.run()
        # w = self.domain.summits.highest[0]
        # dt.localProminentRegion(w)
        print(lpr)