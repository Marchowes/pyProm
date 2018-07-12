"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.containers.summits import SummitsContainer
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit


class SummitsContainerTests(unittest.TestCase):
    def setUp(self):
        """Set Up Tests."""
        pass

    def testSummitsContainerBadInitiation(self):
        """Ensure creating a SummitsContainer with a list of Saddles fails"""
        saddles = [Saddle(1,2,3)]
        with self.assertRaises(TypeError):
            SummitsContainer(saddles)

    def testSummitsContainerEmptyInitiation(self):
        """Ensure creating a SaddlesContainer with an empty list is OK"""
        container = SummitsContainer([])
        self.assertEqual(len(container.summits), 0)

    def testSummitsContainerGoodInitiation(self):
        """
        Ensure creating a SummitsContainer with a list of Summits succeeds
        """
        summits = [Summit(1,2,3)]
        container = SummitsContainer(summits)
        self.assertEqual(len(container.points), 1)
        self.assertEqual(len(container.summits), 1)

    def testSummitsContainerBadAppend(self):
        """
        Ensure adding Saddle to SummitsContainer fails.
        """
        summits = [Summit(1,2,3)]
        container = SummitsContainer(summits)
        with self.assertRaises(TypeError):
            container.append(Saddle(1,2,3))

    def testSummitsContainerGoodAppend(self):
        """
        Ensure adding Summit to SummitsContainer succeeds.
        """
        container = SummitsContainer([])
        container.append(Summit(1,2,3))

    def testSummitsContainerGetItem(self):
        """
        Ensure getting item index succeeds.
        """
        summits = [Summit(1,2,3)]
        container = SummitsContainer(summits)
        self.assertEqual(container[0], summits[0])

    def testSummitsContainerSetItem(self):
        """
        Ensure setting item index succeeds.
        """
        summits = [Summit(1, 2, 3), Summit(1, 2, 3)]
        summit567 = Summit(5, 6, 7)
        container = SummitsContainer(summits)
        container[1] = summit567
        self.assertEqual(container[1], summit567)

    def testSummitsContainerSetItemNegative(self):
        """
        Ensure setting item index fails when non Summit is passed in.
        """
        summits = [Summit(1, 2, 3), Summit(1, 2, 3)]
        saddle567 = Saddle(5, 6, 7)
        container = SummitsContainer(summits)
        with self.assertRaises(TypeError):
            container[1] = saddle567

    def testSummitsContainerRepr(self):
        """ Ensure __repr__ yields expected result"""
        summits = [Summit(1, 2, 3)]
        container = SummitsContainer(summits)
        self.assertEqual(container.__repr__(),
                         "<SummitsContainer> 1 Objects")