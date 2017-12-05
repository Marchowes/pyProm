"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This file acts as the glue between the raster data loaded and the logic
used to analyze the map.
"""

from __future__ import division

import logging
import utm

from .util import dottedDecimaltoDegrees, degreesToDottedDecimal

ARCSEC_DEG = 3600
ARCMIN_DEG = 60


class DataMap(object):
    """
    Base class for Datamap type objects
    """
    def __init__(self, numpy_map, unit):
        self.numpy_map = numpy_map
        valid_units = ["METERS","Foot_US", "Meter"]
        assert unit in valid_units, 'unit must be one of {}, got {}'.format(valid_units, unit)
        self.unit = unit

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
                yield _x, _y, -32768

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
                yield _x, _y, -32768



class DegreesDataMap(DataMap):
    def __init__(self, numpy_map, latitude, longitude,
                 span_latitude, span_longitude, arcsec_resolution, unit):
        super(DegreesDataMap, self).__init__(numpy_map, unit)
        self.logger = logging.getLogger('pyProm.{}'.format(__name__))
        self.logger.info("Datamap Object Created.")
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
        xy = self.latlong_to_xy(latitude, longitude)
        return self.numpy_map[xy[0], xy[1]]

    def latlong_to_xy(self, latitude, longitude):
        return (self._latitude_to_x(latitude), self._longitude_to_y(longitude))

    def _longitude_to_y(self, longitude):
        """
        :param longitude: longitude in dotted decimal notation.
        :return: relative Y position for coordinate in numpy map
        """
        if not self.longitude <= longitude <= self.longitude_max:
            raise ValueError('Invalid Value! must be in the range of'
                             ' {} to {}'.format(self.longitude,
                                                self.longitude_max))
        hms_longitude = dottedDecimaltoDegrees(longitude)
        return int(abs((round(hms_longitude[2] +
                              (hms_longitude[1] * ARCMIN_DEG) +
                              (hms_longitude[0] * ARCSEC_DEG) -
                              (self.longitude) * ARCSEC_DEG)) /
                       self.arcsec_resolution))

    def _latitude_to_x(self, latitude):
        """
        :param latitude: latitude in dotted decimal notation
        :return: relative X position for coordinate in numpy map.
        """
        if not self.latitude <= latitude <= self.latitude_max:
            raise ValueError('Invalid Value! must be in the range of'
                             ' {} to {}'.format(self.latitude,
                                                self.latitude_max))
        hms_latitude = dottedDecimaltoDegrees(latitude)
        return int(abs((round(hms_latitude[2] +
                       (hms_latitude[1] * ARCMIN_DEG) +
                       (hms_latitude[0] * ARCSEC_DEG)) -
                       (self.latitude_max) * ARCSEC_DEG)) /
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

    def x_to_latitude(self, x):
        """
        :param x: x location in `numpy_map`
        :return: position in dotted decimal latitude
        """
        hms = self._position_formula(x)
        return self.latitude_max - degreesToDottedDecimal(*hms)

    def y_to_longitude(self, y):
        """
        :param y: y location in `numpy_map`
        :return: position in dotted decimal longitude
        """
        hms = self._position_formula(y)
        return self.longitude + degreesToDottedDecimal(*hms)

    def xy_to_latlong(self, x, y):
        """
        :param x: x location in `numpy_map`
        :param y: y location in `numpy_map`
        :return: tuple position in dotted decimal lat/long
        """
        hms = self._position_formula(x)
        latitude = self.latitude_max - degreesToDottedDecimal(*hms)
        hms = self._position_formula(y)
        longitude = self.longitude + degreesToDottedDecimal(*hms)
        return (latitude, longitude)

    def subset(self, x, y, xSpan, ySpan):
        """
        :param x: NW corner x coordinate (latitude)
        :param y: NW corner y coordinate (longitude)
        :param xSpan: depth of subset in points (latitude)
        :param ySpan: width of subset in points (longitude)
        :return: :class:`DegreesDataMap`
        """
        keyLat = self.x_to_latitude(x+xSpan) # Southermost
        keyLong = self.y_to_longitude(y+ySpan) # Westernmost
        numpy_map = (self.numpy_map[x:x+xSpan, y:y+ySpan])
        return DegreesDataMap(numpy_map,
                              keyLat,
                              keyLong,
                              xSpan,
                              ySpan,
                              self.arcsec_resolution,
                              self.unit)

    def __repr__(self):
        return "<DataMap> Lat {}, Long {}, SpanLat {}," \
               " SpanLong {}, {} ArcSec/Point".format(
                self.latitude,
                self.longitude,
                self.span_latitude,
                self.span_longitude,
                self.arcsec_resolution)

    __unicode__ = __str__ = __repr__


class ProjectionDataMap(DataMap):
    def __init__(self, numpy_map, utm_lowerLeftY, utm_lowerLeftX,
                 utm_span_y, utm_span_x, linear_unit, hemisphere, utm_zone, unit):
        super(ProjectionDataMap, self).__init__(numpy_map, unit)
        self.logger = logging.getLogger('pyProm.{}'.format(__name__))
        self.logger.info("ProjectedDataMap Object Created")
        # These are deliberately flipped, yes I know it's confusing.
        self.lowerLeftY = utm_lowerLeftX  # SW Corner
        self.lowerLeftX = utm_lowerLeftY  # SW Corner
        self.span_y = utm_span_x
        self.max_y = self.span_y - 1
        self.span_x = utm_span_y
        self.max_x = self.span_x - 1
        self.linear_unit = linear_unit
        self.hemisphere = hemisphere
        self.utm_zone = utm_zone

    def xy_to_latlong(self, x,y):
        """
        :param x: x location in `numpy_map`
        :param y: y location in `numpy_map`
        :return: tuple position in dotted decimal lat/long
        """
        relative_x_position = (self.lowerLeftX + (self.span_x * self.linear_unit)) - (x * self.linear_unit)
        relative_y_position = self.lowerLeftY + (y * self.linear_unit)
        return utm.to_latlon(relative_y_position, relative_x_position, self.utm_zone, northern=self.hemisphere=='N')

    def latlong_to_xy(self, latitude, longitude):
        """
        :param latitude:
        :param longitude:
        :return:
        """
        utm_coord = utm.from_latlon(latitude, longitude)
        x = round(utm_coord[1])
        y = round(utm_coord[0])
        rel_x = x - (self.lowerLeftX + (self.span_x * self.linear_unit))
        rel_y = y - self.lowerLeftY
        return (rel_x, rel_y)

    def elevation(self, latitude, longitude):
        """
        :param latitude: latitude in dotted demical notation
        :param longitude: longitude in dotted decimal notation.
        :return: elevation of coordinate in meters.
        """
        xy = self.latlong_to_xy(latitude, longitude)
        return self.numpy_map[xy[0], xy[1]]

    def subset(self, x, y, xSpan, ySpan):
        """
        :param x: NW corner x coordinate (latitude)
        :param y: NW corner y coordinate (longitude)
        :param xSpan: depth of subset in points (latitude)
        :param ySpan: width of subset in points (longitude)
        :return: :class:`ProjectionDataMap`
        """
        southExtreme = (self.lowerLeftX + (self.span_x*self.linear_unit)) - (x+xSpan) #SouthernMost
        westExtreme = self.lowerLeftY + y #WesternMost
        numpy_map = (self.numpy_map[x:x+xSpan, y:y+ySpan])
        return ProjectionDataMap(numpy_map,
                       westExtreme,
                       southExtreme,
                       ySpan,
                       xSpan,
                       self.linear_unit,
                       self.hemisphere,
                       self.utm_zone)

    def __repr__(self):
        return "<ProjectionDataMap> UTM {} Easting {} Northing, Zone {}, SpanX {}," \
               " SpanY {}, {} Units".format(
                self.lowerLeftX,
                self.lowerLeftY,
                self.utm_zone,
                self.span_y,
                self.span_x,
                self.linear_unit)

    __unicode__ = __str__ = __repr__


class ProjectionDataMapV2(DataMap):
    def __init__(self, numpy_map, lowerLeftY, lowerLeftX, resolutionY, resolutionX,
                 span_y, span_x, linear_unit, unit, transform, reverse_transform):
        super(ProjectionDataMapV2, self).__init__(numpy_map, unit)
        self.logger = logging.getLogger('pyProm.{}'.format(__name__))
        self.logger.info("ProjectedDataMap Object Created")
        # These are deliberately flipped, yes I know it's confusing.
        self.lowerLeftY = lowerLeftX  # SW Corner
        self.lowerLeftX = lowerLeftY  # SW Corner
        self.res_y = resolutionX
        self.res_x = resolutionY
        self.span_y = span_x
        self.max_y = self.span_y - 1
        self.span_x = span_y
        self.max_x = self.span_x - 1
        self.linear_unit = linear_unit
        self.transform = transform
        self.reverse_transform = reverse_transform


    def xy_to_latlong(self, x,y):
        """
        :param x: x location in `numpy_map`
        :param y: y location in `numpy_map`
        :return: (latitude, longitude)
        """

        absolute_x_position = (self.lowerLeftX - (self.span_x * self.res_x)) + (x * self.res_x)
        absolute_y_position = self.lowerLeftY + (y * self.res_y)
        #print (absolute_x_position, absolute_y_position) # Wrong!
        transformed = self.transform.TransformPoint(absolute_y_position, absolute_x_position)[:2]
        return (transformed[1],transformed[0])

    def latlong_to_xy(self, latitude, longitude):
        """
        :param latitude:
        :param longitude:
        :return: (x,y)
        """
        coordinate = self.reverse_transform.TransformPoint(longitude, latitude)
        x = coordinate[1]
        y = coordinate[0]
        rel_x = round((x - (self.lowerLeftX - (self.span_x * self.res_x)))/self.res_x)
        rel_y = round((y - self.lowerLeftY)/self.res_y)
        return (rel_x, rel_y)

    def elevation(self, latitude, longitude):
        """
        :param latitude: latitude in dotted demical notation
        :param longitude: longitude in dotted decimal notation.
        :return: elevation of coordinate in meters.
        """
        xy = self.latlong_to_xy(latitude, longitude)
        return self.numpy_map[xy[0], xy[1]]

    def _leftmost_absolute(self):
        return self.lowerLeftY

    def _rightmost_absolute(self):
        return self.lowerLeftY + (self.res_y * self.span_y)

    def _lowermost_absolute(self):
        return self.lowerLeftX

    def _uppermost_absolute(self):
        return self.lowerLeftX - (self.res_x * self.span_y)

    def x_to_absolute_x(self):
        pass

    def y_to_absolute_y(self):
        pass

    @property
    def upper_left(self):
        transformed = self.transform.TransformPoint(self._leftmost_absolute(), self._uppermost_absolute())
        return (transformed[1],transformed[0])

    @property
    def lower_left(self):
        transformed = self.transform.TransformPoint(self._leftmost_absolute(), self._lowermost_absolute())
        return (transformed[1], transformed[0])

    @property
    def upper_right(self):
        transformed = self.transform.TransformPoint(self._rightmost_absolute(), self._uppermost_absolute())
        return (transformed[1], transformed[0])

    @property
    def lower_right(self):
        transformed = self.transform.TransformPoint(self._rightmost_absolute(), self._lowermost_absolute())
        return (transformed[1], transformed[0])


    def subset(self, x, y, xSpan, ySpan):
        """
        :param x: NW corner x coordinate (latitude)
        :param y: NW corner y coordinate (longitude)
        :param xSpan: depth of subset in points (latitude)
        :param ySpan: width of subset in points (longitude)
        :return: :class:`ProjectionDataMap`
        """
        southExtreme = self._uppermost_absolute() + (x*self.res_x) + ((x*self.res_x)*xSpan)
        westExtreme = self.lowerLeftY + (y*self.res_y)
        numpy_map = (self.numpy_map[x:x+xSpan, y:y+ySpan])
        return ProjectionDataMapV2(numpy_map,
                       westExtreme,
                       southExtreme,
                       self.res_y,
                       self.res_x,
                       ySpan,
                       xSpan,
                       self.linear_unit,
                       self.unit,
                       self.transform,
                       self.reverse_transform)

    def __repr__(self):
        return "<ProjectionDataMap> LowerLeft LatLon {}, LowerLeft Local "\
                "Coords {}, SpanX {}, SpanY {}, {} Units".format(
                 self.lower_left,
                 (self._leftmost_absolute(), self._lowermost_absolute()),
                 self.span_x,
                 self.span_y,
                 self.unit)

    __unicode__ = __str__ = __repr__