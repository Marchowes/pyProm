"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from __future__ import division
import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.domain_map import DomainMap
from pyprom.lib.logic.summit_domain_walk import Walk
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.logic.internal_saddle_network import InternalSaddleNetwork
import logging
logging.basicConfig(level=logging.DEBUG)

class Walk2AziscohosTests(unittest.TestCase):
    """
    Test The Walk Features of feature_discovery
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up shared resources
        """
        logging.basicConfig(level=logging.DEBUG)
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = datafile.datamap
        #cls.aziscohos= cls.datamap.subset(0,0,50,50) #todo: remove
        cls.aziscohos = cls.datamap.subset(622, 3275, 457, 325)
        cls.aziscohosVicinity = DomainMap(cls.aziscohos)
        cls.aziscohosVicinity.run(superSparse=True, rebuildSaddles=False)
        #cls.masterSaddlesDict = saddles.to_dict()


    # def setUp(self):
    #     """
    #     Set Up Tests.
    #     """
    #     self.aziscohosSaddle = [x for x in self.aziscohosVicinity.saddles.multipoints if len(x.multipoint) > 1000][0]

    def test_walk2_intro(self):
        aziscohosSaddle = [x for x in self.aziscohosVicinity.saddles.multipoints if len(x.multipoint) > 1000][0]
        #self.aziscohosVicinity.walkSingleSaddle2(aziscohosSaddle)
        #hs0 = aziscohosSaddle.highPerimeterNeighborhoods[0]
        #isn = InternalSaddleNetwork(aziscohosSaddle, self.aziscohosVicinity.datamap)
        #cs = isn.generate_child_saddles()


        walker = Walk(self.aziscohosVicinity)
        #doms = walker.climb_points(aziscohosSaddle.highPerimeterNeighborhoods[0].to_tuples())



        saddles, runoffs, linkers, summitDomains = walker.climb_from_saddles()
        print("yolo")


    # def test_HLE(self):
    #     #aziscohosSaddle = [x for x in self.aziscohosVicinity.saddles.multipoints if len(x.multipoint) > 1000][0]
    #
    #
    #     #self.aziscohosVicinity.walkSingleSaddle2(aziscohosSaddle)
    #     #hs0 = aziscohosSaddle.highPerimeterNeighborhoods[0]
    #     #isn = InternalSaddleNetwork(aziscohosSaddle, self.aziscohosVicinity.datamap)
    #     #cs = isn.generate_child_saddles()
    #
    #     walker = Walk(self.aziscohosVicinity)
    #     walker.climb_from_saddles()
    #
    #     #walker = Walk(self.aziscohosVicinity)
    #     #doms = walker.climb_points(aziscohosSaddle.highPerimeterNeighborhoods[0].to_tuples())
    #
    #
    #
    #     #saddles, linkers, summitDomains = walker.climb_from_saddles()
    #     print("yolo")