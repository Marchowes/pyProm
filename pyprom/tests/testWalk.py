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
from pyprom.walk import Walk
from pyprom.lib.errors.errors import NoLinkersError


class WalkTests(unittest.TestCase):
    """Test Walk Object."""

    def setUp(self):
        """Set Up Tests."""
        getTestZip()
        self.datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = self.datafile.datamap
        self.islandpondVT = datamap.subset(602, 353, 260, 260)
        self.islandpondVTVicinity = AnalyzeData(self.islandpondVT)
        self.summits, self.saddles = self.islandpondVTVicinity.run()

    def testWrongSaddles(self):
        """Ensure saddles param is actually a :class:SaddlesContainer"""
        with self.assertRaises(TypeError):
            Walk(self.summits, self.summits, self.islandpondVT)

    def testWrongSummits(self):
        """Ensure summits param is actually a :class:SummitsContainer"""
        with self.assertRaises(TypeError):
             Walk(self.saddles, self.saddles, self.islandpondVT)

    def testWrongDatamap(self):
        """Ensure datamap param is actually a :class:Datamap"""
        with self.assertRaises(TypeError):
            Walk(self.summits, self.saddles, self.saddles)

    def testWalkIslandPond(self):
        """Test walk around Island Pond VT."""
        islandPondSaddleContainer = self.saddles.radius(44.810833, -71.8676388, 10)
        islandPondSaddle = islandPondSaddleContainer.points[0]
        walk = Walk(self.summits, islandPondSaddleContainer, self.islandpondVT)
        walk.walk(islandPondSaddle)
        self.assertEqual(len(walk.linkers), 2)
        self.assertEqual(len(islandPondSaddle.summits), 2)
        self.assertEqual(islandPondSaddle.summits[0].summit, self.summits.points[155])
        self.assertEqual(islandPondSaddle.summits[1].summit, self.summits.points[171])

    def testGenerateDomainNoLinkers(self):
        """
        Test that generating a domain from a Walk fails when the walk has not been executed.
        """
        islandPondSaddleContainer = self.saddles.radius(44.810833, -71.8676388, 10)
        walk = Walk(self.summits, islandPondSaddleContainer, self.islandpondVT)
        with self.assertRaises(NoLinkersError):
            domain = walk.domain()

    def testGenerateDomain(self):
        """
        Test that generating a domain from a properly executed Walk succeeds
        """
        islandPondSaddleContainer = self.saddles.radius(44.810833, -71.8676388, 10)
        islandPondSaddle = islandPondSaddleContainer.points[0]
        walk = Walk(self.summits, islandPondSaddleContainer, self.islandpondVT)
        walk.walk(islandPondSaddle)
        d = walk.domain()
        self.assertEqual(len(d.linkers),2)
        self.assertEqual(len(d.summits), 342)
        self.assertEqual(len(d.saddles), 1)


if __name__ == '__main__':
    unittest.main()
