"""
pyProm: Copyright 2025.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This file acts as the glue between the raster data loaded and the logic
used to analyze the map.
"""
from __future__ import annotations
import logging
import numpy

from .constants import METERS_PER_FOOT
from .util import checksum

from math import hypot
from osgeo import osr
from shapely.geometry import Polygon
from numpy import array2string

from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from osgeo import gdal
    from numpy import NDArray
    from pyprom._typing.type_hints import Numpy_X, Numpy_Y, Longitude_Y, Latitude_X

ARCSEC_DEG = 3600
ARCMIN_DEG = 60
FULL_SHIFT_LIST = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                       (0, -1), (-1, -1))
ORTHOGONAL_SHIFT_LIST = ((-1, 0), (0, 1), (1, 0), (0, -1))
DIAGONAL_SHIFT_LIST = ((-1, 1), (1, 1), (1, -1), (-1, -1))
FULL_SHIFT_ORTHOGONAL_DIAGONAL_LIST = ORTHOGONAL_SHIFT_LIST + DIAGONAL_SHIFT_LIST

NON_FILE_SENTINEL = "UnknownSubset"

class DataMap2:
    """Base class for Datamap type objects."""

    def __init__(self,
            working_gdal_dataset: gdal.Dataset, 
            filesystem_gdal_dataset: gdal.Dataset, 
            filename: str,
        ):
        self.filesystem_gdal_dataset = filesystem_gdal_dataset
        self.gdal_dataset = working_gdal_dataset
        self.filename = filename
        self.spatialreference = self.gdal_dataset.GetSpatialRef()
        self.raster_band = self.gdal_dataset.GetRasterBand(1)
        self.numpy_map = numpy.array(
            self.gdal_dataset.GetRasterBand(1).ReadAsArray()
        )

        self.span_x = self.gdal_dataset.RasterXSize  # longitude
        self.span_y = self.gdal_dataset.RasterYSize  # latitude

        # Collect Geo Transform data for later consumption
        (
            self.most_west_longitude, self.resolution_longitude, _, #x
            self.most_north_latitude, _, self.resolution_latitude,  #y
        ) = self.gdal_dataset.GetGeoTransform()

        self.nodata = self.raster_band.GetNoDataValue()

        self.max_y = self.span_y
        self.max_x = self.span_x
        self._x_mapEdge = {0: True, self.max_x: True}
        self._y_mapEdge = {0: True, self.max_y: True}


        self.transform = osr.CoordinateTransformation(self.spatialreference, self.spatialreference)

        self.logger = logging.getLogger('{}'.format(__name__))
        self.logger.info("ProjectedDataMap Object Created")

    def xy_to_longlat(self, x: Numpy_X, y: Numpy_Y) -> Tuple[Longitude_Y, Latitude_X]:
        """
        This function converts a numpy[y][x] coordinate to
        lat/long coordinates.

        :param int x: x location in `numpy_map`
        :param int y: y location in `numpy_map`
        :return: (latitude, longitude)
        """
        absolute_x_position = self.longitude_boundary_west() + (x * self.resolution_longitude)
        absolute_y_position = self.latitude_boundary_north() + (y * self.resolution_latitude)
        return absolute_x_position, absolute_y_position

    def longlat_to_xy(self, longitude, latitude) -> Tuple[Numpy_X, Numpy_Y]:
        """
        This function converts a lat/long coordinate set to numpy[y][x].

        :param int latitude:
        :param int longitude:
        :return: (x,y)
        """
        rel_x = round((longitude - self.longitude_boundary_west()) / self.resolution_longitude)
        rel_y = round((latitude - self.latitude_boundary_north()) / self.resolution_latitude)
        return rel_x, rel_y


    def longitude_boundary_west(self) -> Longitude_Y:
        """
        returns our western bounds in longitude
        """

        return self.most_west_longitude

    def longitude_boundary_east(self) -> Longitude_Y:
        """
        returns our eastern bounds in longitude
        """
        return self.most_west_longitude + (self.resolution_longitude * self.span_x)

    def latitude_boundary_north(self) -> Latitude_X:
        """
        returns our northern bounds in latitude
        """
        return self.most_north_latitude

    def latitude_boundary_south(self) -> Latitude_X:
        """
        returns our northern bounds in latitude        
        """
        return self.most_north_latitude + (self.resolution_latitude * self.span_y)

    def get(self, x: Numpy_X, y: Numpy_Y) -> float:
        """
        retrieves value from numpy map at X,Y 
        """
        return float(self.numpy_map[y, x])

    def is_map_edge(self, x: Numpy_X, y: Numpy_Y) -> bool:
        """
        Determine if x, y is on the map edge.
        """
        return x == 0 or y == 0 or x == self.max_x or y == self.max_y

    def distance(self, us: Tuple[Numpy_X, Numpy_Y], them: Tuple[Numpy_X, Numpy_Y]) -> float:
        """
        :param us: Tuple(x, y)
        :param them: Tuple(x, y)
        :return: distance.
        """
        return hypot((us[0] - them[0]) * self.resolution_longitude, (us[1] - them[1]) * self.resolution_latitude)








        self.numpy_map = numpy_map
        self.file_and_path = filename
        self.filename = filename.split("/")[-1]
        if filename != NON_FILE_SENTINEL:
            self.md5 = checksum(filename)
        else:
            # Not really an MD5, but whatever.
            self.md5 = hash(array2string(self.numpy_map))
        unit_and_substrings = {"METERS": ["meter", "metre", "m"], "FEET": ["foot", "feet"]}
        self.unit = None
        for unitname, unit_options in unit_and_substrings.items():
            for option in unit_options:
                if option.upper() in unit.upper():
                    self.unit = unitname
        if not self.unit:
            raise Exception("Need Meters or Feet. Got {}".format(unit))