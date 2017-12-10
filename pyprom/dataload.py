"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import os
import numpy
import logging

from osgeo import gdal, osr

from .lib.datamap import ProjectionDataMap

EPSGMap = {
            "WGS84": 4326, #http://spatialreference.org/ref/epsg/4326/
            "NAD83": 4269, #http://spatialreference.org/ref/epsg/4269/
}


class Loader(object):
    def __init__(self, filename):
        """
        Base class for data loaders.
        """
        self.filename = os.path.expanduser(filename)
        self.logger = logging.getLogger('{}'.format(__name__))

class GDALLoader(Loader):

    """
    General GDAL datasets.
    """
    def __init__(self, filename, epsg_alias="WGS84"):
        """
        :param filename: full or relative file location.
        :param epsg_alias: common name for epsg code

        latitude and longitude references are always "lower left"
        GDAL raster data is always presented as such:

        Y: left/right
        X: up/down

        UL---UR
        |     |
        LL---LR

        The LL corner is always passed to the Datamap Object with a reference
        to the Native grid Lower Left corner.

        """
        super(GDALLoader, self).__init__(filename)

        # Get our transform target EPSG
        epsg_code = EPSGMap.get(epsg_alias, None)
        if not epsg_code:
            raise Exception("epsg_code not understood.")


        # Load Raster File into GDAL
        self.gdal_dataset = gdal.Open(self.filename)
        # Load Raster Data into numpy array
        raster_band = self.gdal_dataset.GetRasterBand(1)
        self.raster_data = numpy.array(raster_band.
                                      ReadAsArray())
        # Gather span for X and Y axis.
        self.span_x = self.gdal_dataset.RasterXSize # longitude
        self.span_y = self.gdal_dataset.RasterYSize # latitude
        # Collect Geo Transform data for later consumption
        ulx, xres, xskew, uly, yskew, yres =\
            self.gdal_dataset.GetGeoTransform()
        # Get lower left Native Dataset coordinates for passing into
        # the DataMap.
        self.upperLeftY = uly
        self.upperLeftX = ulx
        self.lowerLeftX, self.lowerLeftY =\
            getLowerLeftCoords(ulx, uly, yres, self.span_y)
        spatialRef = osr.SpatialReference(
            wkt=self.gdal_dataset.GetProjection())
        # Are we a projected map?
        if spatialRef.IsProjected:
            # Create target Spatial Reference for converting coordinates.
            target = osr.SpatialReference()
            target.ImportFromEPSG(epsg_code)
            transform = osr.CoordinateTransformation(spatialRef, target)
            # create a reverse transform for translating back
            #  into Native GDAL coordiantes
            reverse_transform = osr.CoordinateTransformation(target,
                                                             spatialRef)
            self.linear_unit = spatialRef.GetLinearUnits()
            self.linear_unit_name = spatialRef.GetLinearUnitsName()

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
                                             transform,
                                             reverse_transform)
        else:
            raise Exception("Unsupported, non projected map")



def getLowerLeftCoords(ulx, uly, yres, ySpan):
    """
    :param ulx:  upper left X
    :param uly: upper left Y
    :param yres: y axis linear resolution
    :param xSpan: raster span on X axis (points) columns
    :param ySpan: raster span on Y axis (points) rows
    :return: tuple of (X,Y) coords
    """
    return (ulx,uly + (ySpan*yres))



