"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing Saddle data.
"""

import json

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
        self.multiPoint = kwargs.get('multiPoint', None)
        self.highShores = kwargs.get('highShores', [])
        self.id = kwargs.get('id', 'sa:' + randomString())
        # Temporary until I've build a linker
        self.summits = list()
        # If this is set, this saddle was spun out of another
        # Saddle with less data.
        self.parent = None  # Parent
        # Saddles that have been spawned off of this one.
        self.children = kwargs.get('children', [])
        # All Edges lead to One summit.
        self.singleSummit = kwargs.get('singleSummit', False)
        # redundant saddle, but too low.
        self.tooLow = kwargs.get('tooLow', False)
        # Non specific disqualification
        self._disqualified = kwargs.get('disqualified', None)
        self.lprBoundary = list()

    def addSummitLinker(self, linker):
        """
        :param linker: :class:`Linker`
        """
        isLinker(linker)
        self.summits.append(linker)

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
            to_dict['toolow'] = self.tooLow
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

        multipoint = saddleDict.get('multipoint', None)
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

    def to_json(self, prettyprint=True, referenceById=True):
        """
        :param prettyprint: human readable,
         but takes more space when written to a file.
        :param referenceById: link external objects by ID
        :return: json string of :class:`Saddle`
        """
        to_json = self.to_dict(referenceById=referenceById)
        if prettyprint:
            return json.dumps(to_json, sort_keys=True,
                              indent=4, separators=(',', ': '))
        else:
            return json.dumps(to_json)

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
