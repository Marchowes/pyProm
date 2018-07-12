"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.containers.gridpoint import GridPointContainer
from pyprom.lib.locations.gridpoint import GridPoint
from pyprom.lib.locations.summit import Summit
from collections import defaultdict


class GridPointContainerTests(unittest.TestCase):
    def setUp(self):
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
        container = GridPointContainer([self.p11, self.p12])
        dd = defaultdict(dict)
        dd[1][1] = self.p11
        dd[1][2] = self.p12
        self.assertEqual(container.fastLookup, dd)

    def testGridPointContainerIterNeighborDiagonal(self):
        """
        Ensure that iterDiagonal returns the expected results.
        Iter diagonal returns all neighbors of a GridPoint contained
        in the GridPointPointContainer
        """
        count = 0
        # Should have two results.
        for point in self.gpc.iterNeighborDiagonal(self.p12):
            count+=1
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
            count+=1
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
        """ ensure findPseudoSummits gives the expected result"""
        ps = self.gpc.findPseudoSummits()
        self.assertEqual(ps,[self.p12, self.p24])


    def testGridPointContainerFindClosestPoints(self):
        """ ensure findClosestPoints gives the expected result"""

        them = GridPointContainer([GridPoint(5, 5, 5),
                                   GridPoint(3, 3, 3)])
        closest = self.gpc.findClosestPoints(them)
        result = (self.p24, GridPoint(3, 3, 3), 1.4142135623730951)
        self.assertTupleEqual(closest, result)

    def testGridPointContainerAppend(self):
        """ ensure append appends to points and updates fastLookup"""

        container = GridPointContainer([self.p11, self.p12])
        dd = defaultdict(dict)
        dd[1][1] = self.p11
        dd[1][2] = self.p12
        dd[1][3] = self.p13
        container.append(self.p13)
        self.assertEqual(container.fastLookup, dd)

    def testGridPointContainerRepr(self):
        """ ensure append __repr__() yields expected results."""

        container = GridPointContainer([self.p11, self.p12])
        self.assertEqual(container.__repr__(), "<GridPointContainer> 2 Objects")
