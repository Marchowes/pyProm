"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""


class Linker(object):
    """
    A Linker links 1 :class:`Summit` with 1 :class:`Saddle`
    :param summit: :class:`Summit`
    :param saddle: :class:`Saddle`
    :param path: data containing the path taken to link this Summit and Saddle
    """
    def __init__(self, summit, saddle, path):
        self.summit = summit
        self.saddle = saddle
        self.path = path
        # disqualified means this Linker has been disqualified from further analysis, but not deleted.
        self.disqualified = False

    @property
    def prom(self):
        """
        :return: altitude difference between saddle and summit in meters.
        """
        return self.summit.elevation - self.saddle.elevation

    @property
    def prom_ft(self):
        """
        :return: altitude difference between saddle and summit in feet.
        """
        return self.summit.feet - self.saddle.feet

    @property
    def summit_saddles(self):
        """
        :return: list of saddles connected to the summit this linker links
        """
        return [x.saddle for x in self.summit.saddles]

    @property
    def saddle_summits(self):
        """
        :return: list of summits connected to the saddle the linker links
        """
        return [x.summit for x in self.saddle.summits]

    def __repr__(self):
        return "<Linker> {} -> {} {}promFt {}promM".format(
                self.saddle,
                self.summit,
                self.prom_ft,
                self.prom)

    def __hash__(self):
        return hash((round(self.summit.latitude, 6),
                     round(self.summit.longitude, 6),
                     round(self.saddle.latitude, 6),
                     round(self.saddle.longitude, 6)))

    def __eq__(self, other):
        return [self.summit, self.saddle] ==\
               [other.summit, other.saddle]

    __unicode__ = __str__ = __repr__