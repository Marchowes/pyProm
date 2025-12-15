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
from .lib.constants import METERS_PER_FOOT, METERS_PER_SURVEY_FOOT, GDAL_METERS, GDAL_FEET, GDAL_SURVEY_FOOT


EPSGMap = {
    "WGS84": 4326,  # http://spatialreference.org/ref/epsg/4326/
    "NAD83": 4269,  # http://spatialreference.org/ref/epsg/4269/
}

class BaseLoader:
    """Base class for data loaders."""

    def __init__(self, filename: str):
        """
        :param str filename: name of file to be loaded.
        """
        self.filename = os.path.expanduser(filename)
        self.logger = logging.getLogger('{}'.format(__name__))


class GDALLoader2(BaseLoader):
    """
    Loads File using GDAL
    """
    def __init__(self, filename: str):
        super().__init__(filename)

        incoming_gdal_dataset = gdal.Open(self.filename)
        if incoming_gdal_dataset is None:
            raise Exception("GDAL failed to load {}".format(filename))

        


        # Ensure our dataset is metric.
        vertical_meter_dataset = self.convert_dataset_vertical_units_to_meters(incoming_gdal_dataset)

        # Ensure we're 4326
        self.gdal_dataset = self.reproject_dataset(vertical_meter_dataset)


    def read(self, dataset: gdal.Dataset):

        # Ensure our dataset is metric.
        vertical_meter_dataset = self.convert_dataset_vertical_units_to_meters(dataset)

        # Ensure we're 4326
        self.gdal_dataset = self.reproject_dataset(vertical_meter_dataset)
        

        # Load Raster Data into numpy array
        raster_band = self.gdal_dataset.GetRasterBand(1)
        self.raster_data = numpy.array(
            raster_band.ReadAsArray()
        )
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
            reverse_transform = osr.CoordinateTransformation(
                target,
                spatialRef)
            self.linear_unit = spatialRef.GetLinearUnits()
            self.linear_unit_name = vertical_unit

            # Create out DataMap Object.
            self.datamap = ProjectionDataMap(
                self.raster_data,
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
                filename
            )
        else:
            raise Exception("Unsupported, non projected map")





    def reproject_dataset(self,
            dataset: gdal.Dataset,
            epsg_code: int | None = 4326,
        ) -> gdal.Dataset:
        """
        Reprojects to a default SRS of 4326.

        Args:
            dataset (gdal.Dataset): dataset to reproject.
            epsg_code (int | None, optional): Target EPSG code. Defaults to 4326.

        Returns:
            gdal.Dataset: reprojected dataset.
        """

        target_srs = osr.SpatialReference()
        target_srs.ImportFromEPSG(epsg_code)
        target_wkt = target_srs.ExportToWkt()

        # Warp our raster to conform to 4326
        mem_driver = gdal.GetDriverByName('MEM')
        return gdal.Warp(
            '',
            dataset,
            format='MEM',
            dstSRS=target_wkt,
            resampleAlg=gdal.GRA_Bilinear
        )

    def convert_dataset_vertical_units_to_meters(self, 
            dataset: gdal.Dataset
        ) -> gdal.Dataset:
        """
        Converts the Vertical units in this dataset to Meters.
        """        
        raster_band = dataset.GetRasterBand(1)

        # As of GDAL 3.9 the recognized units are
        # m, metre, metre, ft, foot, US survey foot
        # see docs https://gdal.org/_/downloads/en/release-3.9/pdf/ pp118
        vertical_unit = raster_band.GetUnitType()
        # Already meters? Bail.
        if vertical_unit in GDAL_METERS:
            return dataset
        
        projection = dataset.GetProjection()
        geotransform = dataset.GetGeoTransform()

        # Convert stupid units to Metric.
        raster_array = raster_band.ReadAsArray()
        if vertical_unit in GDAL_FEET:
            raster_array_meters = raster_array * METERS_PER_FOOT
        elif vertical_unit in GDAL_SURVEY_FOOT:
            raster_array_meters = raster_array * METERS_PER_SURVEY_FOOT
        else:
            raise Exception(f"Could not recognize units. {vertical_unit}")

        # Make sure we set our unit type as 'm' just in case someone reads this later.
        raster_array_meters.SetUnitType('m')

        mem_driver = gdal.GetDriverByName('MEM')
        metric_vertical_dataset = mem_driver.Create('', dataset.RasterXSize, dataset.RasterYSize, 1, raster_band.DataType)
        metric_vertical_dataset.SetGeoTransform(geotransform)
        metric_vertical_dataset.SetProjection(projection)
        metric_vertical_dataset.GetRasterBand(1).WriteArray(raster_array_meters)
        
        return metric_vertical_dataset
















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
