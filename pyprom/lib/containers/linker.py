"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""


class Linker(object):
    """
    Container for :class:`Linker` type lists.
    Allows for various list transformations.
    :param summit:
    :param saddle:
    :param path
    """
    def __init__(self, summit, saddle, path):
        self.summit = summit
        self.saddle = saddle
        self.path = path
        self.disqualified = False

    @property
    def prom(self):
        return self.summit.elevation - self.saddle.elevation

    @property
    def prom_ft(self):
        return self.summit.feet - self.saddle.feet


    def __repr__(self):
        return "<Linker> {} -> {} {}pft {}pm".format(
            self.saddle,
            self.summit,
            self.prom_ft,
            self.prom)