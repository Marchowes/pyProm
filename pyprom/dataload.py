"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import os
import numpy
import logging

from osgeo import gdal, osr

from .lib.datamap import DegreesDataMap, ProjectionDataMap
from .lib.util import seconds_to_arcseconds, arcseconds_to_seconds


class Loader(object):
    def __init__(self, filename):
        """
        Base class for data loaders.
        """
        self.filename = os.path.expanduser(filename)
        self.logger = logging.getLogger('pyProm.{}'.format(__name__))


class SRTMLoader(Loader):
    def __init__(self, filename,
                 arcsec_resolution=1,
                 span_latitude=3601,
                 span_longitude=3601):
        """
        :param filename: File name, for instance ~/N44W072.hgt
        :param arcsec_resolution: how many arcseconds per measurement unit.
        :param span_latitude: source datamap point span along latitude
        :param span_longitude: source datamap point span along longitude
        latitude and longitude references are always "lower left"
        """
        super(SRTMLoader, self).__init__(filename)
        self.logger.info("Loading: {} Latitude span: {}, Longitude span: {}"
                         ", Resolution: {}"
                         " ArcSec/point.".format(filename, span_latitude,
                                                 span_longitude,
                                                 arcsec_resolution))
        self.span_latitude = span_latitude
        self.span_longitude = span_longitude
        self.arcsec_resolution = arcsec_resolution
        self.latitude = self.longitude = None
        self.latlong()
        with open(self.filename) as hgt_data:
            self.elevations = numpy.fromfile(hgt_data, numpy.dtype('>i2'),
                                             self.span_longitude *
                                             self.span_latitude).reshape((
                                              self.span_longitude,
                                              self.span_latitude))

        self.datamap = DegreesDataMap(self.elevations,
                                      self.latitude,
                                      self.longitude,
                                      self.span_latitude,
                                      self.span_longitude,
                                      self.arcsec_resolution,
                                      "METERS")

    def latlong(self):
        """
        Converts hgt filename string to usable latitude and longitude
        """
        filename = self.filename.split('/')[-1]
        latitude = filename[:3]
        longitude = filename[3:7]
        if latitude[0] == 'N':
            self.latitude = int(latitude[1:])
        if latitude[0] == 'S':
            self.latitude = -int(latitude[1:])
        if longitude[0] == 'E':
            self.longitude = int(longitude[1:])
        if longitude[0] == 'W':
            self.longitude = -int(longitude[1:])


class ADFLoader(Loader):
    """
    Arc/Info Binary Grid (.adf)
    """
    def __init__(self, filename):
        """
        :param filename:
        latitude and longitude references are always "lower left"
        """
        super(ADFLoader, self).__init__(filename)
        self.gdal_dataset = gdal.Open(self.filename)
        geotransform = self.gdal_dataset.GetGeoTransform()
        # make sure arcsecond resolution is the same on both axis. We don't
        #  support differing resolutions yet.
        if abs(geotransform[1]) != abs(geotransform[5]):
            non_symmetric_error = \
                ("BORK! arcsecond resolution for X and Y axis must match. "
                 "non symmetric transform resolution not supported yet!")
            self.logger.error(non_symmetric_error)
            raise Exception(non_symmetric_error)

        self.arcsec_resolution = seconds_to_arcseconds(geotransform[1])

        self.elevations = numpy.array(self.gdal_dataset.GetRasterBand(1).
                                      ReadAsArray())
        self.span_latitude = int(self.elevations.shape[0])
        self.span_longitude = int(self.elevations.shape[1])

        self.longitude, self.latitude =\
            getLowerLeftCoords(geotransform,
                               self.span_longitude,
                               self.span_latitude)

        self.logger.info("Loading: {} Latitude span: {}, Longitude span: {}"
                         ", Resolution: {} ArcSec/point, N Boundary {},"
                         " W Boundary {}".format(filename,
                                              self.span_latitude,
                                              self.span_longitude,
                                              self.arcsec_resolution,
                                              self.latitude,
                                              self.longitude))

        self.datamap = DegreesDataMap(self.elevations,
                                      self.latitude,
                                      self.longitude,
                                      self.span_latitude,
                                      self.span_longitude,
                                      self.arcsec_resolution,
                                      "METERS")

class LiDARLoader(Loader):
    # need to be able to extract:
    # dataset=gdal.Open('19_02744882.img')
    # UTM region () dataset.GetProjection() Projection is PROJCS["NAD_1983_UTM_Zone_19N"
    # geotransform = dataset.GetGeoTransform()
    # (274000.0, 1.0, 0.0, 4884000.0, 0.0, -1.0) < -- UTM @ 1 meter res


    """
    General GDAL datasets.
    """
    def __init__(self, filename, hemisphere="N"):
        """
        :param filename:
        latitude and longitude references are always "lower left"
        """
        super(LiDARLoader, self).__init__(filename)
        self.gdal_dataset = gdal.Open(self.filename)
        raster_band = self.gdal_dataset.GetRasterBand(1)
        self.no_data_value = raster_band.GetNoDataValue()
        self.elevations = numpy.array(raster_band.
                                      ReadAsArray())
        self.hemisphere = hemisphere
        self.span_x = self.gdal_dataset.RasterXSize # longitude
        self.span_y = self.gdal_dataset.RasterYSize # latitude
        geotransform = self.gdal_dataset.GetGeoTransform()

        # We don't know what kind of coordinate system we're using yet so jsut call them nX,nY
        self.lowerLeftX, self.lowerLeftY =\
            getLowerLeftCoords(geotransform,
                               self.span_x,
                               self.span_y)
        spatialRef = osr.SpatialReference(wkt=self.gdal_dataset.GetProjection())
        # Are we a projected map?
        if spatialRef.IsProjected:
            self.utmzone = spatialRef.GetUTMZone()
            self.linear_unit = spatialRef.GetLinearUnits()
            self.linear_unit_name = spatialRef.GetLinearUnitsName()


            if not self.utmzone:
                raise Exception("Could not read UTM Zone in projection. "
                                "This may be useful: {}".format(
                                self.gdal_dataset.GetProjectionRef()))
            self.logger.info("Loading: {} X span: {}, Y span: {}"
                             ", Resolution: {} {}, SW Boundary {},{}"
                             "Hemisphere {}, Zone {}".format(filename,
                                                             self.span_x,
                                                             self.span_y,
                                                             self.linear_unit,
                                                             self.linear_unit_name,
                                                             self.lowerLeftX,
                                                             self.lowerLeftY,
                                                             self.hemisphere,
                                                             self.utmzone))
            self.datamap = ProjectionDataMap(self.elevations,
                                             self.lowerLeftY,
                                             self.lowerLeftX,
                                             self.span_y,
                                             self.span_x,
                                             self.linear_unit,
                                             self.hemisphere,
                                             self.utmzone,
                                             self.linear_unit_name)





def getLowerLeftCoords(geoTransform, xSpan, ySpan):
    """
    :param geoTransform:  GetGeoTransform() output from gdal
    :param xSpan: raster span on X axis (points) columns
    :param ySpan: raster span on Y axis (points) rows
    :return: tuple of (X,Y) coords
    """
    x = geoTransform[0]
    y = geoTransform[3] + (ySpan*geoTransform[5])
    return (x,y)



