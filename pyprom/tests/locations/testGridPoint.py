"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.lib.loaders.gdal_loader import GDALLoader
from pyprom.lib.locations.gridpoint import GridPoint
from pyprom.lib.locations.spot_elevation import SpotElevation


class GridPointTests(unittest.TestCase):
    """Test BaseGridPoint."""

    @classmethod
    def setUpClass(cls):
        """
        Set up shared resources
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = datafile.to_datamap()

    def testGridPointCreate(self):
        """
        Ensure we can create a basic :class:`GridPoint`
        """
        gp = GridPoint(1, 2, 3)
        self.assertEqual(gp.x, 1)
        self.assertEqual(gp.y, 2)
        self.assertEqual(gp.elevation, 3)

    def testGridPointToDict(self):
        """
        Ensure to_dict() works as expected
        """
        gp = GridPoint(1, 2, 3)
        gp_dict = gp.to_dict()
        self.assertEqual(gp_dict, {"x": 1, "y": 2, "elevation": 3})

    def testGridPointToTuple(self):
        """
        Ensure to_tuple() works as expected
        """
        gp = GridPoint(1, 2, 3)
        gp_tuple = gp.to_tuple()
        self.assertEqual(gp_tuple, (1, 2, 3))

    def testGridPointFromDict(self):
        """
        Ensure from_dict() works as expected
        """
        gp = GridPoint(1, 2, 3)
        gp_dict = {"x": 1, "y": 2, "elevation": 3}
        self.assertEqual(GridPoint.from_dict(gp_dict), gp)

    def testGridPointFromTuple(self):
        """
        Ensure from_tuple() works as expected
        """
        gp = GridPoint(1, 2, 3)
        gp_tuple = (1, 2, 3)
        self.assertEqual(GridPoint.from_tuple(gp_tuple), gp)

    def testGridPointToTuple(self):
        """
        Ensure to_tuple() works as expected
        """
        gp = GridPoint(1, 2, 3)
        gp_tuple = gp.to_tuple()
        self.assertEqual(gp_tuple, (1, 2, 3))

    def testGridPointToSpotElevation(self):
        """
        Ensure toSpotElevation works as expected
        """
        gp = GridPoint(1, 2, 3)
        se = gp.toSpotElevation(self.datamap)
        se_static = SpotElevation(44.999861111111116, -71.99958333333333, 3)
        self.assertEqual(se, se_static)

    def testGridPointEquals(self):
        """
        Ensure __eq__() works as expected
        """
        gp1 = GridPoint(1, 2, 3)
        gp2 = GridPoint(1, 2, 3)
        self.assertEqual(gp1, gp2)

    def testGridPointNotEquals(self):
        """
        Ensure __ne__() works as expected
        """
        gp1 = GridPoint(1, 2, 3)
        gp2 = GridPoint(2, 2, 3)
        self.assertNotEqual(gp1, gp2)

    def testGridPointLessThan(self):
        """
        Ensure __lt__() works as expected
        """
        gp1 = GridPoint(1, 2, 3)
        gp2 = GridPoint(1, 2, 4)
        self.assertTrue(gp1 < gp2)

    def testGridPointHash(self):
        """
        Ensure __hash__() works as expected
        """
        gp1 = GridPoint(1, 2, 3)
        gp2 = GridPoint(1, 2, 3)
        gp_set = set([gp1, gp2])
        self.assertEqual(len(gp_set), 1)

    def testGridPointRepr(self):
        """
        Ensure __repr__() works as expected
        """
        gp = GridPoint(1, 2, 3)
        self.assertEqual(gp.__repr__(),
                         "<GridPoint> x: 1, y: 2, elevation(m): 3")
