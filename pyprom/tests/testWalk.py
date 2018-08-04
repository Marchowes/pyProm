"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from __future__ import division
import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData
from pyprom.domain import Domain


class WalkTests(unittest.TestCase):
    """
    Test The Walk Features of feature_discovery
    """

    def setUp(self):
        """
        Set Up Tests.
        """
        gettestzip()
        self.datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = self.datafile.datamap
        self.islandpondVT = datamap.subset(602, 353, 260, 260)
        self.islandpondVTVicinity = AnalyzeData(self.islandpondVT)
        self.summits, self.saddles, self.runoffs = \
            self.islandpondVTVicinity.run()
        self.domain = Domain(self.islandpondVT, summits=self.summits,
                             saddles=self.saddles, runoffs=self.runoffs,
                             linkers=[])
        self.no = None

    def testWalkSingleSaddleIslandPond(self):
        """
        Test walk around Island Pond VT.
        """
        islandPondSaddleContainer = self.saddles.radius(44.810833,
                                                        -71.8676388,
                                                        10)
        islandPondSaddle = islandPondSaddleContainer[0]
        self.domain.walkSingleSaddle(islandPondSaddle)
        self.assertEqual(len(self.domain.linkers), 2)
        self.assertEqual(len(islandPondSaddle.summits), 2)
        self.assertEqual(islandPondSaddle.summits[0].summit,
                         self.summits[155])
        self.assertEqual(islandPondSaddle.summits[1].summit,
                         self.summits[171])

    def testWalkIslandPond(self):
        """
        Test walk of island pond vicinity
        """
        self.domain.walk()
        self.assertEqual(len(self.domain.linkers), 1067)

    def testWalkMarkRedundantLinkers(self):
        """
        Test mark_redundant_linkers()
        """
        self.domain.walk()
        self.domain.mark_redundant_linkers()
        self.assertEqual(len([x for x in self.domain.linkers
                              if x.disqualified]), 0)
        self.assertEqual(len([x for x in self.domain.linkers
                              if x.disqualified]), 0)

    def testWalkDisqualifyLowerLinkers(self):
        """
        Test disqualify_lower_linkers
        """
        self.domain.walk()
        self.domain.disqualify_lower_linkers()
        self.assertEqual(len([x for x in self.domain.linkers
                              if x.disqualified]), 288)
        self.domain.disqualify_lower_linkers()
        self.assertEqual(len([x for x in self.domain.linkers
                              if x.disqualified]), 288)
