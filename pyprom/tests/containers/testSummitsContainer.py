"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.containers.summits import SummitsContainer
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit
from pyprom.tests.getData import gettestzip
from pyprom.domain import Domain
from pyprom.dataload import GDALLoader


class SummitsContainerTests(unittest.TestCase):
    """Test SummitsContainer."""

    def testSummitsContainerBadInitiation(self):
        """
        Ensure creating a SummitsContainer with a list of Saddles fails
        """
        saddles = [Saddle(1, 2, 3)]
        with self.assertRaises(TypeError):
            SummitsContainer(saddles)

    def testSummitsContainerEmptyInitiation(self):
        """
        Ensure creating a SaddlesContainer with an empty list is OK
        """
        container = SummitsContainer([])
        self.assertEqual(len(container.summits), 0)

    def testSummitsContainerGoodInitiation(self):
        """
        Ensure creating a SummitsContainer with a list of Summits succeeds
        """
        summits = [Summit(1, 2, 3)]
        container = SummitsContainer(summits)
        self.assertEqual(len(container), 1)
        self.assertEqual(len(container.summits), 1)

    def testSummitsContainerBadAppend(self):
        """
        Ensure adding Saddle to SummitsContainer fails.
        """
        summits = [Summit(1, 2, 3)]
        container = SummitsContainer(summits)
        with self.assertRaises(TypeError):
            container.append(Saddle(1, 2, 3))

    def testSummitsContainerGoodAppend(self):
        """
        Ensure adding Summit to SummitsContainer succeeds.
        """
        container = SummitsContainer([])
        container.append(Summit(1, 2, 3))

    def testSummitsContainerExtend(self):
        """
        Ensure extending Different child Summits
        to SummitsContainer succeeds.
        """
        container = SummitsContainer([])
        summit = Summit(1, 2, 3)
        container.extend([summit])
        self.assertEqual(container.points, [summit])

    def testSummitsContainerExtendNegative(self):
        """
        Ensure extending invalid child Summits
        to SummitsContainer fails.
        """
        container = SummitsContainer([])
        with self.assertRaises(TypeError):
            container.extend([Saddle(1, 2, 3)])

    def testSummitsContainerGetItem(self):
        """
        Ensure getting item index succeeds.
        """
        summits = [Summit(1, 2, 3)]
        container = SummitsContainer(summits)
        self.assertEqual(container[0], summits[0])

    def testSummitsContainerSetItem(self):
        """
        Ensure setting item index succeeds.
        """
        summits = [Summit(1, 2, 3), Summit(1, 2, 3)]
        summit567 = Summit(5, 6, 7)
        container = SummitsContainer(summits)
        container[1] = summit567
        self.assertEqual(container[1], summit567)

    def testSummitsContainerSetItemNegative(self):
        """
        Ensure setting item index fails when non Summit is passed in.
        """
        summits = [Summit(1, 2, 3), Summit(1, 2, 3)]
        saddle567 = Saddle(5, 6, 7)
        container = SummitsContainer(summits)
        with self.assertRaises(TypeError):
            container[1] = saddle567

    def testSummitsContainerRepr(self):
        """
        Ensure __repr__ yields expected result
        """
        summits = [Summit(1, 2, 3)]
        container = SummitsContainer(summits)
        self.assertEqual(container.__repr__(),
                         "<SummitsContainer> 1 Objects")

    def testSummitsContainerFromDictEdge(self):
        """
        Ensure from_dict() produces expected
        results on a Summit
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = datafile.datamap
        someslice = datamap.subset(0, 0, 30, 30)
        domain = Domain(someslice)
        domain.run()
        summits = domain.summits
        summit = summits[3]
        summitDict = summit.to_dict()
        newSummit = Summit.from_dict(summitDict, datamap=someslice)

        self.assertEqual(newSummit, summit)
        self.assertEqual(newSummit.latitude, summit.latitude)
        self.assertEqual(newSummit.longitude, summit.longitude)
        self.assertEqual(newSummit.elevation, summit.elevation)
        self.assertEqual(newSummit.multipoint, summit.multipoint)
        self.assertEqual(newSummit.edgeEffect, summit.edgeEffect)
        self.assertEqual(newSummit.edgePoints, summit.edgePoints)
        self.assertEqual(newSummit.id, summit.id)

    def testSummitsContainerMultiPoint(self):
        """
        Ensure multipoint() returns all multipoint Summits
        """
        s1 = Summit(1, 1, 1)
        s1.multipoint = ["bogus_but_ok_for_test"]
        s2 = Summit(2, 2, 2)
        container = SummitsContainer([s1, s2])
        self.assertEqual(container.multipoints, [s1])