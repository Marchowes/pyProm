from unittest import TestCase
from getData import getTestZip
from ..dataload import SRTMLoader
from ..logic import AnalyzeData


class SRTMDataTests(TestCase):
    def setUp(self):
        getTestZip()
        self.datafile = SRTMLoader('/tmp/N44W072.hgt')

    def testSRTMLoad(self):
        """
        Assert some basic info.
        """
        self.assertEqual(self.datafile.span_latitude, 3601)
        self.assertEqual(self.datafile.span_longitude, 3601)
        self.assertEqual(self.datafile.arcsec_resolution, 1)
