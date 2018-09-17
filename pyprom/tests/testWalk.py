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
        self.datamap = self.datafile.datamap
        self.islandpondVT = self.datamap.subset(602, 353, 260, 260)
        self.islandpondVTVicinity = AnalyzeData(self.islandpondVT)
        self.summits, self.saddles, self.runoffs = \
            self.islandpondVTVicinity.run()
        self.domain = Domain(self.islandpondVT, summits=self.summits,
                             saddles=self.saddles, runoffs=self.runoffs,
                             linkers=[])

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
                         self.summits[146])
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
                              if x.disqualified]), 90)
        self.assertEqual(len([x for x in self.domain.linkers
                              if x.disqualified]), 90)

    def testWalkDisqualifyLowerLinkers(self):
        """
        Test disqualify_lower_linkers
        """
        self.domain.walk()
        self.domain.disqualify_lower_linkers()
        self.assertEqual(len([x for x in self.domain.linkers
                              if x.disqualified]), 78)
        self.domain.disqualify_lower_linkers()
        self.assertEqual(len([x for x in self.domain.linkers
                              if x.disqualified]), 78)


class WalkTestsReal(unittest.TestCase):
    """
    Test The Walk Features of feature_discovery
    """

    def setUp(self):
        """
        Set Up Tests.
        """
        gettestzip()
        self.datafile = GDALLoader('/tmp/N44W072.hgt')
        self.datamap = self.datafile.datamap

    def testWalkPathSingleSummit(self):
        """
        Ensure that a walk path from a saddle which both side leads to
        Washington produces the expected results.
        """
        washingtonVicinityDatamap = self.datamap.subset(2608, 2417, 99, 145)
        washingtonVicinity = AnalyzeData(washingtonVicinityDatamap)
        summits, saddles, runoffs = washingtonVicinity.run()
        saddleUnderTest = saddles[2]
        d = Domain(washingtonVicinityDatamap, summits, saddles, runoffs)
        d.walkSingleSaddle(saddleUnderTest)
        summits = [x.summit for x in saddleUnderTest.summits]
        # Ensure summits are the same
        self.assertEqual(summits[0], summits[1])
        # But the linkers are different (different paths)
        self.assertNotEqual(saddleUnderTest.summits[0],
                            saddleUnderTest.summits[1])
