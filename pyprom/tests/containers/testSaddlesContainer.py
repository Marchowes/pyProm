"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.containers.saddles import SaddlesContainer
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit


class SaddlesContainerTests(unittest.TestCase):
    def setUp(self):
        """Set Up Tests."""
        pass

    def testBadInitiation(self):
        """Ensure creating a SaddlesContainer with a list of Summits fails"""
        summits = [Summit(1,2,3)]
        with self.assertRaises(TypeError):
            SaddlesContainer(summits)

    def testEmptyInitiation(self):
        """Ensure creating a SaddlesContainer with an empty list is OK"""
        container = SaddlesContainer([])
        self.assertEqual(len(container.saddles), 0)

    def testGoodInitiation(self):
        """
        Ensure creating a SaddlesContainer with a list of Summits succeeds
        """
        saddles = [Saddle(1,2,3)]
        container = SaddlesContainer(saddles)
        self.assertEqual(len(container.points), 1)
        self.assertEqual(len(container.saddles), 1)

    def testBadAdd(self):
        """
        Ensure adding Summit to SaddlesContainer fails.
        """
        saddles = [Saddle(1, 2, 3)]
        container = SaddlesContainer(saddles)
        with self.assertRaises(TypeError):
            container.add(Summit(1,2,3))

    def testRebuildSaddles(self):
        """
        see testInternalSaddleNetwork.py::
        InternalSaddleNetworkTests::
        testInternalSaddleNetworkAziscohosViaContainer
        """
        pass


