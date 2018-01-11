"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from __future__ import division
import unittest
from pyprom.tests.getData import getTestZip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData
from pyprom.lib.logic.internal_saddle_network import InternalSaddleNetwork
from pyprom.lib.containers.saddles import SaddlesContainer

class InternalSaddleNetworkTests(unittest.TestCase):
    """Test Walk Object."""

    def setUp(self):
        """Set Up Tests."""
        getTestZip()
        self.datafile = GDALLoader('/tmp/N44W072.hgt')
        self.datamap = self.datafile.datamap
        self.aziscohos = self.datamap.subset(622, 3275, 457, 325)
        self.aziscohosVicinity = AnalyzeData(self.aziscohos)
        self.summits, self.saddles = self.aziscohosVicinity.analyze()
        mp = [x for x in self.saddles.saddles if x.multiPoint]
        self.aziscohosSaddle = [x for x in mp if len(x.multiPoint.points) > 1000][0]

    def testInternalSaddleNetworkAziscohos(self):
        """
        Test to ensure we get the right number of child saddles and their
        parameters are as expected.
        """
        nw = InternalSaddleNetwork(self.aziscohosSaddle, self.datamap)
        new_saddles = nw.generate_child_saddles()
        self.assertEqual(len(new_saddles), 6)
        for saddle in new_saddles:
            self.assertEqual(len(saddle.highShores), 2)
            self.assertEqual(saddle.multiPoint, None)
            self.assertEqual(saddle.disqualified, False)

    def testInternalSaddleNetworkAziscohosViaContainer(self):
        """
        Ensure when approached from a saddle container we get back the parent node as well
        """
        saddleContainer = SaddlesContainer([self.aziscohosSaddle])
        new_saddles = saddleContainer.rebuildSaddles(self.datamap)
        self.assertEqual(len(new_saddles), 7)
        parent = [x for x in new_saddles.points if x.children]
        children = [x for x in new_saddles.points if x.parent]
        self.assertEqual(len(parent), 1)
        self.assertEqual(parent[0].disqualified, True)
        self.assertEqual(parent[0].edgeEffect, True)
        self.assertEqual(len(parent[0].children), 6)
        for child in children:
            self.assertIsNotNone(child.parent)








if __name__ == '__main__':
    unittest.main()