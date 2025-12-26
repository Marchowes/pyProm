"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.containers.runoffs import RunoffsContainer
from pyprom.lib.locations.runoff import Runoff
from pyprom.lib.locations.summit import Summit
from pyprom.domain_map import DomainMap
from pyprom.tests.getData import gettestzip
from pyprom.lib.loaders.gdal_loader import GDALLoader


class RunoffsContainerTests(unittest.TestCase):
    """Test RunoffsContainer."""

    def setUp(self):
        """Set Up Tests."""
        pass

    def testRunoffsContainerBadInitiation(self):
        """
        Ensure creating a RunoffsContainer with a list of Summits fails.
        """
        summits = [Summit(1, 2, 3)]
        with self.assertRaises(TypeError):
            RunoffsContainer(summits)

    def testRunoffsContainerEmptyInitiation(self):
        """
        Ensure creating a RunoffsContainer with an empty list is OK.
        """
        container = RunoffsContainer([])
        self.assertEqual(len(container.saddles), 0)

    def testRunoffsContainerGoodInitiation(self):
        """
        Ensure creating a RunoffsContainer with a list of Summits succeeds.
        """
        runoffs = [Runoff(1, 2, 3)]
        container = RunoffsContainer(runoffs)
        self.assertEqual(len(container), 1)
        self.assertEqual(len(container.saddles), 1)

    def testRunoffsContainerBadAppend(self):
        """
        Ensure appending Summit to RunoffsContainer fails.
        """
        runoffs = [Runoff(1, 2, 3)]
        container = RunoffsContainer(runoffs)
        with self.assertRaises(TypeError):
            container.append(Summit(1, 2, 3))

    def testRunoffsContainerGoodAppend(self):
        """
        Ensure adding Runoff to RunoffsContainer succeeds.
        """
        container = RunoffsContainer([])
        container.append(Runoff(1, 2, 3))

    def testRunoffsContainerExtend(self):
        """
        Ensure extending Different child Runoffs
        to RunoffsContainer succeeds.
        """
        container = RunoffsContainer([])
        runoff = Runoff(1, 2, 3)
        container.extend([runoff])
        self.assertEqual(container.points, [runoff])

    def testRunoffsContainerExtendNegative(self):
        """
        Ensure extending invalid child Runoffs
        to RunoffsContainer fails.
        """
        container = RunoffsContainer([])
        with self.assertRaises(TypeError):
            container.extend([Summit(1, 2, 3)])

    def testRunoffsContainerGetItem(self):
        """
        Ensure getting item index succeeds.
        """
        runoffs = [Runoff(1, 2, 3)]
        container = RunoffsContainer(runoffs)
        self.assertEqual(container[0], runoffs[0])

    def testRunoffsContainerSetItem(self):
        """
        Ensure setting item index succeeds.
        """
        runoffs = [Runoff(1, 2, 3), Runoff(1, 2, 3)]
        runoff567 = Runoff(5, 6, 7)
        container = RunoffsContainer(runoffs)
        container[1] = runoff567
        self.assertEqual(container[1], runoff567)

    def testRunoffsContainerSetItemNegative(self):
        """
        Ensure setting item index fails when non Runoff is passed in.
        """
        runoffs = [Runoff(1, 2, 3), Runoff(1, 2, 3)]
        summit567 = Summit(5, 6, 7)
        container = RunoffsContainer(runoffs)
        with self.assertRaises(TypeError):
            container[1] = summit567

    def testRunoffsContainerRepr(self):
        """
        Ensure __repr__ yields expected result.
        """
        runoffs = [Runoff(1, 2, 3)]
        container = RunoffsContainer(runoffs)
        self.assertEqual(container.__repr__(),
                         "<RunoffsContainer> 1 Objects")

    def testSaddlesContainerFromDictAll(self):
        """
        Ensure from_dict() produces expected results
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = datafile.to_datamap()
        someslice = datamap.subset(0, 0, 30, 30)
        domain = DomainMap(someslice)
        domain.run()
        runoffs = domain.runoffs
        runoffsDict = runoffs.to_dict()
        newRunoffs = RunoffsContainer.from_dict(runoffsDict, datamap=someslice)
        self.assertEqual(newRunoffs, runoffs)
