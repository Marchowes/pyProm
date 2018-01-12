"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from __future__ import division
import unittest
from pyprom.tests.getData import getTestZip
from pyprom.dataload import GDALLoader


class DataMapTests(unittest.TestCase):
    """Test Data Maps."""

    def setUp(self):
        """Set Up Tests."""
        getTestZip()
        self.datafile = GDALLoader('/tmp/N44W072.hgt')
        self.datamap = self.datafile.datamap

    def testGeneralDataMap(self):
        """Test defaults."""
        self.assertEqual(self.datamap.upperLeftX, 45.00013888888889)
        self.assertEqual(self.datamap.upperLeftY, -72.00013888888888)
        self.assertEqual(self.datamap.max_x, 3600)
        self.assertEqual(self.datamap.max_y, 3600)
        self.assertEqual(self.datamap.res_x, -0.0002777777777777778)
        self.assertEqual(self.datamap.res_y, 0.0002777777777777778)
        self.assertEqual(self.datamap.span_x, 3601)
        self.assertEqual(self.datamap.span_y, 3601)
        self.assertEqual(self.datamap.unit, "METERS")
        self.assertEqual(self.datamap.lower_left, (43.999861111111116,
                                                   -72.00013888888888))
        self.assertEqual(self.datamap.upper_left, (45.00013888888889,
                                                   -72.00013888888888))
        self.assertEqual(self.datamap.lower_right, (43.999861111111116,
                                                    -70.9998611111111))
        self.assertEqual(self.datamap.upper_right, (45.00013888888889,
                                                    -70.9998611111111))

    def testLatLongToXY(self):
        """Test Lat-long to XY function."""
        input = [(44.000138, -71.000138888), (44.1, -71.1), (44.2, -71.2),
                 (44.25, -71.25), (44.33333, -71.33333), (44.5, -71.5),
                 (44.6125, -71.6125), (44.75, -71.75), (44.7777, -71.7777),
                 (44.8125, -71.8125), (45.00013888888889, -72.00013888888888)]
        output = [(3600, 3600), (3241, 3241), (2880, 2880), (2701, 2700),
                  (2401, 2401), (1801, 1800), (1396, 1395), (901, 900),
                  (801, 801), (676, 675), (0, 0)]
        for index, value in enumerate(input):
            self.assertEqual(self.datamap.latlong_to_xy(value[0], value[1]),
                             output[index])

    def test_XY_latlong_determinism(self):
        """
        Ensure converting from XY to LATLONG and back returns the same results.
        """
        for x in range(0, 3601, 17):
            for y in range(0, 3601, 1):
                lat, long = self.datamap.xy_to_latlong(x, y)
                _x, _y = self.datamap.latlong_to_xy(lat, long)
                self.assertEqual(_x, x)
                self.assertEqual(_y, y)

    def testSubset(self):
        """Test that datamap subsets return accurate subsets."""
        subset = self.datamap.subset(100, 100, 200, 199)
        self.assertEqual(subset.upperLeftX, 44.97236111111111)
        self.assertEqual(subset.upperLeftY, -71.97236111111111)
        self.assertEqual(subset.max_x, 199)
        self.assertEqual(subset.max_y, 198)
        self.assertEqual(subset.res_x, -0.0002777777777777778)
        self.assertEqual(subset.res_y, 0.0002777777777777778)
        self.assertEqual(subset.span_x, 200)
        self.assertEqual(subset.span_y, 199)
        self.assertEqual(subset.unit, "METERS")
        self.assertEqual(subset.lower_left, (44.916805555555555,
                                             -71.97236111111111))
        self.assertEqual(subset.upper_left, (44.97236111111111,
                                             -71.97236111111111))
        self.assertEqual(subset.lower_right, (44.916805555555555,
                                              -71.91708333333334))
        self.assertEqual(subset.upper_right, (44.97236111111111,
                                              -71.91708333333334))


if __name__ == '__main__':
    unittest.main()
