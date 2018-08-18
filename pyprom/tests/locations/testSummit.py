"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest

from pyprom.tests.getData import gettestzip
from pyprom.domain import Domain
from pyprom.dataload import GDALLoader
from pyprom.lib.locations.summit import Summit


class SummitTests(unittest.TestCase):
    """Test Summit."""

    def testSummitsFromDictEdge(self):
        """
        Ensure from_dict() produces expected
        results on a saddle which has a child.
        """
        gettestzip()
        datafile = GDALLoader('/tmp/N44W072.hgt')
        datamap = datafile.datamap
        someslice = datamap.subset(0, 0, 30, 30)
        domain = Domain(someslice)
        domain.run()
        domain.walk()
        summits = domain.summits
        summit = summits[3]
        summitDict = summit.to_dict()
        newSummit = Summit.from_dict(summitDict, datamap=someslice)

        self.assertEqual(newSummit, summit)
        self.assertEqual(newSummit.latitude, summit.latitude)
        self.assertEqual(newSummit.longitude, summit.longitude)
        self.assertEqual(newSummit.elevation, summit.elevation)
        self.assertEqual(newSummit.multiPoint, summit.multiPoint)
        self.assertEqual(newSummit.edgeEffect, summit.edgeEffect)
        self.assertEqual(newSummit.edgePoints, summit.edgePoints)
        self.assertEqual(newSummit.id, summit.id)