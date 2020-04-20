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

        #self.islandpondVT = self.datamap.subset(582, 333, 300, 300)

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
        islandPondSaddleContainer = self.saddles.radius(44.81069,
                                                        -71.86763,
                                                        10)
        islandPondSaddle = islandPondSaddleContainer[0]
        self.domain.walk([islandPondSaddle])
        self.assertEqual(len(self.domain.linkers), 2)
        saddle = self.domain.linkers[0].saddle
        self.assertEqual(len(saddle.summits), 2)
        self.assertEqual(saddle.summits[0].summit,
                         self.summits[142])
        self.assertEqual(saddle.summits[1].summit,
                         self.summits[171])

    def testWalkIslandPond(self):
        """
        Test walk of island pond vicinity
        """
        self.domain.run(superSparse=True)
        self.domain.walk()
        self.assertEqual(len(self.domain.linkers), 1050)


class WalkRealTests(unittest.TestCase):
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
        summits, saddles, runoffs = washingtonVicinity.run(rebuildSaddles=False)
        d = Domain(washingtonVicinityDatamap, summits, saddles, runoffs)
        sut, _ = d.walk([saddles[2]])
        sut = sut[0]
        summits = [x.summit for x in sut.summits]
        # Ensure summits are the same
        self.assertEqual(summits[0], summits[1])
        # But the linkers are different.
        self.assertNotEqual(sut.summits[0].id,
                            sut.summits[1].id)
