import logging
import os
from pykml.factory import KML_ElementMaker as KML
from lxml import etree
from lib.locations import SpotElevationContainer


class KMLfileWriter(object):
    def __init__(self, kmlList, outputFile):
        """
        :param kmlList: a list of SpotElevation type objects, or a
         SpotElevationContainer object
        :param outputFile: /path/to/your/file.kml
        """
        self.logger = logging.getLogger('pyProm.{}'.format(__name__))
        self.logger.info("KML Output: {}, {} points".format(outputFile,
                                                            len(kmlList)))
        self.kml = kmlList
        self.outputFile = os.path.expanduser(outputFile)
        self.kmlPoints = list()
        if isinstance(kmlList, SpotElevationContainer):
            kmlList = kmlList.points
        for spotElevation in kmlList:
            self.kmlPoints.append(self.generateKMLPlacemark(spotElevation))
        self.kmlFolder = KML.folder(*self.kmlPoints)

    def generateKMLPlacemark(self, spotElevation):
        """
        :param spotElevation:
        :return:
        """
        return KML.Placemark(
            KML.name(spotElevation.feet),
            KML.Point(
                KML.coordinates("{},{}".format(spotElevation.longitude,
                                               spotElevation.latitude))))

    def writeFile(self):
        output = open(self.outputFile, "w")
        output.write(etree.tostring(KML.kml(KML.Document(self.kmlFolder)),
                                    pretty_print=True))
        output.close()
        self.logger.info("KML File Written: {}".format(self.outputFile))
