"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader


class GDALDataTests(unittest.TestCase):
    """Test Data Loader."""

    def setUp(self):
        """Download datafile."""
        gettestzip()
        self.datafile = GDALLoader('/tmp/N44W072.hgt')

    def testGDALLoad(self):
        """Assert some basic info. from some SRTM data."""
        self.assertEqual(self.datafile.linear_unit, 1.0)
        self.assertEqual(self.datafile.linear_unit_name, 'Meter')
        self.assertEqual(self.datafile.upperLeftX, -72.00013888888888)
        self.assertEqual(self.datafile.upperLeftY, 45.00013888888889)
        self.assertEqual(self.datafile.span_x, 3601)
        self.assertEqual(self.datafile.span_y, 3601)


if __name__ == '__main__':
    unittest.main()
