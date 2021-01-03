"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
import cbor
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit
from pyprom.lib.locations.runoff import Runoff

from pyprom.lib.containers.saddles import SaddlesContainer
from pyprom.lib.containers.summits import SummitsContainer
from pyprom.lib.containers.runoffs import RunoffsContainer

from pyprom.lib.contexts.manager import FeatureContextManager

class ManagerTests(unittest.TestCase):
    """Test Context Manager"""

    def setUp(self):
        self.saddle1 = Saddle(1, 2, 3)
        self.saddle2 = Saddle(2, 3, 4)
        self.summit1 = Summit(1, 2, 3)
        self.summit2 = Summit(2, 3, 4)
        self.runoff1 = Runoff(1, 2, 3)
        self.runoff2 = Runoff(2, 3, 4)

        # empty manager.
        self.manager = FeatureContextManager([], [], [])

    # Saddles.

    def testAddSaddleOK(self):
        """
        Add an active Saddle to this context and check for all expected attributes.
        :return:
        """
        self.manager.add_saddle(self.saddle1)
        self.assertEqual(self.manager.saddle_lookup[self.saddle1.id], self.saddle1)
        self.assertEqual(self.manager.saddle_lookup.get(self.saddle2.id), None)
        self.assertIn(self.saddle1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 1)
        self.assertEqual(self.manager.is_disabled(self.saddle1.id), False)
        self.assertIsNotNone(self.saddle1.contexts[self.manager.id])
        self.assertEqual(self.saddle1.contexts[self.manager.id].saddle, self.saddle1)
        self.assertEqual(self.saddle1.contexts[self.manager.id].summits, [])
        self.assertEqual(self.saddle1.contexts[self.manager.id].disabled, False)

    def testAddSaddleDisabled(self):
        """
        Add a disabled Saddle to this context and check for all expected attributes.
        :return:
        """
        self.manager.add_saddle(self.saddle1, disabled=True)
        self.assertEqual(self.manager.saddle_lookup[self.saddle1.id], self.saddle1)
        self.assertEqual(self.manager.saddle_lookup.get(self.saddle2.id), None)
        self.assertIn(self.saddle1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 1)
        self.assertEqual(self.manager.is_disabled(self.saddle1.id), True)
        self.assertIsNotNone(self.saddle1.contexts[self.manager.id])
        self.assertEqual(self.saddle1.contexts[self.manager.id].saddle, self.saddle1)
        self.assertEqual(self.saddle1.contexts[self.manager.id].summits, [])
        self.assertEqual(self.saddle1.contexts[self.manager.id].disabled, True)

    def testRemoveSaddleOK(self):
        """
        Add then remove an active Saddle to this context and check for all expected attributes.
        :return:
        """
        self.manager.add_saddle(self.saddle1)
        self.assertEqual(self.manager.saddle_lookup[self.saddle1.id], self.saddle1)
        self.assertIn(self.saddle1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 1)
        self.assertEqual(self.manager.is_disabled(self.saddle1.id), False)

        self.manager.remove_saddle(self.saddle1)

        self.assertEqual(self.manager.saddle_lookup.get(self.saddle1.id), None)
        self.assertNotIn(self.saddle1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 0)
        self.assertEqual(self.manager.is_disabled(self.saddle1.id), False)

        self.assertIsNone(self.saddle1.contexts.get(self.manager.id))


    def testRemoveSaddleDisabled(self):
        """
        Add then remove disabled Saddle to this context and check for all expected attributes.
        """
        self.manager.add_saddle(self.saddle1, disabled=True)
        self.assertEqual(self.manager.saddle_lookup[self.saddle1.id], self.saddle1)
        self.assertIn(self.saddle1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 1)
        self.assertEqual(self.manager.is_disabled(self.saddle1.id), True)

        self.manager.remove_saddle(self.saddle1)

        self.assertEqual(self.manager.saddle_lookup.get(self.saddle1.id), None)
        self.assertNotIn(self.saddle1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 0)
        self.assertEqual(self.manager.is_disabled(self.saddle1.id), False)
        self.assertIsNone(self.saddle1.contexts.get(self.manager.id))

    def testDisableSaddle(self):
        """
        Add Saddle then disable it
        """
        self.manager.add_saddle(self.saddle1)
        self.assertEqual(self.manager.saddle_lookup[self.saddle1.id], self.saddle1)
        self.assertIn(self.saddle1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 1)
        self.assertEqual(self.manager.is_disabled(self.saddle1.id), False)
        self.assertIsNotNone(self.saddle1.contexts.get(self.manager.id))
        self.assertFalse(self.saddle1.contexts[self.manager.id].disabled)
        # Perform action.
        self.saddle1.contexts[self.manager.id].disable()

        self.assertEqual(self.manager.is_disabled(self.saddle1.id), True)
        self.assertEqual(self.saddle1.contexts[self.manager.id].disabled, True)

    def testEnableSaddle(self):
        """
        Add Disabled Saddle then enable it
        """
        self.manager.add_saddle(self.saddle1, disabled=True)
        self.assertEqual(self.manager.saddle_lookup[self.saddle1.id], self.saddle1)
        self.assertIn(self.saddle1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 1)
        self.assertEqual(self.manager.is_disabled(self.saddle1.id), True)
        self.assertIsNotNone(self.saddle1.contexts.get(self.manager.id))
        self.assertTrue(self.saddle1.contexts[self.manager.id].disabled)
        # Perform action.
        self.saddle1.contexts[self.manager.id].enable()

        self.assertEqual(self.manager.is_disabled(self.saddle1.id), False)
        self.assertEqual(self.saddle1.contexts[self.manager.id].disabled, False)




    # Summits.






    def testAddSummitOK(self):
        """
        Add an active Summit to this context and check for all expected attributes.
        :return:
        """
        self.manager.add_summit(self.summit1)
        self.assertEqual(self.manager.summit_lookup[self.summit1.id], self.summit1)
        self.assertEqual(self.manager.summit_lookup.get(self.saddle2.id), None)
        self.assertIn(self.summit1, self.manager._summits)
        self.assertEqual(len(self.manager._summits), 1)
        self.assertEqual(self.manager.is_disabled(self.summit1.id), False)
        self.assertIsNotNone(self.summit1.contexts[self.manager.id])
        self.assertEqual(self.summit1.contexts[self.manager.id].summit, self.summit1)
        self.assertEqual(self.summit1.contexts[self.manager.id].saddles, [])
        self.assertEqual(self.summit1.contexts[self.manager.id].disabled, False)

    def testAddSummitDisabled(self):
        """
        Add a disabled Summit to this context and check for all expected attributes.
        :return:
        """
        self.manager.add_summit(self.summit1, disabled=True)
        self.assertEqual(self.manager.summit_lookup[self.summit1.id], self.summit1)
        self.assertEqual(self.manager.summit_lookup.get(self.saddle2.id), None)
        self.assertIn(self.summit1, self.manager._summits)
        self.assertEqual(len(self.manager._summits), 1)
        self.assertEqual(self.manager.is_disabled(self.summit1.id), True)
        self.assertIsNotNone(self.summit1.contexts[self.manager.id])
        self.assertEqual(self.summit1.contexts[self.manager.id].summit, self.summit1)
        self.assertEqual(self.summit1.contexts[self.manager.id].saddles, [])
        self.assertEqual(self.summit1.contexts[self.manager.id].disabled, True)


    def testDisableSummit(self):
        """
        Add Summit then disable it
        """
        self.manager.add_summit(self.summit1)
        self.assertEqual(self.manager.summit_lookup[self.summit1.id], self.summit1)
        self.assertIn(self.summit1, self.manager._summits)
        self.assertEqual(len(self.manager._summits), 1)
        self.assertEqual(self.manager.is_disabled(self.summit1.id), False)
        self.assertIsNotNone(self.summit1.contexts.get(self.manager.id))
        self.assertFalse(self.summit1.contexts[self.manager.id].disabled)
        # Perform action.
        self.summit1.contexts[self.manager.id].disable()

        self.assertEqual(self.manager.is_disabled(self.summit1.id), True)
        self.assertEqual(self.summit1.contexts[self.manager.id].disabled, True)

    def testEnableSummit(self):
        """
        Add Disabled Summit then enable it
        """
        self.manager.add_summit(self.summit1, disabled=True)
        self.assertEqual(self.manager.summit_lookup[self.summit1.id], self.summit1)
        self.assertIn(self.summit1, self.manager._summits)
        self.assertEqual(len(self.manager._summits), 1)
        self.assertEqual(self.manager.is_disabled(self.summit1.id), True)
        self.assertIsNotNone(self.summit1.contexts.get(self.manager.id))
        self.assertTrue(self.summit1.contexts[self.manager.id].disabled)
        # Perform action.
        self.summit1.contexts[self.manager.id].enable()

        self.assertEqual(self.manager.is_disabled(self.summit1.id), False)
        self.assertEqual(self.summit1.contexts[self.manager.id].disabled, False)




    # Runoffs.


    def testAddRunoffOK(self):
        """
        Add an active Runoff to this context and check for all expected attributes.
        :return:
        """
        self.manager.add_saddle(self.runoff1)
        self.assertEqual(self.manager.saddle_lookup[self.runoff1.id], self.runoff1)
        self.assertEqual(self.manager.saddle_lookup.get(self.saddle2.id), None)
        self.assertIn(self.runoff1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 1)
        self.assertEqual(self.manager.is_disabled(self.runoff1.id), False)
        self.assertIsNotNone(self.runoff1.contexts[self.manager.id])
        self.assertEqual(self.runoff1.contexts[self.manager.id].saddle, self.runoff1)
        self.assertEqual(self.runoff1.contexts[self.manager.id].summits, [])
        self.assertEqual(self.runoff1.contexts[self.manager.id].disabled, False)

    def testAddRunoffDisabled(self):
        """
        Add a disabled Runoff to this context and check for all expected attributes.
        :return:
        """
        self.manager.add_saddle(self.runoff1, disabled=True)
        self.assertEqual(self.manager.saddle_lookup[self.runoff1.id], self.runoff1)
        self.assertEqual(self.manager.saddle_lookup.get(self.saddle2.id), None)
        self.assertIn(self.runoff1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 1)
        self.assertEqual(self.manager.is_disabled(self.runoff1.id), True)
        self.assertIsNotNone(self.runoff1.contexts[self.manager.id])
        self.assertEqual(self.runoff1.contexts[self.manager.id].saddle, self.runoff1)
        self.assertEqual(self.runoff1.contexts[self.manager.id].summits, [])
        self.assertEqual(self.runoff1.contexts[self.manager.id].disabled, True)


    def testDisableRunoff(self):
        """
        Add Runoff then disable it
        """
        self.manager.add_saddle(self.runoff1)
        self.assertEqual(self.manager.saddle_lookup[self.runoff1.id], self.runoff1)
        self.assertIn(self.runoff1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 1)
        self.assertEqual(self.manager.is_disabled(self.runoff1.id), False)
        self.assertIsNotNone(self.runoff1.contexts.get(self.manager.id))
        self.assertFalse(self.runoff1.contexts[self.manager.id].disabled)
        # Perform action.
        self.runoff1.contexts[self.manager.id].disable()

        self.assertEqual(self.manager.is_disabled(self.runoff1.id), True)
        self.assertEqual(self.runoff1.contexts[self.manager.id].disabled, True)

    def testEnableRunoff(self):
        """
        Add Disabled Runoff then enable it
        """
        self.manager.add_saddle(self.runoff1, disabled=True)
        self.assertEqual(self.manager.saddle_lookup[self.runoff1.id], self.runoff1)
        self.assertIn(self.runoff1, self.manager._saddles)
        self.assertEqual(len(self.manager._saddles), 1)
        self.assertEqual(self.manager.is_disabled(self.runoff1.id), True)
        self.assertIsNotNone(self.runoff1.contexts.get(self.manager.id))
        self.assertTrue(self.runoff1.contexts[self.manager.id].disabled)
        # Perform action.
        self.runoff1.contexts[self.manager.id].enable()

        self.assertEqual(self.manager.is_disabled(self.runoff1.id), False)
        self.assertEqual(self.runoff1.contexts[self.manager.id].disabled, False)


    # Linkages

    def testLinkSaddleSummitCreate(self):
        """
        Simple Saddle Summit linkage creation test.
        """

        # add saddle/summit to manager
        self.manager.add_saddle(self.saddle1)
        self.manager.add_summit(self.summit1)

        # link saddle1 from summit1
        self.manager.get_ctx(self.summit1).link_saddle(self.saddle1)

        # asserts
        sad1_ctx = self.manager.get_ctx(self.saddle1)
        sum1_ctx = self.manager.get_ctx(self.summit1)

        # right summits from saddle?
        self.assertEqual(len(sad1_ctx.summits), 1)
        self.assertEqual(sad1_ctx.summits[0], self.summit1)

        # right saddles from summit?
        self.assertEqual(len(sum1_ctx.saddles), 1)
        self.assertEqual(sum1_ctx.saddles[0], self.saddle1)

        # Tracked in manager?
        self.assertEqual(self.manager.summit_to_saddle_tracker[self.summit1.id][self.saddle1.id], True)
        self.assertEqual(self.manager.saddle_to_summit_tracker[self.saddle1.id][self.summit1.id], True)

    def testDeLinkSaddleSummit(self):
        """
        Simple Saddle Summit destruction test.
        """

        # add saddle/summit to manager
        self.manager.add_saddle(self.saddle1)
        self.manager.add_summit(self.summit1)

        # link saddle1 from summit1
        self.manager.get_ctx(self.summit1).link_saddle(self.saddle1)

        #de-link
        self.manager.get_ctx(self.summit1).remove_saddle(self.saddle1)

        # asserts
        sad1_ctx = self.manager.get_ctx(self.saddle1)
        sum1_ctx = self.manager.get_ctx(self.summit1)

        # right summits from saddle?
        self.assertEqual(len(sad1_ctx.summits), 0)

        # right saddles from summit?
        self.assertEqual(len(sum1_ctx.saddles), 0)

        # Tracked in manager?
        self.assertIsNone(self.manager.summit_to_saddle_tracker[self.summit1.id].get(self.saddle1.id))
        self.assertIsNone(self.manager.saddle_to_summit_tracker[self.saddle1.id].get(self.summit1.id))

    def testLinkRunoffSummitCreate(self):
        """
        Simple Runoff Summit linkage creation test.
        """

        # add saddle/summit to manager
        self.manager.add_saddle(self.runoff1)
        self.manager.add_summit(self.summit1)

        # link saddle1 from summit1
        self.manager.get_ctx(self.summit1).link_saddle(self.runoff1)

        # asserts
        sad1_ctx = self.manager.get_ctx(self.runoff1)
        sum1_ctx = self.manager.get_ctx(self.summit1)

        # right summits from saddle?
        self.assertEqual(len(sad1_ctx.summits), 1)
        self.assertEqual(sad1_ctx.summits[0], self.summit1)

        # right saddles from summit?
        self.assertEqual(len(sum1_ctx.saddles), 1)
        self.assertEqual(sum1_ctx.saddles[0], self.runoff1)

        # Tracked in manager?
        self.assertEqual(self.manager.summit_to_saddle_tracker[self.summit1.id][self.runoff1.id], True)
        self.assertEqual(self.manager.saddle_to_summit_tracker[self.runoff1.id][self.summit1.id], True)

    def testDeLinkRunoffSummit(self):
        """
        Simple Runoff Summit destruction test.
        """

        # add saddle/summit to manager
        self.manager.add_saddle(self.runoff1)
        self.manager.add_summit(self.summit1)

        # link saddle1 from summit1
        self.manager.get_ctx(self.summit1).link_saddle(self.runoff1)

        #de-link
        self.manager.get_ctx(self.summit1).remove_saddle(self.runoff1)

        # asserts
        sad1_ctx = self.manager.get_ctx(self.runoff1)
        sum1_ctx = self.manager.get_ctx(self.summit1)

        # right summits from saddle?
        self.assertEqual(len(sad1_ctx.summits), 0)

        # right saddles from summit?
        self.assertEqual(len(sum1_ctx.saddles), 0)

        # Tracked in manager?
        self.assertIsNone(self.manager.summit_to_saddle_tracker[self.summit1.id].get(self.runoff1.id))
        self.assertIsNone(self.manager.saddle_to_summit_tracker[self.runoff1.id].get(self.summit1.id))

    def testLinkSummitSaddleCreate(self):
        """
        Simple Saddle Summit linkage creation test.
        """

        # add saddle/summit to manager
        self.manager.add_saddle(self.saddle1)
        self.manager.add_summit(self.summit1)

        # link summit1 from saddle1
        self.manager.get_ctx(self.saddle1).link_summit(self.summit1)

        # asserts
        sad1_ctx = self.manager.get_ctx(self.saddle1)
        sum1_ctx = self.manager.get_ctx(self.summit1)

        # right summits from saddle?
        self.assertEqual(len(sad1_ctx.summits), 1)
        self.assertEqual(sad1_ctx.summits[0], self.summit1)

        # right saddles from summit?
        self.assertEqual(len(sum1_ctx.saddles), 1)
        self.assertEqual(sum1_ctx.saddles[0], self.saddle1)

        # Tracked in manager?
        self.assertEqual(self.manager.summit_to_saddle_tracker[self.summit1.id][self.saddle1.id], True)
        self.assertEqual(self.manager.saddle_to_summit_tracker[self.saddle1.id][self.summit1.id], True)

    def testDeLinkSummitSaddle(self):
        """
        Simple Saddle Summit linkage destruction test.
        """

        # add saddle/summit to manager
        self.manager.add_saddle(self.saddle1)
        self.manager.add_summit(self.summit1)

        # link saddle1 from summit1
        self.manager.get_ctx(self.saddle1).link_summit(self.summit1)

        #de-link
        self.manager.get_ctx(self.saddle1).remove_summit(self.summit1)

        # asserts
        sad1_ctx = self.manager.get_ctx(self.saddle1)
        sum1_ctx = self.manager.get_ctx(self.summit1)

        # right summits from saddle?
        self.assertEqual(len(sad1_ctx.summits), 0)

        # right saddles from summit?
        self.assertEqual(len(sum1_ctx.saddles), 0)

        # Tracked in manager?
        self.assertIsNone(self.manager.summit_to_saddle_tracker[self.summit1.id].get(self.saddle1.id))
        self.assertIsNone(self.manager.saddle_to_summit_tracker[self.saddle1.id].get(self.summit1.id))

    def testDuplicateLinkWithRemovalFromSummitSide(self):
        """
        This test demonstrates the functionality which automatically
        disables a Saddle when a duplicate link is created. from the Summits
        perspective
        """

        # add saddle/summit to manager
        self.manager.add_saddle(self.saddle1)
        self.manager.add_summit(self.summit1)


        # Links saddles to summits
        self.manager.get_ctx(self.summit1).link_saddle(self.saddle1)
        ok, dupe = self.manager.get_ctx(self.summit1).link_saddle(self.saddle1)

        sad1_ctx = self.manager.get_ctx(self.saddle1)
        sum1_ctx = self.manager.get_ctx(self.summit1)

        self.assertTrue(ok)
        self.assertTrue(dupe)

        # right summits from saddle?
        self.assertEqual(len(sad1_ctx.summits), 0)

        # right saddles from summit?
        self.assertEqual(len(sum1_ctx.saddles), 0)

        # Tracked in manager?
        self.assertIsNone(self.manager.summit_to_saddle_tracker[self.summit1.id].get(self.saddle1.id))
        self.assertIsNone(self.manager.saddle_to_summit_tracker[self.saddle1.id].get(self.summit1.id))

        # disabled?
        self.assertTrue(sad1_ctx.disabled)
        self.assertTrue(self.manager.disabled_tracker[self.saddle1.id])


    def testDuplicateLinkWithRemovalFromSaddleSide(self):
        """
        This test demonstrates the functionality which automatically
        disables a Saddle when a duplicate link is created. from the Saddles
        perspective
        """

        # add saddle/summit to manager
        self.manager.add_saddle(self.saddle1)
        self.manager.add_summit(self.summit1)

        # Links summits to saddles
        ok, dupe = self.manager.get_ctx(self.saddle1).link_summit(self.summit1)
        self.assertTrue(ok)
        self.assertFalse(dupe)

        ok, dupe = self.manager.get_ctx(self.saddle1).link_summit(self.summit1)

        sad1_ctx = self.manager.get_ctx(self.saddle1)
        sum1_ctx = self.manager.get_ctx(self.summit1)

        self.assertTrue(ok)
        self.assertTrue(dupe)

        # right summits from saddle?
        self.assertEqual(len(sad1_ctx.summits), 0)

        # right saddles from summit?
        self.assertEqual(len(sum1_ctx.saddles), 0)

        # Tracked in manager?
        self.assertIsNone(self.manager.summit_to_saddle_tracker[self.summit1.id].get(self.saddle1.id))
        self.assertIsNone(self.manager.saddle_to_summit_tracker[self.saddle1.id].get(self.summit1.id))

        # disabled?
        self.assertTrue(sad1_ctx.disabled)
        self.assertTrue(self.manager.disabled_tracker[self.saddle1.id])

    def testDuplicateLinkWithoutRemovalFromSummitSide(self):
        """
        Test duplicate links with disable_duplicate=False.

        This should Not create a duplicate link,
        it will preserve the existing link and will not
        disable the saddle
        """

        # add saddle/summit to manager
        self.manager.add_saddle(self.saddle1)
        self.manager.add_summit(self.summit1)

        # Links saddles to summits
        ok, dupe = self.manager.get_ctx(self.summit1).link_saddle(self.saddle1)
        self.assertTrue(ok)
        self.assertFalse(dupe)

        ok, dupe = self.manager.get_ctx(self.summit1).link_saddle(self.saddle1, disable_duplicate=False)

        sad1_ctx = self.manager.get_ctx(self.saddle1)
        sum1_ctx = self.manager.get_ctx(self.summit1)

        self.assertTrue(ok)
        self.assertTrue(dupe)

        # right summits from saddle?
        self.assertEqual(len(sad1_ctx.summits), 1)
        self.assertEqual(sad1_ctx.summits[0], self.summit1)

        # right saddles from summit?
        self.assertEqual(len(sum1_ctx.saddles), 1)
        self.assertEqual(sum1_ctx.saddles[0], self.saddle1)

        # Tracked in manager?
        self.assertEqual(self.manager.summit_to_saddle_tracker[self.summit1.id].get(self.saddle1.id), True)
        self.assertEqual(self.manager.saddle_to_summit_tracker[self.saddle1.id].get(self.summit1.id), True)

        # disabled?
        self.assertFalse(sad1_ctx.disabled)
        self.assertFalse(self.manager.disabled_tracker[self.saddle1.id])

    def testDuplicateLinkWithoutRemovalFromSaddleSide(self):
        """
        Test duplicate links with disable_duplicate=False.

        This should Not create a duplicate link,
        it will preserve the existing link and will not
        disable the saddle
        """

        # add saddle/summit to manager
        self.manager.add_saddle(self.saddle1)
        self.manager.add_summit(self.summit1)

        # Links saddles to summits
        ok, dupe = self.manager.get_ctx(self.saddle1).link_summit(self.summit1)
        self.assertTrue(ok)
        self.assertFalse(dupe)

        ok, dupe = self.manager.get_ctx(self.saddle1).link_summit(self.summit1, disable_duplicate=False)

        sad1_ctx = self.manager.get_ctx(self.saddle1)
        sum1_ctx = self.manager.get_ctx(self.summit1)

        self.assertTrue(ok)
        self.assertTrue(dupe)

        # right summits from saddle?
        self.assertEqual(len(sad1_ctx.summits), 1)
        self.assertEqual(sad1_ctx.summits[0], self.summit1)

        # right saddles from summit?
        self.assertEqual(len(sum1_ctx.saddles), 1)
        self.assertEqual(sum1_ctx.saddles[0], self.saddle1)

        # Tracked in manager?
        self.assertEqual(self.manager.summit_to_saddle_tracker[self.summit1.id].get(self.saddle1.id), True)
        self.assertEqual(self.manager.saddle_to_summit_tracker[self.saddle1.id].get(self.summit1.id), True)

        # disabled?
        self.assertFalse(sad1_ctx.disabled)
        self.assertFalse(self.manager.disabled_tracker[self.saddle1.id])


