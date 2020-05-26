"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""
import unittest

from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader

from pyprom.domain_map import DomainMap
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit
from pyprom.lib.containers.linker import Linker
from pyprom.lib.locations.spot_elevation import SpotElevation
from pyprom.lib.locations.runoff import Runoff
from pyprom.lib.containers.runoffs import RunoffsContainer
from pyprom.lib.containers.saddles import SaddlesContainer
from pyprom.lib.containers.summits import SummitsContainer
from pyprom.lib.containers.summit_domain import SummitDomain
from pyprom.lib.containers.spot_elevation import SpotElevationContainer

from pyprom.lib.kmlwriter import KMLFileWriter


class KMLFileWriterTest(unittest.TestCase):
    """KMLFileWriterTest tests the KMLFileWriter"""

    def setUp(self):
        """Set Up."""
        self.saddle1 = Saddle(1, 1, 100)
        self.saddle2 = Saddle(2, 2, 200)
        self.summit1 = Summit(1, 1, 100)
        self.summit2 = Summit(2, 2, 200)
        self.runoff1 = Runoff(1, 1, 100)
        self.runoff2 = Runoff(2, 2, 200)
        self.spotelevation1 = SpotElevation(1, 1, 100)
        self.spotelevation2 = SpotElevation(2, 2, 200)
        self.linker1 = Linker(self.summit1, self.saddle1)
        self.linker2 = Linker(self.summit2, self.saddle2)

        self.saddlescontainer = SaddlesContainer([self.saddle1, self.saddle2])
        self.summitscontainer = SummitsContainer([self.summit1, self.summit2])
        self.runoffscontainer = RunoffsContainer([self.runoff1, self.runoff2])
        self.spotelevationcontainer =\
            SpotElevationContainer([self.spotelevation1, self.spotelevation2])
        self.kfw = KMLFileWriter("someFile.kml", documentName="myDocument")

    def testDomainAppendKML(self):
        """
        Ensure Appending a single :class:`DomainMap` object works as expected.
        """
        gettestzip()
        domain = DomainMap(GDALLoader('/tmp/N44W072.hgt'), self.summitscontainer,
                           self.saddlescontainer, self.runoffscontainer, [],
                           [self.linker1])
        summit_domain1 = SummitDomain(domain.datamap,
                                           self.summit1,
                                           self.saddle1,
                                           [(1, 1, 1)])
        domain.summit_domains = [summit_domain1]
        self.kfw.append(domain)
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (2 2)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (2 2)'])
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (2 2)'])
        self.assertTrue(self.kfw.linkers_wkt['LINESTRING (1 1, 1 1)'])
        # We dont track summitDomains in a hash
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 6)
        self.assertEqual(len(self.kfw.linkers_wkt.items()), 1)
        self.assertEqual(len(self.kfw.linkers._features), 1)
        self.assertEqual(len(self.kfw.saddles._features), 2)
        self.assertEqual(len(self.kfw.summits._features), 2)
        self.assertEqual(len(self.kfw.runoffs._features), 2)
        self.assertEqual(len(self.kfw.summitDomains._features), 1)

    def testSaddlesAppendKML(self):
        """
        Ensure Appending a single :class:`Saddle` object works as expected.
        """
        self.kfw.append(self.saddle1)
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (1 1)'])
        self.kfw.append(self.saddle2)
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.saddles._features), 2)

    def testSaddlesAppendSameKML(self):
        """
        Ensure Appending a single same :class:`Saddle` object yields
        only one saddle entry
        """
        self.kfw.append(self.saddle1)
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (1 1)'])
        self.kfw.append(self.saddle1)
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 1)
        self.assertEqual(len(self.kfw.saddles._features), 1)

    def testSaddleContainerAppendKML(self):
        """
        Ensure Appending a single :class:`SaddlesContainer` object works
        as expected.
        """
        self.kfw.append(self.saddlescontainer)
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.saddles._features), 2)

    def testSaddleExtendKML(self):
        """
        Ensure Extending two :class:`Saddle` objects works
        as expected.
        """
        self.kfw.extend([self.saddle1, self.saddle2])
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.saddles._features), 2)

    def testSaddleContainerExtendKML(self):
        """
        Ensure Extending a single :class:`SaddlesContainer` object works
        as expected.
        """
        self.kfw.extend(self.saddlescontainer)
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.saddles._features), 2)

    def testSummitsAppendKML(self):
        """
        Ensure Appending a single :class:`Summit` object works as expected.
        """
        self.kfw.append(self.summit1)
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (1 1)'])
        self.kfw.append(self.summit2)
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.summits._features), 2)

    def testSummitsAppendSameKML(self):
        """
        Ensure Appending a single same :class:`Summit` object yields
        only one summit entry
        """
        self.kfw.append(self.summit1)
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (1 1)'])
        self.kfw.append(self.summit1)
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 1)
        self.assertEqual(len(self.kfw.summits._features), 1)

    def testSummitsContainerAppendKML(self):
        """
        Ensure Appending a single :class:`SummitsContainer` object works
        as expected.
        """
        self.kfw.append(self.summitscontainer)
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.summits._features), 2)

    def testSummitExtendKML(self):
        """
        Ensure Extending two :class:`Summit` objects works
        as expected.
        """
        self.kfw.extend(self.summitscontainer)
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.summits._features), 2)

    def testSummitsContainerExtendKML(self):
        """
        Ensure Extending a single :class:`SummitsContainer` object works
        as expected.
        """
        self.kfw.extend(self.summitscontainer)
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.summits._features), 2)

    def testRunoffsAppendKML(self):
        """
        Ensure Appending a single :class:`Runoff` object works as expected.
        """
        self.kfw.append(self.runoff1)
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (1 1)'])
        self.kfw.append(self.runoff2)
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.runoffs._features), 2)

    def testRunoffsAppendSameKML(self):
        """
        Ensure Appending a single same:class:`Runoff` object yields only
        one runoff entry
        """
        self.kfw.append(self.runoff1)
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (1 1)'])
        self.kfw.append(self.runoff1)
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 1)
        self.assertEqual(len(self.kfw.runoffs._features), 1)

    def testRunoffsContainerAppendKML(self):
        """
        Ensure Appending a single :class:`RunoffsContainer` object works
        as expected.
        """
        self.kfw.append(self.runoffscontainer)
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.runoffs._features), 2)

    def testRunoffsExtendKML(self):
        """
        Ensure Extending two :class:`Runoff` objects works
        as expected.
        """
        self.kfw.extend([self.runoff1, self.runoff2])
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.runoffs._features), 2)

    def testRunoffsContainerExtendKML(self):
        """
        Ensure Extending a single :class:`RunoffsContainer` object works
        as expected.
        """
        self.kfw.extend(self.runoffscontainer)
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.runoffs._features), 2)

    def testSpotElevationAppendKML(self):
        """
        Ensure Appending a single :class:`SpotElevation` object
        works as expected.
        """
        self.kfw.append(self.spotelevation1)
        self.assertTrue(self.kfw.spotElevation_wkt['SpotElevationPOINT (1 1)'])
        self.kfw.append(self.spotelevation2)
        self.assertTrue(self.kfw.spotElevation_wkt['SpotElevationPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.spotElevations._features), 2)

    def testSpotElevationAppendSameKML(self):
        """
        Ensure Appending a single same :class:`SpotElevation` object
        yields only one Spot Elevation entry
        """
        self.kfw.append(self.spotelevation1)
        self.assertTrue(self.kfw.spotElevation_wkt['SpotElevationPOINT (1 1)'])
        self.kfw.append(self.spotelevation1)
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 1)
        self.assertEqual(len(self.kfw.spotElevations._features), 1)

    def testSpotElevationContainerAppendKML(self):
        """
        Ensure Appending a single :class:`SpotElevationContainer` object
        works as expected.
        """
        self.kfw.append(self.spotelevationcontainer)
        self.assertTrue(self.kfw.spotElevation_wkt['SpotElevationPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SpotElevationPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.spotElevations._features), 2)

    def testSpotElevationExtendKML(self):
        """
        Ensure Extend two :class:`SpotElevation` objects
        works as expected.
        """
        self.kfw.extend([self.spotelevation1, self.spotelevation2])
        self.assertTrue(self.kfw.spotElevation_wkt['SpotElevationPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SpotElevationPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.spotElevations._features), 2)

    def testSpotElevationContainerExtendKML(self):
        """
        Ensure Extend a single :class:`SpotElevationContainer` object
        works as expected.
        """
        self.kfw.extend(self.spotelevationcontainer)
        self.assertTrue(self.kfw.spotElevation_wkt['SpotElevationPOINT (1 1)'])
        self.assertTrue(self.kfw.spotElevation_wkt['SpotElevationPOINT (2 2)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(self.kfw.spotElevations._features), 2)

    def testLinkersAppendKML(self):
        """
        Ensure Appending a single :class:`Linker` object works as expected.
        """
        self.kfw.append(self.linker1)
        self.assertTrue(self.kfw.linkers_wkt['LINESTRING (1 1, 1 1)'])
        self.kfw.append(self.linker2)
        self.assertTrue(self.kfw.linkers_wkt['LINESTRING (2 2, 2 2)'])
        self.assertEqual(len(self.kfw.linkers_wkt.items()), 2)
        self.assertEqual(len(self.kfw.linkers._features), 2)

    def testLinkersAppendSameKML(self):
        """
        Ensure Appending a single same :class:`Linker`
        object works as expected.
        """
        self.kfw.append(self.linker1)
        self.assertTrue(self.kfw.linkers_wkt['LINESTRING (1 1, 1 1)'])
        self.kfw.append(self.linker1)
        self.assertEqual(len(self.kfw.linkers_wkt.items()), 1)
        self.assertEqual(len(self.kfw.linkers._features), 1)

    def testLinkersExtendKML(self):
        """
        Ensure Extend two :class:`Linker` objects works as expected.
        """
        self.kfw.extend([self.linker1, self.linker2])
        self.assertTrue(self.kfw.linkers_wkt['LINESTRING (1 1, 1 1)'])
        self.assertTrue(self.kfw.linkers_wkt['LINESTRING (2 2, 2 2)'])
        self.assertEqual(len(self.kfw.linkers_wkt.items()), 2)
        self.assertEqual(len(self.kfw.linkers._features), 2)

    def testSameLocationDifferentTypeAppendKML(self):
        """
        Ensure same locations of a differing type are added
        """
        self.kfw.append(self.saddle1)
        self.assertTrue(self.kfw.spotElevation_wkt['SaddlePOINT (1 1)'])
        self.kfw.append(self.summit1)
        self.assertTrue(self.kfw.spotElevation_wkt['SummitPOINT (1 1)'])
        self.kfw.append(self.runoff1)
        self.assertTrue(self.kfw.spotElevation_wkt['RunOffPOINT (1 1)'])
        self.kfw.append(self.spotelevation1)
        self.assertTrue(self.kfw.spotElevation_wkt['SpotElevationPOINT (1 1)'])
        self.assertEqual(len(self.kfw.spotElevation_wkt.items()), 4)
        self.assertEqual(len(self.kfw.spotElevations._features), 1)
        self.assertEqual(len(self.kfw.saddles._features), 1)
        self.assertEqual(len(self.kfw.summits._features), 1)
        self.assertEqual(len(self.kfw.runoffs._features), 1)

    def testCreateWithListOfLocations(self):
        """
        Create KMLFileWriter with single objects
        """
        kfw = KMLFileWriter("someFile.kml",
                            documentName="myDocument",
                            features=[self.saddle1,
                                      self.summit1])
        self.assertTrue(kfw.spotElevation_wkt['SaddlePOINT (1 1)'])
        self.assertTrue(kfw.spotElevation_wkt['SummitPOINT (1 1)'])
        self.assertEqual(len(kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(kfw.summits._features), 1)
        self.assertEqual(len(kfw.saddles._features), 1)

    def testCreateWithSingleContainer(self):
        """
        Create KMLFileWriter with single container
        """
        kfw = KMLFileWriter("someFile.kml",
                            documentName="myDocument",
                            features=self.saddlescontainer)
        self.assertTrue(kfw.spotElevation_wkt['SaddlePOINT (1 1)'])
        self.assertTrue(kfw.spotElevation_wkt['SaddlePOINT (2 2)'])
        self.assertEqual(len(kfw.spotElevation_wkt.items()), 2)
        self.assertEqual(len(kfw.saddles._features), 2)

    def testCreateWithContainersAndLocations(self):
        """
        Create KMLFileWriter with containers and locations
        """
        kfw = KMLFileWriter("someFile.kml",
                            documentName="myDocument",
                            features=[self.saddlescontainer, self.summit1])
        self.assertTrue(kfw.spotElevation_wkt['SaddlePOINT (1 1)'])
        self.assertTrue(kfw.spotElevation_wkt['SaddlePOINT (2 2)'])
        self.assertTrue(kfw.spotElevation_wkt['SummitPOINT (1 1)'])
        self.assertEqual(len(kfw.spotElevation_wkt.items()), 3)
        self.assertEqual(len(kfw.saddles._features), 2)
        self.assertEqual(len(kfw.summits._features), 1)

    def testRaisesErrorOnInvalidElement(self):
        """
        Create KMLFileWriter with containers and locations
        """
        with self.assertRaises(Exception):
            self.kfw.append(dict())
