"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""
import unittest

from numpy import array
from shapely.geometry import Polygon
from shapely.ops import unary_union
from pyprom.tests.getData import gettestzip
from pyprom.lib.loaders.gdal_loader import GDALLoader
from pyprom import DataMap

class DataMapTests(unittest.TestCase):
    """Test DataMaps."""

    def setUp(self):
        """Set Up Tests."""
        gettestzip()
        self.datafile = GDALLoader('/tmp/N44W072.hgt')
        self.datamap = self.datafile.to_datamap()

    def testDataMapGeneralDataMap(self):
        """Test defaults."""
        self.assertEqual(self.datamap.max_x, 3600)
        self.assertEqual(self.datamap.max_y, 3600)
        self.assertEqual(self.datamap.lower_left, (44.00013888888889,
                                                   -72.00013888888888))
        self.assertEqual(self.datamap.upper_left, (45.00013888888889,
                                                   -72.00013888888888))
        self.assertEqual(self.datamap.lower_right, (44.00013888888889,
                                                    -71.00013888888888))
        self.assertEqual(self.datamap.upper_right, (45.00013888888889,
                                                    -71.00013888888888))

    def testDataMapLatLongToXY(self):
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

    def testDataMap_XY_latlong_determinism(self):
        """
        Ensure converting from XY to LATLONG and back returns the same results.
        """
        for x in range(0, 3601, 17):
            for y in range(0, 3601, 17):
                lat, long = self.datamap.xy_to_latlon(x, y)
                _x, _y = self.datamap.latlong_to_xy(lat, long)
                self.assertEqual(_x, x)
                self.assertEqual(_y, y)

    def testDataMapSubset(self):
        """Test that datamap subsets return accurate subsets."""
        subset = self.datamap.subset(100, 100, 200, 199)
        self.assertEqual(subset.max_x, 199)
        self.assertEqual(subset.max_y, 198)
        self.assertEqual(subset.geotransform[5], -0.0002777777777777778)
        self.assertEqual(subset.geotransform[1], 0.0002777777777777778)
        self.assertEqual(subset.lower_left, (44.91708333333334,
                                             -71.97236111111111))
        self.assertEqual(subset.upper_left, (44.97236111111111,
                                             -71.97236111111111))
        self.assertEqual(subset.lower_right, (44.91708333333334,
                                              -71.9173611111111))
        self.assertEqual(subset.upper_right, (44.97236111111111,
                                              -71.9173611111111))

    def testDataMapGeom(self):
        """
        Ensure the expected Polygon is produced from a single point
        """
        polygon = self.datamap.point_geom(100, 100)
        expected_polygon = Polygon(((-71.97222222222223, 44.9725),
                                    (-71.97222222222223, 44.97222222222223),
                                    (-71.9725, 44.97222222222223),
                                    (-71.9725, 44.9725)))
        self.assertEqual(polygon, expected_polygon)

    def testDataMapGeomUnaryUnion(self):
        """
        Ensure a unary union on polygons derived from two neighboring points
        provides a proper rectangle and not some hot mess.
        """
        composite_polygon = unary_union((self.datamap.point_geom(100, 100),
                                         self.datamap.point_geom(100, 101)))
        expected_polygon = Polygon(((-71.9725, 44.97222222222223),
                                    (-71.9725, 44.9725),
                                    (-71.97222222222223, 44.9725),
                                    (-71.97194444444443, 44.9725), 
                                    (-71.97194444444443, 44.97222222222223), 
                                    (-71.97222222222223, 44.97222222222223),
                                    (-71.9725, 44.97222222222223)))
        # expected_polygon = Polygon(((-71.97222222222223, 44.97222222222223),
        #                             (-71.9725, 44.97222222222223),
        #                             (-71.9725, 44.9725),
        #                             (-71.97222222222223, 44.9725),
        #                             (-71.97194444444443, 44.9725),
        #                             (-71.97194444444443, 44.97222222222223)))
        self.assertEqual(composite_polygon, expected_polygon)

    def testDataMapDistance(self):
        """
        Ensure distance calculation produces expected results.
        """
        self.assertEqual(self.datamap.distance((0, 0), (1, 1)),
                                               0.00039283710065919305)
        self.assertEqual(self.datamap.distance((0, 0), (0, 1)),
                                               0.0002777777777777778)

    def testDataMapGet(self):
        """
        Ensure distance calculation produces expected results.
        """
        self.assertEqual(self.datamap.get(0, 0),
                         415.0)

    class DataMapSteepestNeighborTests(unittest.TestCase):
        """Test DataMap.steepestNeighbor()"""

    def setUp(self):
        """Set Up Tests."""
        gettestzip()
        self.datafile = GDALLoader('/tmp/N44W072.hgt')
        self.datamap = self.datafile.to_datamap()
        self.datamap = self.datamap.subset(0,0,3,3)

    def testSteepestNeighborAbove(self):
        """
        Ensure point (0, 1) is found to be the steepest.
        """
        numpy_map = array([[11, 15, 12],
                           [13, 10, 9],
                           [14, 11, 8]])
        self.datamap.numpy_array_override(numpy_map)
        self.assertEqual(self.datamap.steepestNeighbor(1, 1), (0, 1, 15.0))

    def testSteepestNeighborBelow(self):
        """
        Ensure point (2, 1) is found to be the steepest.
        """
        numpy_map = array([[11, 15, 12],
                           [13, 10, 9],
                           [14, 16, 8]])
        self.datamap.numpy_array_override(numpy_map)
        self.assertEqual(self.datamap.steepestNeighbor(1, 1), (2, 1, 16.0))

    def testSteepestNeighborAboveButDiagonalHigherJustNotHighEnough(self):
        """
        Ensure point (0, 1) is found to be the steepest even tho (0, 0)
        is higher. This is due to distance.
        """
        numpy_map = array([[17, 15, 12],
                           [13, 10, 9],
                           [14, 11, 8]])
        self.datamap.numpy_array_override(numpy_map)
        self.assertEqual(self.datamap.steepestNeighbor(1, 1), (0, 1, 15.0))

    def testSteepestNeighborDiagonalHigher(self):
        """
        Ensure point (0, 0) is found to be the steepest
        """
        numpy_map = array([[18, 15, 12],
                           [13, 10, 9],
                           [14, 11, 8]])
        self.datamap.numpy_array_override(numpy_map)
        self.assertEqual(self.datamap.steepestNeighbor(1, 1), (0, 0, 18.0))

    def testSteepestNeighborCorner(self):
        """
        Ensure we don't crash when scanning the corner.
        """
        numpy_map = array([[15, 16, 12],
                           [13, 10, 15],
                           [14, 11, 8]])
        self.datamap.numpy_array_override(numpy_map)
        self.assertEqual(self.datamap.steepestNeighbor(0, 0), (0, 1, 16.0))

if __name__ == '__main__':
    unittest.main()
