"""
pyProm: Copyright 2018

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing Runoff data.
"""

from .saddle import Saddle

class Runoff(Saddle):
    """
    Runoff object stores relevant runoff data.
    """
    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        """
        :param latitude: latitude in dotted decimal
        :param longitude: longitude in dotted decimal
        :param elevation: elevation in meters
        :param multiPoint: :class:`MultiPoint` object
        :param highShores: :class:`HighEdgeContainer` object
        :param edge: (bool) does this :class:`SpotElevation` have an edge
        Effect?
        """
        super(Runoff, self).__init__(latitude, longitude,
                                     elevation, *args, **kwargs)

    def __repr__(self):
        """
        :return: string representation of this object.
        """
        return "<Runoff> lat {} long {} {}ft {}m MultiPoint {}".format(
            self.latitude,
            self.longitude,
            self.feet,
            self.elevation,
            bool(self.multiPoint))

    __unicode__ = __str__ = __repr__