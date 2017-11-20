from __future__ import division
import unittest
from .getData import getTestZip
from pyprom.dataload import SRTMLoader
from pyprom.logic import AnalyzeData
from pyprom.walk import Walk

class WalkTests(unittest.TestCase):
    def setUp(self):
        getTestZip()
        self.datafile = SRTMLoader('/tmp/N44W072.hgt')
        datamap = self.datafile.datamap
        self.islandpondVT = datamap.subset(602, 353, 260, 260)
        self.islandpondVTVicinity = AnalyzeData(self.islandpondVT)
        self.summits, self.saddles = self.islandpondVTVicinity.analyze()


    def testWalkIslandPond(self):
        #we
        whittle = self.saddles.elevationRangeMetric(353,355)
        pond = [z for z in whittle.points if len(z.multiPoint.points) > 100][0]
        walk = Walk(self.summits, [pond], self.islandpondVT)
        linkers = walk.walk(pond)
        #temporary
        self.assertEqual(len(linkers), 2)


if __name__ == '__main__':
    unittest.main()


