"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit
from pyprom.lib.containers.linker import Linker
from pyprom.lib.containers.walkpath import WalkPath
from pyprom.lib.containers.saddles import SaddlesContainer
from pyprom.lib.containers.summits import SummitsContainer


class LinkerTests(unittest.TestCase):
    """Test Linker Containers."""

    def setUp(self):
        """Set Up Tests.
        In practice, a Saddle will never have more than 2 Linkers
        (Summits) but the objects themselves do support such a thing
        and we can exploit that for testing.

        Master Topology

        |---[disqualifiedLinker1] (DEAD) -- DisqualifiedSaddle (DEAD)
        |
        Summit1--[linker1]--Saddle1
        |
        |---[linker2]--Saddle2--[linker3]--Summit2
                          |
            [disqualifiedLinkerLocallyDeadSummit] (DEAD)
                          |
                     locallyDeadSummit
        """
        self.summit1 = Summit(1, 1, 1000)
        self.saddle1 = Saddle(5, 5, 100)
        self.summit2 = Summit(10, 10, 1000)
        self.saddle2 = Saddle(15, 15, 100)

        self.disqualifiedSaddle1 = Saddle(100, 100, 1000)
        self.disqualifiedSaddle1.disqualified = True

        self.locallyDeadSummit = Summit(100, 100, 1000)

        self.path1 = WalkPath([(0, 0), (0, 1), (0, 2)])

        self.linker1 = Linker(self.summit1, self.saddle1, self.path1)
        self.linker2 = Linker(self.summit1, self.saddle2, self.path1)
        self.linker3 = Linker(self.summit2, self.saddle2, self.path1)

        self.disqualifiedLinker1 = Linker(
            self.summit1, self.disqualifiedSaddle1, self.path1)
        self.disqualifiedLinker1.disqualified = True

        self.disqualifiedLinkerLocallyDeadSummit = Linker(
            self.locallyDeadSummit, self.saddle2, self.path1)
        self.disqualifiedLinkerLocallyDeadSummit.disqualified = True

        self.summit1.saddles = [self.linker1, self.linker2,
                                self.disqualifiedLinker1]
        self.summit2.saddles = [self.linker3]
        self.locallyDeadSummit.saddles = [
            self.disqualifiedLinkerLocallyDeadSummit]

        self.saddle1.summits = [self.linker1]
        self.saddle2.summits = [self.linker2, self.linker3,
                                self.disqualifiedLinkerLocallyDeadSummit]
        self.disqualifiedLinker1.summits = [self.disqualifiedLinker1]

    def testLinkerProminence(self):
        """
        Ensure prominence calculations are as expected
        """
        self.assertEqual(self.linker1.prom, 900)

    def testLinkerProminenceFeet(self):
        """
        Ensure foot prominence calculation are as expected
        """
        self.assertEqual(self.linker1.prom_ft, 2952.755905511811)

    def testLinkerSaddlesConnectedViaSummit(self):
        """
        Ensure Saddles Connected Via Summit returns expected results when
        skipDisqualified = True (default)
        exemptLinkers = {} (default)
        """
        result = self.linker1.saddles_connected_via_summit()
        self.assertEqual(len(result), 2)
        self.assertIn(self.saddle1, result)
        self.assertIn(self.saddle2, result)

    def testLinkerSaddlesConnectedViaSummitSelfExempt(self):
        """
        Ensure Saddles Connected Via Summit returns expected results when
        skipDisqualified = True (default)
        exemptLinkers = {self.id: True}
        """
        result = self.linker1.saddles_connected_via_summit(
            exemptLinkers={self.linker1.id: True})
        self.assertEqual(len(result), 0)

    def testLinkerSaddlesConnectedViaSummitSkipDisqualifiedFalse(self):
        """
        Ensure Saddles Connected Via Summit returns expected results when
        skipDisqualified = False
        exemptLinkers = {} (default)
        """
        result = self.linker1.saddles_connected_via_summit(
            skipDisqualified=False)
        self.assertEqual(len(result), 3)
        self.assertIn(self.saddle1, result)
        self.assertIn(self.saddle2, result)
        self.assertIn(self.disqualifiedSaddle1, result)

    def testLinkerSaddlesConnectedViaSummitSelfDisqualified(self):
        """
        Ensure Saddles Connected Via Summit returns expected results when
        skipDisqualified = True (default)
        exemptLinkers = {} (default)
        and self.linker1.disqualified = True
        """
        self.linker1.disqualified = True
        result = self.linker1.saddles_connected_via_summit()
        self.assertEqual(len(result), 0)

    def testLinkerSaddlesConnectedViaSmtSlfDsqlfidSkpDsqalfidFls(self):
        """
        Ensure Saddles Connected Via Summit returns expected results when
        skipDisqualified = False
        exemptLinkers = {} (default)
        and self.linker1.disqualified = True
        """
        self.linker1.disqualified = True
        result = self.linker1.saddles_connected_via_summit(
            skipDisqualified=False)
        self.assertEqual(len(result), 3)
        self.assertIn(self.saddle1, result)
        self.assertIn(self.saddle2, result)
        self.assertIn(self.disqualifiedSaddle1, result)

    def testLinkerSaddlesCnectdViaSmtWthExmptnAnSkpDsqlfd(self):
        """
        Ensure Saddles Connected Via Summit returns expected results when
        skipDisqualified = True (default)
        exemptLinkers = {linkerNew.id: True}
        """
        saddleNew = Saddle(1, 2, 3)
        linkerNew = Linker(self.summit1, saddleNew, self.path1)
        saddleNew.summits = [linkerNew]
        self.summit1.saddles.append(linkerNew)

        # ensure we get all 3, minus the Disqualified one.
        result = self.linker1.saddles_connected_via_summit()
        self.assertEqual(len(result), 3)
        self.assertIn(self.saddle1, result)
        self.assertIn(self.saddle2, result)
        self.assertIn(saddleNew, result)

        # exempt our new linker.
        exemptLinker = {linkerNew.id: True}
        result = self.linker1.saddles_connected_via_summit(
            exemptLinkers=exemptLinker)
        self.assertEqual(len(result), 2)
        self.assertIn(self.saddle1, result)
        self.assertIn(self.saddle2, result)

    def testLinkerSaddlesCnectedVaSmtWthExmptnBtNSkipDsqlfed(self):
        """
        Ensure Saddles Connected Via Summit returns expected results when
        skipDisqualified = False
        exemptLinkers = {linkerNew.id: True}
        """
        saddleNew = Saddle(1, 2, 3)
        linkerNew = Linker(self.summit1, saddleNew, self.path1)
        saddleNew.summits = [linkerNew]
        self.summit1.saddles.append(linkerNew)

        # ensure we get all 4.
        result = self.linker1.saddles_connected_via_summit(
            skipDisqualified=False)
        self.assertEqual(len(result), 4)
        self.assertIn(self.saddle1, result)
        self.assertIn(self.saddle2, result)
        self.assertIn(self.disqualifiedSaddle1, result)
        self.assertIn(saddleNew, result)

        # exempt our new linker.
        exemptLinker = {linkerNew.id: True}
        result = self.linker1.saddles_connected_via_summit(
            exemptLinkers=exemptLinker,
            skipDisqualified=False)
        self.assertEqual(len(result), 3)
        self.assertIn(self.saddle1, result)
        self.assertIn(self.saddle2, result)
        self.assertIn(self.disqualifiedSaddle1, result)

    def testLinkerSummitsConnectedViaSaddle(self):
        """
        Ensure Summits Connected Via Saddle returns expected results when
        skipDisqualified = True (default)
        exemptLinkers = {} (default)
        """
        result = self.linker2.summits_connected_via_saddle()
        self.assertEqual(len(result), 2)
        self.assertIn(self.summit1, result)
        self.assertIn(self.summit2, result)

    def testLinkerSummitsConnectedViaSaddleSelfExempt(self):
        """
        Ensure Summits Connected Via Saddle returns expected results when
        skipDisqualified = True (default)
        exemptLinkers = {self.id: True}
        """
        result = self.linker3.summits_connected_via_saddle(
            exemptLinkers={self.linker3.id: True})
        self.assertEqual(len(result), 0)

    def testLinkerSummitsConnectedViaSaddleSkipDisqualifiedFalse(self):
        """
        Ensure Summits Connected Via Saddle returns expected results when
        skipDisqualified = False
        exemptLinkers = {} (default)
        """
        result = self.linker2.summits_connected_via_saddle(
            skipDisqualified=False)
        self.assertEqual(len(result), 3)
        self.assertIn(self.summit1, result)
        self.assertIn(self.summit2, result)
        self.assertIn(self.locallyDeadSummit, result)

    def testLinkerSummitsConnectedViaSaddleSelfDisqualified(self):
        """
        Ensure Summits Connected Via Saddle returns expected results when
        skipDisqualified = True (default)
        exemptLinkers = {} (default)
        and self.linker1.disqualified = True
        """
        self.linker1.disqualified = True
        result = self.linker1.summits_connected_via_saddle()
        self.assertEqual(len(result), 0)

    def testLinkerSummitsConnectedViaSaddleSelfDsqlfdSkpDsqlfedFse(self):
        """
        Ensure Summits Connected Via Saddle returns expected results when
        skipDisqualified = False
        exemptLinkers = {} (default)
        and self.linker1.disqualified = True
        """
        self.linker2.disqualified = True
        result = self.linker2.summits_connected_via_saddle(
            skipDisqualified=False)
        self.assertEqual(len(result), 3)
        self.assertIn(self.summit1, result)
        self.assertIn(self.summit2, result)
        self.assertIn(self.locallyDeadSummit, result)

    def testLinkerSummitsConnectedViaSdleWthExmptnAnSkpDqalfed(self):
        """
        Ensure Summits Connected Via Saddle returns expected results when
        skipDisqualified = True (default)
        exemptLinkers = {linkerNew.id: True}
        """
        summitNew = Summit(1, 2, 3)
        linkerNew = Linker(summitNew, self.saddle2, self.path1)
        self.saddle2.summits.append(linkerNew)
        summitNew.saddles.append(linkerNew)

        # ensure we get all 3, minus the Disqualified one.
        result = self.linker2.summits_connected_via_saddle()
        self.assertEqual(len(result), 3)
        self.assertIn(self.summit1, result)
        self.assertIn(self.summit2, result)
        self.assertIn(summitNew, result)

        # exempt our new linker.
        exemptLinker = {linkerNew.id: True}
        result = self.linker2.summits_connected_via_saddle(
            exemptLinkers=exemptLinker)
        self.assertEqual(len(result), 2)
        self.assertIn(self.summit1, result)
        self.assertIn(self.summit2, result)

    def testLinkerSummitsCnnctdSaddleWhExemnBtNSkpDsqalfid(self):
        """
        Ensure Summits Connected Via Saddle returns expected results when
        skipDisqualified = False
        exemptLinkers = {linkerNew.id: True}
        """
        summitNew = Summit(1, 2, 3)
        linkerNew = Linker(summitNew, self.saddle2, self.path1)
        self.saddle2.summits.append(linkerNew)
        summitNew.saddles.append(linkerNew)

        # ensure we get all 4.
        result = self.linker2.summits_connected_via_saddle(
            skipDisqualified=False)
        self.assertEqual(len(result), 4)
        self.assertIn(self.summit1, result)
        self.assertIn(self.summit2, result)
        self.assertIn(summitNew, result)
        self.assertIn(self.locallyDeadSummit, result)

        # exempt our new linker.
        exemptLinker = {linkerNew.id: True}
        result = self.linker2.summits_connected_via_saddle(
            skipDisqualified=False,
            exemptLinkers=exemptLinker)
        self.assertEqual(len(result), 3)
        self.assertIn(self.summit1, result)
        self.assertIn(self.summit2, result)
        self.assertIn(self.locallyDeadSummit, result)

    def testLinkerLinkersToSaddlesConnectedViaSummit(self):
        """
        Ensure Linkers to Saddles Connected Via Summit returns expected
        results when:
        skipDisqualified = True (default)
        excludeSelf = True (default)
        """
        result = self.linker1.linkers_to_saddles_connected_via_summit()
        self.assertEqual(len(result), 1)
        self.assertIn(self.linker2, result)

    def testLinkerLinkersToSaddlesConnectedViaSummitNoSkipDQ(self):
        """
        Ensure Linkers to Saddles Connected Via Summit returns expected
        results when:
        skipDisqualified = False
        excludeSelf = True (default)
        """
        result = self.linker1.linkers_to_saddles_connected_via_summit(
            skipDisqualified=False)
        self.assertEqual(len(result), 2)
        self.assertIn(self.linker2, result)
        self.assertIn(self.disqualifiedLinker1, result)

    def testLinkerLinkersToSaddlesConnectedViaSummitNoSkipSelf(self):
        """
        Ensure Linkers to Saddles Connected Via Summit returns expected
        results when:
        skipDisqualified = True (default)
        excludeSelf = False
        """
        result = self.linker1.linkers_to_saddles_connected_via_summit(
            excludeSelf=False)
        self.assertEqual(len(result), 2)
        self.assertIn(self.linker2, result)
        self.assertIn(self.linker1, result)

    def testLinkerLinkersToSaddlesConnectedViaSummitNoSkipSelfOrDQ(self):
        """
        Ensure Linkers to Saddles Connected Via Summit returns expected
        results when:
        skipDisqualified = False
        excludeSelf = False
        """
        result = self.linker1.linkers_to_saddles_connected_via_summit(
            excludeSelf=False, skipDisqualified=False)
        self.assertEqual(len(result), 3)
        self.assertIn(self.linker1, result)
        self.assertIn(self.linker2, result)
        self.assertIn(self.disqualifiedLinker1, result)

    def testLinkerLinkersToSummitsConnectedViaSaddle(self):
        """
        Ensure Linkers to Summits Connected Via Saddle returns expected
        results when:
        skipDisqualified = True (default)
        excludeSelf = True (default)
        """
        result = self.linker2.linkers_to_summits_connected_via_saddle()
        self.assertEqual(len(result), 1)
        self.assertIn(self.linker3, result)

    def testLinkerLinkersToSummitsConnectedViaSaddleNoSkipDQ(self):
        """
        Ensure Linkers to Summits Connected Via Saddle returns expected
        results when:
        skipDisqualified = False
        excludeSelf = True (default)
        """
        result = self.linker2.linkers_to_summits_connected_via_saddle(
            skipDisqualified=False)
        self.assertEqual(len(result), 2)
        self.assertIn(self.linker3, result)
        self.assertIn(self.disqualifiedLinkerLocallyDeadSummit, result)

    def testLinkerLinkersToSummitsConnectedViaSaddleNoSkipSelf(self):
        """
        Ensure Linkers to Summits Connected Via Saddle returns expected
        results when:
        skipDisqualified = True (default)
        excludeSelf = False
        """
        result = self.linker2.linkers_to_summits_connected_via_saddle(
            excludeSelf=False)
        self.assertEqual(len(result), 2)
        self.assertIn(self.linker3, result)
        self.assertIn(self.linker2, result)

    def testLinkerLinkersToSummitsConnectedViaSaddleNoSkipSelfOrDQ(self):
        """
        Ensure Linkers to Summits Connected Via Saddle returns expected
        results when:
        skipDisqualified = False
        excludeSelf = False
        """
        result = self.linker2.linkers_to_summits_connected_via_saddle(
            excludeSelf=False, skipDisqualified=False)
        self.assertEqual(len(result), 3)
        self.assertIn(self.linker3, result)
        self.assertIn(self.linker2, result)
        self.assertIn(self.disqualifiedLinkerLocallyDeadSummit, result)

    def testLinkerRepr(self):
        """
        Ensure __repr__ is as expected
        """
        expected = "<Linker> <Saddle> lat 5 long 5 328.0839895013123ft" \
                   " 100m MultiPoint False -> <Summit> lat 1 long 1" \
                   " 3280.839895013123ft 1000m MultiPoint False" \
                   " 2952.755905511811promFt" \
                   " 900promM"
        self.assertEqual(self.linker1.__repr__(), expected)

    def testLinkerHash(self):
        """
        Ensure __hash__ feature works as expected
        """
        self.assertEqual(len(set([self.linker1, self.linker1])), 1)
        self.assertEqual(len(set([self.linker1, self.linker2])), 2)

    def testLinkerEq(self):
        """
        Ensure __eq__ feature works as expected
        """
        self.assertEqual(self.linker1, self.linker1)
        testLinker = Linker(self.summit1, self.saddle1, self.path1)
        self.assertEqual(self.linker1, testLinker)

    def testLinkerNe(self):
        """
        Ensure __ne__ feature works as expected
        """
        self.assertNotEqual(self.linker1, self.linker2)

    def testLinkerAddToRemoteSaddleAndSummit(self):
        """
        Ensure add_to_remote_saddle_and_summit() feature works as expected
        """
        # Make sure actual function works.
        self.summit1.saddles = []
        self.saddle1.summits = []
        self.assertEqual(len(self.summit1.saddles), 0)
        self.assertEqual(len(self.saddle1.summits), 0)

        self.linker1.add_to_remote_saddle_and_summit()
        self.assertEqual(self.summit1.saddles[0], self.linker1)
        self.assertEqual(self.saddle1.summits[0], self.linker1)

        # Make sure we don't re-add linkers already there.
        self.linker1.add_to_remote_saddle_and_summit()
        self.assertEqual(len(self.summit1.saddles), 1)
        self.assertEqual(len(self.saddle1.summits), 1)

    def testLinkerAddToRemoteSaddleAndSummitIgnoreDuplicates(self):
        """
        Ensure add_to_remote_saddle_and_summit() feature works as expected
        """
        # Make sure actual function works.
        self.summit1.saddles = []
        self.saddle1.summits = []
        self.assertEqual(len(self.summit1.saddles), 0)
        self.assertEqual(len(self.saddle1.summits), 0)

        self.linker1.add_to_remote_saddle_and_summit(ignoreDuplicates=False)
        self.assertEqual(self.summit1.saddles[0], self.linker1)
        self.assertEqual(self.saddle1.summits[0], self.linker1)

        # Make sure we do re-add linkers already there.
        self.linker1.add_to_remote_saddle_and_summit(ignoreDuplicates=False)
        self.assertEqual(len(self.summit1.saddles), 2)
        self.assertEqual(len(self.saddle1.summits), 2)

    def testLinkerFromDict(self):
        """
        Ensure from_dict produces expected results.
        """
        linkerDict = self.linker1.to_dict(noWalkPath=False)
        saddlesContainer = SaddlesContainer([self.saddle1, self.saddle2])
        summitsContainer = SummitsContainer([self.summit1, self.summit2])
        newLinker = Linker.from_dict(linkerDict,
                                     saddlesContainer,
                                     summitsContainer)

        self.assertEqual(newLinker, self.linker1)
        self.assertEqual(newLinker.saddle, self.saddle1)
        self.assertEqual(newLinker.summit, self.summit1)
        self.assertEqual(newLinker.path, self.path1)
