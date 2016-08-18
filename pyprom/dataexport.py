from pykml.factory import KML_ElementMaker as KML
from lxml import etree
class KMLfileWriter(object):
    def __init__(self, kmlList, outputFile):
        self.kml = kmlList
        self.outputFile = outputFile
        self.kmlPoints = list()


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
                KML.coordinates("{},{}".format(spotElevation.longitude, spotElevation.latitude))))

    def writeFile(self):
        output = open(self.outputFile, "w")
        output.write(etree.tostring(KML.kml(KML.Document(self.kmlFolder)), pretty_print=True))
        output.close()