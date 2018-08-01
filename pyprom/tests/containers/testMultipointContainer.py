"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData
from pyprom.lib.locations.base_coordinate import BaseCoordinate
from pyprom.lib.locations.base_gridpoint import BaseGridPoint
from pyprom.lib.containers.multipoint import MultiPoint


class MultipointTests(unittest.TestCase):
    """Test Multipoint Container."""

    @classmethod
    def setUpClass(cls):
        """Set Up Tests."""
        gettestzip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = cls.datafile.datamap
        cls.someslice = cls.datamap.subset(1000, 1000, 100, 100)
        cls.somewhere = AnalyzeData(cls.someslice)
        cls.summits, cls.saddles, cls.runoffs = cls.somewhere.run()
        cls.saddle = cls.runoffs.saddles[0]
        cls.summitWithoutMultipointEdge = cls.summits.summits[4]
        cls.bgp11 = BaseGridPoint(1, 1)
        cls.bgp22 = BaseGridPoint(2, 2)
        cls.bgp33 = BaseGridPoint(3, 3)

    def testMultipointPointsLatLong(self):
        """
        Test multipoint container ability to convert GridPoints
        to BaseCoordinates.
        """
        multipoint = self.summitWithoutMultipointEdge.multiPoint
        bc0 = BaseCoordinate(44.70986111111111, -71.71263888888889)
        bc1 = BaseCoordinate(44.70986111111111, -71.71236111111111)
        self.assertEqual(multipoint.pointsLatLong[0], bc0)
        self.assertEqual(multipoint.pointsLatLong[1], bc1)

    def testMultipointJsonNoEdge(self):
        """
        Test multipoint container perimeter count is as expected.
        """
        multipoint = self.saddle.multiPoint
        self.assertEqual(len(multipoint.perimeter), 7)

    def testMultipointToJSON(self):
        """
        Test multipoint to json produces expected results.
        """
        result = """[
    {
        "coordinate": {
            "latitude": 44.72236111111111,
            "longitude": -71.72180555555556
        },
        "gridpoint": {
            "x": 0,
            "y": 2
        }
    },
    {
        "coordinate": {
            "latitude": 44.72236111111111,
            "longitude": -71.72152777777778
        },
        "gridpoint": {
            "x": 0,
            "y": 3
        }
    },
    {
        "coordinate": {
            "latitude": 44.72236111111111,
            "longitude": -71.72125
        },
        "gridpoint": {
            "x": 0,
            "y": 4
        }
    },
    {
        "coordinate": {
            "latitude": 44.72208333333334,
            "longitude": -71.72097222222223
        },
        "gridpoint": {
            "x": 1,
            "y": 5
        }
    }
]"""
        multipoint = self.saddle.multiPoint
        self.assertEqual(result, multipoint.to_json())

    def testMultipointRepr(self):
        """
        Ensure __repr__ returns expected results.
        """
        multipoint = self.saddle.multiPoint
        self.assertEqual(multipoint.__repr__(),
                         "<Multipoint> elevation(m): 552.0, points 4")

    def testMultipointIterator(self):
        """
        Ensure __iter__ returns expected results.
        """
        self.assertEqual(len([x for x in
                              self.summitWithoutMultipointEdge.multiPoint]), 2)

    def testMultipointLen(self):
        """
        Ensure __len__ returns expected results.
        """
        self.assertEqual(len(self.summitWithoutMultipointEdge.multiPoint), 2)

    def testMultipointSetItem(self):
        """
        Ensure __setattr__ works as expected.
        """
        multipoint = MultiPoint([self.bgp11], 100, self.datamap)
        self.assertEqual(len(multipoint), 1)
        multipoint[0] = self.bgp22
        self.assertEqual(multipoint[0], self.bgp22)

    def testMultipointSetItemNeg(self):
        """
        Ensure __setattr__ Disallows Non BaseGridpoints to be set.
        """
        multipoint = MultiPoint([self.bgp11], 100, self.datamap)
        self.assertEqual(len(multipoint), 1)
        with self.assertRaises(TypeError):
            multipoint[0] = "wtf"

    def testMultipointGetItem(self):
        """
        Ensure __getattr__ works as expected.
        """
        multipoint = MultiPoint([self.bgp11], 100, self.datamap)
        self.assertEqual(len(multipoint), 1)
        self.assertEqual(multipoint[0], self.bgp11)

    def testMultipointBadAppend(self):
        """
        Ensure adding string to Multipoint fails.
        """
        multipoint = MultiPoint([self.bgp11], 100, self.datamap)
        with self.assertRaises(TypeError):
            multipoint.append("stuff")

    def testMultipointGoodAppend(self):
        """
        Ensure adding GridPoint to SummitsContainer succeeds.
        """
        multipoint = MultiPoint([self.bgp11], 100, self.datamap)
        multipoint.append(self.bgp22)
        self.assertEqual(len(multipoint), 2)

    def testMultipointEq(self):
        """
        Ensure __eq__ works as expected.
        """
        multipoint = MultiPoint([self.bgp11], 100, self.datamap)
        multipoint2 = MultiPoint([self.bgp11], 100, self.datamap)
        multipoint3 = MultiPoint([self.bgp22], 100, self.datamap)

        self.assertEqual(multipoint, multipoint2)
        test = multipoint2 == multipoint3
        self.assertFalse(test)

    def testMultipointNe(self):
        """
        Ensure __ne__ works as expected.
        """
        multipoint = MultiPoint([self.bgp11], 100, self.datamap)
        multipoint2 = MultiPoint([self.bgp11], 100, self.datamap)
        multipoint3 = MultiPoint([self.bgp22], 100, self.datamap)

        self.assertNotEqual(multipoint, multipoint3)
        test = multipoint != multipoint2
        self.assertFalse(test)
