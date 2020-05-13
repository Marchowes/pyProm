"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData
from pyprom.lib.containers.spot_elevation import SpotElevationContainer
from pyprom.lib.locations.summit import Summit
from pyprom.lib.locations.saddle import Saddle


class SpotElevationContainerTests(unittest.TestCase):
    """Test SpotElevationContainer"""

    @classmethod
    def setUpClass(cls):
        """Set Up Tests."""
        gettestzip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = cls.datafile.datamap
        cls.someslice = datamap.subset(65, 55, 100, 100)
        cls.somewhere = AnalyzeData(cls.someslice)
        cls.summits, cls.saddles, cls.runoffs = cls.somewhere.run()
        cls.oneKMradius = cls.summits.radius(44.954583, -71.957916, 1000)

    def testSpotElevationContainerLowest(self):
        """
        Make sure the lowest summit is what we expect.
        """
        self.assertEqual(self.summits.lowest[0].elevation, 501.0)
        self.assertEqual(len(self.summits.lowest), 1)

        # add another Summit with the same elevation as the lowest.
        self.summits.append(Summit(1, 1, self.summits.lowest[0].elevation))
        self.assertEqual(len(self.summits.lowest), 2)

    def testSpotElevationContainerHighest(self):
        """
        Make sure the highest summit is what we expect.
        """
        self.assertEqual(self.summits.highest[0].elevation, 585.0)
        self.assertEqual(len(self.summits.highest), 1)

        # add another Summit with the same elevation as the highest.
        self.summits.append(Summit(1, 1, self.summits.highest[0].elevation))
        self.assertEqual(len(self.summits.highest), 2)

    def testSpotElevationContainerRadiusMeters(self):
        """
        Make sure radius calculation results are the same for meters.
        """
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

    def testSpotElevationContainerRadiusKilometers(self):
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

    def testSpotElevationContainerRadiusFeet(self):
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

    def testSpotElevationContainerRadiusMiles(self):
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

    def testSpotElevationContainerRectangle(self):
        """
        Ensure taking out a rectangle subsection yields expected results.
        """
        rectangle = self.summits.rectangle(44.954583, -71.957916,
                                           44.98125, -71.9609)
        self.assertEqual(len(rectangle), 6)
        # flip lat/long around, should still be able to figure out rectangle.
        rectangle = self.summits.rectangle(44.98125, -71.9609,
                                           44.954583, -71.957916)
        self.assertEqual(len(rectangle), 6)

    def testSpotElevationContainerElevationRange(self):
        """
        Ensure elevation range yields expected results.
        """
        elevationRange = self.summits.elevationRange(1640, 1740)
        self.assertEqual(len(elevationRange.summits), 16)
        elevationRange = self.summits.elevationRange(1640, 1840)
        self.assertEqual(len(elevationRange.summits), 44)

    def testSpotElevationContainerElevationRangeMetric(self):
        """
        Ensure metric elevation range yields expected results.
        """
        elevationRange = self.summits.elevationRangeMetric(500, 550)
        self.assertEqual(len(elevationRange.summits), 39)
        elevationRange = self.summits.elevationRangeMetric(500, 580)
        self.assertEqual(len(elevationRange.summits), 53)

    def testSpotElevationContainerLen(self):
        """
        Ensure __len__ produces expected results.
        """
        self.assertEqual(len(self.summits), 55)

    def testSpotElevationContainerAppend(self):
        """
        Ensure appending Different child SpotElevations
        to SpotElevationContainer succeeds.
        """
        container = SpotElevationContainer([])
        container.append(Summit(1, 2, 3))
        container.append(Saddle(1, 2, 3))

    def testSpotElevationContainerExtend(self):
        """
        Ensure extending Different child SpotElevations
        to SpotElevationContainer succeeds.
        """
        container = SpotElevationContainer([])
        container.extend([Summit(1, 2, 3), Saddle(1, 2, 3)])

    def testSpotElevationContainerExtendNegative(self):
        """
        Ensure extending invalid child SpotElevations
        to SpotElevationContainer fails.
        """
        container = SpotElevationContainer([])
        with self.assertRaises(TypeError):
            container.extend(['what?'])

    def testSpotElevationContainerSetItem(self):
        """
        Ensure setting item index succeeds.
        """
        sum = Summit(1, 2, 3)
        sad = Saddle(1, 2, 3)
        sum2 = Summit(2, 3, 4)
        container = SpotElevationContainer([sum, sad])
        container[1] = sum2
        self.assertEqual(container[1], sum2)

    def testSpotElevationContainerSetItemNegative(self):
        """
        Ensure setting item index succeeds.
        """
        sum = Summit(1, 2, 3)
        sad = Saddle(1, 2, 3)
        container = SpotElevationContainer([sum, sad])
        with self.assertRaises(TypeError):
            container[1] = "wtf"

    def testSpotElevationContainerGetItem(self):
        """
        Ensure setting item index succeeds.
        """
        sum = Summit(1, 2, 3)
        sad = Saddle(1, 2, 3)

        container = SpotElevationContainer([sum, sad])
        self.assertEqual(container[0], sum)
        self.assertEqual(container[1], sad)

    def testSpotElevationContainerEquals(self):
        """
        Ensure __eq__ produces expected results.
        """
        self.assertEqual(SpotElevationContainer([Summit(1, 2, 3)]),
                         SpotElevationContainer([Summit(1, 2, 3)]))

    def testSpotElevationContainerNotEquals(self):
        """
        Ensure __ne__ produces expected results.
        """
        self.assertNotEqual(SpotElevationContainer([Summit(1, 2, 3)]),
                            SpotElevationContainer([Summit(2, 2, 3)]))

    def testSpotElevationContainerIndex(self):
        """
        Ensure index() returns the expected values.
        """
        se0 = Saddle(1, 2, 3)
        se1 = Summit(4, 5, 6)
        fake = Summit(7, 8, 9)

        container = SpotElevationContainer([se0, se1])
        self.assertEqual(container.index(se0), 0)
        self.assertEqual(container.index(se1), 1)
        self.assertEqual(container.index(fake), None)

    def testSpotElevationContainerRepr(self):
        """
        Ensure __repr__ produces expected results.
        """
        container = SpotElevationContainer([])
        self.assertEqual(container.__repr__(),
                         "<SpotElevationContainer> 0 Objects")

    def testSpotElevationContainerByIDinit(self):
        """
        Ensure by_id works on __init__ obj
        """
        se0 = Saddle(1, 2, 3)
        container = SpotElevationContainer([se0])
        self.assertEqual(container.by_id(se0.id), se0)

    def testSpotElevationContainerByIDappend(self):
        """
        Ensure by_id works on append obj
        """
        se0 = Saddle(1, 2, 3)
        container = SpotElevationContainer([])
        container.append(se0)
        self.assertEqual(container.by_id(se0.id), se0)

    def testSpotElevationContainerByIDextend(self):
        """
        Ensure by_id works on extended obj
        """
        se0 = Saddle(1, 2, 3)
        container = SpotElevationContainer([])
        container.extend([se0])
        self.assertEqual(container.by_id(se0.id), se0)