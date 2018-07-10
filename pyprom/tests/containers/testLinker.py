"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.locations.summit import Summit
from pyprom.lib.containers.linker import Linker

class LinkerTests(unittest.TestCase):

    def setUp(self):
        self.summit1 = Summit(1, 1, 1000)
        self.saddle1 = Saddle(5, 5, 100)
        self.summit2 = Summit(10, 10, 1000)
        self.saddle2 = Saddle(15, 15, 100)

        self.linker1 = Linker(self.summit1, self.saddle1, None)
        self.linker2 = Linker(self.summit1, self.saddle2, None)
        self.linker3 = Linker(self.summit2, self.saddle2, None)

        self.summit1.saddles = [self.linker1, self.linker2]
        self.summit2.saddles = [self.linker3]
        self.saddle1.summits = [self.linker1]
        self.saddle2.summits = [self.linker2, self.linker3]

    def testLinkerProminence(self):
        """ Ensure prominence calculation are as expected """
        self.assertEqual(self.linker1.prom, 900)

    def testLinkerProminenceFeet(self):
        """ Ensure foot prominence calculation are as expected """
        self.assertEqual(self.linker1.prom_ft, 2952.7200000000003)

    def testLinkerSummitSaddles(self):
        """ Ensure summit saddles calculation are as expected """
        self.assertEqual(len(self.linker1.summit_saddles), 2)
        self.assertIn(self.saddle1, self.linker1.summit_saddles)
        self.assertIn(self.saddle2, self.linker1.summit_saddles)

    def testLinkerSaddlesSummit(self):
        """ Ensure saddle summits calculation are as expected """
        self.assertEqual(len(self.linker2.saddle_summits), 2)
        self.assertIn(self.summit1, self.linker2.saddle_summits)
        self.assertIn(self.summit2, self.linker2.saddle_summits)

    def testLinkerRepr(self):
        """ Ensure __repr__ is as expected """
        expected = "<Linker> <Saddle> lat 5 long 5 328.08000000000004ft" \
                   " 100m MultiPoint False -> <Summit> lat 1 long 1" \
                   " 3280.8ft 1000m MultiPoint False" \
                   " 2952.7200000000003promFt" \
                   " 900promM"
        self.assertEqual(self.linker1.__repr__(), expected)

    def testLinkerHash(self):
        """ Ensure __hash__ feature works as expected """
        self.assertEqual(len(set([self.linker1, self.linker1])), 1)
        self.assertEqual(len(set([self.linker1, self.linker2])), 2)

    def testLinkerEq(self):
        """ Ensure __eq__ feature works as expected """
        self.assertEqual(self.linker1, self.linker1)
        testLinker = Linker(self.summit1, self.saddle1, None)
        self.assertEqual(self.linker1, testLinker)
