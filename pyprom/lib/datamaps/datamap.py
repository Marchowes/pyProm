"""
pyProm: Copyright Marc Howes 2016 - 2025.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This file acts as the glue between the raster data loaded and the logic
used to analyze the map.
"""
from __future__ import annotations
import logging

from .base_datamap import BaseDataMap
import numpy
from osgeo import gdal
from shapely.geometry import Polygon
from pyprom.lib.util import checksum
from numpy import array2string

from typing import TYPE_CHECKING, Self, Any, Tuple
if TYPE_CHECKING:
    from pyprom.lib.loaders.gdal_loader import GDALLoader
    from pyprom._typing.type_hints import (
        Numpy_X, Numpy_Y, 
        Longitude_Y, Latitude_X, 
        XY,
        Elevation,
        LatLon
    )


class DataMap(BaseDataMap):
    """
    Datamap is the the interface between pyProm and 
    our raster data.

    Datamap provides the base numpy array as well as a
    number of utility functions for translating numpy x/y values
    to WGS84 geographic coordinates, iterators and more.
    """
    gdal_dataset: gdal.Dataset
    geotransform: Tuple[float, float, float, float, float ,float]
    max_x: int
    max_y: int
    nodata: Any
    numpy_array: numpy.NDArray

    def __init__(self,
        loader: GDALLoader,
        gdal_dataset: gdal.Dataset,
    ) -> None:
        self.loader = loader
        self.gdal_dataset = gdal_dataset
        raster_band = self.gdal_dataset.GetRasterBand(1)
        self.nodata = raster_band.GetNoDataValue()
        self.numpy_array = numpy.array(
            raster_band.ReadAsArray(buf_type=gdal.GDT_Float32)
        )
        self.md5 = f'{checksum(loader.filename)}{hash(array2string(self.numpy_array))}'
        self.geotransform = self.gdal_dataset.GetGeoTransform()

        self.max_y = self.gdal_dataset.RasterXSize - 1 # longitude, or NUMPY_Y
        self.max_x = self.gdal_dataset.RasterYSize - 1 # latitude, or NUMPY_X

        self._x_mapEdge = {0: True, self.max_x: True}
        self._y_mapEdge = {0: True, self.max_y: True}

    @classmethod
    def from_loader(cls, loader: GDALLoader) -> Self:
        """
        Creates DataMap from a GDALLoader
        """
        return cls(loader, loader.gdal_dataset)


    def xy_to_latlon(self, x: Numpy_X, y: Numpy_Y) -> LatLon:
        """
        Convert numpy array indices to WGS84(4326) coordinates
        """
        lon = self.geotransform[0] + y * self.geotransform[1] + x * self.geotransform[2]
        lat = self.geotransform[3] + y * self.geotransform[4] + x * self.geotransform[5]
        # lon = self.geotransform[0] + (y * self.geotransform[1])
        # lat = self.geotransform[3] + (x * self.geotransform[4])
        return lat, lon

    def latlong_to_xy(self, lat: Latitude_X, lon: Longitude_Y) -> XY:
        """
        convert WGS84(4326) to numpy_array[x][y]
        """

        numpy_y = round((lon - self.geotransform[0]) / self.geotransform[1])
        numpy_x = round((lat - self.geotransform[3]) / self.geotransform[5])

        return numpy_x, numpy_y

    def elevation(self, lat: Latitude_X, lon: Longitude_Y) -> Elevation:
        """
        This function returns the elevation at a certain lat/long in Meters.

        :param latitude: latitude in dotted decimal notation
        :param longitude: longitude in dotted decimal notation.
        :return: elevation of coordinate in meters.
        """
        return self.get(*self.latlong_to_xy(lat, lon))

    def subset(self, x: Numpy_X, y: Numpy_Y, x_span: int, y_span: int) -> Self:
        """
        Produce a subset of this datamap.
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

        return DataMap(self.loader, dataset)

    def point_geom(self, x: Numpy_X, y: Numpy_Y) -> Polygon:
        """
        :param x: x coordinate
        :param y: y coordinate
        :return: :class:`shapely.geometry.polygon.Polygon` of this point
        """
        local_lat, local_long = self.xy_to_latlon(x, y)
        corners = list()
        for c_x, c_y, _ in self.iterateDiagonal(x, y):
            remote_lat, remote_long = self.xy_to_latlon(c_x, c_y)
            #shapely coords is long, lat
            corners.append(((local_long + remote_long)/2, (local_lat + remote_lat)/2))
        return Polygon(corners)

    @property
    def upper_left(self) -> LatLon:
        return self.xy_to_latlon(0, 0)

    @property
    def lower_left(self) -> LatLon:
        return self.xy_to_latlon(self.max_x, 0)

    @property
    def upper_right(self) -> LatLon:
        return self.xy_to_latlon(0, self.max_y)

    @property
    def lower_right(self) -> LatLon:
        return self.xy_to_latlon(self.max_x, self.max_y)

    def numpy_array_override(self, 
            numpy_array: numpy.ndarray
        ) -> None:
        """
        Override our numpy array with a different array of the same shape (x/y span)
        (useful for testing)
        """
        assert numpy_array.shape == self.numpy_array.shape
        self.numpy_array = numpy_array