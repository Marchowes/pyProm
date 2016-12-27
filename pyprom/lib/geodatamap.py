"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This file acts as the glue between the raster data loaded and the logic
used to analyze the map.
"""

from __future__ import division

import logging

from util import dottedDecimaltoDegrees, degreesToDottedDecimal

ARCSEC_DEG = 3600
ARCMIN_DEG = 60


class DataMap(object):
    def __init__(self, numpy_map, latitude, longitude,
                 span_latitude, span_longitude, arcsec_resolution):
        self.logger = logging.getLogger('pyProm.{}'.format(__name__))
        self.logger.info("Datamap Object Created.")
        self.numpy_map = numpy_map
        self.latitude = latitude  # SW Corner
        self.longitude = longitude  # SW Corner
        self.span_latitude = span_latitude
        self.max_x = span_latitude - 1
        self.span_longitude = span_longitude
        self.max_y = span_longitude - 1
        self.arcsec_resolution = arcsec_resolution
        self.latitude_max = float("{0:.10f}".format(((((
                                        self.span_latitude-1) *
                                        self.arcsec_resolution)) /
                                        ARCSEC_DEG) + self.latitude))

        self.longitude_max = float("{0:.10f}".format(((((
                                        self.span_longitude-1) *
                                        self.arcsec_resolution)) /
                                        ARCSEC_DEG) + self.longitude))

    def elevation(self, latitude, longitude):
        """
        :param latitude: latitude in dotted demical notation
        :param longitude: longitude in dotted decimal notation.
        :return: elevation of coordinate in meters.
        """
        hms_relative_position_long =\
            self.relative_position_longitude(longitude)
        hms_relative_position_lat =\
            self.relative_position_latitude(latitude)
        return self.numpy_map[hms_relative_position_lat,
                              hms_relative_position_long]

    def relative_position_longitude(self, longitude):
        """
        :param longitude: longitude in dotted decimal notation.
        :return: relative Y position for coordinate in numpy map
        """
        if not self.longitude <= longitude <= self.longitude_max:
            raise ValueError('Invalid Value! must be in the range of'
                             ' {} to {}'.format(self.longitude,
                                                self.longitude_max))
        hms_longitude = dottedDecimaltoDegrees(longitude)
        return int(abs((hms_longitude[2] +
                       (hms_longitude[1] * ARCMIN_DEG) +
                       (hms_longitude[0] * ARCSEC_DEG)) -
                       (self.longitude) * ARCSEC_DEG) /
                   self.arcsec_resolution)

    def relative_position_latitude(self, latitude):
        """
        :param latitude: latitude in dotted decimal notation
        :return: relative X position for coordinate in numpy map.
        """
        if not self.latitude <= latitude <= self.latitude_max:
            raise ValueError('Invalid Value! must be in the range of'
                             ' {} to {}'.format(self.latitude,
                                                self.latitude_max))
        hms_latitude = dottedDecimaltoDegrees(latitude)
        return int(abs((hms_latitude[2] +
                       (hms_latitude[1] * ARCMIN_DEG) +
                       (hms_latitude[0] * ARCSEC_DEG)) -
                       (self.latitude_max) * ARCSEC_DEG) /
                   self.arcsec_resolution)

    def _position_formula(self, x):
        """
        Produces a relative coordinate based on x value and arcsec_resolution
        :param x: relative location
        :return: relative (hours, minutes, seconds)
        """
        hours = int(x/(ARCSEC_DEG / self.arcsec_resolution))
        minutes = (((x/(ARCSEC_DEG / self.arcsec_resolution) * ARCMIN_DEG)) -
                   (hours*ARCMIN_DEG))
        seconds = (minutes - int(minutes)) * ARCMIN_DEG
        minutes = int(minutes)
        return hours, minutes, seconds

    def x_position_latitude(self, x):
        """
        :param x: x location in `numpy_map`
        :return: position in dotted decimal latitude
        """
        hms = self._position_formula(x)
        return self.latitude_max - degreesToDottedDecimal(*hms)

    def y_position_longitude(self, y):
        """
        :param y: y location in `numpy_map`
        :return: position in dotted decimal longitude
        """
        hms = self._position_formula(y)
        return self.longitude + degreesToDottedDecimal(*hms)

    def iterateDiagonal(self, x, y):
        """
        Generator returns 8 closest neighbors to a raster grid location,
        that is, all points touching including the diagonals.
        """
        shiftList = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1],
                     [0, -1], [-1, -1]]
        # 0, 45, 90, 135, 180, 225, 270, 315

        for shift in shiftList:
            _x = x + shift[0]
            _y = y + shift[1]
            if 0 <= _x <= self.max_x and \
               0 <= _y <= self.max_y:
                yield _x, _y, float(self.numpy_map[_x, _y])
            else:
                yield _x, _y, None

    def iterateOrthogonal(self, x, y):
        """
        generator returns 4 closest neighbors to a raster grid location,
        that is, all points touching excluding the diagonals.
        """
        shiftList = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        # 0, 90, 180, 270

        for shift in shiftList:
            _x = x + shift[0]
            _y = y + shift[1]
            if 0 <= _x <= self.max_x and \
               0 <= _y <= self.max_y:
                yield _x, _y, float(self.numpy_map[_x, _y])
            else:
                yield _x, _y, None
