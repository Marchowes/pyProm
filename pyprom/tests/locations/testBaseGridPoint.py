"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.locations.base_gridpoint import BaseGridPoint


class BaseGridPointTests(unittest.TestCase):
    """Test BaseGridPoint."""

    def testCreateBaseGridPoint(self):
        """
        Test creation of object through __init__
        """
        test = BaseGridPoint(100, 101)
        self.assertEqual(test.x, 100)
        self.assertEqual(test.y, 101)

    def testBaseGridPointToDict(self):
        """
        Ensure to_dict() returns expected results.
        """
        test = BaseGridPoint(1, 2)
        self.assertEqual(test.to_dict(), {'x': 1, 'y': 2})

    def testBaseGridPointDistance(self):
        """
        Ensure distance() returns expected results.
        """
        gp1 = BaseGridPoint(0,0)
        gp2 = BaseGridPoint(10,0)
        distance = gp1.distance(gp2)
        self.assertEqual(distance,10)

    def testBaseGridPointHash(self):
        """
        Ensure __hash__() returns expected results.
        """
        x = 4
        y = 5
        test = BaseGridPoint(x,y)
        self.assertEqual(hash((x, y)), test.__hash__())

    def testBaseGridPointEq(self):
        """
        Ensure __eq__() returns expected results.
        """
        gp1 = BaseGridPoint(0,0)
        gp2 = BaseGridPoint(0,0)
        self.assertEqual(gp1, gp2)

    def testBaseGridPointLt(self):
        """
        Ensure __lt__() returns expected results.
        The concept of lt for a BaseGridPoint is arbitrary and only
        exists for other Python features.
        """
        gp1 = BaseGridPoint(0,0)
        gp2 = BaseGridPoint(1,0)
        self.assertLess(gp1, gp2)

    def testBaseGridPointRepr(self):
        """
        Ensure __repr__() returns expected results.
        """
        test = BaseGridPoint(10, 100)
        self.assertEqual(test.__repr__(), "<BaseGridPoint> x: 10, y: 100")


