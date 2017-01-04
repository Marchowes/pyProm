"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing Saddle data.
"""

import json
from .spot_elevation import SpotElevation


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
        """
        super(Saddle, self).__init__(latitude, longitude,
                                     elevation, *args, **kwargs)
        self.multiPoint = kwargs.get('multiPoint', None)
        self.highShores = kwargs.get('highShores', None)
        #Temporary until I've build a linker
        self.summits = list()
        self.disqualified = False


    def to_dict(self, recurse=False):
        """
        :param recurse: include multipoint
        :return: dict of :class:`Saddle`
        """
        to_dict = {'type': 'Saddle',
                   'latitude': self.latitude,
                   'longitude': self.longitude,
                   'elevation': self.elevation,
                   'edge': self.edgeEffect}
        if self.multiPoint and recurse:
            to_dict['multipoint'] = self.multiPoint.to_dict()
        if self.highShores:
            to_dict['highShores'] = list()
            for shore in self.highShores:
                hs = [x.to_dict() for x in shore.points]
                to_dict['highShores'].append(hs)
        return to_dict

    def to_json(self, recurse=False):
        """
        :param recurse: include multipoint
        :return: json string of :class:`Saddle`
        """
        to_json = self.to_dict(recurse=recurse)
        return json.dumps(to_json)

    def __repr__(self):
        return "<Saddle> lat {} long {} {}ft {}m MultiPoint {}".format(
            self.latitude,
            self.longitude,
            self.feet,
            self.elevation,
            bool(self.multiPoint))

    __unicode__ = __str__ = __repr__
