"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest

from pyprom.domain_map import DomainMap
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit
from pyprom.lib.containers.linker import Linker
from pyprom.lib.containers.summit_domain import SummitDomain
from pyprom.tests.getData import gettestzip
from pyprom.lib.loaders.gdal_loader import GDALLoader
from pyprom.feature_discovery import AnalyzeData

def make_em():
    """
    Helper for making parent - child related saddles
    """
    child = Saddle(1, 1, 1)
    parent = Saddle(2, 2, 2)
    child.parent = parent
    parent.children = [child]
    return parent, child

class SaddleTests(unittest.TestCase):
    """Test Saddles."""

    @classmethod
    def setUpClass(cls):
        """
        Set up shared resources.
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = datafile.to_datamap()

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
        self.assertEqual(newSaddle.multipoint, saddle.multipoint)
        self.assertEqual(newSaddle.highPerimeterNeighborhoods, saddle.highPerimeterNeighborhoods)
        self.assertEqual(newSaddle.edgeEffect, saddle.edgeEffect)
        self.assertEqual(newSaddle.edgePoints, saddle.edgePoints)
        self.assertEqual(newSaddle.id, saddle.id)
        self.assertEqual(newSaddle.disqualified, saddle.disqualified)
        self.assertEqual(newSaddle.basinSaddle, saddle.basinSaddle)
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
        domain = DomainMap(someslice)
        domain.run()
        saddles = domain.saddles
        saddle = saddles[7]
        saddleDict = saddle.to_dict()
        newSaddle = Saddle.from_dict(saddleDict, datamap=someslice)
        self.assertEqual(newSaddle, saddle)
        self.assertEqual(newSaddle.latitude, saddle.latitude)
        self.assertEqual(newSaddle.longitude, saddle.longitude)
        self.assertEqual(newSaddle.elevation, saddle.elevation)
        self.assertEqual(newSaddle.multipoint, saddle.multipoint)
        self.assertEqual(newSaddle.highPerimeterNeighborhoods, saddle.highPerimeterNeighborhoods)
        self.assertEqual(newSaddle.edgeEffect, saddle.edgeEffect)
        self.assertEqual(newSaddle.edgePoints, saddle.edgePoints)
        self.assertEqual(newSaddle.id, saddle.id)
        self.assertEqual(newSaddle.disqualified, saddle.disqualified)
        self.assertEqual(newSaddle.basinSaddle, saddle.basinSaddle)
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
        domain = DomainMap(someslice)
        domain.run()
        saddles = domain.saddles
        saddle = saddles[18]
        saddleDict = saddle.to_dict()
        newSaddle = Saddle.from_dict(saddleDict, datamap=someslice)
        self.assertTrue(saddle.parent)
        self.assertEqual(newSaddle, saddle)
        self.assertEqual(newSaddle.latitude, saddle.latitude)
        self.assertEqual(newSaddle.longitude, saddle.longitude)
        self.assertEqual(newSaddle.elevation, saddle.elevation)
        self.assertEqual(newSaddle.multipoint, saddle.multipoint)
        self.assertEqual(newSaddle.highPerimeterNeighborhoods, saddle.highPerimeterNeighborhoods)
        self.assertEqual(newSaddle.edgeEffect, saddle.edgeEffect)
        self.assertEqual(newSaddle.edgePoints, saddle.edgePoints)
        self.assertEqual(newSaddle.id, saddle.id)
        self.assertEqual(newSaddle.disqualified, saddle.disqualified)
        self.assertEqual(newSaddle.basinSaddle, saddle.basinSaddle)
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
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        saddle1000 = Saddle(1000, 1000, 1000)
        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit2, saddle1000)
        for linker in [linkerH1a, linkerH1b]:
            linker.add_to_remote_saddle_and_summit()
        self.assertEqual(saddle1000.feature_neighbors(), [summit1, summit2])

    def testSaddleFeatureNeighbors(self):
        """
        Ensure domains getter returns expected results.
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        saddle1000 = Saddle(1000, 1000, 1000)
        summit_domain1 = SummitDomain(self.datamap, summit1, saddle1000, [])
        summit1.domain = summit_domain1
        summit_domain2 = SummitDomain(self.datamap, summit2, saddle1000, [])
        summit2.domain = summit_domain2
        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit2, saddle1000)
        for linker in [linkerH1a, linkerH1b]:
            linker.add_to_remote_saddle_and_summit()
        self.assertEqual(saddle1000.domains, [summit_domain1, summit_domain2])

    def testSaddleEmancipate(self):
        """
        Ensure emancipate() works as expected
        """
        # Basic test
        parent, child = make_em()
        child.emancipate()
        self.assertEqual([], parent.children)
        self.assertEqual(None, child.parent)

        # Make sure we can emancipate, even if parent is unaware
        parent, child = make_em()
        parent.children = []
        child.emancipate()
        self.assertEqual([], parent.children)
        self.assertEqual(None, child.parent)

        # Make sure other children are left alone
        parent, child = make_em()
        sibling = parent = Saddle(3, 3, 3)
        parent.children.append(sibling)
        child.emancipate()
        self.assertEqual([sibling], parent.children)
        self.assertEqual(None, child.parent)

        # Twins? Make sure the twin is left alone
        parent, child = make_em()
        twin = Saddle(2, 2, 2)
        parent.children.append(twin)
        child.emancipate()
        self.assertEqual([twin], parent.children)
        self.assertEqual(None, child.parent)

        # Clones? make sure the clone is removed
        parent, child = make_em()
        parent.children.append(child)
        self.assertTrue(len(parent.children) == 2)
        child.emancipate()
        self.assertEqual([], parent.children)
        self.assertEqual(None, child.parent)

    def testSaddleDisownChildren(self):
        """
        Ensure disown_children() works as expected
        """
        # Basic test
        parent, child = make_em()
        parent.disown_children()
        self.assertEqual([], parent.children)
        self.assertEqual(None, child.parent)

        # Make sure multiple children are removed
        parent, child = make_em()
        sibling = Saddle(3, 3, 3)
        sibling.parent = parent
        parent.children.append(sibling)
        parent.disown_children()
        self.assertEqual([], parent.children)
        self.assertEqual(None, child.parent)
        self.assertEqual(None, sibling.parent)

        # Make sure multiple children are removed, including
        # ones with incomplete references to parent.
        parent, child = make_em()
        sibling = Saddle(3, 3, 3)
        parent.children.append(sibling)
        parent.disown_children()
        self.assertEqual([], parent.children)
        self.assertEqual(None, child.parent)
        self.assertEqual(None, sibling.parent)

        # Clones? make sure no Exception
        parent, child = make_em()
        parent.children.append(child)
        parent.disown_children()
        self.assertEqual([], parent.children)
        self.assertEqual(None, child.parent)

    def testSaddleSoftDelete(self):
        """
        Ensure soft_delete() works as expected
        """
        # Basic test
        parent, child = make_em()
        eqhtbasinsad = Saddle(3, 3, 1)
        eqhtbasinsad.basinSaddleAlternatives = [child]
        child.basinSaddleAlternatives = [eqhtbasinsad]
        child.soft_delete()
        self.assertEqual([], parent.children)
        self.assertEqual(None, child.parent)
        self.assertEqual([], child.basinSaddleAlternatives)
        self.assertEqual([], eqhtbasinsad.basinSaddleAlternatives)
        self.assertTrue(child.disqualified)

        # 3 equal heights and a linker
        parent, child = make_em()
        child.summits = [Linker(None, child)]
        eqhtbasinsad = Saddle(3, 3, 1)
        eqhtbasinsad2 = Saddle(4, 4, 1)
        eqhtbasinsad.basinSaddleAlternatives = [child, eqhtbasinsad2]
        eqhtbasinsad2.basinSaddleAlternatives = [child, eqhtbasinsad]
        child.basinSaddleAlternatives = [eqhtbasinsad, eqhtbasinsad2]
        child.soft_delete()
        self.assertEqual([], parent.children)
        self.assertEqual(None, child.parent)
        self.assertEqual([], child.basinSaddleAlternatives)
        self.assertEqual([eqhtbasinsad2], eqhtbasinsad.basinSaddleAlternatives)
        self.assertEqual([eqhtbasinsad], eqhtbasinsad2.basinSaddleAlternatives)
        self.assertTrue(child.summits[0].disqualified)


    def testSaddleHighPerimeterHoodShortestPath(self):
        """
        Ensure high_perimeter_neighborhood_shortest_path() produces expected results.
        Single Point.
        """
        someslice = self.datamap.subset(0, 0, 30, 30)
        domain = DomainMap(someslice)
        domain.run()
        saddles = domain.saddles
        saddle = saddles[7]
        point1, point2, middle = saddle.high_perimeter_neighborhood_shortest_path(someslice)
        self.assertEqual(point1, (12, 9, 423.0))
        self.assertEqual(point2, (14, 10, 423.0))
        self.assertEqual(middle, (13, 9))

    def testSaddleHighPerimeterHoodShortestPathMultiPoint(self):
        """
        Ensure high_perimeter_neighborhood_shortest_path() produces expected results.
        Multipoint
        """
        someslice = self.datamap.subset(0, 0, 30, 30)
        domain = DomainMap(someslice)
        domain.run()
        saddles = domain.saddles
        saddle = saddles.multipoints[1]
        point1, point2, middle = saddle.high_perimeter_neighborhood_shortest_path(someslice)
        self.assertEqual(point1, (7, 27, 425.0))
        self.assertEqual(point2, (4, 27, 425.0))
        self.assertEqual(middle, (5, 27))


def make_em():
    """
    Helper for making parent - child related saddles
    """
    child = Saddle(1, 1, 1)
    parent = Saddle(2, 2, 2)
    child.parent = parent
    parent.children = [child]
    return parent, child


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
        allof = self.saddle2.all_neighbors(filterDisqualified=False)
        self.assertEqual(allof, [self.saddle1,
                               self.saddle2,
                               self.saddle2,
                               self.saddle3,
                               self.saddle2])

    def testSaddleNeighbors(self):
        """
        Ensure neighbors() returns expected results.
        """
        self.assertEqual(self.saddle2.neighbors, [self.saddle1])
