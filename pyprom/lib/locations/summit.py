"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing Summit data.
"""

import json
from .spot_elevation import SpotElevation


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
        self.multiPoint = kwargs.get('multiPoint', None)
        self.saddles = list()
        self.localHighest = None
        self.parent = None

    def to_dict(self, recurse=False):
        """
        :param recurse: include multipoint
        :return: dict of :class:`Summit`
        """
        to_dict = {'latitude': self.latitude,
                   'longitude': self.longitude,
                   'elevation': self.elevation,
                   'edge': self.edgeEffect}
        if self.multiPoint and recurse:
            to_dict['multipoint'] = self.multiPoint.to_dict()
        return to_dict

    def to_json(self, recurse=False, prettyprint=True):
        """
        :param recurse: include multipoint
        :param prettyprint: human readable,
         but takes more space when written to a file.
        :return: json string of :class:`Summit`
        """
        to_json = self.to_dict(recurse=recurse)
        if prettyprint:
            return json.dumps(to_json, sort_keys=True,
                              indent=4, separators=(',', ': '))
        else:
            return json.dumps(to_json)

    def __repr__(self):
        return "<Summit> lat {} long {} {}ft {}m MultiPoint {}".format(
            self.latitude,
            self.longitude,
            self.feet,
            self.elevation,
            bool(self.multiPoint))

    __unicode__ = __str__ = __repr__
