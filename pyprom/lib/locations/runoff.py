"""
pyProm: Copyright 2018

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing Runoff data.
"""

from .saddle import Saddle
from ..util import randomString


class Runoff(Saddle):
    """
    Runoff object stores relevant runoff data. A Runoff is a mapEdge feature.
    It can either be a Saddle stand in, or a Summit stand in, tho, for our
    purposes these are Saddle-like. This is a child object of
    :class:`pyprom.lib.locations.saddle.Saddle`
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
        :param highShores: list of GridPointContainers representing a highShore
        :type highShores:
         list(:class:`pyprom.lib.containers.gridPoint.GridPointContainer`)
        """
        super(Runoff, self).__init__(latitude, longitude,
                                     elevation, *args, **kwargs)
        self.id = kwargs.get('id', 'ru:' + randomString())
        self.edgeEffect = True  # Runoffs are, as a rule, edge features.

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<Runoff> lat {} long {} {}ft {}m MultiPoint {}".format(
            self.latitude,
            self.longitude,
            self.feet,
            self.elevation,
            bool(self.multipoint))

    __unicode__ = __str__ = __repr__
