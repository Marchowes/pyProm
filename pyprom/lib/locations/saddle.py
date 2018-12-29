"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing Saddle data.
"""

from .spot_elevation import SpotElevation
from .base_gridpoint import BaseGridPoint
from ..containers.multipoint import MultiPoint
from ..containers.gridpoint import GridPointContainer
from ..containers.linker import isLinker
from ..util import randomString


class Saddle(SpotElevation):
    """
    Saddle object stores relevant saddle data.
    """

    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        """
        :param latitude: latitude in dotted decimal
        :param longitude: longitude in dotted decimal
        :param elevation: elevation in meters
        :param multiPoint: :class:`MultiPoint` object
        :param highShores: :class:`HighEdgeContainer` object
        :param edge: (bool) does this :class:`Saddle` have an edge
        Effect?
        """
        super(Saddle, self).__init__(latitude, longitude,
                                     elevation, *args, **kwargs)
        self.multiPoint = kwargs.get('multiPoint', [])
        self.highShores = kwargs.get('highShores', [])
        self.id = kwargs.get('id', 'sa:' + randomString())
        # List of linkers to summits
        self.summits = []
        # If this is set, this saddle was spun out of another
        # Saddle with less data.
        self.parent = None  # Parent
        # Saddles that have been spawned off of this one.
        self.children = kwargs.get('children', [])
        # All Edges lead to One summit.
        self.singleSummit = kwargs.get('singleSummit', False)
        # redundant saddle, but too low.
        self.tooLow = kwargs.get('tooLow', False)
        # alternative basin saddles
        self.basinSaddleAlternatives = []
        # Non specific disqualification
        self._disqualified = kwargs.get('disqualified', None)
        self.lprBoundary = []

    def addSummitLinker(self, linker):
        """
        :param linker: :class:`Linker`
        """
        isLinker(linker)
        self.summits.append(linker)

    def feature_neighbors(self):
        """
        :return: returns all Summits. This is, in effect, an interface.
        """
        return [feature.summit for feature in self.summits]

    @property
    def neighbors(self):
        """
        :return: list of unique neighboring saddles by way of
        neighboring summits excluding self.
        """
        neighborSet = set(self.all_neighbors())
        neighborSet.discard(self)
        return list(neighborSet)

    def all_neighbors(self, filterDisqualified=True):
        """
        all_neighbors will return all neighboring saddles by way of the
        connected summit.
        This function deliberately makes no effort to filter out redundant
        neighbors.
        :param filterDisqualified: bool Filter out disqualified linkers.
        :return: list of neighboring saddles by way of neighboring summits.
        """
        neighbors = []
        if filterDisqualified:
            [neighbors.extend(linker.saddles_connected_via_summit())
                for linker in self.summits if not linker.disqualified]
        else:
            [neighbors.extend(linker.saddles_connected_via_summit(
                skipDisqualified=False))
                for linker in self.summits]
        return neighbors

    @property
    def summits_set(self):
        """
        :return: set of linked :class:`Summit`s
        """
        return set([x.summit for x in self.summits])

    @property
    def disqualified(self):
        """
        :return: if any values that indicate disqualification are set,
         return True.
        """
        # Allow for a manual override from user.
        if self._disqualified in [True, False]:
            return self._disqualified
        else:
            return self.singleSummit | self.tooLow

    @disqualified.setter
    def disqualified(self, value):
        """
        :param value: True or False. Override system disqualification
        """
        self._disqualified = value

    def disqualify_self_and_linkers(self, tooLow=False,
                                    singleSummit=False):
        """
        Disqualify this :class:`Saddle` and linked :class:`Linker`s.
        :param tooLow: set tooLow
        :param singleSummit: set singleSummit
        """
        if tooLow:
            self.tooLow = tooLow
        if singleSummit:
            self.singleSummit = singleSummit
        if not (tooLow | singleSummit):
            self._disqualified = True
        for linker in self.summits:
            linker.disqualified = True

    def to_dict(self, referenceById=True):
        """
        :param referenceById: reference Summits by ID.
        :return: dict() representation of :class:`Saddle`
        """
        to_dict = {'lat': self.latitude,
                   'lon': self.longitude,
                   'ele': self.elevation,
                   'edge': self.edgeEffect,
                   'edgepoints': [x.to_dict() for x in self.edgePoints],
                   'id': self.id}
        if self.singleSummit:
            to_dict['singlesummit'] = self.singleSummit
        if self.tooLow:
            to_dict['tooLow'] = self.tooLow
        if self._disqualified:
            to_dict['disqualified'] = self._disqualified

        # TODO: lprBoundary will be needed someday.

        if self.multiPoint:
            to_dict['multipoint'] = self.multiPoint.to_dict()
        if self.highShores:
            to_dict['highShores'] = list()
            for shore in self.highShores:
                hs = shore.to_dict()
                to_dict['highShores'].append(hs)
        # These values are not unloaded by from_dict()
        if referenceById:
            to_dict['children'] =\
                [x.id for x in self.children]  # saddles by ID
            to_dict['summits'] =\
                [x.id for x in self.summits]  # linker by ID
            if self.parent:
                to_dict['parent'] = self.parent.id
        return to_dict

    @classmethod
    def from_dict(cls, saddleDict, datamap=None):
        """
        Create :class:`Saddle` from dictionary representation
        :return: :class:`Saddle`
        """
        lat = saddleDict['lat']
        long = saddleDict['lon']
        elevation = saddleDict['ele']
        edge = saddleDict['edge']
        edgePoints = [BaseGridPoint(pt['x'], pt['y'])
                      for pt in saddleDict['edgepoints']]
        id = saddleDict['id']
        singleSummit = saddleDict.get('singleSummit', False)
        tooLow = saddleDict.get('tooLow', False)
        disqualified = saddleDict.get('disqualified', None)

        multipoint = saddleDict.get('multipoint', [])
        if multipoint:
            multipoint = MultiPoint.from_dict(multipoint, datamap=datamap)
        highshores = saddleDict.get('highShores', [])
        if highshores:
            highshores = [GridPointContainer.from_dict(x) for x in highshores]
        return cls(lat, long, elevation,
                   multiPoint=multipoint,
                   highShores=highshores,
                   edge=edge,
                   edgePoints=edgePoints,
                   id=id,
                   singleSummit=singleSummit,
                   tooLow=tooLow,
                   disqualified=disqualified)

    def __hash__(self):
        """
        :return: returns unique hash of this Saddle
        Takes into account the lat, long, and elevation of the saddle
        As well as a hash of all the highShores
        """
        masterHash = super(SpotElevation, self).__hash__()
        pointsTuple = tuple(self.highShores)
        return hash((masterHash, hash(pointsTuple)))

    def __repr__(self):
        """
        :return: string representation of this object.
        """
        return "<Saddle> lat {} long {} {}ft {}m MultiPoint {}".format(
            self.latitude,
            self.longitude,
            self.feet,
            self.elevation,
            bool(self.multiPoint))

    __unicode__ = __str__ = __repr__


def isSaddle(saddle):
    """
    :param saddle: object under scrutiny
    :raises: TypeError if other not of :class:`Saddle`
    """
    if not isinstance(saddle, Saddle):
        raise TypeError("Expected Saddle Object.")
