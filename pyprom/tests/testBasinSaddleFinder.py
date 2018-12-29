# flake8: noqa
"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.lib.containers.saddles import SaddlesContainer
from pyprom.lib.containers.linker import Linker
from pyprom.lib.locations.summit import Summit
from pyprom.lib.locations.saddle import Saddle
from pyprom.lib.logic.basin_saddle_finder import BasinSaddleFinder


class BasinSaddleFinderTests(unittest.TestCase):
    """Test Basin Saddle Finder."""

    def testBasinSaddleFinderSingleSummit(self):
        r"""
        Test disqualification of saddles which has two
        linkers leading to one summit
                /--(L1 - x)--\
        Summit1              Saddle1 (x)
               \--(L2 - x)---/
        """
        summit1 = Summit(1, 1, 10000)
        saddle1 = Saddle(2, 2, 1000)
        linker1 = Linker(summit1, saddle1)
        linker2 = Linker(summit1, saddle1)
        saddle1.summits.extend([linker1, linker2])
        summit1.saddles.extend([linker1, linker2])
        saddles = SaddlesContainer([saddle1])

        cf = BasinSaddleFinder(saddles)
        cf.disqualify_basin_saddles()

        self.assertTrue(saddle1.disqualified)
        self.assertTrue(linker1.disqualified)
        self.assertTrue(linker2.disqualified)
        self.assertTrue(saddle1.singleSummit)

    def testBasinSaddleFinderDiamond(self):
        r"""
        Ensure lowest Saddle and linkers in a diamond configuration
        are disqualified
                /--(H1)-------Saddle 1000 -----(H2)-------\
        Summit1                                           Summit2
               \--(L1 - x)----Saddle 100 (x) --(L2 - x)---/
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        saddle1000 = Saddle(1, 1, 1000)
        saddle100 = Saddle(2, 2, 100)

        linkerL1 = Linker(summit1, saddle100)
        linkerH1 = Linker(summit1, saddle1000)
        linkerL2 = Linker(summit2, saddle100)
        linkerH2 = Linker(summit2, saddle1000)

        doomed_linkers = [linkerL1, linkerL2]
        doomed_saddles = [saddle100]
        ok_linkers = [linkerH1, linkerH2]
        ok_saddles = [saddle1000]
        self._build_and_validate(doomed_linkers, doomed_saddles,
                                 ok_linkers, ok_saddles)

    def testBasinSaddleFinderDoubleDiamond(self):
        r"""
        Ensure lowest 2 Saddles and linkers in a diamond
        configuration are disqualified
               /--(H1)-------Saddle 1000 -----(H2)-------\
        Summit1--(L1 - x)----Saddle 100 (x) --(L2 - x)----Summit2
               \--(Le1 - x)--Saddle 1 (x) ----(Le2 - x)--/
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        saddleHigh = Saddle(1000, 1000, 1000)
        saddleLow = Saddle(100, 100, 100)
        saddleLowest = Saddle(1, 1, 1)
        linkerL1 = Linker(summit1, saddleLow)
        linkerLe1 = Linker(summit1, saddleLowest)
        linkerH1 = Linker(summit1, saddleHigh)
        linkerL2 = Linker(summit2, saddleLow)
        linkerLe2 = Linker(summit2, saddleLowest)
        linkerH2 = Linker(summit2, saddleHigh)

        doomed_linkers = [linkerL1, linkerL2, linkerLe1, linkerLe2]
        doomed_saddles = [saddleLow, saddleLowest]
        ok_linkers = [linkerH1, linkerH2]
        ok_saddles = [saddleHigh]
        self._build_and_validate(doomed_linkers, doomed_saddles, ok_linkers, ok_saddles)

    def testBasinSaddleFinderEightWayDiamond(self):
        """
        Ensure lowest 8 Saddles and linkers in a diamond configuration are disqualified
               |--(H1a)-------Saddle 1000 ------(H1b)------|
               |-(L1a - x)----Saddle 100 (x) --(L1b x)-----|
               |-(L2a - x)----Saddle 200 (x) --(L2b - x)---|
               |-(L3a - x)----Saddle 300 (x) --(L3b - x)---|
        Summit1--(L4a - x)----Saddle 400 (x) --(L4b - x)----Summit2
               |--(L5a - x)--Saddle 500 (x) ----(L5b - x)--|
               |--(L6a - x)--Saddle 600 (x) ----(L6b - x)--|
               |--(L7a - x)--Saddle 700 (x) ----(L7b - x)--|
               |--(Le1a- x)--Saddle 1 (x) ----(Le1b - x)---|
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        saddle1000 = Saddle(1000, 1000, 1000)
        saddle100 = Saddle(100, 100, 100)
        saddle200 = Saddle(200, 200, 200)
        saddle300 = Saddle(300, 300, 300)
        saddle400 = Saddle(400, 400, 400)
        saddle500 = Saddle(500, 500, 500)
        saddle600 = Saddle(600, 600, 600)
        saddle700 = Saddle(700, 700, 700)
        saddle1 = Saddle(1, 1, 1)

        linkerL1a = Linker(summit1, saddle100)
        linkerL1b = Linker(summit2, saddle100)
        linkerL2a = Linker(summit1, saddle200)
        linkerL2b = Linker(summit2, saddle200)
        linkerL3a = Linker(summit1, saddle300)
        linkerL3b = Linker(summit2, saddle300)
        linkerL4a = Linker(summit1, saddle400)
        linkerL4b = Linker(summit2, saddle400)
        linkerL5a = Linker(summit1, saddle500)
        linkerL5b = Linker(summit2, saddle500)
        linkerL6a = Linker(summit1, saddle600)
        linkerL6b = Linker(summit2, saddle600)
        linkerL7a = Linker(summit1, saddle700)
        linkerL7b = Linker(summit2, saddle700)

        linkerLe1a = Linker(summit1, saddle1)
        linkerLe1b = Linker(summit2, saddle1)

        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit2, saddle1000)

        doomed_linkers = [linkerL1a, linkerL1b,
                          linkerL2a, linkerL2b,
                          linkerL3a, linkerL3b,
                          linkerL4a, linkerL4b,
                          linkerL5a, linkerL5b,
                          linkerL6a, linkerL6b,
                          linkerL7a, linkerL7b,
                          linkerLe1a, linkerLe1b,
                          ]
        doomed_saddles = [saddle1, saddle100, saddle200,
                          saddle300, saddle400, saddle500,
                          saddle600, saddle700]

        ok_linkers = [linkerH1a, linkerH1b]
        ok_saddles = [saddle1000]
        self._build_and_validate(doomed_linkers, doomed_saddles,
                                 ok_linkers, ok_saddles)

    def testBasinSaddleFinderDoubleDiamondWithStubs(self):
        """
        Ensure double diamond with 3 dead end stubs produces expected results.
               |--(H1a)-------Saddle 1000 ------(H1b)------|        |--(L3a - x)--Saddle 300 (x)
         Summit1--(L1a - x)----Saddle 100 (x) --(L1b - x)----Summit2---(L4a - x)--Saddle 400 (x)
               |--(L2a - x)--Saddle 200 (x) ----(L2b - x)--|        |--(L5a - x)--Saddle 500 (x)
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        saddle1000 = Saddle(1000, 1000, 1000)
        saddle100 = Saddle(100, 100, 100)
        saddle200 = Saddle(200, 200, 200)
        saddle300 = Saddle(300, 300, 300)
        saddle400 = Saddle(400, 400, 400)
        saddle500 = Saddle(500, 500, 500)

        linkerL1a = Linker(summit1, saddle100)
        linkerL1b = Linker(summit2, saddle100)
        linkerL2a = Linker(summit1, saddle200)
        linkerL2b = Linker(summit2, saddle200)
        linkerL3a = Linker(summit2, saddle300)
        linkerL4a = Linker(summit2, saddle400)
        linkerL5a = Linker(summit2, saddle500)

        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit2, saddle1000)

        doomed_linkers = [linkerL1a, linkerL1b,
                          linkerL2a, linkerL2b,
                          linkerL3a,
                          linkerL4a,
                          linkerL5a,
                          ]
        doomed_saddles = [saddle100, saddle200,
                          saddle300, saddle400,
                          saddle500]

        ok_linkers = [linkerH1a, linkerH1b]
        ok_saddles = [saddle1000]
        self._build_and_validate(doomed_linkers, doomed_saddles,
                                 ok_linkers, ok_saddles)

    def testBasinSaddleFinderDoubleDiamondWithStubsOnBothSides(self):
        """
        Ensure double diamond with 3 dead end stubs produces expected results.
               |--(H1a)-------Saddle 1000 ------(H1b)------|        |--(L3a - x)--Saddle 300 (x)
         Summit1--(L1a - x)----Saddle 100 (x) --(L1b - x)----Summit2
               |--(L2a - x)--Saddle 200 (x) ----(L2b - x)--|        |--(L5a - x)--Saddle 500 (x)
               |--(L4a - x)--Saddle 400 (x) <-- stub
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        saddle1000 = Saddle(1000, 1000, 1000)
        saddle100 = Saddle(100, 100, 100)
        saddle200 = Saddle(200, 200, 200)
        saddle300 = Saddle(300, 300, 300)
        saddle400 = Saddle(400, 400, 400)
        saddle500 = Saddle(500, 500, 500)

        linkerL1a = Linker(summit1, saddle100)
        linkerL1b = Linker(summit2, saddle100)
        linkerL2a = Linker(summit1, saddle200)
        linkerL2b = Linker(summit2, saddle200)
        linkerL3a = Linker(summit2, saddle300)
        linkerL4a = Linker(summit1, saddle400)
        linkerL5a = Linker(summit2, saddle500)

        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit2, saddle1000)

        doomed_linkers = [linkerL1a, linkerL1b,
                          linkerL2a, linkerL2b,
                          linkerL3a,
                          linkerL4a,
                          linkerL5a,
                          ]
        doomed_saddles = [saddle100, saddle200,
                          saddle300, saddle400,
                          saddle500]

        ok_linkers = [linkerH1a, linkerH1b]
        ok_saddles = [saddle1000]
        self._build_and_validate(doomed_linkers, doomed_saddles,
                                 ok_linkers, ok_saddles)

    def testBasinSaddleFinderDoubleDiamondWithLongStub(self):
        """
        Ensure double diamond with 3 dead end stubs produces expected results.
               |--(H1a)-------Saddle 1000 ------(H1b)------|        |--(H0a)--Saddle 001 --(H0b)--|
         Summit1--(L1a - x)----Saddle 100 (x) --(L1b - x)----Summit2                              |
               |--(L2a - x)--Saddle 200 (x) ----(L2b - x)--|          Saddle 300 (x)-(L3a -x)--Summit100
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        summit100 = Summit(100, 100, 100000)

        saddle1000 = Saddle(1000, 1000, 1000)
        saddle100 = Saddle(100, 100, 100)
        saddle200 = Saddle(200, 200, 200)
        saddle300 = Saddle(300, 300, 300)
        saddle001 = Saddle(1, 1, 1)

        linkerL1a = Linker(summit1, saddle100)
        linkerL1b = Linker(summit2, saddle100)
        linkerL2a = Linker(summit1, saddle200)
        linkerL2b = Linker(summit2, saddle200)
        linkerL3a = Linker(summit100, saddle300)

        linkerH0a = Linker(summit2, saddle001)
        linkerH0b = Linker(summit100, saddle001)
        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit2, saddle1000)

        doomed_linkers = [linkerL1a, linkerL1b,
                          linkerL2a, linkerL2b,
                          linkerL3a,
                          ]
        doomed_saddles = [saddle100, saddle200,
                          saddle300]

        ok_linkers = [linkerH1a, linkerH1b,
                      linkerH0a, linkerH0b]
        ok_saddles = [saddle1000, saddle001]

        self._build_and_validate(doomed_linkers, doomed_saddles,
                                 ok_linkers, ok_saddles)

    def testBasinSaddleFinderTransitive(self):
        r"""
        Ensure lowest 2 Saddles and linkers in a diamond configuration
        are disqualified
               /--(H1a)------Saddle 1000 -----(H1b)-----\
        Summit1                                         Summit2
               \                                       /
                (L1a)                                 /
                \                                    /
                Saddle 100                          (L2b - x)
                 \                                 /
                 (L1b)                            /
                  \                              /
                  Summit3--(L2a-x)--Saddle 1(x)--
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        summit3 = Summit(3, 3, 30000)
        saddle1 = Saddle(1, 1, 1)
        saddle100 = Saddle(100, 100, 100)
        saddle1000 = Saddle(1000, 1000, 1000)

        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit2, saddle1000)

        linkerL1a = Linker(summit1, saddle100)
        linkerL1b = Linker(summit3, saddle100)
        linkerL2a = Linker(summit3, saddle1)
        linkerL2b = Linker(summit2, saddle1)

        doomed_linkers = [linkerL2a, linkerL2b]
        doomed_saddles = [saddle1]

        ok_linkers = [linkerH1a, linkerH1b, linkerL1a, linkerL1b]
        ok_saddles = [saddle100, saddle1000]

        self._build_and_validate(doomed_linkers, doomed_saddles,
                                 ok_linkers, ok_saddles)

    def testBasinSaddleFinderMultiTransitive(self):
        """
        Ensure Transitive multi loops are applied accurately
               |-(L2a - x)----Saddle 200 (x) --(L2b - x)---Summit210--(L2c)--Saddle 201 --(L2d)--|
               |-(L3a - x)----Saddle 300 (x) --(L3b - x)---Summit310--(L3c)--Saddle 301 --(L3d)--|
        Summit1--(L4a - x)----Saddle 400 (x) --(L4b - x)---Summit410--(L4c)--Saddle 401 --(L4d)--Summit2
               |--(L5a - x)--Saddle 500 (x) ----(L5b - x)--Summit510--(L5c)--Saddle 501 --(L5d)--|
               |--(H1a - x)--Saddle 1000 (x)----(H1b - x)--Summit1010--(H1c)--Saddle 1001-(H1d)--|
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        summit210 = Summit(210, 210, 21000)
        summit310 = Summit(310, 310, 31000)
        summit410 = Summit(410, 410, 41000)
        summit510 = Summit(510, 510, 51000)
        summit1010 = Summit(1010, 1010, 101000)

        saddle1000 = Saddle(1000, 1000, 1000)
        saddle200 = Saddle(200, 200, 200)
        saddle300 = Saddle(300, 300, 300)
        saddle400 = Saddle(400, 400, 400)
        saddle500 = Saddle(500, 500, 500)
        saddle201 = Saddle(201, 201, 201)
        saddle301 = Saddle(301, 301, 301)
        saddle401 = Saddle(401, 401, 401)
        saddle501 = Saddle(501, 501, 501)
        saddle1001 = Saddle(601, 601, 601)

        linkerL2a = Linker(summit1, saddle200)
        linkerL2b = Linker(summit210, saddle200)
        linkerL2c = Linker(summit210, saddle201)
        linkerL2d = Linker(summit2, saddle201)

        linkerL3a = Linker(summit1, saddle300)
        linkerL3b = Linker(summit310, saddle300)
        linkerL3c = Linker(summit310, saddle301)
        linkerL3d = Linker(summit2, saddle301)

        linkerL4a = Linker(summit1, saddle400)
        linkerL4b = Linker(summit410, saddle400)
        linkerL4c = Linker(summit410, saddle401)
        linkerL4d = Linker(summit2, saddle401)

        linkerL5a = Linker(summit1, saddle500)
        linkerL5b = Linker(summit510, saddle500)
        linkerL5c = Linker(summit510, saddle501)
        linkerL5d = Linker(summit2, saddle501)

        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit1010, saddle1000)
        linkerH1c = Linker(summit1010, saddle1001)
        linkerH1d = Linker(summit2, saddle1001)

        doomed_linkers = [linkerL2a, linkerL2b,
                          linkerL3a, linkerL3b,
                          linkerL4a, linkerL4b,
                          linkerL5a, linkerL5b,
                          ]
        doomed_saddles = [saddle200, saddle300, saddle400, saddle500]

        ok_linkers = [linkerH1a, linkerH1b, linkerH1c, linkerH1d,
                      linkerL2c, linkerL2d,
                      linkerL3c, linkerL3d,
                      linkerL4c, linkerL4d,
                      linkerL5c, linkerL5d,
                      ]
        ok_saddles = [saddle201, saddle301, saddle401, saddle501,
                      saddle1000, saddle1001]
        self._build_and_validate(doomed_linkers, doomed_saddles,
                                 ok_linkers, ok_saddles)

    def testBasinSaddleFinderMultiTransitiveWithEqualHeight(self):
        """
        Ensure Transitive multi loops with equal height candidates
        (alternative basin saddles) are properly identified.

               |-(L2a - x)----Saddle 200 (x) --(L2b - x)---Summit210--(L2c)--Saddle 200a --(L2d)--|
               |-(L3a - x)----Saddle 300 (x) --(L3b - x)---Summit310--(L3c)--Saddle 301 --(L3d)--|
        Summit1--(L4a - x)----Saddle 400 (x) --(L4b - x)---Summit410--(L4c)--Saddle 400a --(L4d)--Summit2
               |--(L5a - x)--Saddle 500 (x) ----(L5b - x)--Summit510--(L5c)--Saddle 501 --(L5d)--|
               |--(H1a - x)--Saddle 1000 (x)----(H1b - x)--Summit1010--(H1c)--Saddle 1001-(H1d)--|
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        summit210 = Summit(210, 210, 21000)
        summit310 = Summit(310, 310, 31000)
        summit410 = Summit(410, 410, 41000)
        summit510 = Summit(510, 510, 51000)
        summit1010 = Summit(1010, 1010, 101000)

        saddle1000 = Saddle(1000, 1000, 1000)
        saddle200 = Saddle(200, 200, 200)
        saddle300 = Saddle(300, 300, 300)
        saddle400 = Saddle(400, 400, 400)
        saddle500 = Saddle(500, 500, 500)
        saddle200a = Saddle(201, 201, 200)
        saddle301 = Saddle(301, 301, 301)
        saddle400a = Saddle(401, 401, 400)
        saddle501 = Saddle(501, 501, 501)
        saddle1001 = Saddle(601, 601, 601)

        linkerL2a = Linker(summit1, saddle200)
        linkerL2b = Linker(summit210, saddle200)
        linkerL2c = Linker(summit210, saddle200a)
        linkerL2d = Linker(summit2, saddle200a)

        linkerL3a = Linker(summit1, saddle300)
        linkerL3b = Linker(summit310, saddle300)
        linkerL3c = Linker(summit310, saddle301)
        linkerL3d = Linker(summit2, saddle301)

        linkerL4a = Linker(summit1, saddle400)
        linkerL4b = Linker(summit410, saddle400)
        linkerL4c = Linker(summit410, saddle400a)
        linkerL4d = Linker(summit2, saddle400a)

        linkerL5a = Linker(summit1, saddle500)
        linkerL5b = Linker(summit510, saddle500)
        linkerL5c = Linker(summit510, saddle501)
        linkerL5d = Linker(summit2, saddle501)

        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit1010, saddle1000)
        linkerH1c = Linker(summit1010, saddle1001)
        linkerH1d = Linker(summit2, saddle1001)

        doomed_linkers = [linkerL2a, linkerL2b,
                          linkerL3a, linkerL3b,
                          linkerL4a, linkerL4b,
                          linkerL5a, linkerL5b,
                          ]
        doomed_saddles = [saddle200, saddle300, saddle400, saddle500]

        ok_linkers = [linkerH1a, linkerH1b, linkerH1c, linkerH1d,
                      linkerL2c, linkerL2d,
                      linkerL3c, linkerL3d,
                      linkerL4c, linkerL4d,
                      linkerL5c, linkerL5d,
                      ]
        ok_saddles = [saddle200a, saddle301, saddle400a, saddle501,
                      saddle1000, saddle1001]
        self._build_and_validate(doomed_linkers, doomed_saddles,
                                 ok_linkers, ok_saddles)

        # Ensure Basin Saddle alternatives are accounted for.
        self.assertEqual(saddle200a.basinSaddleAlternatives, [saddle200])
        self.assertEqual(saddle200.basinSaddleAlternatives, [saddle200a])
        self.assertEqual(saddle400a.basinSaddleAlternatives, [saddle400])
        self.assertEqual(saddle400.basinSaddleAlternatives, [saddle400a])

    def testBasinSaddleFinderIgnoreEdgeEffectSaddle(self):
        """
        Ensure diamond with a low edge effect is ignored
               |--(H1a)-------Saddle 1000 ------(H1b)------|
         Summit1                                           Summit2
               |--(L1a)------Saddle 100 (edge)--(L1b)------|
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        saddle1000 = Saddle(1000, 1000, 1000)
        saddle100 = Saddle(100, 100, 100)
        saddle100.edgeEffect = True

        linkerL1a = Linker(summit1, saddle100)
        linkerL1b = Linker(summit2, saddle100)

        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit2, saddle1000)

        doomed_linkers = []
        doomed_saddles = []

        ok_linkers = [linkerH1a, linkerH1b, linkerL1a, linkerL1b]
        ok_saddles = [saddle1000, saddle100]
        self._build_and_validate(doomed_linkers, doomed_saddles,
                                 ok_linkers, ok_saddles)

    def testBasinSaddleFinderDiamondWithStub(self):
        r"""
        Ensure lowest 2 Saddles and linkers in a diamond configuration are
        disqualified
               /--(H1)------Saddle 1000 --(H2)-----\   /----(SS1a - x)-\
        Summit1-                                   Summit2     Saddle 100 (x)
               \--(L1 - x)-Saddle 1 (x) -(L2 - x)--/   \----(SS1b -x)-/
        """
        summit1 = Summit(1, 1, 10000)
        summit2 = Summit(2, 2, 20000)
        saddle1000 = Saddle(1000, 1000, 1000)
        saddle100 = Saddle(100, 100, 100)
        saddle1 = Saddle(1, 1, 1)

        linkerSS1a = Linker(summit1, saddle100)
        linkerSS1b = Linker(summit1, saddle100)

        linkerL1a = Linker(summit1, saddle1)
        linkerL1b = Linker(summit2, saddle1)

        linkerH1a = Linker(summit1, saddle1000)
        linkerH1b = Linker(summit2, saddle1000)

        doomed_linkers = [linkerL1a, linkerL1b, linkerSS1a, linkerSS1b]
        doomed_saddles = [saddle1, saddle100]

        ok_linkers = [linkerH1a, linkerH1b]
        ok_saddles = [saddle1000]
        self._build_and_validate(doomed_linkers, doomed_saddles,
                                 ok_linkers, ok_saddles)

    def _build_and_validate(self, doomed_linkers, doomed_saddles,
                            ok_linkers, ok_saddles):

        all_linkers = ok_linkers + doomed_linkers

        for linker in all_linkers:
            linker.add_to_remote_saddle_and_summit(ignoreDuplicates=False)

        saddles = SaddlesContainer(doomed_saddles + ok_saddles)

        cf = BasinSaddleFinder(saddles)
        cf.disqualify_basin_saddles()

        for doomed_linker in doomed_linkers:
            self.assertTrue(doomed_linker.disqualified,
                            "{} produced unexpected results".format(
                                doomed_linker))

        for doomed_saddle in doomed_saddles:
            self.assertTrue(doomed_saddle.disqualified,
                            "{} produced unexpected results".format(
                                doomed_saddle))

        for ok_linker in ok_linkers:
            self.assertFalse(ok_linker.disqualified,
                             "{} produced unexpected results".format(
                                 ok_linker))

        for ok_saddle in ok_saddles:
            self.assertFalse(ok_saddle.disqualified,
                             "{} produced unexpected results".format(
                                 ok_saddle))
