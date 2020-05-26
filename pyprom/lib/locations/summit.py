"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing Summit data.
"""

from .spot_elevation import SpotElevation
from ..containers.multipoint import MultiPoint
from ..containers.linker import isLinker
from ..util import randomString


class Summit(SpotElevation):
    """
    | Summit object stores relevant summit data.
    | A Summit is by definition a point, or set of equal height points
    | (MultiPoint) which have all points around it's perimeter lower
    | that the point or Multipoint. A Summit is a Child object of
    | :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
    |
    | Examples:
    |
    | Single Point Summit:
    | ``[0][0][0]``
    | ``[0][1][0]   [1] = Summit``
    | ``[0][0][0]``
    |
    |
    | MultiPoint Summit:
    | ``[0][0][0][0]``
    | ``[0][1][1][0]  [1][1] = Summit``
    | ``[0][0][0][0]``
    """

    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        """
        :param latitude: latitude in dotted decimal
        :type latitude: int, float
        :param longitude: longitude in dotted decimal
        :type longitude: int, float
        :param elevation: elevation in meters
        :type elevation: int, float
        :param multipoint: MultiPoint object
        :type multipoint: :class:`pyprom.lib.containers.multipoint.MultiPoint`,
         None
        """
        super(Summit, self).__init__(latitude, longitude,
                                     elevation, *args, **kwargs)
        self.multipoint = kwargs.get('multipoint', [])
        self.id = kwargs.get('id', 'su:' + randomString())
        # saddles contains a list of linker objects linking this summit to a
        # saddle. These are populated by :class:`Walk`
        self.saddles = list()

        self.disqualified = False
        self.localHighest = None
        self.parent = None
        self.lprBoundary = []
        self.lprPaths = None
        self.domain = None

    def addSaddleLinker(self, linker):
        """
        Adds linker to this :class:`Summit`

        :param linker: linker to be added
        :type linker: :class:`pyprom.lib.containers.linker.Linker`
        """
        isLinker(linker)
        self.saddles.append(linker)

    def feature_neighbors(self):
        """
        :return: returns all linked Saddles.
         This is, in effect, an interface.
        :rtype: list(:class:`pyprom.lib.locations.saddle.Saddle`)
        """
        return [feature.saddle for feature in self.saddles]

    @property
    def neighbors(self, filterDisqualified=True):
        """
        neighbors will return all neighboring summits by way of the
        connected saddle.
        This function will filter out redundant neighbors.

        :param bool filterDisqualified: Filter out disqualified linkers.
        :return: list of unique neighboring summits by way of
         neighboring summits excluding self.
        :rtype: list(:class:`Summit`)
        """
        neighborSet = set(self.all_neighbors(filterDisqualified))
        neighborSet.discard(self)
        return list(neighborSet)

    def all_neighbors(self, filterDisqualified=True):
        """
        all_neighbors will return all neighboring summits by way of the saddle.
        This function deliberately makes no effort to filter out redundant
        neighbors.

        :param bool filterDisqualified: Filter out disqualified linkers.
        :return: list of neighboring
         :class:`pyprom.lib.locations.summit.Summit`s by way of linked
         :class:`pyprom.lib.locations.saddle.Saddle`.
        """
        neighbors = []
        if filterDisqualified:
            [neighbors.extend(linker.summits_connected_via_saddle())
                for linker in self.saddles if not linker.disqualified]
        else:
            [neighbors.extend(linker.summits_connected_via_saddle(
                skipDisqualified=False))
                for linker in self.saddles]
        return neighbors

    def to_dict(self, referenceById=True):
        """
        Create the dictionary representation of this object.

        :param bool referenceById: reference linekd Saddles by ID.
        :return: dict() representation of :class:`Summit`
        :rtype: dict()
        """
        to_dict = {'lat': self.latitude,
                   'lon': self.longitude,
                   'ele': self.elevation,
                   'edge': self.edgeEffect,
                   'edgepoints': self.edgePoints,
                   'id': self.id
                   }
        # TODO: localhighest (for divide tree time)
        if self.multipoint:
            to_dict['multipoint'] = self.multipoint.to_dict()
        # These values are not unloaded by from_dict()
        if referenceById:
            to_dict['saddles'] = [x.id for x in self.saddles]  # linker by ID
        return to_dict

    @classmethod
    def from_dict(cls, summitDict, datamap=None):
        """
        Create this object from dictionary representation

        :param dict summitDict: dict representation of this object.
        :param datamap: Datamap to build this object from.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: a new Summit
        :rtype: :class:`Summit`
        """
        lat = summitDict['lat']
        long = summitDict['lon']
        elevation = summitDict['ele']
        edge = summitDict['edge']
        edgePoints = [tuple(pt) for pt in summitDict['edgepoints']]
        id = summitDict['id']
        multipoint = summitDict.get('multipoint', [])
        if multipoint:
            multipoint = MultiPoint.from_dict(multipoint, datamap=datamap)
        return cls(lat, long, elevation,
                   multipoint=multipoint,
                   edge=edge,
                   edgePoints=edgePoints,
                   id=id)

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<Summit> lat {} long {} {}ft {}m MultiPoint {}".format(
            self.latitude,
            self.longitude,
            self.feet,
            self.elevation,
            bool(self.multipoint))

    __unicode__ = __str__ = __repr__


def isSummit(summit):
    """
    Check if passed in object is a :class:`Summit`

    :param summit: object under scrutiny
    :raises: TypeError if other not of :class:`Summit`
    """
    if not isinstance(summit, Summit):
        raise TypeError("Expected Summit Object.")
