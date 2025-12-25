"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This file acts as the glue between the raster data loaded and the logic
used to analyze the map.
"""
from __future__ import annotations
import logging

from  .base_datamap import BaseDataMap
import pyproj
from math import hypot
from shapely.geometry import Polygon
import numpy

from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from osgeo import osr
    from pyprom.lib.loaders.gdal_loader import GDALLoader
    from pyprom._typing.type_hints import NUMPY_X, NUMPY_Y, LONGITUDE_X, LATITUDE_Y


ARCSEC_DEG = 3600
ARCMIN_DEG = 60
FULL_SHIFT_LIST = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                       (0, -1), (-1, -1))
ORTHOGONAL_SHIFT_LIST = ((-1, 0), (0, 1), (1, 0), (0, -1))
DIAGONAL_SHIFT_LIST = ((-1, 1), (1, 1), (1, -1), (-1, -1))
FULL_SHIFT_ORTHOGONAL_DIAGONAL_LIST = ORTHOGONAL_SHIFT_LIST + DIAGONAL_SHIFT_LIST

NON_FILE_SENTINEL = "UnknownSubset"



class DataMap(BaseDataMap):
    def __init__(self,
        loader: GDALLoader, 
        numpy_array: numpy.NDArray = None
    ) -> None:

        self.loader = loader
        self.gdal_dataset = self.loader.gdal_dataset
        raster_band = self.gdal_dataset.GetRasterBand(1)
        self.nodata = raster_band.GetNoDataValue()
        self.numpy_array = (
            numpy_array or 
            numpy.array(
                raster_band.ReadAsArray()
            )
        )
        self.geotransform = self.gdal_dataset.GetGeoTransform()
        self.inv_geotransform = self.calculate_invert_geotransform()
        self.inv_gt = self.geotransform[1] * self.geotransform[5] - self.geotransform[2] * self.geotransform[4]    

        self.max_y = self.gdal_dataset.RasterXSize - 1 # longitude, or NUMPY_Y
        self.max_x = self.gdal_dataset.RasterYSize - 1 # latitude, or NUMPY_X

        self._x_mapEdge = {0: True, self.max_x: True}
        self._y_mapEdge = {0: True, self.max_y: True}

    # OK
    def xy_to_latlon(self, x: NUMPY_X, y: NUMPY_Y):
        """
        Convert numpy array indices to WGS84(4326) coordinates
        """

        lon = self.geotransform[0] + y * self.geotransform[1] + x * self.geotransform[2]
        lat = self.geotransform[3] + y * self.geotransform[4] + x * self.geotransform[5]
        return lat, lon
    

    def latlong_to_xy(self, lat, lon):
        """
        convert WGS84(4326) to numpy_array[x][y]
        """

        numpy_y = round((lon - self.geotransform[0]) / self.geotransform[1])
        numpy_x = round((lat - self.geotransform[3]) / self.geotransform[5])

        return numpy_x, numpy_y

    def elevation(self, latitude, longitude):
        """
        This function returns the elevation at a certain lat/long in Meters.

        :param latitude: latitude in dotted decimal notation
        :param longitude: longitude in dotted decimal notation.
        :return: elevation of coordinate in meters.
        """
        x, y = self.latlong_to_xy(latitude, longitude)
        return self.get(x, y)


    def calculate_invert_geotransform(self):
        """
        Convert projected coordinates to pixel coordinates
        
        Args:
            dataset: gdal.Dataset
            proj_x: projected x coordinate
            proj_y: projected y coordinate
        
        Returns:
            tuple: (px, py) - may be floats, use int() or round() if needed
        """
        # Calculate inverse geotransform
        det = self.geotransform[1] * self.geotransform[5] - self.geotransform[2] * self.geotransform[4]
        
        if det == 0:
            raise ValueError("Geotransform is not invertible")
        
        inv_gt = [
            -self.geotransform[0] * self.geotransform[5] + self.geotransform[2] * self.geotransform[3],
            self.geotransform[5] / det,
            -self.geotransform[2] / det,
            self.geotransform[0] * self.geotransform[4] - self.geotransform[1] * self.geotransform[3],
            -self.geotransform[4] / det,
            self.geotransform[1] / det
        ]

        return inv_gt



    #     # Necessary to extracting metadata.
    #     self.gdal_dataset = filesystem_gdal_dataset
    #     # Working  dataset
    #     self.gdal_dataset = working_gdal_dataset
    #     self.filename = filename
    #     self.spatialreference = self.gdal_dataset.GetSpatialRef()
    #     self.raster_band = self.gdal_dataset.GetRasterBand(1)
    #     self.numpy_map = numpy.array(
    #         self.gdal_dataset.GetRasterBand(1).ReadAsArray()
    #     )

    #     self.span_x = self.gdal_dataset.RasterXSize  # longitude
    #     self.span_y = self.gdal_dataset.RasterYSize  # latitude

    #     # Collect Geo Transform data for later consumption
    #     (
    #         self.most_west_longitude, self.resolution_longitude, _, #x
    #         self.most_north_latitude, _, self.resolution_latitude,  #y
    #     ) = self.gdal_dataset.GetGeoTransform()

    #     self.nodata = self.raster_band.GetNoDataValue()

    #     self.max_y = self.span_y
    #     self.max_x = self.span_x
    #     self._x_mapEdge = {0: True, self.max_x: True}
    #     self._y_mapEdge = {0: True, self.max_y: True}