class ManagerLoadSaveTests(unittest.TestCase):
    """Test Context Manager ability to load/save to/from dict"""

    def setUp(self):
        self.saddle1 = Saddle(1, 2, 3)
        self.saddle2 = Saddle(2, 3, 4)
        self.summit1 = Summit(1, 2, 3)
        self.summit2 = Summit(2, 3, 4)
        self.runoff1 = Runoff(1, 2, 3)
        self.runoff2 = Runoff(2, 3, 4)

        self.summits = SummitsContainer([self.summit1, self.summit2])
        self.saddles = SaddlesContainer([self.saddle1, self.saddle2])
        self.runoffs = RunoffsContainer([self.runoff1, self.runoff2])


        self.manager = FeatureContextManager(self.summits.points,
                                             self.saddles.points,
                                             self.runoffs.points)

    def test_to_from_dict(self):
        """
        Test exporting to dict and importing.

        This uses to_dict to generate a dict of this context,
        then cbors the result, uncbors, and loads with from_dict


        """
        #Links
        self.manager.get_ctx(self.saddle1).link_summit(self.summit1)
        self.manager.get_ctx(self.saddle1).link_summit(self.summit2)
        self.manager.get_ctx(self.runoff1).link_summit(self.summit1)
        self.manager.get_ctx(self.runoff2).link_summit(self.summit1)
        self.manager.get_ctx(self.saddle2).link_summit(self.summit1)
        self.manager.get_ctx(self.saddle2).link_summit(self.summit2)

        self.manager.get_ctx(self.saddle2).disable()
        self.manager.get_ctx(self.runoff2).disable()

        # Export!
        ctx_dict = self.manager.to_dict()

        # serialize/deserialize
        cbored_ctx_dict = cbor.loads(cbor.dumps(ctx_dict))

        # blow away old context references, but stash objects for later comparison.
        oldecontexts={}
        for i in self.saddles.points + self.summits.points + self.runoffs.points:
            oldecontexts[i.id] = i.contexts[self.manager.id]
            i.contexts = {}

        #reload!
        new = FeatureContextManager.from_dict(cbored_ctx_dict, self.saddles, self.summits, self.runoffs)

        # Do our members have this context?
        for i in self.saddles.points + self.summits.points + self.runoffs.points:
            self.assertTrue(new.id in i.contexts.keys())

        # saddles populated?
        for saddle in self.saddles:
            self.assertIn(saddle, new._saddles)
            self.assertEqual(saddle, new.saddle_lookup[saddle.id])

        # runoffs populated?
        for runoff in self.runoffs:
            self.assertIn(runoff, new._saddles)
            self.assertEqual(runoff, new.saddle_lookup[runoff.id])

        self.assertEqual(len(new._saddles), 4)

        # summits populated?
        for summit in self.summits:
            self.assertIn(summit, new._summits)
            self.assertEqual(summit, new.summit_lookup[summit.id])

        # our disabled resources still disabled?
        self.assertTrue(new.get_ctx(self.saddle2).disabled)
        self.assertTrue(new.get_ctx(self.runoff2).disabled)

        # link records match?
        self.assertDictEqual(new.summit_to_saddle_tracker, self.manager.summit_to_saddle_tracker)
        self.assertDictEqual(new.saddle_to_summit_tracker, self.manager.saddle_to_summit_tracker)

        # disabled tracker match?
        self.assertDictEqual(new.disabled_tracker, self.manager.disabled_tracker)

        # Are our links in contexts as expected?
        self.assertEqual(new.get_ctx(self.saddle1).summits, oldecontexts[self.saddle1.id].summits)
        self.assertEqual(new.get_ctx(self.saddle2).summits, oldecontexts[self.saddle2.id].summits)
        self.assertEqual(new.get_ctx(self.summit1).saddles, oldecontexts[self.summit1.id].saddles)
        self.assertEqual(new.get_ctx(self.summit2).saddles, oldecontexts[self.summit2.id].saddles)
        self.assertEqual(new.get_ctx(self.runoff1).summits, oldecontexts[self.runoff1.id].summits)
        self.assertEqual(new.get_ctx(self.runoff2).summits, oldecontexts[self.runoff2.id].summits)

        # disabled state as expected?
        self.assertEqual(new.get_ctx(self.saddle1).disabled, oldecontexts[self.saddle1.id].disabled)
        self.assertEqual(new.get_ctx(self.saddle2).disabled, oldecontexts[self.saddle2.id].disabled)
        self.assertEqual(new.get_ctx(self.summit1).disabled, oldecontexts[self.summit1.id].disabled)
        self.assertEqual(new.get_ctx(self.summit2).disabled, oldecontexts[self.summit2.id].disabled)
        self.assertEqual(new.get_ctx(self.runoff1).disabled, oldecontexts[self.runoff1.id].disabled)
        self.assertEqual(new.get_ctx(self.runoff2).disabled, oldecontexts[self.runoff2.id].disabled)
