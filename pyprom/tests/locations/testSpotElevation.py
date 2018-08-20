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
