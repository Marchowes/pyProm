"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest

from pyprom.tests.getData import gettestzip
from pyprom.domain_map import DomainMap
from pyprom.lib.loaders.gdal_loader import GDALLoader
from pyprom.lib.locations.summit import Summit
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.containers.linker import Linker


class SummitTests(unittest.TestCase):
    """Test Summit."""

    def setUp(self):
        """
        Set up test topology:

        masterSummit
        | |
        | --linker_m1----Saddle1--linker1-------Summit1
        |---linker_m2----Saddle2--linker2-------Summit2
                           |------linker_dead---Summit_locally_dead
        """
        self.masterSummit = Summit(0, 0, 0)

        self.summit1 = Summit(1, 1, 1)
        self.summit2 = Summit(2, 2, 2)
        self.summit_locally_dead = Summit(3, 3, 3)

        self.saddle1 = Saddle(1, 1, 1)
        self.saddle2 = Saddle(2, 2, 2)

        self.linker_m1 = Linker(self.masterSummit, self.saddle1)
        self.linker_m1.add_to_remote_saddle_and_summit()
        self.linker_m2 = Linker(self.masterSummit, self.saddle2)
        self.linker_m2.add_to_remote_saddle_and_summit()
        self.linker1 = Linker(self.summit1, self.saddle1)
        self.linker1.add_to_remote_saddle_and_summit()
        self.linker2 = Linker(self.summit2, self.saddle2)
        self.linker2.add_to_remote_saddle_and_summit()
        self.linker_dead = Linker(self.summit_locally_dead, self.saddle2)
        self.linker_dead.add_to_remote_saddle_and_summit()
        self.linker_dead.disqualified = True

    def testSummitFromDictEdge(self):
        """
        Ensure from_dict() produces expected
        results on a saddle which has a child.
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = datafile.to_datamap()
        someslice = datamap.subset(0, 0, 30, 30)
        domain = DomainMap(someslice)
        domain.run()
        summits = domain.summits
        summit = summits[0]
        summitDict = summit.to_dict()
        newSummit = Summit.from_dict(summitDict, datamap=someslice)

        self.assertTrue(summit.edgeEffect)
        self.assertEqual(newSummit, summit)
        self.assertEqual(newSummit.latitude, summit.latitude)
        self.assertEqual(newSummit.longitude, summit.longitude)
        self.assertEqual(newSummit.elevation, summit.elevation)
        self.assertEqual(newSummit.multipoint, summit.multipoint)
        self.assertEqual(newSummit.edgeEffect, summit.edgeEffect)
        self.assertEqual(newSummit.edgePoints, summit.edgePoints)
        self.assertEqual(newSummit.id, summit.id)

    def testSummitAllNeighbors(self):
        """
        Ensure all_neighbors returns expected results
        filterDisqualified=True (Default)
        """
        all = self.masterSummit.all_neighbors()
        self.assertEqual(all, [self.masterSummit,
                               self.summit1,
                               self.masterSummit,
                               self.summit2])

    def testSummitAllNeighborsNoFilter(self):
        """
        Ensure all_neighbors returns expected results
        filterDisqualified=False
        """
        all = self.masterSummit.all_neighbors(filterDisqualified=False)
        self.assertEqual(all, [self.masterSummit,
                               self.summit1,
                               self.masterSummit,
                               self.summit2,
                               self.summit_locally_dead])

    def testSummitNeighbors(self):
        """
        Ensure neighbors() returns expected results.
        """
        self.assertEqual(self.masterSummit.neighbors, [self.summit1,
                                                       self.summit2])

    def testSummitAddSaddleLinker(self):
        """
        Ensure addSaddleLinker adds linker.
        """
        linker = Linker(self.masterSummit, Saddle(10, 10, 10))
        self.masterSummit.addSaddleLinker(linker)
        self.assertIn(linker, self.masterSummit.saddles)

        # Ensure non linker objects are rejected.
        with self.assertRaises(TypeError):
            self.masterSummit.addSaddleLinker(19)

    def testSummitFeatureNeighbors(self):
        """
        Ensure feature_neighbors() produces expected results on
        a summit with linked saddles.
        """
        summit2 = Summit(2, 2, 20000)
        saddle1000 = Saddle(1000, 1000, 1000)
        saddle100 = Saddle(100, 100, 100)
        linkerL1b = Linker(summit2, saddle100)
        linkerH1b = Linker(summit2, saddle1000)
        for linker in [linkerL1b, linkerH1b]:
            linker.add_to_remote_saddle_and_summit()
        self.assertEqual(summit2.feature_neighbors(), [saddle100, saddle1000])
