"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import getTestZip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData


class LogicTests(unittest.TestCase):
    """Test Logic."""

    def setUp(self):
        """
        Set Up Tests.
        """
        getTestZip()
        self.datafile = GDALLoader('/tmp/N44W072.hgt')
        self.datamap = self.datafile.datamap
        self.mtWashingtonDM = self.datamap.subset(2600, 2500, 30, 30)
        self.washingtonVicinity = AnalyzeData(self.mtWashingtonDM)
        self.summits, self.saddles, self.runoffs = self.washingtonVicinity.run()

    def testFindSummits(self):
        """
        Make sure we find the right number of summits and cols.
        """
        # Should find 3 Summits
        self.assertEqual(len(self.summits), 3)
        # Should find 2 Cols (non edge Effect)
        self.assertEqual(len([x for x in self.saddles
                              if not x.edgeEffect]), 2)
        # Should find 13 cols with edgeEffect.
        self.assertEqual(len(self.saddles), 2)
        self.assertEqual(len(self.runoffs), 4)

    def testFindSummitsHighest(self):
        """
        Ensure testFindSummitsHighest finds Mt Washington to be the highest.
        """
        washington = self.summits.highest[0]
        # Metric Elevation
        self.assertEqual(washington.elevation, 1914.0)
        # Feet
        self.assertEqual(washington.feet, 6279.4512)

    def testFindTheMultipoint(self):
        """
        Make sure
        <Summit> lat 44.2822225556 long -71.299723 6082.6032ft
        1854.0m MultiPoint True is found to be a multipoint.
        """
        mpSummit = self.summits[0]
        # make sure we find 2 points
        self.assertEqual(len(mpSummit.multiPoint), 2)
