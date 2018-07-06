"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import getTestZip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData
from pyprom.lib.containers.summits import SummitsContainer
from pyprom.lib.locations.summit import Summit

class SpotElevationContainerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set Up Tests."""
        getTestZip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = cls.datafile.datamap
        cls.someslice = datamap.subset(65, 55, 100, 100)
        cls.somewhere = AnalyzeData(cls.someslice)
        cls.summits, cls.saddles = cls.somewhere.run()
        cls.oneKMradius =  cls.summits.radius(44.954583, -71.957916, 1000)


    def testLowest(self):
        """ Make sure the lowest summit is what we expect."""
        self.assertEqual(self.summits.lowest[0].elevation, 501.0)
        self.assertEqual(len(self.summits.lowest), 1)

        # add another Summit with the same elevation as the lowest.
        self.summits.add(Summit(1, 1, self.summits.lowest[0].elevation))
        self.assertEqual(len(self.summits.lowest), 2)


    def testHighest(self):
        """ Make sure the highest summit is what we expect."""
        self.assertEqual(self.summits.highest[0].elevation, 585.0)
        self.assertEqual(len(self.summits.highest),1)

        # add another Summit with the same elevation as the highest.
        self.summits.add(Summit(1, 1, self.summits.highest[0].elevation))
        self.assertEqual(len(self.summits.highest), 2)

    def testRadiusMeters(self):
        """ Make sure radius calculation results are the same for meters. """
        meters = self.summits.radius(44.954583, -71.957916, 1000)
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1000, "m")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1000, "meter")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1000, "meters")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1000, "M")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1000, "Meter")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1000, "Meters")
        self.assertEqual(meters.summits, self.oneKMradius.summits)

    def testRadiusKilometers(self):
        """
        Make sure radius calculation results are the same for kilometers.
        """
        meters = self.summits.radius(44.954583, -71.957916, 1, "km")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1, "kilometer")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1, "kilometers")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1, "KM")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1, "Km")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1, "KiloMeter")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 1, "KiloMeters")
        self.assertEqual(meters.summits, self.oneKMradius.summits)

    def testRadiusFeet(self):
        """
        Make sure radius calculation results are the same for feet.
        """
        meters = self.summits.radius(44.954583, -71.957916, 3280.84, "feet")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 3280.84, "foot")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 3280.84, "ft")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 3280.84, "Feet")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 3280.84, "Foot")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 3280.84, "Ft")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 3280.84, "FT")
        self.assertEqual(meters.summits, self.oneKMradius.summits)

    def testRadiusMiles(self):
        """
        Make sure radius calculation results are the same for feet.
        """
        meters = self.summits.radius(44.954583, -71.957916, 0.621371, "mile")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 0.621371, "miles")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 0.621371, "mi")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 0.621371, "Mile")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 0.621371, "Miles")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 0.621371, "Mi")
        self.assertEqual(meters.summits, self.oneKMradius.summits)
        meters = self.summits.radius(44.954583, -71.957916, 0.621371, "MI")
        self.assertEqual(meters.summits, self.oneKMradius.summits)

    def testRectangle(self):
        """
        Ensure taking out a rectangle subsection yields expected results.
        """
        rectangle = self.summits.rectangle(44.954583,-71.957916, 44.98125, -71.9609)
        self.assertEqual(len(rectangle.points), 6)
        # flip lat/long around, should still be able to figure out rectangle.
        rectangle = self.summits.rectangle(44.98125, -71.9609, 44.954583,-71.957916, )
        self.assertEqual(len(rectangle.points), 6)

    def testElevationRange(self):
        """
        Ensure elevation range yields expected results.
        """
        elevationRange = self.summits.elevationRange(1640, 1740)
        self.assertEqual(len(elevationRange.summits), 16)
        elevationRange = self.summits.elevationRange(1640, 1840)
        self.assertEqual(len(elevationRange.summits), 44)


    def testElevationRangeMetric(self):
        """
        Ensure metric elevation range yields expected results.
        """
        elevationRange = self.summits.elevationRangeMetric(500, 550)
        self.assertEqual(len(elevationRange.summits), 39)
        elevationRange = self.summits.elevationRangeMetric(500, 580)
        self.assertEqual(len(elevationRange.summits), 53)

    def testJSON(self):
        """
        Ensure basic json encoding works.
        """
        jsonString = self.summits.to_json()

        summits = SummitsContainer([])
        summits.from_json(jsonString, self.someslice)
        self.assertEqual(self.summits.summits, summits.summits)
