from unittest import TestCase
from getData import getTestZip
from ..dataload import SRTMLoader
from ..logic import AnalyzeData
from ..lib.locations.summit import Summit
from ..lib.locations.saddle import Saddle


class LogicTests(TestCase):
    def setUp(self):
        getTestZip()
        self.datafile = SRTMLoader('/tmp/N44W072.hgt')
        self.datamap = self.datafile.datamap
        self.mtWashingtonDM = self.datamap.subset(2600, 2500, 30, 30)
        self.washingtonVicinity = AnalyzeData(self.mtWashingtonDM)
        self.summits, self.saddles = self.washingtonVicinity.analyze()

    def testFindSummits(self):
        """
        Make sure we find the right number of summits and cols.
        """

        # Should find 3 Summits
        self.assertEqual(len(self.summits.points), 3)
        # Should find 2 Cols (non edge Effect)
        self.assertEqual(len([x for x in self.saddles.points if not x.edgeEffect]), 2)
        # Should find 13 cols with edgeEffect.
        self.assertEqual(len(self.saddles.points), 13)


    def testFindSummitsHighest(self):
        """
        Ensure it finds Mt Washington to be the highest.
        """
        washington = self.summits.highest[0]
        # Metric Elevation
        self.assertEqual(washington.elevation, 1914.0)
        # Feet
        self.assertEqual(washington.feet, 6279.4512)

    def testFindTheMultipoint(self):
        """
        Make sure
        <Summit> lat 44.2822225556 long -71.299723 6082.6032ft 1854.0m MultiPoint True
        is found to be a multipoint.
        """
        mpSummit = self.summits.points[0]
        # make sure we find 2 points
        self.assertEqual(len(mpSummit.multiPoint.points),2)









