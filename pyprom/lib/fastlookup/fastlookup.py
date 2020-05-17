"""
pyProm: Copyright 2019

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict
from ..locations.base_gridpoint import BaseGridPoint
from ..locations.gridpoint import GridPoint
from ..locations.base_coordinate import BaseCoordinate
from ..locations.spot_elevation import SpotElevation

class FastLookup:
    """
    Fastlookup is a simple object for storing the value of a 2D array in a
    hash. In pyProm terms, these are typically used to mark if an X, Y
    coordinate has been explored, but can also be used to store other values
    associated with any sort of 2d array.
    """
    def __init__(self, points, lookup_hash = None, default=None, only_existence=False):
        """
        :param points: list of points
        :param lookup_hash: a prebuilt lookup hash.
        :param default: default value for an unassigned array value.
        :param only_existence: if building from points,
        """
        self.lookup_hash = defaultdict(dict) if not lookup_hash else lookup_hash
        self.default = default

        # don't bother building points, we've already got a lookup_hash set.
        if self.lookup_hash:
            return

        # just go with an empty defaultdict(dict).

        if not points:
            pass
        # for performance sake, only check the first list item.
        elif isinstance(points[0], tuple):
            # (x, y)
            if len(points[0]) == 2:
                for pt in points:
                    self.lookup_hash[pt[0]][pt[1]] = True
            # (x, y, val)
            if len(points[0]) == 3:
                for pt in points:
                    self.lookup_hash[pt[0]][pt[1]] = pt[2] if not only_existence else True
        # GridPoints track elevation unless only_existence is true
        elif isinstance(points[0], GridPoint):
            for pt in points:
                self.lookup_hash[pt.x][pt.y] = pt.elevation if not only_existence else True
        # BaseGridPoints just check existence.
        elif isinstance(points[0], BaseGridPoint):
            for pt in points:
                self.lookup_hash[pt.x][pt.y] = True
        # SpotElevation track elevation unless only_existence is true
        elif isinstance(points[0], SpotElevation):
            for pt in points:
                self.lookup_hash[pt.latitude][pt.longitude] = pt.elevation if not only_existence else True
        # BaseCoordinate just check existence.
        elif isinstance(points[0], BaseCoordinate):
            for pt in points:
                self.lookup_hash[pt.latitude][pt.longitude] = True

    def set(self, x, y, value):
        """
        :param x: first dimension
        :param y: second dimension
        :param value: value to be assigned to x,y
        """
        self.lookup_hash[x][y] = value

    def get(self, x, y):
        """
        :param x: first dimension
        :param y: second dimension
        :return: value associated with that x,y, or default if unassigned
        """
        return self.lookup_hash[x].get(y, self.default)

    def remove(self, x, y):
        """
        :param x: first dimension
        :param y: second dimension
        """
        self.lookup_hash[x][y] = None

    def slice(self, lowerx, lowery, upperx, uppery):
        """
        Generates a slice of this fastlookup using upper/lower x/y bounds
        :param lowerx:
        :param lowery:
        :param upperx:
        :param uppery:
        :return: FastLookup slice
        """
        new_lookup = defaultdict(dict)
        for x in self.lookup_hash.keys():
            if x <= upperx and x >= lowerx:
                for y in x.keys():
                    if y <= uppery and y >= lowery:
                        new_lookup[x][y] = self.lookup_hash[x][y]
        return FastLookup(None, lookup_hash=new_lookup, default=self.default)

