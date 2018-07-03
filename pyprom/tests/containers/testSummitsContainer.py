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

    def testBadInitiation(self):
        """Ensure creating a SummitsContainer with a list of Saddles fails"""
        saddles = [Saddle(1,2,3)]
        with self.assertRaises(TypeError):
            SummitsContainer(saddles)

    def testEmptyInitiation(self):
        """Ensure creating a SaddlesContainer with an empty list is OK"""
        container = SummitsContainer([])
        self.assertEqual(len(container.summits), 0)

    def testGoodInitiation(self):
        """
        Ensure creating a SummitsContainer with a list of Summits succeeds
        """
        summits = [Summit(1,2,3)]
        container = SummitsContainer(summits)
        self.assertEqual(len(container.points), 1)
        self.assertEqual(len(container.summits), 1)

    def testBadAdd(self):
        """
        Ensure adding Saddle to SummitsContainer fails.
        """
        summits = [Summit(1,2,3)]
        container = SummitsContainer(summits)
        with self.assertRaises(TypeError):
            container.add(Saddle(1,2,3))


