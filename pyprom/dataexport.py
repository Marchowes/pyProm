"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import logging
import os
from fastkml import kml
from shapely.geometry import Point
from .lib.containers.spot_elevation import SpotElevationContainer


class KMLfileWriter(object):
    """
    KML file writer
    """

    def __init__(self, kmlList, outputFile):
        """
        :param kmlList: a list of SpotElevation type objects, or a
         SpotElevationContainer object
        :param outputFile: /path/to/your/file.kml
        """
        self.logger = logging.getLogger('{}'.format(__name__))
        if isinstance(kmlList, SpotElevationContainer):
            kmlList = kmlList.points
        self.kml = kmlList
        self.outputFile = os.path.expanduser(outputFile)
        self.kmlPoints = list()
        self.logger.info("KML Output: {}, {} points".format(outputFile,
                                                            len(kmlList)))
        self.k = kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'

        # Create a KML Document and add it to the KML root object
        d = kml.Document(ns,
                         'docid',
                         'doc name',
                         'doc description')
        self.k.append(d)
        self.kmlFolder = kml.Folder(ns,
                                    'timedatepeaks',
                                    'peaks',
                                    'kml map of summits')
        for spotElevation in kmlList:
            self.kmlFolder.append(self.generateKMLPlacemark(spotElevation))
        d.append(self.kmlFolder)

    def generateKMLPlacemark(self, spotElevation):
        """
        :param spotElevation:
        :return:
        """
        ns = '{http://www.opengis.net/kml/2.2}'
        p = kml.Placemark(ns,
                          "{:.3f}".format(spotElevation.feet),
                          "{:.3f}".format(spotElevation.feet),
                          'Summit')
        p.geometry = Point(spotElevation.longitude, spotElevation.latitude)
        return p

    def writeFile(self):
        """
        Write KML file.
        """
        output = open(self.outputFile, "w")
        output.write(self.k.to_string(prettyprint=True))
        output.close()
        self.logger.info("KML File Written: {}".format(self.outputFile))
