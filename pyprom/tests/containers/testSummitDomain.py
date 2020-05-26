"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.domain_map import DomainMap
from pyprom.lib.locations.base_gridpoint import BaseGridPoint
from pyprom.lib.locations.base_coordinate import BaseCoordinate
from pyprom.lib.locations.spot_elevation import SpotElevation
from pyprom.lib.containers.summit_domain import SummitDomain
from pyprom.lib.locations.gridpoint import GridPoint

class SummitsDomainTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set Up Tests."""
        gettestzip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = cls.datafile.datamap
        cls.someslice = cls.datamap.subset(1000, 1000, 100, 100)
        cls.domain = DomainMap(cls.someslice)
        cls.domain.run(superSparse=True, rebuildSaddles=False)
        cls.domain.walk()
        cls.summit_domains = list(cls.domain.summit_domains)
        cls.test_summit_domain = cls.summit_domains[1]

    def copy(self, sd):
        return SummitDomain(sd.datamap, sd.summit, sd.saddles[:], sd.points[:])

    def testSummitDomainMembers(self):
        """
        Ensure members are returned as BaseCoordinates.
        """
        bcs = [x for x in self.test_summit_domain.members if not type(x) == BaseCoordinate]
        self.assertEqual(25, len(self.test_summit_domain.points))
        self.assertEqual([], bcs)

    def testSummitDomainBaseCoordinate(self):
        """
        Ensure members are returned as BaseCoordinates.
        """
        bcs = [x for x in self.test_summit_domain.baseCoordinate() if not type(x) == BaseCoordinate]
        self.assertEqual(25, len(self.test_summit_domain.points))
        self.assertEqual([], bcs)

    def testSummitDomainSpotElevation(self):
        """
        Ensure members are returned as SpotElevations.
        """
        ses = [x for x in self.test_summit_domain.spotElevation() if not type(x) == SpotElevation]
        self.assertEqual(25, len(self.test_summit_domain.points))
        self.assertEqual([], ses)

    def testSummitDomainBaseGridPoint(self):
        """
        Ensure members are returned as BaseGridPoint.
        """
        bgps = [x for x in self.test_summit_domain.baseGridPoint() if not type(x) == BaseGridPoint]
        self.assertEqual(25, len(self.test_summit_domain.points))
        self.assertEqual([], bgps)

    def testSummitDomainGridPoint(self):
        """
        Ensure members are returned as GridPoints.
        """
        gps = [x for x in self.test_summit_domain.gridPoint() if not type(x) == GridPoint]
        self.assertEqual(25, len(self.test_summit_domain.points))
        self.assertEqual([], gps)

    def testSummitDomainAppend(self):
        """
        Ensure append works.
        """
        sd = self.copy(self.test_summit_domain)
        sd.append((1, 1, 1))
        self.assertIn((1, 1, 1), sd.points)

        # make sure external hash works too..
        hash = {2:{2: None}}
        sd.append((2, 2, 2), externalHash=hash)
        self.assertEqual(hash[2][2], sd)

    def testSummitDomainExtend(self):
        """
        Ensure extend works.
        """
        sd = self.copy(self.test_summit_domain)
        sd.extend([(1, 1, 1)])
        self.assertIn((1, 1, 1), sd.points)

        # make sure external hash works too..
        hash = {2:{2: None}}
        sd.extend([(2, 2, 2)], externalHash=hash)
        self.assertEqual(hash[2][2], sd)

    def testSummitDomainRemoveSaddle(self):
        """
        Ensure Saddle removal function works.
        """
        sd = self.copy(self.test_summit_domain)
        self.assertEqual(3, len(sd.saddles))
        doomed = sd.saddles[0]
        sd.remove_saddle(doomed)
        self.assertEqual(2, len(sd.saddles))
        self.assertNotIn(doomed, sd.saddles)

    def testSummitDomainIterateBaseCoordinate(self):
        """
        Ensure IterateBaseCoordinate works as expected.
        """
        for ibc in self.test_summit_domain.iterateBaseCoordinate():
            self.assertEqual(type(ibc), BaseCoordinate)

    def testSummitDomainIterateSpotElevation(self):
        """
        Ensure IterateSpotElevation works as expected.
        """
        for ise in self.test_summit_domain.iterateSpotElevation():
            self.assertEqual(type(ise), SpotElevation)

    def testSummitDomainIterateBaseGridPoint(self):
        """
        Ensure IterateBaseGridPoint works as expected.
        """
        for ibgp in self.test_summit_domain.iterateBaseGridPoint():
            self.assertEqual(type(ibgp), BaseGridPoint)

    def testSummitDomainIterateGridPoint(self):
        """
        Ensure IterateGridPoint works as expected.
        """
        for igp in self.test_summit_domain.iterateGridPoint():
            self.assertEqual(type(igp), GridPoint)

    def testSummitDomainToDict(self):
        """
        Ensure to_dict() works as expected.
        """
        sd = self.summit_domains[0]
        test_dict = sd.to_dict()
        expected = {'points': sd.points,
                    'saddles': [sd.saddles[0].id,
                                sd.saddles[1].id],
                    'summit': sd.summit.id}
        self.assertEqual(test_dict, expected)

    def testSummitDomainFromDict(self):
        """
        Ensure from_dict() works as expected.
        """
        sd = self.summit_domains[0]
        nsd = SummitDomain.from_dict(sd.to_dict(),
                                     self.domain.saddles,
                                     self.domain.summits,
                                     sd.datamap)
        self.assertEqual(nsd.points, sd.points)
        self.assertEqual(nsd.summit, sd.summit)
        self.assertEqual(nsd.saddles, sd.saddles)

    def testSummitDomainShape(self):
        """
        Ensure shape produces expected result.
        """
        wkt = "MULTIPOLYGON (((-71.70333333333333 44.72194444444445," \
              " -71.70333333333333 44.72166666666666, -71.70361111111112" \
              " 44.72166666666666, -71.70361111111112 44.72194444444445," \
              " -71.70333333333333 44.72194444444445)), ((-71.70305555555555" \
              " 44.7213888888889, -71.70305555555555 44.72111111111111," \
              " -71.70333333333333 44.72111111111111, -71.70333333333333" \
              " 44.7213888888889, -71.70333333333333 44.72166666666666," \
              " -71.70305555555555 44.72166666666666, -71.70305555555555" \
              " 44.7213888888889)))"
        sd = self.summit_domains[0]
        self.assertEqual(sd.shape.wkt, wkt)

    def testSummitDomainEq(self):
        """
        Ensure __eq__ works as expected.
        """
        sd = self.copy(self.test_summit_domain)
        self.assertEqual(sd, self.test_summit_domain)

    def testSummitDomainHash(self):
        """
        Ensure __hash__ works as expected. (hash on summit)
        """
        self.assertEqual(self.test_summit_domain.__hash__(),
                         self.test_summit_domain.summit.__hash__())

    def testSummitDomainRepr(self):
        """
        Ensure __repr__ works as expected.
        """
        repr = "<SummitDomain> Of <Summit> lat 44.70930555555556" \
               " long -71.70902777777778 2687.007874015748ft 819.0m" \
               " MultiPoint True - 25 points"
        self.assertEqual(self.test_summit_domain.__repr__(), repr)
