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
    A Linker links one single :class:`pyprom.lib.locations.summit.Summit`
    with one single :class:`pyprom.lib.locations.saddle.Saddle`
    """

    def __init__(self, summit, saddle, path=WalkPath([]), id=None):
        """
        :param summit: Summit this linker links.
        :type summit: :class:`pyprom.lib.locations.summit.Summit`
        :param saddle: Saddle this linker links.
        :type saddle: :class:`pyprom.lib.locations.saddle.Saddle`
        :param path: data containing the path taken to link this
         Summit and Saddle
        :type path: :class:`pyprom.lib.containers.walkpath.WalkPath`
        :param str id: id for this object.
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
        Calculates how much higher the summit is than the Saddle in meters

        :return: altitude difference between saddle and summit in meters.
        :rtype: float, int
        """
        return self.summit.elevation - self.saddle.elevation

    @property
    def prom_ft(self):
        """
        Calculates how much higher the summit is than the Saddle in feet

        :return: altitude difference between saddle and summit in feet.
        :rtype: float, int
        """
        return self.summit.feet - self.saddle.feet

    def saddles_connected_via_summit(self, skipDisqualified=True,
                                     exemptLinkers={}):
        """
        Returns all saddles connected to the
        :class:`pyprom.lib.locations.summit.Summit` that this
        :class:`Linker` links.

        :param bool skipDisqualified: If true, disregard disqualified
         remote linkers.
        :param exemptLinkers: hash of linkers regarded as
         dead.
        :type exemptLinkers: dict(linker.id: bool)
        :return: list of Saddles
        :rtype list(:class:`pyprom.lib.locations.saddle.Saddle`)
        """
        if skipDisqualified and self.disqualified:
            return []
        # This linker is already exempt.
        if exemptLinkers.get(self.id):
            return []
        return [linker.saddle for linker in self.summit.saddles if
                _linker_ok(linker, skipDisqualified, exemptLinkers)]

    def summits_connected_via_saddle(self, skipDisqualified=True,
                                     exemptLinkers={}):
        """
        Returns all summits connected to the
        :class:`pyprom.lib.locations.saddle.Saddle` that this
        :class:`Linker` links.

        :param bool skipDisqualified: If true, disregard disqualified
         remote linkers.
        :param exemptLinkers: hash of linkers regarded as
         dead.
        :type exemptLinkers: dict(linker.id: bool)
        :return: list of Summits
        :rtype: list(:class:`pyprom.lib.locations.summit.Summit`)
        """
        if skipDisqualified and self.disqualified:
            return []
        # This linker is already exempt.
        if exemptLinkers.get(self.id):
            return []
        return [linker.summit for linker in self.saddle.summits if
                _linker_ok(linker, skipDisqualified, exemptLinkers)]

    def _help_exclude_self(self, linker, excludeSelf):
        """
        Determine if this :class:`Linker` is to be included in list.

        :param linker: :class:`Linker`
        :param bool excludeSelf: exclude self from results.
        :return: If this linker is to be included in a list.
        :rtype: bool
        """
        if excludeSelf:
            if self.id == linker.id:
                return False
        return True

    def linkers_to_saddles_connected_via_summit(self, excludeSelf=True,
                                                skipDisqualified=True):
        """
        Returns linkers linking Saddles to the Summit this linker links.

        :param bool exclude: exclude this linker from results.
        :param bool skipDisqualified: If true, do not return disqualified
         linkers
        :return: list of linkers to saddles connected to the summit this
         linker links
        :rtype: list(:class:`Linker`)
        """
        return [linker for linker in self.summit.saddles
                if _linker_ok(linker, skipDisqualified, {}) and
                self._help_exclude_self(linker, excludeSelf)]

    def linkers_to_summits_connected_via_saddle(self, excludeSelf=True,
                                                skipDisqualified=True):
        """
        Returns linkers linking Summits to the Saddle this linker links.

        :param bool exclude: exclude this linker from results.
        :param bool skipDisqualified: If true, do not return disqualified
         linkers
        :return: list of linkers to summits connected to the saddle this
         linker links
        :rtype: list(:class:`Linker`)
        """
        return [linker for linker in self.saddle.summits
                if _linker_ok(linker, skipDisqualified, {}) and
                self._help_exclude_self(linker, excludeSelf)]

    def add_to_remote_saddle_and_summit(self, ignoreDuplicates=True):
        """
        Safely adds this linker to the remote
        :class:`pyprom.lib.locations.saddle.Saddle` and
        :class:`pyprom.lib.locations.summit.Summit`

        :param bool ignoreDuplicates: if True, will not add self to feature
         if already present.
        """
        if ignoreDuplicates:
            if self not in self.summit.saddles:
                self.summit.addSaddleLinker(self)
            if self not in self.saddle.summits:
                self.saddle.addSummitLinker(self)
        else:
            self.summit.addSaddleLinker(self)
            self.saddle.addSummitLinker(self)

    def to_dict(self, referenceById=True, noWalkPath=True):
        """
        Create the dictionary representation of this object.

        :param bool referenceById: only use ID of linked objects.
        :param bool noWalkPath: exclude WalkPath
        :return: dict() representation of :class:`Linker`
        :rtype: dict()
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
        Create this object from dictionary representation

        :return: a new Linker
        :rtype: :class:`Linker`
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
        Produces the hash representation of this object.

        :return: Hash representation of this object
        :rtype: str
        """
        return hash(self.saddle.__hash__() + self.summit.__hash__())

    def __eq__(self, other):
        """
        Determines if this object is equal to another.

        :param other: :class:`Linker` to be compared against
        :type other: :class:`Linker`
        :return: equality
        :rtype: bool
        :raises: TypeError if other not of :class:`Linker`
        """
        isLinker(other)
        return [self.summit, self.saddle, self.path] ==\
               [other.summit, other.saddle, other.path]

    def __ne__(self, other):
        """
        Determines if this object is not equal to another.

        :param other: :class:`Linker` to be compared against
        :type other: :class:`Linker`
        :return: inequality
        :rtype: bool
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
    Check if passed in object is a :class:`Linker`

    :param linker: object under scrutiny
    :raises: TypeError if other not of :class:`Summit`
    """
    if not isinstance(linker, Linker):
        raise TypeError("Expected Linker Object.")


def _linker_ok(linker, skipDisqualified, exemptLinkers={}):
    """
    Determine if :class:`Linker` is either disqualified, or exempted.

    :param linker: object to be tested
    :type linker: :class:`Linker`
    :param bool skipDisqualified: If we regard Disqualified Links as dead
    :param dict exemptLinkers: {linker.id: bool} hash of linkers regarded as dead.
    :return: if linker is OK or not.
    :rtype: bool
    """
    if skipDisqualified:
        if linker.disqualified or exemptLinkers.get(linker.id):
            return False
        return True
    if exemptLinkers.get(linker.id):
        return False
    return True
