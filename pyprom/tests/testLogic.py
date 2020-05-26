"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData


class LogicTests(unittest.TestCase):
    """Test Logic."""

    @classmethod
    def setUpClass(cls):
        """
        Set Up Class.
        These tests make no modification to the objects,
        so we can generate them at the Class level.
        """
        gettestzip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = cls.datafile.datamap
        cls.mtWashingtonDM = cls.datamap.subset(2600, 2500, 30, 30)
        cls.washingtonVicinity = AnalyzeData(cls.mtWashingtonDM)
        cls.summits, cls.saddles, cls.runoffs =\
            cls.washingtonVicinity.run()

    def testFindSummits(self):
        """
        Make sure we find the right number of summits and cols.
        """
        # Should find 3 Summits
        self.assertEqual(len(self.summits), 3)
        # Should find 2 Cols (non edge Effect)
        self.assertEqual(len([x for x in self.saddles
                              if not x.edgeEffect]), 2)
        # Should find 2 Cols. and 8 runoffs
        self.assertEqual(len(self.saddles), 2)
        self.assertEqual(len(self.runoffs), 8)

    def testFindSummitsHighest(self):
        """
        Ensure testFindSummitsHighest finds Mt Washington to be the highest.
        """
        washington = self.summits.highest[0]
        # Metric Elevation
        self.assertEqual(washington.elevation, 1914.0)
        # Feet
        self.assertEqual(washington.feet, 6279.527559055117)

    def testFindTheMultipoint(self):
        """
        Make sure
        <Summit> lat 44.2822225556 long -71.299723 6082.6032ft
        1854.0m MultiPoint True is found to be a multipoint.
        """
        mpSummit = self.summits[0]
        # make sure we find 2 points
        self.assertEqual(len(mpSummit.multipoint), 2)
