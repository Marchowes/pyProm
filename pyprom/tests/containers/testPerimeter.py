"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from collections import defaultdict

from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.lib.locations.gridpoint import GridPoint
from pyprom.lib.containers.perimeter import Perimeter


class PerimeterTests(unittest.TestCase):
    """Test Perimeter Container."""

    @classmethod
    def setUpClass(cls):
        """Set Up Tests."""
        gettestzip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = cls.datafile.datamap
        # contigous Perimeter
        cls.perimeterI = defaultdict(dict)
        cls.perimeterI[1][1] = cls.p11 = (1, 1, 553)
        cls.perimeterI[1][2] = cls.p12 = (1, 2, 554)
        cls.perimeterI[1][3] = cls.p13 = (1, 3, 554)
        cls.perimeterI[1][4] = cls.p14 = (1, 4, 553)
        cls.perimeterI[2][4] = cls.p24 = (2, 4, 555)
        cls.perimeterI[2][5] = cls.p25 = (2, 5, 554)
        cls.perimeterI[2][6] = cls.p26 = (2, 6, 553)
        cls.perimeter = Perimeter(pointIndex=cls.perimeterI,
                                  datamap=cls.datamap)

    def testPerimeterBothIndexAndList(self):
        """
        Ensure passing in a pointList and pointIndex raises exception
        """
        with self.assertRaises(Exception):
            Perimeter(pointIndex=self.perimeterI, pointList=[(1, 1)], datamap=self.datamap)

    def testPerimeterListBuildsIndex(self):
        """
        Ensure passing in a pointList produces a pointIndex
        """
        perm = Perimeter(pointList=self.perimeter.points, datamap=self.datamap)
        self.assertDictEqual(perm.pointIndex['1'], self.perimeter.pointIndex['1'])
        self.assertDictEqual(perm.pointIndex['2'], self.perimeter.pointIndex['2'])

    def testPerimeterIndexBuildsList(self):
        """
        Ensure passing in a pointList produces a pointIndex
        """
        perm = Perimeter(pointIndex=self.perimeter.pointIndex, datamap=self.datamap)
        self.assertEqual(perm.points, self.perimeter.points)

    def testPerimeterIterNeighborDiagonal(self):
        """
        Ensure that iterDiagonal returns the expected results.
        Iter diagonal returns all neighbors of a GridPoint contained
        in the Perimeter Container
        """
        count = 0
        # Should have two results.
        for point in self.perimeter.iterNeighborDiagonal(self.p12):
            count += 1
            self.assertIn(point, [self.p11,
                                  self.p13])
        self.assertEqual(count, 2)
        count = 0
        # Should have just the one result.
        for point in self.perimeter.iterNeighborDiagonal(self.p11):
            count += 1
            self.assertIn(point, [self.p12])
        self.assertEqual(count, 1)
        count = 0
        # Should have three results.
        for point in self.perimeter.iterNeighborDiagonal(self.p24):
            count += 1
            self.assertIn(point, [self.p14,
                                  self.p25,
                                  self.p13])
        self.assertEqual(count, 3)
        count = 0
        # Should have three results.
        for point in self.perimeter.iterNeighborDiagonal(self.p13):
            count += 1
            self.assertIn(point, [self.p12,
                                  self.p14,
                                  self.p24])
        self.assertEqual(count, 3)

    def testPerimeterIterNeighborOrthogonal(self):
        """
        Ensure that iterOrthogonal returns the expected results.
        Iter diagonal returns all orthogonal (right angle) neighbors
        of an GridPoint contained in the Perimeter container
        """
        count = 0
        # Should have two results.
        for point in self.perimeter.iterNeighborOrthogonal(self.p12):
            count += 1
            self.assertIn(point, [self.p11,
                                  self.p13])
        self.assertEqual(count, 2)
        count = 0
        # Should have just the one result.
        for point in self.perimeter.iterNeighborOrthogonal(self.p11):
            count += 1
            self.assertIn(point, [self.p12])
        self.assertEqual(count, 1)
        count = 0
        # Should have two results.
        for point in self.perimeter.iterNeighborOrthogonal(self.p24):
            count += 1
            self.assertIn(point, [self.p14,
                                  self.p25])
        self.assertEqual(count, 2)
        count = 0
        # Should have two results.
        for point in self.perimeter.iterNeighborOrthogonal(self.p13):
            count += 1
            self.assertIn(point, [self.p12,
                                  self.p14])
        self.assertEqual(count, 2)

    def testPerimeterFindHighEdges(self):
        """
        Test findHighEdges on a discontigous GridPoint set
        """
        perimeterId = defaultdict(dict)
        perimeterId[1][1] = self.p11
        perimeterId[1][2] = self.p12
        perimeterId[1][4] = self.p14
        perimeterId[2][4] = self.p24
        perimeterId[2][5] = self.p25
        perimeterId[2][6] = self.p26
        perimeterDiscontigous = \
            Perimeter(pointIndex=perimeterId,
                      datamap=self.datamap)
        highEdges = perimeterDiscontigous.findHighEdges(552)
        self.assertEqual(2, len(highEdges))
        self.assertEqual(highEdges[0].points, [GridPoint.from_tuple(self.p11), GridPoint.from_tuple(self.p12)])
        self.assertEqual(highEdges[1].points, [GridPoint.from_tuple(self.p14), GridPoint.from_tuple(self.p24),
                                               GridPoint.from_tuple(self.p25), GridPoint.from_tuple(self.p26)])

    def testPerimeterFindHighEdgesOrthogonallyDiscontigous(self):
        """
        Test findHighEdges on a orthogonally discontigous perimeter set.
        two subsets connected diagonally thus creating one set.
        """
        perimeterId = defaultdict(dict)
        perimeterId[1][1] = self.p11
        perimeterId[1][2] = self.p12
        perimeterId[1][3] = self.p13
        perimeterId[2][4] = self.p24
        perimeterId[2][5] = self.p25
        perimeterId[2][6] = self.p26
        perimeterOrthogonallyDiscontigous = \
            Perimeter(pointIndex=perimeterId,
                      datamap=self.datamap)
        highEdges = perimeterOrthogonallyDiscontigous.findHighEdges(552)
        self.assertEqual(1, len(highEdges))
        self.assertEqual(6, len(highEdges[0].points))

    def testPerimeterfindHighPerimeter(self):
        """
        Ensure findHighPerimeter produces expected results
        """
        higher554 = self.perimeter.findHighPerimeter(554)
        self.assertEqual(1, len(higher554.points))

        higher553 = self.perimeter.findHighPerimeter(553)
        self.assertEqual(4, len(higher553.points))

        higher552 = self.perimeter.findHighPerimeter(552)
        self.assertEqual(7, len(higher552.points))

    def testPerimeterIterator(self):
        """
        Ensure __iter__ returns expected results.
        """
        self.assertEqual(len([x for x in self.perimeter]), 7)

    def testPerimeterLen(self):
        """
        Ensure __len__ returns expected results.
        """
        self.assertEqual(len(self.perimeter), 7)

    def testPerimeterSetItem(self):
        """
        Ensure __setattr__ works as expected.
        """
        perimeter = \
            Perimeter(pointList=[self.p11],
                      datamap=self.datamap)
        self.assertEqual(len(perimeter), 1)
        perimeter[0] = self.p12
        self.assertEqual(perimeter[0], self.p12)

    def testPerimeterSetItemNeg(self):
        """
        Ensure __setattr__ Disallows Non Gridpoints to be set.
        """
        perimeter = \
            Perimeter(pointList=[self.p11],
                      datamap=self.datamap)
        self.assertEqual(len(perimeter), 1)
        with self.assertRaises(TypeError):
            perimeter[0] = "wtf"

    def testPerimeterGetItem(self):
        """
        Ensure __getattr__ works as expected.
        """
        perimeter = \
            Perimeter(pointList=[self.p11],
                      datamap=self.datamap)
        self.assertEqual(len(perimeter), 1)
        self.assertEqual(perimeter[0], self.p11)

    def testPerimeterBadAppend(self):
        """
        Ensure adding string to Perimeter fails.
        """
        perimeter = \
            Perimeter(pointList=[self.p11],
                      datamap=self.datamap)
        with self.assertRaises(TypeError):
            perimeter.append("stuff")

    def testPerimeterGoodAppend(self):
        """
        Ensure adding GridPoint to SummitsContainer succeeds.
        """
        perimeter = \
            Perimeter(pointList=[self.p11],
                      datamap=self.datamap)
        perimeter.append(self.p12)
        self.assertEqual(len(perimeter), 2)

    def testPerimeterEq(self):
        """
        Ensure __eq__ works as expected.
        """
        perimeter = \
            Perimeter(pointList=[self.p11],
                      datamap=self.datamap)
        perimeter2 = \
            Perimeter(pointList=[self.p11],
                      datamap=self.datamap)
        perimeter3 = \
            Perimeter(pointList=[self.p12],
                      datamap=self.datamap)

        self.assertEqual(perimeter, perimeter2)
        test = perimeter2 == perimeter3
        self.assertFalse(test)

    def testPerimeterNe(self):
        """
        Ensure __ne__ works as expected.
        """
        perimeter = \
            Perimeter(pointList=[self.p11],
                      datamap=self.datamap)
        perimeter2 = \
            Perimeter(pointList=[self.p11],
                      datamap=self.datamap)
        perimeter3 = \
            Perimeter(pointList=[self.p12],
                      datamap=self.datamap)

        self.assertNotEqual(perimeter, perimeter3)
        test = perimeter != perimeter2
        self.assertFalse(test)

    def testPerimeterRepr(self):
        """
        Ensure repr returns expected results.
        """
        self.assertEqual(self.perimeter.__repr__(),
                         "<Perimeter> 7 Objects")

    def testPerimeterFromDict(self):
        """
        Ensure From Dict works as expected.
        """
        self.perimeter.mapEdge = True
        self.perimeter.mapEdgePoints = [GridPoint.from_tuple(self.p11)]

        perimeterDict = self.perimeter.to_dict()

        newPerimeter = Perimeter.from_dict(perimeterDict,
                                           datamap=self.datamap)
        self.assertEqual(newPerimeter.points, self.perimeter.points)
        self.assertEqual(newPerimeter.mapEdge, self.perimeter.mapEdge)
        self.assertEqual(newPerimeter.mapEdgePoints,
                         self.perimeter.mapEdgePoints)
        self.assertEqual(newPerimeter.pointIndex, self.perimeter.pointIndex)
