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
import numpy
from osgeo import gdal
from typing import TYPE_CHECKING, Tuple, Self
if TYPE_CHECKING:

    from pyprom.lib.loaders.gdal_loader import GDALLoader
    from pyprom._typing.type_hints import (
        NUMPY_X, NUMPY_Y, 
        LONGITUDE_X, LATITUDE_Y, 
        XY_COORD,
    )

class DataMap(BaseDataMap):
    def __init__(self,
        gdal_dataset: gdal.DataSet,
    ) -> None:

        self.gdal_dataset = gdal_dataset
        raster_band = self.gdal_dataset.GetRasterBand(1)
        self.nodata = raster_band.GetNoDataValue()
        self.numpy_array = numpy.array(
            raster_band.ReadAsArray()
        )
        self.geotransform = self.gdal_dataset.GetGeoTransform()

        self.max_y = self.gdal_dataset.RasterXSize - 1 # longitude, or NUMPY_Y
        self.max_x = self.gdal_dataset.RasterYSize - 1 # latitude, or NUMPY_X

        self._x_mapEdge = {0: True, self.max_x: True}
        self._y_mapEdge = {0: True, self.max_y: True}

    def xy_to_latlon(self, x: NUMPY_X, y: NUMPY_Y):
        """
        Convert numpy array indices to WGS84(4326) coordinates
        """

        lon = self.geotransform[0] + y * self.geotransform[1] + x * self.geotransform[2]
        lat = self.geotransform[3] + y * self.geotransform[4] + x * self.geotransform[5]
        return lat, lon

    def latlong_to_xy(self, lat: LATITUDE_Y, lon: LONGITUDE_X) -> XY_COORD:
        """
        convert WGS84(4326) to numpy_array[x][y]
        """

        numpy_y = round((lon - self.geotransform[0]) / self.geotransform[1])
        numpy_x = round((lat - self.geotransform[3]) / self.geotransform[5])

        return numpy_x, numpy_y

    def elevation(self, lat: LATITUDE_Y, lon: LONGITUDE_X):
        """
        This function returns the elevation at a certain lat/long in Meters.

        :param latitude: latitude in dotted decimal notation
        :param longitude: longitude in dotted decimal notation.
        :return: elevation of coordinate in meters.
        """
        return self.get(*self.latlong_to_xy(lat, lon))

    def subset(self, x: NUMPY_X, y: NUMPY_Y, x_span: int, y_span: int) -> Self:
        """
        Produce a subset  of this datamap.
        Crucially, the x,y origin and spans are NUMPY origins and spans. NOT cartesian.
        so, in this context:
        X = LONGITUDE
        Y = LATITUDE 
        """

        # remember, GDAL XY is cartesian, unlike a numpy array
        x_offset = y
        y_offset = x
        x_size = y_span
        y_size  = x_span

        dataset = gdal.Translate(
            '',
            self.gdal_dataset,
            srcWin=[x_offset, y_offset, x_size, y_size],
            format='MEM'
        )

        return DataMap(dataset)
