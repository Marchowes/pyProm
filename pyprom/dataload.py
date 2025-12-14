"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import os
import numpy
import logging

from osgeo import gdal, osr

from .lib.datamap import ProjectionDataMap

EPSGMap = {
    "WGS84": 4326,  # http://spatialreference.org/ref/epsg/4326/
    "NAD83": 4269,  # http://spatialreference.org/ref/epsg/4269/
}


class Loader:
    """Base class for data loaders."""

    def __init__(self, filename):
        """
        :param str filename: name of file to be loaded.
        """
        self.filename = os.path.expanduser(filename)
        self.logger = logging.getLogger('{}'.format(__name__))


class GDALLoader(Loader):
    """
    | Loads Raster Data from GDAL.
    | Raster data is made available at self.datamap
    """

    def __init__(self, filename, epsg_alias="WGS84"):
        """
        :param str filename: full or relative file location.
        :param str epsg_alias: common name for epsg code
        :raises: Exception when not a Projection Map.

        | latitude and longitude references are always "lower left"
        | GDAL raster data is always presented as such:

        | Y: left/right
        | X: up/down

        | ``UL---UR``
        | ``|     |``
        | ``LL---LR``

        | The LL corner is always passed to the Datamap Object with a reference
        | to the Native grid Lower Left corner.
        """
        super(GDALLoader, self).__init__(filename)

        # Get our transform target EPSG
        epsg_code = EPSGMap.get(epsg_alias, None)
        if not epsg_code:
            raise Exception("epsg_code not understood.")

        # Load Raster File into GDAL
        self.gdal_dataset = gdal.Open(self.filename)
        if self.gdal_dataset is None:
            raise Exception("GDAL failed to load {}".format(filename))
        # Load Raster Data into numpy array
        raster_band = self.gdal_dataset.GetRasterBand(1)
        self.raster_data = numpy.array(raster_band.
                                       ReadAsArray())
        nodata = raster_band.GetNoDataValue()
        vertical_unit = raster_band.GetUnitType()
        # Gather span for X and Y axis.
        self.span_x = self.gdal_dataset.RasterXSize  # longitude
        self.span_y = self.gdal_dataset.RasterYSize  # latitude
        # Collect Geo Transform data for later consumption
        ulx, xres, xskew, uly, yskew, yres =\
            self.gdal_dataset.GetGeoTransform()
        # Get lower left Native Dataset coordinates for passing into
        # the DataMap.
        self.upperLeftY = uly
        self.upperLeftX = ulx
        spatialRef = osr.SpatialReference(
            wkt=self.gdal_dataset.GetProjection())
        # Are we a projected map?
        if spatialRef.IsProjected:
            # Create target Spatial Reference for converting coordinates.
            target = osr.SpatialReference()
            target.ImportFromEPSG(epsg_code)
            transform = osr.CoordinateTransformation(spatialRef, target)
            # create a reverse transform for translating back
            #  into Native GDAL coordinates
            reverse_transform = osr.CoordinateTransformation(target,
                                                             spatialRef)
            self.linear_unit = spatialRef.GetLinearUnits()
            self.linear_unit_name = vertical_unit

            # Create out DataMap Object.
            self.datamap = ProjectionDataMap(self.raster_data,
                                             self.upperLeftY,
                                             self.upperLeftX,
                                             yres,
                                             xres,
                                             self.span_y,
                                             self.span_x,
                                             self.linear_unit,
                                             self.linear_unit_name,
                                             nodata,
                                             transform,
                                             reverse_transform,
                                             filename)
        else:
            raise Exception("Unsupported, non projected map")
