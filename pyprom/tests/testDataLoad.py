"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.lib.loaders.gdal_loader import GDALLoader


class GDALDataTests(unittest.TestCase):
    """Test Data Loader."""

    def setUp(self):
        """Download datafile."""
        gettestzip()
        self.filename = '/tmp/N44W072.hgt'
        self.datafile = GDALLoader('/tmp/N44W072.hgt')

    def testGDALLoad(self):
        """Assert some basic info. from some SRTM data."""
        self.assertEqual(str(self.datafile.filename), self.filename)
        self.assertIsNotNone(self.datafile.source_gdal_dataset)
        self.assertEqual(self.datafile.source_gdal_dataset.RasterCount, 1)
        self.assertEqual(self.datafile.source_gdal_dataset.RasterXSize, 3601)
        self.assertEqual(self.datafile.source_gdal_dataset.RasterYSize, 3601)

        self.assertIsNotNone(self.datafile.gdal_dataset)
        self.assertEqual(self.datafile.source_gdal_dataset.RasterCount, 1)
        self.assertEqual(self.datafile.source_gdal_dataset.RasterXSize, 3601)
        self.assertEqual(self.datafile.source_gdal_dataset.RasterYSize, 3601)

if __name__ == '__main__':
    unittest.main()
