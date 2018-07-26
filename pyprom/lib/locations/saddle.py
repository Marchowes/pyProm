"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing Saddle data.
"""

import json

from .spot_elevation import SpotElevation
from ..containers.linker import isLinker

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
        # Temporary until I've build a linker
        self.summits = list()
        # If this is set, this saddle was spun out of another
        # Saddle with less data.
        self.parent = None # Parent
        # Saddles that have been spawned off of this one.
        self.children = list()
        self.singleSummit = False  # All Edges lead to One summit.
        self.tooLow = False # redundant saddle, but too low.
        self._disqualified = None # Non specific disqualification
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

    def to_dict(self, recurse=False):
        """
        :param recurse: include multipoint
        :return: dict of :class:`Saddle`
        """
        to_dict = {'latitude': self.latitude,
                   'longitude': self.longitude,
                   'elevation': self.elevation,
                   'type': 'Saddle',
                   'edge': self.edgeEffect}
        if self.multiPoint and recurse:
            to_dict['multipoint'] = self.multiPoint.to_dict()
        if self.highShores:
            to_dict['highShores'] = list()
            for shore in self.highShores:
                hs = [x.to_dict() for x in shore.points]
                to_dict['highShores'].append(hs)
        return to_dict

    def to_json(self, recurse=False, prettyprint=True):
        """
        :param recurse: include multipoint
        :param prettyprint: human readable,
         but takes more space when written to a file.
        :return: json string of :class:`Saddle`
        """
        to_json = self.to_dict(recurse=recurse)
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