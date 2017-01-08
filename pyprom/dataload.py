"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import os
import gdal
import numpy
import logging

from lib.datamap import DataMap


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

        self.datamap = DataMap(self.elevations,
                               self.latitude,
                               self.longitude,
                               self.span_latitude,
                               self.span_longitude,
                               self.arcsec_resolution)

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
    latitude/longitude should be from the Lower Left corner of the map. see
    USGS_NED_13_XXXXX_ArcGrid_meta.txt for these values.
    """
    def __init__(self, filename,
                 latitude, longitude,
                 arcsec_resolution=1):
        super(ADFLoader, self).__init__(filename)
        self.latitude = latitude
        self.longitude = longitude
        self.arcsec_resolution = arcsec_resolution

        gdal_raster = gdal.Open(self.filename)
        self.elevations = numpy.array(gdal_raster.GetRasterBand(1).
                                      ReadAsArray())
        self.span_latitude = int(self.elevations.shape[0])
        self.span_longitude = int(self.elevations.shape[1])
        self.logger.info("Loading: {} Latitude span: {}, Longitude span: {}"
                         ", Resolution: {}"
                         " ArcSec/point.".format(filename,
                                                 self.span_latitude,
                                                 self.span_longitude,
                                                 arcsec_resolution))

        self.datamap = DataMap(self.elevations,
                               self.latitude,
                               self.longitude,
                               self.span_latitude,
                               self.span_longitude,
                               self.arcsec_resolution)
