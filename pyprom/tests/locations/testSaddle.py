"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest

from pyprom.domain import Domain
from pyprom.lib.locations.saddle import Saddle
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData


class SaddleTests(unittest.TestCase):
    """Test Saddles."""

    def testSaddleFromDictEdge(self):
        """
        Ensure from_dict() produces expected
        results on a saddle which has a child.
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = datafile.datamap
        someslice = datamap.subset(0, 0, 30, 30)
        somewhere = AnalyzeData(someslice)
        summits, saddles, runoffs = somewhere.run()
        saddle = saddles[10]
        saddleDict = saddle.to_dict()
        newSaddle = Saddle.from_dict(saddleDict, datamap=someslice)
        self.assertEqual(newSaddle, saddle)
        self.assertEqual(newSaddle.latitude, saddle.latitude)
        self.assertEqual(newSaddle.longitude, saddle.longitude)
        self.assertEqual(newSaddle.elevation, saddle.elevation)
        self.assertEqual(newSaddle.multiPoint, saddle.multiPoint)
        self.assertEqual(newSaddle.highShores, saddle.highShores)
        self.assertEqual(newSaddle.edgeEffect, saddle.edgeEffect)
        self.assertEqual(newSaddle.edgePoints, saddle.edgePoints)
        self.assertEqual(newSaddle.id, saddle.id)
        self.assertEqual(newSaddle.disqualified, saddle.disqualified)
        self.assertEqual(newSaddle.tooLow, saddle.tooLow)
        self.assertEqual(newSaddle.singleSummit, saddle.singleSummit)
        self.assertEqual(newSaddle._disqualified, saddle._disqualified)
        # check child id
        self.assertEqual(saddleDict['children'][0], saddle.children[0].id)

    def testSaddleFromDict(self):
        """
        Ensure from_dict() produces expected results on
        a saddle with linked summits.
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = datafile.datamap
        someslice = datamap.subset(0, 0, 30, 30)
        domain = Domain(someslice)
        domain.run()
        domain.walk()
        saddles = domain.saddles
        saddle = saddles[7]
        saddleDict = saddle.to_dict()
        newSaddle = Saddle.from_dict(saddleDict, datamap=someslice)
        self.assertEqual(newSaddle, saddle)
        self.assertEqual(newSaddle.latitude, saddle.latitude)
        self.assertEqual(newSaddle.longitude, saddle.longitude)
        self.assertEqual(newSaddle.elevation, saddle.elevation)
        self.assertEqual(newSaddle.multiPoint, saddle.multiPoint)
        self.assertEqual(newSaddle.highShores, saddle.highShores)
        self.assertEqual(newSaddle.edgeEffect, saddle.edgeEffect)
        self.assertEqual(newSaddle.edgePoints, saddle.edgePoints)
        self.assertEqual(newSaddle.id, saddle.id)
        self.assertEqual(newSaddle.disqualified, saddle.disqualified)
        self.assertEqual(newSaddle.tooLow, saddle.tooLow)
        self.assertEqual(newSaddle.singleSummit, saddle.singleSummit)
        self.assertEqual(newSaddle._disqualified, saddle._disqualified)
        # Ensure linker ids are correct.
        self.assertEqual(saddleDict['summits'][0], saddle.summits[0].id)
        self.assertEqual(saddleDict['summits'][1], saddle.summits[1].id)

    def testSaddleFromDictAsChild(self):
        """
        Ensure from_dict() produces expected results on a
         saddle which has a parent.
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = datafile.datamap
        someslice = datamap.subset(0, 0, 30, 30)
        domain = Domain(someslice)
        domain.run()
        domain.walk()
        saddles = domain.saddles
        saddle = saddles[18]
        saddleDict = saddle.to_dict()
        newSaddle = Saddle.from_dict(saddleDict, datamap=someslice)
        self.assertEqual(newSaddle, saddle)
        self.assertEqual(newSaddle.latitude, saddle.latitude)
        self.assertEqual(newSaddle.longitude, saddle.longitude)
        self.assertEqual(newSaddle.elevation, saddle.elevation)
        self.assertEqual(newSaddle.multiPoint, saddle.multiPoint)
        self.assertEqual(newSaddle.highShores, saddle.highShores)
        self.assertEqual(newSaddle.edgeEffect, saddle.edgeEffect)
        self.assertEqual(newSaddle.edgePoints, saddle.edgePoints)
        self.assertEqual(newSaddle.id, saddle.id)
        self.assertEqual(newSaddle.disqualified, saddle.disqualified)
        self.assertEqual(newSaddle.tooLow, saddle.tooLow)
        self.assertEqual(newSaddle.singleSummit, saddle.singleSummit)
        self.assertEqual(newSaddle._disqualified, saddle._disqualified)
        self.assertEqual(saddleDict['summits'][0], saddle.summits[0].id)
        self.assertEqual(saddleDict['summits'][1], saddle.summits[1].id)
        # Ensure parentage is correct
        self.assertEqual(saddleDict['parent'], saddles[19].id)
