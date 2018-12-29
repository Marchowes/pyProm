"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest

from pyprom.domain import Domain
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit
from pyprom.lib.containers.linker import Linker
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.feature_discovery import AnalyzeData


class SaddleTests(unittest.TestCase):
    """Test Saddles."""

    @classmethod
    def setUpClass(cls):
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = datafile.datamap

    def testSaddleFromDictEdge(self):
        """
        Ensure from_dict() produces expected
        results on a saddle which has a child.
        """
        someslice = self.datamap.subset(0, 0, 30, 30)
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
        someslice = self.datamap.subset(0, 0, 30, 30)
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
        someslice = self.datamap.subset(0, 0, 30, 30)
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

    def testSaddleFeatureNeighbors(self):
        """
        Ensure feature_neighbors() produces expected results on
        a saddle with linked summits.
        """
        summit1 = Summit(1,1,10000)
        summit2 = Summit(2,2,20000)
        saddle1000 = Saddle(1000,1000,1000)
        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit2, saddle1000)
        for linker in [linkerH1a, linkerH1b]:
            linker.add_to_remote_saddle_and_summit()
        self.assertEqual(saddle1000.feature_neighbors(), [summit1, summit2])


class SaddleNetworkTests(unittest.TestCase):
    """Test Saddles with neighbors"""

    def setUp(self):
        """
        Set up test topology:

        masterSummit
        | |
        | --linker_m1----Saddle1--linker1-------Summit1
        |---linker_m2----Saddle2--linker2-------Summit2
                           |------linker_dead---Summit_locally_dead
                                                      |
                                        Saddle3-----linker3
        """

        self.masterSummit = Summit(0, 0, 0)

        self.summit1 = Summit(1, 1, 1)
        self.summit2 = Summit(2, 2, 2)
        self.summit_locally_dead = Summit(3, 3, 3)

        self.saddle1 = Saddle(1, 1, 1)
        self.saddle2 = Saddle(2, 2, 2)
        self.saddle3 = Saddle(3, 3, 3)


        self.linker_m1 = Linker(self.masterSummit, self.saddle1)
        self.linker_m1.add_to_remote_saddle_and_summit()
        self.linker_m2 = Linker(self.masterSummit, self.saddle2)
        self.linker_m2.add_to_remote_saddle_and_summit()
        self.linker1 = Linker(self.summit1, self.saddle1)
        self.linker1.add_to_remote_saddle_and_summit()
        self.linker2 = Linker(self.summit2, self.saddle2)
        self.linker2.add_to_remote_saddle_and_summit()
        self.linker3 = Linker(self.summit_locally_dead, self.saddle3)
        self.linker3.add_to_remote_saddle_and_summit()
        self.linker_dead = Linker(self.summit_locally_dead, self.saddle2)
        self.linker_dead.add_to_remote_saddle_and_summit()
        self.linker_dead.disqualified = True



    def testSaddleAllNeighbors(self):
        """
        Ensure all_neighbors returns expected results
        filterDisqualified=True (Default)
        """
        all = self.saddle2.all_neighbors()
        self.assertEqual(all, [self.saddle1,
                               self.saddle2,
                               self.saddle2])

    def testSaddleAllNeighborsNoFilter(self):
        """
        Ensure all_neighbors returns expected results
        filterDisqualified=False
        """
        all = self.saddle2.all_neighbors(filterDisqualified=False)
        self.assertEqual(all, [self.saddle1,
                               self.saddle2,
                               self.saddle2,
                               self.saddle3,
                               self.saddle2])

    def testSaddleNeighbors(self):
        """
        Ensure neighbors() returns expected results.
        """
        self.assertEqual(self.saddle2.neighbors, [self.saddle1])
