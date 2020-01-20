"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.util.helpers import generate_multiPoint_saddle
from pyprom.lib.containers.saddles import SaddlesContainer
from pyprom.lib.containers.base_gridpoint import BaseGridPointContainer
from pyprom.lib.containers.gridpoint import GridPointContainer
from pyprom.lib.locations.base_gridpoint import BaseGridPoint
from pyprom.lib.locations.gridpoint import GridPoint
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit
from pyprom.domain import Domain
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader


class SaddlesContainerTests(unittest.TestCase):
    """Test SaddlesContainer."""

    def testSaddlesContainerBadInitiation(self):
        """
        Ensure creating a SaddlesContainer with a list of Summits fails
        """
        summits = [Summit(1, 2, 3)]
        with self.assertRaises(TypeError):
            SaddlesContainer(summits)

    def testSaddlesContainerEmptyInitiation(self):
        """
        Ensure creating a SaddlesContainer with an empty list is OK
        """
        container = SaddlesContainer([])
        self.assertEqual(len(container.saddles), 0)

    def testSaddlesContainerGoodInitiation(self):
        """
        Ensure creating a SaddlesContainer with a list of Summits succeeds
        """
        saddles = [Saddle(1, 2, 3)]
        container = SaddlesContainer(saddles)
        self.assertEqual(len(container), 1)
        self.assertEqual(len(container.saddles), 1)

    def testSaddlesContainerBadAppend(self):
        """
        Ensure appending Summit to SaddlesContainer fails.
        """
        saddles = [Saddle(1, 2, 3)]
        container = SaddlesContainer(saddles)
        with self.assertRaises(TypeError):
            container.append(Summit(1, 2, 3))

    def testSaddlesContainerGoodAppend(self):
        """
        Ensure adding Saddle to SaddlesContainer succeeds.
        """
        container = SaddlesContainer([])
        container.append(Saddle(1, 2, 3))

    def testSaddlesContainerGetItem(self):
        """
        Ensure getting item index succeeds.
        """
        saddles = [Saddle(1, 2, 3)]
        container = SaddlesContainer(saddles)
        self.assertEqual(container[0], saddles[0])

    def testSaddlesContainerSetItem(self):
        """
        Ensure setting item index succeeds.
        """
        saddles = [Saddle(1, 2, 3), Saddle(1, 2, 3)]
        saddle567 = Saddle(5, 6, 7)
        container = SaddlesContainer(saddles)
        container[1] = saddle567
        self.assertEqual(container[1], saddle567)

    def testSaddlesContainerSetItemNegative(self):
        """
        Ensure setting item index fails when non Saddle is passed in.
        """
        saddles = [Saddle(1, 2, 3), Saddle(1, 2, 3)]
        summit567 = Summit(5, 6, 7)
        container = SaddlesContainer(saddles)
        with self.assertRaises(TypeError):
            container[1] = summit567

    def testSaddlesContainerRepr(self):
        """
        Ensure __repr__ yields expected result
        """
        saddles = [Saddle(1, 2, 3)]
        container = SaddlesContainer(saddles)
        self.assertEqual(container.__repr__(),
                         "<SaddlesContainer> 1 Objects")

    def testSaddlesContainerFromDictAll(self):
        """
        Ensure from_dict() produces expected results
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = datafile.datamap
        someslice = datamap.subset(0, 0, 30, 30)
        domain = Domain(someslice)
        domain.run()
        saddles = domain.saddles
        saddleDict = saddles.to_dict()
        newSaddles = SaddlesContainer.from_dict(saddleDict, datamap=someslice)
        self.assertEqual(newSaddles, saddles)

    def testSaddlesContainerDisqualified(self):
        """
        Ensure disqualified() returns all disqualified
        """
        s1 = Saddle(1, 1, 1)
        s2 = Saddle(2, 2, 2)
        sd3 = Saddle(3, 3, 3)
        sd4 = Saddle(4, 4, 4)
        sd3.disqualified = sd4.disqualified = True
        container = SaddlesContainer([s1, s2, sd3, sd4])
        self.assertEqual(container.disqualified, [sd3, sd4])

    def testSaddlesContainerMultiPoint(self):
        """
        Ensure multipoint() returns all multipoint Summits
        """
        s1 = Saddle(1, 1, 1)
        s1.multiPoint = ["bogus_but_ok_for_test"]
        s2 = Saddle(2, 2, 2)
        container = SaddlesContainer([s1, s2])
        self.assertEqual(container.multipoints, [s1])


class SaddlesContainerRebuildTests(unittest.TestCase):
    """
    SaddlesContainerRebuildTests
    These tests exercise both rebuildSaddles() as well as test
    some InternalSaddleNetwork features.
    """

    @classmethod
    def setUpClass(cls):
        """
        Grab the datamap
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = datafile.datamap

    def setUp(self):
        """
        Set up
        """
        self.elevation = 1000
        self.islands = [BaseGridPointContainer([BaseGridPoint(103, 203)]),
                        BaseGridPointContainer([BaseGridPoint(107, 207)])]
        self.island = [BaseGridPointContainer([BaseGridPoint(105, 205)])]

    def testSaddlesContainerRebuildTwoIslandsTwoPerimeter(self):
        """
        Ensure rebuildSaddles produces expected results.
        2 islands, 2 perimeter high shores.
        Must generate 3 new Saddles (len(hs)-1)
        This exercises InternalSaddleNetwork which is called when hs > 2
        """
        twoIslands = SaddlesContainer([generate_multiPoint_saddle(100,
                                      200, 10, 10,
                                      self.datamap,
                                      self.elevation,
                                      self.islands, 2)])

        newSaddles = twoIslands.rebuildSaddles(self.datamap)

        ns0 = Saddle(44.97097222222222, -71.94319444444444, 1000)
        ns0.highShores = [twoIslands[0].highShores[0],
                          twoIslands[0].highShores[1]]
        ns1 = Saddle(44.97208333333334, -71.94430555555554, 1000)
        ns1.highShores = [twoIslands[0].highShores[3],
                          twoIslands[0].highShores[0]]
        ns2 = Saddle(44.97236111111111, -71.94458333333333, 1000)
        ns2.highShores = [twoIslands[0].highShores[3],
                          twoIslands[0].highShores[2]]
        self.assertEqual(len(newSaddles), 3)
        self.assertEqual(newSaddles[0], ns0)
        self.assertEqual(newSaddles[1], ns1)
        self.assertEqual(newSaddles[2], ns2)

    def testSaddlesContainerRebuildOneIslandTwoPerimeter(self):
        """
        Ensure rebuildSaddles produces expected results.
        1 island, 2 perimeter high shores.
        Must generate 2 new Saddles (len(hs)-1)
        This exercises InternalSaddleNetwork which is called when hs > 2
        """
        oneIsland = SaddlesContainer([generate_multiPoint_saddle(100,
                                     200, 10, 10,
                                     self.datamap,
                                     self.elevation,
                                     self.island, 2)])

        newSaddles = oneIsland.rebuildSaddles(self.datamap)
        ns0 = Saddle(44.971805555555555, -71.94402777777778, 1000)
        ns0.highShores = [oneIsland[0].highShores[0],
                          oneIsland[0].highShores[2]]
        ns1 = Saddle(44.97236111111111, -71.94458333333333, 1000)
        ns1.highShores = [oneIsland[0].highShores[2],
                          oneIsland[0].highShores[1]]
        self.assertEqual(len(newSaddles), 2)
        self.assertEqual(newSaddles[0], ns0)
        self.assertEqual(newSaddles[1], ns1)

    def testSaddlesContainerRebuildNoIslandTwoPerimeter(self):
        """
        Ensure rebuildSaddles produces expected results.
        0 island, 2 perimeter high shores.
        Must generate 1 new Saddle (len(hs)-1)
        This exercises the internal logic inside the
        :class:`SaddlesContainer` which bypasses
        InternalSaddleNetwork logic.
        """
        noIsland = SaddlesContainer([generate_multiPoint_saddle(100,
                                    200, 10, 10,
                                    self.datamap,
                                    self.elevation, [], 2)])
        newSaddles = noIsland.rebuildSaddles(self.datamap)
        ns0 = Saddle(44.97236111111111, -71.94458333333333, 1000)
        ns0.highShores = [noIsland[0].highShores[1], noIsland[0].highShores[0]]
        self.assertEqual(len(newSaddles), 1)
        self.assertEqual(newSaddles[0], ns0)

    def testSaddlesContainerRebuildOneIslandOnePerimeter(self):
        """
        Ensure rebuildSaddles produces expected results.
        1 island, 1 perimeter high shores.
        Must generate 1 new Saddle (len(hs)-1)
        This exercises the internal logic inside the :class:`SaddlesContainer`
        which bypasses InternalSaddleNetwork logic.
        """
        oneIslandOnePerimeter = SaddlesContainer(
            [generate_multiPoint_saddle(100,
             200, 10, 10,
             self.datamap,
             self.elevation,
             self.island, 1)])
        newSaddles = oneIslandOnePerimeter.rebuildSaddles(self.datamap)
        ns0 = Saddle(44.971805555555555, -71.94402777777778, 1000)
        ns0.highShores = [oneIslandOnePerimeter[0].highShores[1],
                          oneIslandOnePerimeter[0].highShores[0]]
        self.assertEqual(len(newSaddles), 1)
        self.assertEqual(newSaddles[0], ns0)

    def testSaddlesContainerRebuildOnePerimeter(self):
        """
        Ensure rebuildSaddles produces expected results.
        0 island, 1 perimeter high shores.
        Since there is only a single highEdge this fast
        exits and returns the same Saddle.
        """
        oneIslandOnePerimeter = SaddlesContainer(
            [generate_multiPoint_saddle(100,
                                        200, 10, 10,
                                        self.datamap,
                                        self.elevation,
                                        [], 1)])
        newSaddles = oneIslandOnePerimeter.rebuildSaddles(self.datamap)
        self.assertEqual(newSaddles[0], oneIslandOnePerimeter[0])

    def testSaddlesContainerRebuildThreeHSNoMultiPoint(self):
        """
        Ensure rebuildSaddles produces expected results.
        non multipoint, 3 high shores.
        This exercises logic inside generate_child_saddles()
        from InternalSaddleNetwork which skips over multipoint
        centerpoint calculations
        """
        saddle = Saddle(44.97236111111111, -71.94458333333333, 1000)
        saddle.highShores = [GridPointContainer([GridPoint(99, 199, 1001)]),
                             GridPointContainer([GridPoint(99, 201, 1001)]),
                             GridPointContainer([GridPoint(101, 199, 1001)]),
                             ]
        saddles = SaddlesContainer([saddle])
        newSaddles = saddles.rebuildSaddles(self.datamap)
        ns0 = Saddle(44.97236111111111, -71.94458333333333, 1000)
        ns0.highShores = [saddle.highShores[0], saddle.highShores[1]]
        ns1 = Saddle(44.97236111111111, -71.94458333333333, 1000)
        ns1.highShores = [saddle.highShores[1], saddle.highShores[2]]
        self.assertEqual(len(newSaddles), 2)
        self.assertEqual(newSaddles[0], ns0)
        self.assertEqual(newSaddles[1], ns1)
