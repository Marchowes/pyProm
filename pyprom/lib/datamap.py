"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This file acts as the glue between the raster data loaded and the logic
used to analyze the map.
"""

from __future__ import division

import logging

ARCSEC_DEG = 3600
ARCMIN_DEG = 60
DIAGONAL_SHIFT_LIST = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                       (0, -1), (-1, -1))
ORTHOGONAL_SHIFT_LIST = ((-1, 0), (0, 1), (1, 0), (0, -1))


class DataMap:
    """Base class for Datamap type objects."""

    def __init__(self, numpy_map, unit, filename):
        """__init__."""
        self.numpy_map = numpy_map
        self.filename = filename
        unit_and_substrings = {"METERS": ["meter"], "FEET": ["foot", "feet"]}
        self.unit = None
        for unitname, unit_options in unit_and_substrings.items():
            for option in unit_options:
                if option.upper() in unit.upper():
                    self.unit = unitname
        if not self.unit:
            raise Exception("Need Meters or Feet. Got {}".format(unit))

    def iterateDiagonal(self, x, y):
        """
        Generator returns 8 closest neighbors to a raster grid location,
        that is, all points touching including the diagonals.
        """
        # 0, 45, 90, 135, 180, 225, 270, 315
        for shift in DIAGONAL_SHIFT_LIST:
            _x = x + shift[0]
            _y = y + shift[1]
            if 0 <= _x <= self.max_x and \
               0 <= _y <= self.max_y:
                if self.unit == 'FEET':
                    yield _x, _y, float(.3048 * self.numpy_map[_x, _y])
                else:
                    yield _x, _y, float(self.numpy_map[_x, _y])
            else:
                yield _x, _y, self.nodata

    def iterateOrthogonal(self, x, y):
        """
        Generator returns 4 closest neighbors to a raster grid location,
        that is, all points touching excluding the diagonals.
        """
        # 0, 90, 180, 270
        for shift in ORTHOGONAL_SHIFT_LIST:
            _x = x + shift[0]
            _y = y + shift[1]
            if 0 <= _x <= self.max_x and \
               0 <= _y <= self.max_y:
                if self.unit == 'FEET':
                    yield _x, _y, float(.3048 * self.numpy_map[_x, _y])
                else:
                    yield _x, _y, float(self.numpy_map[_x, _y])
            else:
                yield _x, _y, self.nodata


class ProjectionDataMap(DataMap):
    """
    ProjectionDataMap is a Datamap object for projection style
    datasets from GDAL.
    """

    def __init__(self, numpy_map, upperLeftY, upperLeftX, resolutionY,
                 resolutionX, span_y, span_x, linear_unit, unit, nodata,
                 transform, reverse_transform, filename):
        """
        :param numpy_map: numpy_array multidimensional array of data
         numpy_map[x][y]
        :param upperLeftY: Upper Left Y native coordinate from GDAL. This
         is the X axis for Numpy.
        :param upperLeftX: Upper Left X native coordinate from GDAL. This
         is the Y axis for Numpy
        :param resolutionY: Number of units per pixel on GDAL native Y axis.
         This is the X axis for Numpy
        :param resolutionX: Number of units per pixel on GDAL native X axis.
         This is the Y axis for Numpy
        :param span_y: number of units along GDAL native Y axis. This is the
         X axis for Numpy
        :param span_x: number of units along GDAL native X axis. This is the
         Y axis for Numpy
        :param linear_unit: Linear unit scale.
        :param unit: Linear unit
        :param nodata: raster point value indicating a NULL Value
        :param transform: osr.CoordinateTransformation from GDAL native to
         selected units (degrees)
        :param reverse_transform: osr.CoordinateTransformation from selected
         units degrees scale to GDAL native


        GDAL Native coordiante system oriented:
        Y: east/west
        X: north/south

        numpy_map is oriented:
        Y: north/south
        X: east/west

        called like:
        numpy_map[x][y]
        """
        super(ProjectionDataMap, self).__init__(numpy_map, unit, filename)
        self.logger = logging.getLogger('{}'.format(__name__))
        self.logger.info("ProjectedDataMap Object Created")
        # These are deliberately flipped, yes I know it's confusing.
        self.upperLeftY = upperLeftX  # SW Corner
        self.upperLeftX = upperLeftY  # SW Corner
        self.res_y = resolutionX
        self.res_x = resolutionY
        self.span_y = span_x
        self.max_y = self.span_y - 1
        self.span_x = span_y
        self.max_x = self.span_x - 1
        self.linear_unit = linear_unit
        self.nodata = nodata
        self.transform = transform
        self.reverse_transform = reverse_transform

    def xy_to_latlong(self, x, y):
        """
        This function converts a numpy[x][y] coordinate to
        lat/long coordinates.
        :param x: x location in `numpy_map`
        :param y: y location in `numpy_map`
        :return: (latitude, longitude)
        """
        absolute_x_position = self._uppermost_absolute() + (x * self.res_x)
        absolute_y_position = self._leftmost_absolute() + (y * self.res_y)
        transformed = self.transform.TransformPoint(absolute_y_position,
                                                    absolute_x_position)[:2]
        return (transformed[1], transformed[0])

    def latlong_to_xy(self, latitude, longitude):
        """
        This function converts a lat/long coordinate set to numpy[x][y].
        :param latitude:
        :param longitude:
        :return: (x,y)
        """
        coordinate = self.reverse_transform.TransformPoint(longitude, latitude)
        x = coordinate[1]
        y = coordinate[0]
        rel_x = round((x - self._uppermost_absolute()) / self.res_x)
        rel_y = round((y - self._leftmost_absolute()) / self.res_y)
        return (rel_x, rel_y)

    def elevation(self, latitude, longitude):
        """
        This function returns the elevation at a certain lat/long in Meters.
        :param latitude: latitude in dotted demical notation
        :param longitude: longitude in dotted decimal notation.
        :return: elevation of coordinate in meters.
        """
        x, y = self.latlong_to_xy(latitude, longitude)
        if self.unit == 'FEET':
            return float(.3048 * self.numpy_map[x, y])
        else:
            return self.numpy_map[x, y]

    def _leftmost_absolute(self):
        """Returns the Leftmost GDAL Native X coordinate (Y for numpy_map)."""
        return self.upperLeftY

    def _rightmost_absolute(self):
        """
        Returns the Rightmost GDAL Native X coordinate (Y for numpy_map).
        """
        return self.upperLeftY + (self.res_y * self.span_y)

    def _lowermost_absolute(self):
        """
        Returns the Lowermost GDAL Native Y coordinate (X for numpy_map).
        """
        return self.upperLeftX + (self.res_x * self.span_x)

    def _uppermost_absolute(self):
        """
        Returns the Uppermost GDAL Native Y coordinate
        (X for numpy_map).
        """
        return self.upperLeftX

    def x_to_native_x(self, x):
        """
        Converts a numpy X coordinate the the gdal native Y
        (X for numpy_map).
        """
        return self._uppermost_absolute() + (x * self.res_x)

    def y_to_native_y(self, y):
        """
        Converts a numpy Y coordinate the the gdal native X
        (Y for numpy_map).
        """
        return self._leftmost_absolute() + (y * self.res_y)

    @property
    def upper_left(self):
        """Produce the upper leftmost coordinate value in degrees."""
        transformed =\
            self.transform.TransformPoint(self._leftmost_absolute(),
                                          self._uppermost_absolute())
        return (transformed[1], transformed[0])

    @property
    def lower_left(self):
        """Produce the upper leftmost coordinate value in degrees."""
        transformed =\
            self.transform.TransformPoint(self._leftmost_absolute(),
                                          self._lowermost_absolute())
        return (transformed[1], transformed[0])

    @property
    def upper_right(self):
        """Produce the upper leftmost coordinate value in degrees."""
        transformed =\
            self.transform.TransformPoint(self._rightmost_absolute(),
                                          self._uppermost_absolute())
        return (transformed[1], transformed[0])

    @property
    def lower_right(self):
        """Produce the upper leftmost coordinate value in degrees."""
        transformed =\
            self.transform.TransformPoint(self._rightmost_absolute(),
                                          self._lowermost_absolute())
        return (transformed[1], transformed[0])

    def subset(self, x, y, xSpan, ySpan):
        """
        Subset produces a subset of the parent (self) map. Uses numpy X,Y
        axis where X,Y are the upper left coordinates.
        :param x: NW corner x coordinate (latitude)
        :param y: NW corner y coordinate (longitude)
        :param xSpan: depth of subset in points (latitude)
        :param ySpan: width of subset in points (longitude)
        :return: :class:`ProjectionDataMap`
        """
        southExtreme = self.x_to_native_x(x)
        westExtreme = self.y_to_native_y(y)
        numpy_map = (self.numpy_map[x:x + xSpan, y:y + ySpan])
        return ProjectionDataMap(numpy_map,
                                 southExtreme,
                                 westExtreme,
                                 self.res_x,
                                 self.res_y,
                                 xSpan,
                                 ySpan,
                                 self.linear_unit,
                                 self.unit,
                                 self.nodata,
                                 self.transform,
                                 self.reverse_transform,
                                 "UnknownSubset")

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<ProjectionDataMap> LowerLeft LatLon {}, LowerLeft Local "\
            "Coords {}, SpanX {}, SpanY {}, {} Units".format(
                self.lower_left,
                (self._leftmost_absolute(), self._lowermost_absolute()),
                self.span_x,
                self.span_y,
                self.unit)

    __unicode__ = __str__ = __repr__
