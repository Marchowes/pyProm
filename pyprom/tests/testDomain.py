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
    """Test Domain."""

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
        self.assertEqual(newDomain.summit_domains, self.domain.summit_domains)

    def testDomainFromCbor(self):
        """
        Ensure loading cbor binary into :class:`Domain`
        """
        domainCbor = self.domain.to_cbor()
        newDomain = Domain.from_cbor(domainCbor, self.someslice)
        self.assertEqual(newDomain.saddles, self.domain.saddles)
        self.assertEqual(newDomain.summits, self.domain.summits)
        self.assertEqual(newDomain.runoffs, self.domain.runoffs)
        self.assertEqual(newDomain.linkers, self.domain.linkers)
        self.assertEqual(newDomain.summit_domains, self.domain.summit_domains)

    def testDomainReadWriteFile(self):
        """
        Ensure loading cbor into :class:`Domain`
        """
        self.domain.write('/tmp/deletemePyPromTest.dom')
        newDomain = Domain.read('/tmp/deletemePyPromTest.dom', self.someslice)
        self.assertEqual(newDomain.saddles, self.domain.saddles)
        self.assertEqual(newDomain.summits, self.domain.summits)
        self.assertEqual(newDomain.runoffs, self.domain.runoffs)
        self.assertEqual(newDomain.linkers, self.domain.linkers)

    def testDomainReadWriteFileSuffix(self):
        """
        Ensure loading cbor into :class:`Domain`
        Ensure dom suffix is appended.
        """
        self.domain.write('/tmp/deletemePyPromTest')
        newDomain = Domain.read('/tmp/deletemePyPromTest.dom', self.someslice)
        self.assertEqual(newDomain.saddles, self.domain.saddles)
        self.assertEqual(newDomain.summits, self.domain.summits)
        self.assertEqual(newDomain.runoffs, self.domain.runoffs)
        self.assertEqual(newDomain.linkers, self.domain.linkers)

    def testDomainCullingSingleSummits(self):
        """
        Ensure single Summit culling works.
        9 Disqualified
        6 Single Summit
        3 Basin Saddles
        -- 1 Basin Saddle with basinSaddleAlternative
        -- 2 Lone Basin Saddle
        Results:
                3 Basin Saddles should remain.
        """
        # alter some Saddles.
        self.domain.saddles[0].basinSaddle = True
        self.domain.saddles[0].basinSaddleAlternatives = [self.domain.saddles[2]]
        self.domain.saddles[11].basinSaddle = True
        self.domain.saddles[12].basinSaddle = True
        self.domain.saddles.disqualified[0].singleSummit = True # basin, dqed, single
        self.domain.saddles.disqualified[1].singleSummit = True # parent, dqed, single

        # Make sure we've got 9 Saddles to start with
        self.assertEqual(len(self.domain.saddles.disqualified), 9)
        self.assertEqual(len(self.domain.saddles), 20)
        parent = self.domain.saddles.disqualified[1]
        child = self.domain.saddles.disqualified[0]
        self.assertEqual(child.parent, parent)
        self.assertEqual(len(parent.children), 1)
        self.assertEqual(child, parent.children[0])
        self.domain.purge_saddles(singleSummit=True,
                                  basinSaddle=False)
        # Make sure 7 DQ saddle remains, 18 overall
        self.assertEqual(len(self.domain.saddles.disqualified), 7)
        self.assertEqual(len(self.domain.saddles), 18)
        self.assertEqual(child.parent, None)
        self.assertEqual(parent.children, [])
        self.assertTrue(child.summits[0].disqualified) # ensure link dqed
        self.assertEqual(parent.summits, []) # never was linked.

    def testDomainCullingNonAlternateBasinSaddle(self):
        """
        Ensure single Summit culling works.
        9 Disqualified
        6 Single Summit
        3 Basin Saddles
        -- 1 Basin Saddle with basinSaddleAlternative
        -- 2 Lone Basin Saddle
        Results:
                6 Single Summit should remain, 1 Basin with Alternate
                should remain
        """
        # alter some Saddles.
        self.domain.saddles[0].basinSaddle = True
        self.domain.saddles[0].basinSaddleAlternatives =\
            [self.domain.saddles[2]]
        self.domain.saddles[11].basinSaddle = True
        self.domain.saddles[12].basinSaddle = True

        # Make sure we've got 9 Saddles to start with
        self.assertEqual(len(self.domain.saddles.disqualified), 9)
        self.assertEqual(len(self.domain.saddles), 20)
        self.domain.purge_saddles(singleSummit=False,
                                  basinSaddle=True)
        # Make sure 7 saddle remains
        self.assertEqual(len(self.domain.saddles.disqualified), 7)
        self.assertEqual(len(self.domain.saddles), 18)

    def testDomainCullingAllBasinSaddle(self):
        """
        Ensure single Summit culling works.
        9 Disqualified
        6 Single Summit
        3 Basin Saddles
        -- 1 Basin Saddle with basinSaddleAlternative
        -- 2 Lone Basin Saddle
        Results:
                6 Single Summit should remain.
        """
        # alter some Saddles.
        self.domain.saddles[0].basinSaddle = True
        self.domain.saddles[0].basinSaddleAlternatives =\
            [self.domain.saddles[2]]
        self.domain.saddles[11].basinSaddle = True
        self.domain.saddles[12].basinSaddle = True

        # Make sure we've got 9 Saddles to start with
        self.assertEqual(len(self.domain.saddles.disqualified), 9)
        self.assertEqual(len(self.domain.saddles), 20)
        self.domain.purge_saddles(singleSummit=False,
                                  basinSaddle=False,
                                  allBasinSaddles=True)
        # Make sure 6 saddle remains
        self.assertEqual(len(self.domain.saddles.disqualified), 6)
        self.assertEqual(len(self.domain.saddles), 17)

    def testDomainCullingDefault(self):
        """
        Ensure single Summit culling works.
        9 Disqualified
        2 Single Summit
        3 Basin Saddles
        -- 1 Basin Saddle with basinSaddleAlternative
        -- 2 Lone Basin Saddle
        Results:
                1 Basin with Alternate should remain
        """
        # alter some Saddles.
        self.domain.saddles[0].basinSaddle = True
        self.domain.saddles[0].basinSaddleAlternatives =\
            [self.domain.saddles[2]]
        self.domain.saddles[11].basinSaddle = True
        self.domain.saddles[12].basinSaddle = True
        self.domain.saddles.disqualified[1].singleSummit = True
        self.domain.saddles.disqualified[2].singleSummit = True

        # Make sure we've got 9 Saddles to start with
        self.assertEqual(len(self.domain.saddles.disqualified), 9)
        self.assertEqual(len(self.domain.saddles), 20)
        self.domain.purge_saddles()
        # Make sure 5 dq saddle remains
        self.assertEqual(len(self.domain.saddles.disqualified), 5)
        # 1 with BSA
        self.assertEqual(len([x for x in self.domain.saddles.disqualified if x.basinSaddleAlternatives]), 1)
        self.assertEqual(len(self.domain.saddles), 16)