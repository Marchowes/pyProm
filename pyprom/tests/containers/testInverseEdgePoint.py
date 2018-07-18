"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from collections import defaultdict

from pyprom.tests.getData import getTestZip
from pyprom.dataload import GDALLoader
from pyprom.lib.locations.inverse_edgepoint import InverseEdgePoint
from pyprom.lib.containers.inverse_edgepoint import InverseEdgePointContainer

class InverseEdgePointContainerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set Up Tests."""
        getTestZip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = cls.datafile.datamap
        cls.someslice = cls.datamap.subset(1000, 1000, 10, 10)
        # contigous InverseEdgePointContainer
        cls.iepi = defaultdict(dict)
        cls.iepi[1][1] = cls.p11 = InverseEdgePoint(1, 1, 553)
        cls.iepi[1][2] = cls.p12 = InverseEdgePoint(1, 2, 554)
        cls.iepi[1][3] = cls.p13 = InverseEdgePoint(1, 3, 554)
        cls.iepi[1][4] = cls.p14 = InverseEdgePoint(1, 4, 553)
        cls.iepi[2][4] = cls.p24 = InverseEdgePoint(2, 4, 555)
        cls.iepi[2][5] = cls.p25 = InverseEdgePoint(2, 5, 554)
        cls.iepi[2][6] = cls.p26 = InverseEdgePoint(2, 6, 553)
        cls.iep = InverseEdgePointContainer(inverseEdgePointIndex=cls.iepi,
                                            datamap=cls.datamap)

    def testPerimeterIterNeighborDiagonal(self):
        """
        Ensure that iterDiagonal returns the expected results.
        Iter diagonal returns all neighbors of an inverseEdgePoint contained
        in the InverseEdgePoint container
        """
        count = 0
        # Should have two results.
        for point in self.iep.iterNeighborDiagonal(self.p12):
            count+=1
            self.assertIn(point, [self.p11,
                                  self.p13])
        self.assertEqual(count, 2)
        count = 0
        # Should have just the one result.
        for point in self.iep.iterNeighborDiagonal(self.p11):
            count += 1
            self.assertIn(point, [self.p12])
        self.assertEqual(count, 1)
        count = 0
        # Should have three results.
        for point in self.iep.iterNeighborDiagonal(self.p24):
            count += 1
            self.assertIn(point, [self.p14,
                                  self.p25,
                                  self.p13])
        self.assertEqual(count, 3)
        count = 0
        # Should have three results.
        for point in self.iep.iterNeighborDiagonal(self.p13):
            count += 1
            self.assertIn(point, [self.p12,
                                  self.p14,
                                  self.p24])
        self.assertEqual(count, 3)

    def testPerimeterIterNeighborOrthogonal(self):
        """
        Ensure that iterOrthogonal returns the expected results.
        Iter diagonal returns all orthogonal (right angle) neighbors
        of an inverseEdgePoint contained in the InverseEdgePoint container
        """
        count = 0
        # Should have two results.
        for point in self.iep.iterNeighborOrthogonal(self.p12):
            count+=1
            self.assertIn(point, [self.p11,
                                  self.p13])
        self.assertEqual(count, 2)
        count = 0
        # Should have just the one result.
        for point in self.iep.iterNeighborOrthogonal(self.p11):
            count += 1
            self.assertIn(point, [self.p12])
        self.assertEqual(count, 1)
        count = 0
        # Should have two results.
        for point in self.iep.iterNeighborOrthogonal(self.p24):
            count += 1
            self.assertIn(point, [self.p14,
                                  self.p25])
        self.assertEqual(count, 2)
        count = 0
        # Should have two results.
        for point in self.iep.iterNeighborOrthogonal(self.p13):
            count += 1
            self.assertIn(point, [self.p12,
                                  self.p14])
        self.assertEqual(count, 2)

    def testPerimeterFindHighEdges(self):
        """
        test findHighEdges on a discontigous iep set
        """
        iepid = defaultdict(dict)
        iepid[1][1] = self.p11
        iepid[1][2] = self.p12
        iepid[1][4] = self.p14
        iepid[2][4] = self.p24
        iepid[2][5] = self.p25
        iepid[2][6] = self.p26
        iepDiscontigous =\
            InverseEdgePointContainer(inverseEdgePointIndex=iepid,
                                      datamap=self.datamap)
        highEdges = iepDiscontigous.findHighEdges(552)
        self.assertEqual(2,len(highEdges))
        self.assertEqual(highEdges[0].points, [self.p11,self.p12])
        self.assertEqual(highEdges[1].points, [self.p14, self.p24,
                                               self.p25, self.p26])

    def testPerimeterFindHighEdgesOrthogonallyDiscontigous(self):
        """
        Test findHighEdges on a orthogonally discontigous iep set.
        two subsets connected diagonally thus creating one set.
        """
        iepid = defaultdict(dict)
        iepid[1][1] = self.p11
        iepid[1][2] = self.p12
        iepid[1][3] = self.p13
        iepid[2][4] = self.p24
        iepid[2][5] = self.p25
        iepid[2][6] = self.p26
        iepOrthogonallyDiscontigous =\
            InverseEdgePointContainer(inverseEdgePointIndex=iepid,
                                      datamap=self.datamap)
        highEdges = iepOrthogonallyDiscontigous.findHighEdges(552)
        self.assertEqual(1,len(highEdges))
        self.assertEqual(6,len(highEdges[0].points))

    def testPerimeterFindHighInverseEdgePoints(self):
        """
        Ensure findHighInverseEdgePoints produces expected results
        """
        higher554 = self.iep.findHighInverseEdgePoints(554)
        self.assertEqual(1, len(higher554.points))

        higher553 = self.iep.findHighInverseEdgePoints(553)
        self.assertEqual(4, len(higher553.points))

        higher552 = self.iep.findHighInverseEdgePoints(552)
        self.assertEqual(7, len(higher552.points))

    def testPerimeterIterator(self):
        """
        Ensure __iter__ returns expected results.
        """
        self.assertEqual(len([x for x in self.iep]), 7)

    def testPerimeterLen(self):
        """
        Ensure __len__ returns expected results.
        """
        self.assertEqual(len(self.iep), 7)

    def testPerimeterSetItem(self):
        """
        Ensure __setattr__ works as expected.
        """

        perimeter =\
            InverseEdgePointContainer(inverseEdgePointList = [self.p11],
                                      datamap = self.datamap)
        self.assertEqual(len(perimeter), 1)
        perimeter[0] = self.p12
        self.assertEqual(perimeter[0], self.p12)

    def testPerimeterSetItemNeg(self):
        """
        Ensure __setattr__ Disallows Non Gridpoints to be set.
        """

        perimeter =\
            InverseEdgePointContainer(inverseEdgePointList = [self.p11],
                                      datamap = self.datamap)
        self.assertEqual(len(perimeter), 1)
        with self.assertRaises(TypeError):
            perimeter[0] = "wtf"

    def testPerimeterGetItem(self):
        """
        Ensure __getattr__ works as expected.
        """

        perimeter =\
            InverseEdgePointContainer(inverseEdgePointList = [self.p11],
                                      datamap = self.datamap)
        self.assertEqual(len(perimeter), 1)
        self.assertEqual(perimeter[0], self.p11)

    def testPerimeterBadAppend(self):
        """
        Ensure adding string to Perimeter fails.
        """
        perimeter =\
            InverseEdgePointContainer(inverseEdgePointList = [self.p11],
                                      datamap = self.datamap)
        with self.assertRaises(TypeError):
            perimeter.append("stuff")

    def testPerimeterGoodAppend(self):
        """
        Ensure adding GridPoint to SummitsContainer succeeds.
        """
        perimeter =\
            InverseEdgePointContainer(inverseEdgePointList = [self.p11],
                                      datamap = self.datamap)
        perimeter.append(self.p12)
        self.assertEqual(len(perimeter), 2)

    def testPerimeterEq(self):
        """
        Ensure __eq__ works as expected.
        """
        perimeter =\
            InverseEdgePointContainer(inverseEdgePointList = [self.p11],
                                      datamap = self.datamap)
        perimeter2 =\
            InverseEdgePointContainer(inverseEdgePointList = [self.p11],
                                      datamap = self.datamap)
        perimeter3 =\
            InverseEdgePointContainer(inverseEdgePointList = [self.p12],
                                      datamap = self.datamap)

        self.assertEqual(perimeter, perimeter2)
        test = perimeter2 == perimeter3
        self.assertFalse(test)

    def testPerimeterNe(self):
        """
        Ensure __ne__ works as expected.
        """
        perimeter = \
            InverseEdgePointContainer(inverseEdgePointList=[self.p11],
                                      datamap=self.datamap)
        perimeter2 = \
            InverseEdgePointContainer(inverseEdgePointList=[self.p11],
                                      datamap=self.datamap)
        perimeter3 = \
            InverseEdgePointContainer(inverseEdgePointList=[self.p12],
                                      datamap=self.datamap)

        self.assertNotEqual(perimeter, perimeter3)
        test = perimeter != perimeter2
        self.assertFalse(test)

    def testPerimeterRepr(self):
        """
        Ensure repr returns expected results.
        """
        self.assertEqual(self.iep.__repr__(),
                         "<InverseEdgePointContainer> 7 Objects")
