"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing Summit data.
"""

from .spot_elevation import SpotElevation
from .base_gridpoint import BaseGridPoint
from ..containers.multipoint import MultiPoint
from ..containers.linker import isLinker
from ..util import randomString


class Summit(SpotElevation):
    """
    Summit object stores relevant summit data.
    """

    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        """
        :param latitude: latitude in dotted decimal
        :param longitude: longitude in dotted decimal
        :param elevation: elevation in meters
        :param multiPoint: :class:`MultiPoint` object
        """
        super(Summit, self).__init__(latitude, longitude,
                                     elevation, *args, **kwargs)
        self.multiPoint = kwargs.get('multiPoint', [])
        self.id = kwargs.get('id', 'su:' + randomString())
        # saddles contains a list of linker objects linking this summit to a
        # saddle. These are populated by :class:`Walk`
        self.saddles = list()

        self.localHighest = None
        self.parent = None
        self.lprBoundary = []
        self.lprPaths = None

    def addSaddleLinker(self, linker):
        """
        Adds linker to this :class:`Summit`
        :param linker: :class:`Linker`
        """
        isLinker(linker)
        self.saddles.append(linker)

    @property
    def neighbors(self):
        """
        :return: list of directly neighboring summits excluding self.
        """
        neighborSet = set(self.all_neighbors())
        neighborSet.discard(self)
        return list(neighborSet)

    def all_neighbors(self, filterDisqualified=True):
        """
        all_neighbors will return all neighboring summits by way of the saddle.
        This function deliberately makes no effort to filter out redundant
        neighbors.
        :param filterDisqualified: bool Filter out disqualified linkers.
        :return: list of neighboring summits by way of neighboring saddles.
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
        :param referenceById: reference Saddles by ID.
        :return: dict() representation of :class:`Summit`
        """
        to_dict = {'lat': self.latitude,
                   'lon': self.longitude,
                   'ele': self.elevation,
                   'edge': self.edgeEffect,
                   'edgepoints': [x.to_dict() for x in self.edgePoints],
                   'id': self.id
                   }
        # TODO: localhighest (for divide tree time)
        if self.multiPoint:
            to_dict['multipoint'] = self.multiPoint.to_dict()
        # These values are not unloaded by from_dict()
        if referenceById:
            to_dict['saddles'] = [x.id for x in self.saddles]  # linker by ID
        return to_dict

    @classmethod
    def from_dict(cls, summitDict, datamap=None):
        """
        Create :class:`Summit` from dictionary representation
        :return: :class:`Summit`
        """
        lat = summitDict['lat']
        long = summitDict['lon']
        elevation = summitDict['ele']
        edge = summitDict['edge']
        edgePoints = [BaseGridPoint(pt['x'], pt['y'])
                      for pt in summitDict['edgepoints']]
        id = summitDict['id']
        multipoint = summitDict.get('multipoint', [])
        if multipoint:
            multipoint = MultiPoint.from_dict(multipoint, datamap=datamap)
        return cls(lat, long, elevation,
                   multiPoint=multipoint,
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
            bool(self.multiPoint))

    __unicode__ = __str__ = __repr__


def isSummit(summit):
    """
    :param summit: object under scrutiny
    :raises: TypeError if other not of :class:`Summit`
    """
    if not isinstance(summit, Summit):
        raise TypeError("Expected Summit Object.")
