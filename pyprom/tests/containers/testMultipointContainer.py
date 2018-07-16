"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import getTestZip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData
from pyprom.lib.locations.base_coordinate import BaseCoordinate


class MultipointTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set Up Tests."""
        getTestZip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = cls.datafile.datamap
        cls.someslice = datamap.subset(1000, 1000, 100, 100)
        cls.somewhere = AnalyzeData(cls.someslice)
        cls.summits, cls.saddles = cls.somewhere.run()
        cls.saddle = cls.saddles.saddles[0]
        cls.summitWithoutMultipointEdge = cls.summits.summits[4]

    def testMultipointPointsLatLong(self):
        """
        Test multipoint container ability to convert GridPoints
        to BaseCoordinates
        """
        multipoint = self.summitWithoutMultipointEdge.multiPoint
        bc0 = BaseCoordinate(44.70986111111111, -71.71263888888889)
        bc1 = BaseCoordinate(44.70986111111111, -71.71236111111111)
        self.assertEqual(multipoint.pointsLatLong[0], bc0)
        self.assertEqual(multipoint.pointsLatLong[1], bc1)

    def testMultipointJsonNoEdge(self):
        """
        Test multipoint container inverseEdgePoints count is as expected.
        """
        multipoint = self.saddle.multiPoint
        self.assertEqual(len(multipoint.inverseEdgePoints.points), 7)

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
        Test multipoint container inverseEdgePoints count is as expected.
        """
        multipoint = self.saddle.multiPoint
        self.assertEqual(multipoint.__repr__(), "<Multipoint> elevation(m): 552.0, points 4")
