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
        domainDict = self.domain.to_dict()
        newDomain = Domain.from_dict(domainDict, self.someslice)
        self.assertEqual(newDomain.saddles, self.domain.saddles)
        self.assertEqual(newDomain.summits, self.domain.summits)
        self.assertEqual(newDomain.runoffs, self.domain.runoffs)
        self.assertEqual(newDomain.linkers, self.domain.linkers)

    def testDomainFromJson(self):
        """
        Ensure loading json into :class:`Domain`
        """
        domainJSON = self.domain.to_json()
        newDomain = Domain.from_json(domainJSON, self.someslice)
        self.assertEqual(newDomain.saddles, self.domain.saddles)
        self.assertEqual(newDomain.summits, self.domain.summits)
        self.assertEqual(newDomain.runoffs, self.domain.runoffs)
        self.assertEqual(newDomain.linkers, self.domain.linkers)

    def testDomainreadWriteFile(self):
        """
        Ensure loading json into :class:`Domain`
        """
        self.domain.write('/tmp/deletemePyPromTest')
        newDomain = Domain.read('/tmp/deletemePyPromTest', self.someslice)
        self.assertEqual(newDomain.saddles, self.domain.saddles)
        self.assertEqual(newDomain.summits, self.domain.summits)
        self.assertEqual(newDomain.runoffs, self.domain.runoffs)
        self.assertEqual(newDomain.linkers, self.domain.linkers)