from __future__ import division
import unittest
from .getData import getTestZip
from pyprom.dataload import SRTMLoader




class DataMapTests(unittest.TestCase):
    def setUp(self):
        getTestZip()
        self.datafile = SRTMLoader('/tmp/N44W072.hgt')
        self.datamap = self.datafile.datamap

    def testGeneralDataMap(self):
        """
        Test defaults
        """
        self.assertEqual(self.datamap.latitude, 44)
        self.assertEqual(self.datamap.longitude, -72)
        self.assertEqual(self.datamap.latitude_max, 45.0)
        self.assertEqual(self.datamap.longitude_max, -71.0)
        self.assertEqual(self.datamap.arcsec_resolution, 1)

    def testLatitudeToX(self):
        """
        Test Latitude to X function
        """
        input = [44, 44.1, 44.2, 44.25, 44.33333, 44.5, 44.6125, 44.75,
                 44.7777, 44.8125, 45.0]
        output = [3600, 3240, 2880, 2700, 2400, 1800, 1395, 900, 800, 675, 0]
        for index, value in enumerate(input):
            self.assertEqual(self.datamap.latitude_to_x(value), output[index])

    def testLongitudeToY(self):
        """
        Test Longitude to Y function
        """
        input = [-71, -71.1, -71.2, -71.25, -71.3333, -71.45, -71.5, -71.6125,
                 -71.75, -71.7777, -71.8125, -71.83122, -71.9, -72]
        output = [3600, 3240, 2880, 2700, 2400, 1980, 1800, 1395, 900, 800,
                  675, 608, 360, 0]
        for index, value in enumerate(input):
            self.assertEqual(self.datamap.longitude_to_y(value), output[index])

    def testXtoLatitude(self):
        """
        Test X to Latitude function
        """
        results = [x/100 for x in range(4500,4400, -1)]
        for index, value in enumerate([x for x in range(0, 3600, 36)]):
            self.assertEqual(self.datamap.x_to_latitude(value), results[index])


    def testYtoLongitude(self):
        """
        Test Y to Longitude function
        """
        results = [x / 100 for x in range(-7200, -7100, 1)]
        for index, value in enumerate([x for x in range(0, 3600, 36)]):
            self.assertEqual(self.datamap.y_to_longitude(value), results[index])

    def testSubset(self):
        subset = self.datamap.subset(100,100,200,200)
        self.assertEqual(subset.latitude, 44.916667)
        self.assertEqual(subset.longitude, -71.916667)
        self.assertEqual(subset.latitude_max, 44.9719447778)
        self.assertEqual(subset.longitude_max, -71.8613892222)
        self.assertEqual(subset.arcsec_resolution, 1)

if __name__ == '__main__':
    unittest.main()