"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.containers.saddles import SaddlesContainer
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit
from pyprom.domain import Domain
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader


class SaddlesContainerTests(unittest.TestCase):
    """Test SaddlesContainer."""

    def setUp(self):
        """Set Up Tests."""
        pass

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

    def testSaddlesContainerRebuildSaddles(self):
        """
        See testInternalSaddleNetwork.py::
        InternalSaddleNetworkTests::
        testInternalSaddleNetworkAziscohosViaContainer
        """
        pass

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
        domain.walk()
        saddles = domain.saddles
        saddleDict = saddles.to_dict()
        newSaddles = SaddlesContainer.from_dict(saddleDict, datamap=someslice)
        self.assertEqual(newSaddles, saddles)
