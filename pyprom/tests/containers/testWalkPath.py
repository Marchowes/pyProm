"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest

from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.lib.locations.gridpoint import GridPoint
from pyprom.lib.locations.base_gridpoint import BaseGridPoint
from pyprom.lib.locations.base_coordinate import BaseCoordinate
from pyprom.lib.locations.spot_elevation import SpotElevation
from pyprom.lib.containers.walkpath import WalkPath


class WalkPathTests(unittest.TestCase):
    """Test WalkPath Container."""

    @classmethod
    def setUpClass(cls):
        """Pull down datamaps just once"""
        gettestzip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = cls.datafile.datamap

    def setUp(self):
        """Set up tests."""
        self.path = [(44.13847222222223, -71.02402777777777),
                     (44.13847222222223, -71.02402777777777),
                     (44.138194444444444, -71.02402777777777),
                     (44.13791666666667, -71.02374999999999),
                     (44.137638888888894, -71.02374999999999),
                     (44.13736111111111, -71.02374999999999),
                     (44.13736111111111, -71.02374999999999),
                     (44.13708333333334, -71.02374999999999),
                     (44.136805555555554, -71.02347222222221),
                     (44.13708333333334, -71.02319444444444),
                     (44.13708333333334, -71.02319444444444),
                     (44.136805555555554, -71.02291666666666),
                     (44.13708333333334, -71.02263888888888),
                     (44.13708333333334, -71.02236111111111),
                     (44.137638888888894, -71.02263888888888),
                     (44.13736111111111, -71.02263888888888),
                     (44.13708333333334, -71.02236111111111),
                     (44.13708333333334, -71.02208333333333),
                     (44.13736111111111, -71.02236111111111)]

        self.walkpath = WalkPath(self.path)

    def testWalkPathPath(self):
        """
        Ensure path getter produces expected output.
        """
        self.assertEqual(self.walkpath.path, [BaseCoordinate(x[0], x[1])
                                              for x in self.path])

    def testWalkPathSpotElevation(self):
        """
        Ensure SpotElevation() produces expected output.
        """
        se = []
        for lat, long in self.path:
            x, y = self.datamap.latlong_to_xy(lat, long)
            elevation = self.datamap.numpy_map[x, y]
            se.append(SpotElevation(lat, long, elevation))
        self.assertEqual(self.walkpath.spotElevation(self.datamap), se)

    def testWalkPathBaseGridPoint(self):
        """
        Ensure BaseGridPoint() produces expected output.
        """
        bgp = []
        for lat, long in self.path:
            x, y = self.datamap.latlong_to_xy(lat, long)
            bgp.append(BaseGridPoint(x, y))
        self.assertEqual(self.walkpath.baseGridPoint(self.datamap), bgp)

    def testWalkPathGridPoint(self):
        """
        Ensure GridPoint() produces expected output.
        """
        gp = []
        for lat, long in self.path:
            x, y = self.datamap.latlong_to_xy(lat, long)
            elevation = self.datamap.numpy_map[x, y]
            gp.append(GridPoint(x, y, elevation))
        self.assertEqual(self.walkpath.gridPoint(self.datamap), gp)

    def testWalkPathFromDict(self):
        """
        Ensure to_dict() and from_dict() produce the expected results.
        """
        wpDict = self.walkpath.to_dict()
        newWp = WalkPath.from_dict(wpDict)
        self.assertEqual(self.walkpath, newWp)
