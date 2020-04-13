"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData
from pyprom.lib.locations.base_coordinate import BaseCoordinate
from pyprom.lib.locations.base_gridpoint import BaseGridPoint
from pyprom.lib.locations.gridpoint import GridPoint
from pyprom.lib.containers.multipoint import MultiPoint
from pyprom.lib.locations.spot_elevation import SpotElevation


class MultipointTests(unittest.TestCase):
    """Test Multipoint Container."""

    @classmethod
    def setUpClass(cls):
        """Set Up Tests."""
        gettestzip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = cls.datafile.datamap
        cls.someslice = cls.datamap.subset(1000, 1000, 100, 100)
        cls.somewhere = AnalyzeData(cls.someslice)
        cls.summits, cls.saddles, cls.runoffs = cls.somewhere.run()
        cls.saddle = cls.saddles.multipoints[3]
        cls.summitWithoutMultipointEdge = cls.summits.summits[4]
        cls.bgp11 = BaseGridPoint(1, 1)
        cls.bgp22 = BaseGridPoint(2, 2)
        cls.bgp33 = BaseGridPoint(3, 3)

    def testMultipointPointsLatLong(self):
        """
        Test multipoint container ability to convert GridPoints
        to BaseCoordinates.
        """
        multipoint = self.summitWithoutMultipointEdge.multiPoint
        bc0 = BaseCoordinate(44.70986111111111, -71.71263888888889)
        bc1 = BaseCoordinate(44.70986111111111, -71.71236111111111)
        self.assertIn(bc0, multipoint.pointsLatLong)
        self.assertIn(bc1, multipoint.pointsLatLong)

    def testMultipointPerimeterNoEdge(self):
        """
        Test multipoint container perimeter count is as expected.
        """
        multipoint = self.saddle.multiPoint
        self.assertEqual(len(multipoint.perimeter), 8)

    def testMultipointRepr(self):
        """
        Ensure __repr__ returns expected results.
        """
        multipoint = self.saddle.multiPoint
        self.assertEqual(multipoint.__repr__(),
                         "<Multipoint> elevation(m): 551.0, points 4")

    def testMultipointIterator(self):
        """
        Ensure __iter__ returns expected results.
        """
        self.assertEqual(len([x for x in
                              self.summitWithoutMultipointEdge.multiPoint]), 2)

    def testMultipointLen(self):
        """
        Ensure __len__ returns expected results.
        """
        self.assertEqual(len(self.summitWithoutMultipointEdge.multiPoint), 2)

    def testMultipointSetItem(self):
        """
        Ensure __setattr__ works as expected.
        """
        multipoint = MultiPoint([], 100, self.datamap)
        multipoint.append(self.bgp11)
        self.assertEqual(len(multipoint), 1)
        multipoint[0] = self.bgp22
        self.assertEqual(multipoint[0], self.bgp22)

    def testMultipointSetItemNeg(self):
        """
        Ensure __setattr__ Disallows Non BaseGridpoints to be set.
        """
        multipoint = MultiPoint([], 100, self.datamap)
        multipoint.append(self.bgp11)
        self.assertEqual(len(multipoint), 1)
        with self.assertRaises(TypeError):
            multipoint[0] = "wtf"

    def testMultipointGetItem(self):
        """
        Ensure __getattr__ works as expected.
        """
        multipoint = MultiPoint([], 100, self.datamap)
        multipoint.append(self.bgp11)
        self.assertEqual(len(multipoint), 1)
        self.assertEqual(multipoint[0], self.bgp11)

    def testMultipointBadAppend(self):
        """
        Ensure adding string to Multipoint fails.
        """
        multipoint = MultiPoint([], 100, self.datamap)
        multipoint.append(self.bgp11)
        with self.assertRaises(TypeError):
            multipoint.append("stuff")

    def testMultipointGoodAppend(self):
        """
        Ensure adding GridPoint to SummitsContainer succeeds.
        """
        multipoint = MultiPoint([], 100, self.datamap)
        multipoint.append(self.bgp11)
        multipoint.append(self.bgp22)
        self.assertEqual(len(multipoint), 2)

    def testMultipointEq(self):
        """
        Ensure __eq__ works as expected.
        """
        multipoint = MultiPoint([], 100, self.datamap)
        multipoint.append(self.bgp11)
        multipoint2 = MultiPoint([], 100, self.datamap)
        multipoint2.append(self.bgp11)
        multipoint3 = MultiPoint([], 100, self.datamap)
        multipoint3.append(self.bgp22)

        self.assertEqual(multipoint, multipoint2)
        test = multipoint2 == multipoint3
        self.assertFalse(test)

    def testMultipointNe(self):
        """
        Ensure __ne__ works as expected.
        """
        multipoint = MultiPoint([], 100, self.datamap)
        multipoint.append(self.bgp11)
        multipoint2 = MultiPoint([], 100, self.datamap)
        multipoint2.append(self.bgp11)
        multipoint3 = MultiPoint([], 100, self.datamap)
        multipoint3.append(self.bgp22)

        self.assertNotEqual(multipoint, multipoint3)
        test = multipoint != multipoint2
        self.assertFalse(test)

    def testMultipointEdgePointsGetterEdgeWithMulti(self):
        """
        Ensure edge effect Saddle-like multipoint objects
        generate an edgePoint list.
        """
        edgePoint = (99, 49, 552.0)
        edgeMulti = self.saddles[20]
        self.assertTrue(edgeMulti.edgeEffect)
        self.assertEqual(edgeMulti.edgePoints, [edgePoint])

    def testMultipointEdgePointsGetterEdgeSinglePoint(self):
        """
        Ensure edge effect Saddle-like objects generate an edgePoint list.
        """
        edgePoint = (37, 99, 605.0)
        edgeMulti = self.runoffs[9]
        self.assertTrue(edgeMulti.edgeEffect)
        self.assertEqual(edgeMulti.edgePoints, [edgePoint])

    def testMultipointEdgePointsGetterWithMulti(self):
        """
        Ensure non edge effect Saddle-like multipoint objects
        generate an edgePoint list.
        """
        edgeMulti = self.saddles[19]
        self.assertFalse(edgeMulti.edgeEffect)
        self.assertEqual(edgeMulti.edgePoints, [])

    def testMultipointEdgePointsGetterSinglePoint(self):
        """
        Ensure non edge effect Saddle-like objects generate an edgePoint list.
        """
        edgeMulti = self.saddles[6]
        self.assertFalse(edgeMulti.edgeEffect)
        self.assertEqual(edgeMulti.edgePoints, [])

    def testMultiPointFromDict(self):
        """
        Ensure From Dict works as expected.
        """
        mp = self.saddles[3].multiPoint
        mp_dict = mp.to_dict()
        newMp = MultiPoint.from_dict(mp_dict, mp.datamap)
        self.assertEqual(newMp, mp)
        self.assertEqual(newMp.points, mp.points)
        self.assertEqual(newMp.datamap, mp.datamap)
        self.assertEqual(newMp.elevation, mp.elevation)
        self.assertEqual(newMp.perimeter, mp.perimeter)

    def testMultiPointClosest(self):
        """
        Ensure closestPoint() returns the expected results
        asSpotElevation = False (Default)
        """
        points = []
        for x in range(100, 110):
            for y in range(200, 210):
                points.append((x, y))
        mp = MultiPoint(points, 100, self.datamap)

        # Inside the MP
        expectedResult = GridPoint(105, 205, 100)
        result = mp.closestPoint(expectedResult)
        self.assertEqual(expectedResult, result)

        # To the top left corner
        expectedResult = GridPoint(100, 200, 100)
        point = GridPoint(1, 1, 1)
        result = mp.closestPoint(point)
        self.assertEqual(expectedResult, result)

        # To the left
        expectedResult = GridPoint(100, 205, 100)
        point = GridPoint(1, 205, 1)
        result = mp.closestPoint(point)
        self.assertEqual(expectedResult, result)

        # To the bottom left corner
        expectedResult = GridPoint(100, 209, 100)
        point = GridPoint(1, 500, 1)
        result = mp.closestPoint(point)
        self.assertEqual(expectedResult, result)

        # To the bottom
        expectedResult = GridPoint(105, 209, 100)
        point = GridPoint(105, 500, 1)
        result = mp.closestPoint(point)
        self.assertEqual(expectedResult, result)

        # To the bottom right corner
        expectedResult = GridPoint(109, 209, 100)
        point = GridPoint(200, 500, 1)
        result = mp.closestPoint(point)
        self.assertEqual(expectedResult, result)

        # To the right
        expectedResult = GridPoint(109, 205, 100)
        point = GridPoint(200, 205, 1)
        result = mp.closestPoint(point)
        self.assertEqual(expectedResult, result)

        # To the top right
        expectedResult = GridPoint(109, 200, 100)
        point = GridPoint(200, 0, 1)
        result = mp.closestPoint(point)
        self.assertEqual(expectedResult, result)

        # To the top
        expectedResult = GridPoint(105, 200, 100)
        point = GridPoint(105, 0, 1)
        result = mp.closestPoint(point)
        self.assertEqual(expectedResult, result)

    def testMultiPointClosestSE(self):
        """
        Ensure closestPoint() returns the expected results
        asSpotElevation = True
        """
        points = []
        for x in range(100, 110):
            for y in range(200, 210):
                points.append((x, y))
        mp = MultiPoint(points, 100, self.datamap)

        # Inside the MP
        point = GridPoint(105, 205, 100)
        expectedResult = GridPoint(105, 205, 100)
        expectedResult = expectedResult.toSpotElevation(mp.datamap)
        result = mp.closestPoint(point, asSpotElevation=True)
        self.assertEqual(expectedResult, result)

        # To the top left corner
        expectedResult = GridPoint(100, 200, 100)
        expectedResult = expectedResult.toSpotElevation(mp.datamap)
        point = GridPoint(1, 1, 1)
        result = mp.closestPoint(point, asSpotElevation=True)
        self.assertEqual(expectedResult, result)




    def testMultiPointClosestHighPerimeterPoint(self):
        """
        Ensure closestHighPerimeterPoint() returns the expected results
        asSpotElevation = False
        """
        mp = self.saddles.multipoints[0].multiPoint

        closest = mp.closestHighPerimeterPoint((0, 0, 0))
        self.assertEqual(closest, (4, 55, 559))

        closest = mp.closestHighPerimeterPoint((0, 55, 0))
        self.assertEqual(closest, (0, 56, 559))

        closest = mp.closestHighPerimeterPoint((10, 0, 0))
        self.assertEqual(closest, (4, 55, 559))

        closest = mp.closestHighPerimeterPoint((10, 60, 0))
        self.assertEqual(closest, (5, 58, 559))

    def testMultiPointClosestHighPerimeterPointSpotElevation(self):
        """
        Ensure closestHighPerimeterPoint() returns the expected results
        asSpotElevation = True
        """
        mp = self.saddles.multipoints[0].multiPoint

        closest = mp.closestHighPerimeterPoint((0, 0, 0),
                                               asSpotElevation=True)
        self.assertEqual(closest, (SpotElevation(44.721250000000005, -71.70708333333333, 559)))

        closest = mp.closestHighPerimeterPoint((0, 55, 0),
                                               asSpotElevation=True)
        self.assertEqual(closest, (SpotElevation(44.72236111111111, -71.70680555555556, 559)))

        closest = mp.closestHighPerimeterPoint((10, 0, 0),
                                               asSpotElevation=True)
        self.assertEqual(closest, (SpotElevation(44.721250000000005, -71.70708333333333, 559)))

        closest = mp.closestHighPerimeterPoint((10, 60, 0),
                                               asSpotElevation=True)
        self.assertEqual(closest, (SpotElevation(44.72097222222222, -71.70625, 559)))
