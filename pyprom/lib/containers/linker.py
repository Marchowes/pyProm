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


    def saddles_connected_via_summit(self, skipDisqualified=True,
                                     exemptLinkers={}):
        """
        Returns all saddles connected to the :class:`Summit` that this
         :class:`Linker` links.
        :param skipDisqualified: (bool), if true, disregard disqualified
         remote linkers.
        :param exemptLinkers: {linker.id: bool} hash of linkers regarded as
         dead.
        :return: list of saddles
        """
        if exemptLinkers.get(self.id):
            return []
        if skipDisqualified and self.disqualified:
            return []
        return [linker.saddle for linker in self.summit.saddles if
                _linker_ok(linker, skipDisqualified, exemptLinkers)]

    def summits_connected_via_saddle(self, skipDisqualified=True, exemptLinkers={}):
        """
        Returns all summits connected to the :class:`Saddle` that this
         :class:`Linker` links.
        :param skipDisqualified: (bool), if true, disregard disqualified
         remote linkers.
        :param exemptLinkers: {linker.id: bool} hash of linkers regarded as
         dead.
        :return: list of summits
        """
        if exemptLinkers.get(self.id):
            return []
        if skipDisqualified and self.disqualified:
            return []
        return [linker.summit for linker in self.saddle.summits if
                _linker_ok(linker, skipDisqualified, exemptLinkers)]

    def _help_exclude_self(self, linker, excludeSelf):
        """
        Determine if this linker is to be included in list.
        :param linker: :class:`Linker`
        :param excludeSelf: bool
        :return: bool
        """
        if excludeSelf:
            if self.id == linker.id:
                return False
        return True

    def linkers_to_saddles_connected_via_summit(self, excludeSelf=True,
                                                skipDisqualified=True):
        """
        :param: exclude (bool) exclude this linker.
        :param: skipDisqualified (bool) If true, do not return disqualified
        linkers
        :return: list of linkers to saddles connected to the summit the linker links
        """


        return [linker for linker in self.summit.saddles
                if _linker_ok(linker, skipDisqualified, {})
                and self._help_exclude_self(linker, excludeSelf)]

    def linkers_to_summits_connected_via_saddle(self, excludeSelf=True,
                                                skipDisqualified=True):
        """
        :param: excludeSelf (bool) exclude self from results
        :param: skipDisqualified (bool) If true, do not return disqualified
        linkers
        :return: list of linkers to summits connected to the saddle the
        linker links
        """
        return [linker for linker in self.saddle.summits
                if _linker_ok(linker, skipDisqualified, {}) and
                self._help_exclude_self(linker, excludeSelf)]

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
        Loads the dict() representation of :class:`Linker`
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
        return hash(self.saddle.__hash__() + self.summit.__hash__())

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

def _linker_ok(linker, skipDisqualified, exemptLinkers={}):
    """
    :param linker: :class:`Linker` object to be tested
    :param skipDisqualified: (bool), if we regard Disqualified Links as dead
    :param exemptLinkers: {linker.id: bool} hash of linkers regarded as dead.
    :return: bool
    """
    if skipDisqualified:
        if linker.disqualified or exemptLinkers.get(linker.id):
            return False
        return True
    if exemptLinkers.get(linker.id):
        return False
    return True