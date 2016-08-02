import os
import numpy
from lib.geodatamap import DataMap

class SRTMLoader(object):
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
        self.span_latitude = span_latitude
        self.span_longitude = span_longitude
        self.arcsec_resolution = arcsec_resolution
        self.filename = os.path.expanduser(filename)
        self.latitude = self.longitude = None
        self.latlong()
        with open(self.filename) as hgt_data:
            self.elevations = numpy.fromfile(hgt_data, numpy.dtype('>i2'),
                              self.span_longitude*
                              self.span_latitude).reshape((
                              self.span_longitude,
                              self.span_latitude))

        self.geodatamap = DataMap(self.elevations,
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

