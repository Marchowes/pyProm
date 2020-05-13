"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.containers.gridpoint import GridPointContainer
from pyprom.lib.locations.gridpoint import GridPoint
from collections import defaultdict


class GridPointContainerTests(unittest.TestCase):
    """Test GridPointContainer"""

    def setUp(self):
        """Set Up Tests."""
        self.p11 = GridPoint(1, 1, 553)
        self.p12 = GridPoint(1, 2, 554)
        self.p13 = GridPoint(1, 3, 554)
        self.p14 = GridPoint(1, 4, 553)
        self.p24 = GridPoint(2, 4, 555)
        self.p25 = GridPoint(2, 5, 554)
        self.p26 = GridPoint(2, 6, 553)
        self.gpc = GridPointContainer([self.p11, self.p12,
                                       self.p13, self.p14,
                                       self.p24, self.p25,
                                       self.p26])

    def testGridPointContainerCreate(self):
        """
        Ensure Creating a basic GridPointContainer works.
        """
        container = GridPointContainer([self.p11, self.p12])
        dd = defaultdict(dict)
        dd[1][1] = self.p11
        dd[1][2] = self.p12
        self.assertEqual(container.fastLookup, dd)

    def testGridPointContainerBadInitiation(self):
        """
        Ensure creating a GridPointContainer with a list of strings fails
        """
        with self.assertRaises(TypeError):
            GridPointContainer(["wtf"])

    def testGridPointContainerEmptyInitiation(self):
        """
        Ensure creating a GridPointContainer with an empty list is OK
        """
        container = GridPointContainer([])
        self.assertEqual(len(container), 0)

    def testGridPointContainerIterNeighborDiagonal(self):
        """
        Ensure that iterDiagonal returns the expected results.
        Iter diagonal returns all neighbors of a GridPoint contained
        in the GridPointPointContainer
        """
        count = 0
        # Should have two results.
        for point in self.gpc.iterNeighborDiagonal(self.p12):
            count += 1
            self.assertIn(point, [self.p11,
                                  self.p13])
        self.assertEqual(count, 2)
        count = 0
        # Should have just the one result.
        for point in self.gpc.iterNeighborDiagonal(self.p11):
            count += 1
            self.assertIn(point, [self.p12])
        self.assertEqual(count, 1)
        count = 0
        # Should have three results.
        for point in self.gpc.iterNeighborDiagonal(self.p24):
            count += 1
            self.assertIn(point, [self.p14,
                                  self.p25,
                                  self.p13])
        self.assertEqual(count, 3)
        count = 0
        # Should have three results.
        for point in self.gpc.iterNeighborDiagonal(self.p13):
            count += 1
            self.assertIn(point, [self.p12,
                                  self.p14,
                                  self.p24])
        self.assertEqual(count, 3)

    def testGridPointContainerIterNeighborOrthogonal(self):
        """
        Ensure that iterOrthogonal returns the expected results.
        Iter diagonal returns all orthogonal (right angle) neighbors
        of a GridPoint contained in the GridPointContainer
        """
        count = 0
        # Should have two results.
        for point in self.gpc.iterNeighborOrthogonal(self.p12):
            count += 1
            self.assertIn(point, [self.p11,
                                  self.p13])
        self.assertEqual(count, 2)
        count = 0
        # Should have just the one result.
        for point in self.gpc.iterNeighborOrthogonal(self.p11):
            count += 1
            self.assertIn(point, [self.p12])
        self.assertEqual(count, 1)
        count = 0
        # Should have two results.
        for point in self.gpc.iterNeighborOrthogonal(self.p24):
            count += 1
            self.assertIn(point, [self.p14,
                                  self.p25])
        self.assertEqual(count, 2)
        count = 0
        # Should have two results.
        for point in self.gpc.iterNeighborOrthogonal(self.p13):
            count += 1
            self.assertIn(point, [self.p12,
                                  self.p14])
        self.assertEqual(count, 2)

    def testGridPointContainerFindPseudoSummits(self):
        """
        Ensure findPseudoSummits gives the expected result
        """
        ps = self.gpc.findPseudoSummits()
        self.assertEqual(ps, [self.p12, self.p24])

    def testGridPointContainerFindClosestPoints(self):
        """
        Ensure findClosestPoints gives the expected result
        """
        them = GridPointContainer([GridPoint(5, 5, 5),
                                   GridPoint(3, 3, 3)])
        closest = self.gpc.findClosestPoints(them)
        result = (self.p24, GridPoint(3, 3, 3), 1.4142135623730951)
        self.assertTupleEqual(closest, result)

    def testSortGridPointContainer(self):
        """
        Ensure pass through to sort() works as expected.
        """
        originalPoints = [self.p11, self.p12, self.p13, self.p14,
                          self.p24, self.p25, self.p26]
        self.assertEqual(self.gpc.points, originalPoints)

        self.gpc.sort(key=lambda x: x.elevation, reverse=True)
        orderedPoints = [self.p24, self.p12, self.p13, self.p25,
                         self.p11, self.p14, self.p26]
        self.assertEqual(self.gpc.points, orderedPoints)

    def testGridPointContainerLen(self):
        """
        Ensure __len__ produces the expected result.
        """
        container = GridPointContainer([GridPoint(5, 5, 5)])
        self.assertEqual(len(container), 1)

    def testGridPointContainerAppend(self):
        """
        Ensure append appends to points and updates fastLookup
        """
        container = GridPointContainer([self.p11, self.p12])
        dd = defaultdict(dict)
        dd[1][1] = self.p11
        dd[1][2] = self.p12
        dd[1][3] = self.p13
        container.append(self.p13)
        self.assertEqual(container.fastLookup, dd)

    def testGridPointContainerBadAppend(self):
        """
        Ensure adding !GridPoint to GridPointContainer fails.
        """
        gridpoints = [self.p11]
        container = GridPointContainer(gridpoints)
        with self.assertRaises(TypeError):
            container.append("wtf")

    def testGridPointContainerGoodAppend(self):
        """
        Ensure adding GridPoint to GridPointContainer succeeds.
        """
        container = GridPointContainer([])
        container.append(self.p11)

    def testGridPointContainerGetItem(self):
        """
        Ensure getting item on index succeeds.
        """
        gridpoints = [self.p11]
        container = GridPointContainer(gridpoints)
        self.assertEqual(container[0], gridpoints[0])

    def testGridPointContainerSetItem(self):
        """
        Ensure setting item on index succeeds.
        """
        gridpoints = [self.p11, self.p12]
        container = GridPointContainer(gridpoints)
        container[1] = self.p13
        self.assertEqual(container[1], self.p13)

    def testGridPointContainerSetItemNegative(self):
        """
        Ensure setting item index fails when non GridPoint is passed in.
        """
        gridpoints = [self.p11, self.p12]
        container = GridPointContainer(gridpoints)
        with self.assertRaises(TypeError):
            container[1] = "wtf"

    def testGridPointContainerEqual(self):
        """
        Ensure Equality Test works as expected.
        """
        gridpoints = [self.p11, self.p12]
        container = GridPointContainer(gridpoints)
        container2 = GridPointContainer(gridpoints)
        container3 = GridPointContainer([])

        c1c2 = container == container2
        c1c3 = container == container3

        self.assertTrue(c1c2)
        self.assertFalse(c1c3)

    def testGridPointContainerNotEqual(self):
        """
        Ensure Inequality Test works as expected.
        """
        gridpoints = [self.p11, self.p12]
        container = GridPointContainer(gridpoints)
        container2 = GridPointContainer(gridpoints)
        container3 = GridPointContainer([])

        c1c2 = container != container2
        c1c3 = container != container3

        self.assertFalse(c1c2)
        self.assertTrue(c1c3)

    def testGridPointContainerHash(self):
        """
        Ensure __hash__() produces the expected results.
        """
        gridpoints = [self.p11, self.p12]
        container = GridPointContainer(gridpoints)
        self.assertEqual(container.__hash__(), 4150162461373869217)

    def testGridPointContainerRepr(self):
        """
        Ensure append __repr__() yields expected results.
        """
        container = GridPointContainer([self.p11, self.p12])
        self.assertEqual(container.__repr__(),
                         "<GridPointContainer> 2 Objects")

    def testGridPointContainerFromDict(self):
        """
        Ensure from_dict() produces expected results
        """
        gpcDict = self.gpc.to_dict()
        newGpc = GridPointContainer.from_dict(gpcDict)
        self.assertEqual(newGpc, self.gpc)

    def testGridPointContainerIndex(self):
        """
        Ensure index() returns expected results.
        """
        self.assertEqual(self.gpc.index(self.p14), 3)
        # Negative
        self.assertEqual(self.gpc.index("yolo"), None)

    def testGridPointContainerLowest(self):
        """
        Ensure lowest() produces expected results.
        """
        lowest = self.gpc.lowest
        self.assertEqual(lowest, [self.p11, self.p14, self.p26])

    def testGridPointContainerlHighest(self):
        """
        Ensure highest() produces expected results.
        """
        highest = self.gpc.highest
        self.assertEqual(highest, [self.p24])

    def testGridPointContainerlToTuples(self):
        """
        Ensure to_tuples() produces expected results
        """
        gp1 = GridPoint(1, 2, 3)
        gp2 = GridPoint(3, 2, 1)
        gps = GridPointContainer([gp1, gp2])
        self.assertEqual(gps.to_tuples(), [(1, 2, 3), (3, 2, 1)])
