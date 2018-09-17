"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""

from .walkpath import WalkPath
from ..util import randomString


class Linker:
    """
    A Linker links 1 :class:`Summit` with 1 :class:`Saddle`
    :param summit: :class:`Summit`
    :param saddle: :class:`Saddle`
    :param path: data containing the path taken to link this Summit and Saddle
    """

    def __init__(self, summit, saddle, path=WalkPath([]), id=None):
        """
        :param summit: :class:`Summit`
        :param saddle: :class:`Saddle`
        :param path: :class:`WalkPath`
        :param id: id for this object.
        """
        self.summit = summit
        self.saddle = saddle
        self.path = path
        if id:
            self.id = id
        else:
            self.id = 'li:' + randomString()
        # disqualified means this Linker has been disqualified
        # from further analysis, but not deleted.
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

    @property
    def saddle_summit_linkers(self, exclude=True):
        """
        :return: list of linkers to summits connected to the saddle the linker links
        """
        if exclude:
            return [x for x in self.saddle.summits if x.summit != self.summit]
        return [x for x in self.saddle.summits]

    @property
    def summit_saddle_linkers(self, exclude=True):
        """
        :return: list of linkers to saddles connected to the summit the linker links
        """
        if exclude:
            return [x for x in self.summit.saddles if x.saddle != self.saddle]
        return [x for x in self.summit.saddles]

    def add_to_remote_saddle_and_summit(self):
        """
        Adds this linker to the remote :class:`Saddle` and :class:`Summit`
        """
        if self not in self.summit.saddles:
            self.summit.addSaddleLinker(self)
        if self not in self.saddle.summits:
            self.saddle.addSummitLinker(self)

    def to_dict(self, referenceById=True, noWalkPath=True):
        """
        :return: dict() representation of :class:`Linker`
        """
        to_dict = dict()
        to_dict['id'] = self.id
        if self.path and not noWalkPath:
            to_dict['path'] = self.path.to_dict()
        if self.disqualified:
            to_dict['disqualified'] = self.disqualified
        if referenceById:
            to_dict['saddle'] = self.saddle.id
            to_dict['summit'] = self.summit.id
        return to_dict

    @classmethod
    def from_dict(cls, linkerDict, saddlesContainer, summitsContainer):
        """
        :return: :class:`Linker`
        """
        pathDict = linkerDict.get('path', None)
        if pathDict:
            path = WalkPath.from_dict(pathDict)
        else:
            path = WalkPath([])
        saddle = saddlesContainer.fast_lookup[linkerDict['saddle']]

        summit = summitsContainer.fast_lookup[linkerDict['summit']]

        # create linker
        linker = cls(summit, saddle, path)
        # add linker to foreign saddles/summits
        linker.add_to_remote_saddle_and_summit()
        linker.disqualified = linkerDict.get('disqualified', False)
        return linker

    def __hash__(self):
        """
        Generates hash based on points.
        :return: string representation of hash
        """
        return hash((round(self.summit.latitude, 6),
                     round(self.summit.longitude, 6),
                     round(self.saddle.latitude, 6),
                     round(self.saddle.longitude, 6)))

    def __eq__(self, other):
        """
        Determines if Linker is equal to another.
        :param other: :class:`Linker` to be compared against
        :return: bool of equality
        :raises: TypeError if other not of :class:`Linker`
        """
        isLinker(other)
        return [self.summit, self.saddle, self.path] ==\
               [other.summit, other.saddle, other.path]

    def __ne__(self, other):
        """
        Determines if Linker is not equal to another.
        :param other: :class:`Linker` to be compared against
        :return: bool of inequality
        :raises: TypeError if other not of :class:`Linker`
        """
        isLinker(other)
        return [self.summit, self.saddle, self.path] !=\
               [other.summit, other.saddle, other.path]

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<Linker> {} -> {} {}promFt {}promM".format(
            self.saddle,
            self.summit,
            self.prom_ft,
            self.prom)
    __unicode__ = __str__ = __repr__


def isLinker(linker):
    """
    :param linker: object under scrutiny
    :raises: TypeError if other not of :class:`Summit`
    """
    if not isinstance(linker, Linker):
        raise TypeError("Expected Linker Object.")
