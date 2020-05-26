"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import unittest
from pyprom.tests.getData import gettestzip
from pyprom.dataload import GDALLoader
from pyprom.domain_map import DomainMap
from pyprom.lib.logic.shortest_path_by_points import (closest_point_by_distance_brute_force,
                                                      closest_point_by_distance_kdtree,
                                                      find_closest_points,
                                                      closest_points_between_sets_brute_force,
                                                      closest_points_between_sets_kdtree,
                                                      find_closest_point_by_distance_map
                                                      )

class ShortestPathByPointsTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set Up Tests."""
        gettestzip()
        cls.datafile = GDALLoader('/tmp/N44W072.hgt')
        cls.datamap = cls.datafile.datamap
        cls.someslice = cls.datamap.subset(1000, 1000, 100, 100)
        cls.domain = DomainMap(cls.someslice)
        cls.domain.run(superSparse=True, rebuildSaddles=False)

    def testKDTreeAndBruteForceSameResultsClosestPoints(self):
        """
        Ensure closest points algorithms all return same values
        """
        for saddle in self.domain.saddles:
            bf = closest_points_between_sets_brute_force(saddle.highShores[0], saddle.highShores[1], self.someslice)
            kd = closest_points_between_sets_kdtree(saddle.highShores[0], saddle.highShores[1], self.someslice)
            com = find_closest_points(saddle.highShores[0], saddle.highShores[1], self.someslice)
            # look at distance, point might be different since multiple points can have the same distance.
            self.assertEqual(bf[2], kd[2])
            self.assertEqual(kd[2], com[2])

    def testKDTreeAndBruteForceSameResultsClosestPointsMap(self):
        """
        Ensure closest points map algorithms all return same values
        """
        for saddle in self.domain.saddles:
            bf = closest_point_by_distance_brute_force(saddle.highShores[0], saddle.highShores[1])
            kd = closest_point_by_distance_kdtree(saddle.highShores[0], saddle.highShores[1])
            com = find_closest_point_by_distance_map(saddle.highShores[0], saddle.highShores[1])
            self.assertEqual(bf, kd)
            self.assertEqual(kd, com)