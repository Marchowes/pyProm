"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.domain import Domain


class DomainTests(unittest.TestCase):
    """Test Logic."""

    def setUp(self):
        """
        Set Up Tests.
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = datafile.datamap
        self.someslice = datamap.subset(0, 0, 30, 30)
        self.domain = Domain(self.someslice)
        self.domain.run()
        self.domain.walk()

    def testDomainFromDict(self):
        """
        Ensure loading dict into :class:`Domain`
        """
        domainDict = self.domain.to_dict(noWalkPath=False)
        newDomain = Domain.from_dict(domainDict, self.someslice)
        self.assertEqual(newDomain.saddles, self.domain.saddles)
        self.assertEqual(newDomain.summits, self.domain.summits)
        self.assertEqual(newDomain.runoffs, self.domain.runoffs)
        self.assertEqual(newDomain.linkers, self.domain.linkers)

    def testDomainFromCbor(self):
        """
        Ensure loading cbor binary into :class:`Domain`
        """
        domainCbor = self.domain.to_cbor(noWalkPath=False)
        newDomain = Domain.from_cbor(domainCbor, self.someslice)
        self.assertEqual(newDomain.saddles, self.domain.saddles)
        self.assertEqual(newDomain.summits, self.domain.summits)
        self.assertEqual(newDomain.runoffs, self.domain.runoffs)
        self.assertEqual(newDomain.linkers, self.domain.linkers)

    def testDomainReadWriteFile(self):
        """
        Ensure loading cbor into :class:`Domain`
        """
        self.domain.write('/tmp/deletemePyPromTest', noWalkPath=False)
        newDomain = Domain.read('/tmp/deletemePyPromTest', self.someslice)
        self.assertEqual(newDomain.saddles, self.domain.saddles)
        self.assertEqual(newDomain.summits, self.domain.summits)
        self.assertEqual(newDomain.runoffs, self.domain.runoffs)
        self.assertEqual(newDomain.linkers, self.domain.linkers)
