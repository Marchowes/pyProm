"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.locations.spot_elevation import SpotElevation
from pyprom.lib.locations.base_gridpoint import BaseGridPoint


class SpotElevationTests(unittest.TestCase):
    """Test SpotElevationContainer"""

    def testSpotElevationCreate(self):
        """
        Ensure we can create a SpotElevation Object
        """
        se = SpotElevation(1, 10, 100,
                           edge=True,
                           edgePoints=[BaseGridPoint(1, 1)])
        self.assertEqual(se.latitude, 1)
        self.assertEqual(se.longitude, 10)
        self.assertEqual(se.elevation, 100)
        self.assertEqual(se.edgeEffect, True)
        self.assertEqual(se.edgePoints, [BaseGridPoint(1, 1)])
        self.assertEqual(len(se.id), 15)

    def testSpotElevationDMS(self):
        """
        Ensure dms produces expected results.
        """
        se = SpotElevation(44.11291666666667, -71.37791666666666, 100)
        shouldBe = ((44, 6, 46.50000000001398), (-71, 22, 40.49999999999045))
        self.assertTupleEqual(se.dms, shouldBe)
