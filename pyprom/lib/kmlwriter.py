"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import logging
import os
import datetime
from fastkml import kml, styles
from shapely.geometry import Point, LineString

from .locations.summit import Summit
from .locations.saddle import Saddle
from .locations.runoff import Runoff
from .locations.spot_elevation import SpotElevation
from .containers.spot_elevation import SpotElevationContainer
from .containers.linker import Linker

NS = '{http://www.opengis.net/kml/2.2}'

SADDLE_URL = "http://maps.google.com/mapfiles/kml/paddle/grn-blank.png"
BASIN_SADDLE_URL = "http://maps.google.com/mapfiles/kml/paddle/grn-circle.png"
RUNOFF_URL = "http://maps.google.com/mapfiles/kml/paddle/blu-blank.png"
SUMMIT_URL = "http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png"
SPOTELEVATION_URL = "http://maps.google.com/mapfiles/kml/paddle/wht-blank.png"


SADDLE_ICON = styles.IconStyle(icon_href=SADDLE_URL, id="saddle")
BASIN_SADDLE_ICON = styles.IconStyle(icon_href=BASIN_SADDLE_URL,
                                     id="basinsaddle")
SUMMIT_ICON = styles.IconStyle(icon_href=SUMMIT_URL, id="summit")
RUNOFF_ICON = styles.IconStyle(icon_href=RUNOFF_URL, id="runoff")
SPOTELEVATION_ICON = styles.IconStyle(icon_href=SPOTELEVATION_URL,
                                      id="spotelevation")


SADDLE_STYLE = styles.Style(id="saddle", styles=[SADDLE_ICON])
BASIN_SADDLE_STYLE = styles.Style(id="basinsaddle",
                                  styles=[BASIN_SADDLE_ICON])
SUMMIT_STYLE = styles.Style(id="summit", styles=[SUMMIT_ICON])
RUNOFF_STYLE = styles.Style(id="runoff", styles=[RUNOFF_ICON])
SPOTELEVATION_STYLE = styles.Style(id="spotelevation",
                                   styles=[SPOTELEVATION_ICON])


class KMLFileWriter:
    """
    KMLFileWriter consumes a list of Location objects, or a Container, or a
    list of Locations and Containers and produces a KML Document which contains
    folders by location type.
    """

    def __init__(self, outputFileName, documentName=None, features=[]):
        """
        :param outputFileName: Full path and for output file.
        :param documentName: Name of root document.
        :param features: [] list of containers or locations OR a container.
        """
        self.logger = logging.getLogger('{}'.format(__name__))
        self.filename = os.path.expanduser(outputFileName)

        self.spotElevation_wkt = {}
        self.linkers_wkt = {}

        self.documentName = documentName

        self.linkers = kml.Folder(NS,
                                  name="Linkers",
                                  description="Linker Folder")
        self.saddles = kml.Folder(NS,
                                  name="Saddles",
                                  description="Saddle Folder")
        self.summits = kml.Folder(NS,
                                  name="Summits",
                                  description="Summit Folder")
        self.runOffs = kml.Folder(NS,
                                  name="RunOffs",
                                  description="RunOff Folder")
        self.spotElevations = kml.Folder(NS,
                                         name="SpotElevations",
                                         description="SpotElevation Folder")

        if features:
            self.extend(features)

    def extend(self, features):
        """
        Extend extends features onto this KMLFileWriter.
        This is intended for lists of locations, or location containers.
        :param features: list, or container
        """
        for feature in features:
            self.append(feature)

    def append(self, feature):
        """
        Append feature, or in the case of containers, pass on to extend.
        :param feature: Location or Container
        """
        # Allow appending of Containers
        if isinstance(feature, SpotElevationContainer):
            self.extend(feature)

        if isinstance(feature, Summit):
            self._append_spotElevation_derivative(feature, "Summit")

        if isinstance(feature, Runoff):
            self._append_spotElevation_derivative(feature, "RunOff")

        elif isinstance(feature, Saddle):
            self._append_spotElevation_derivative(feature, "Saddle")

        if type(feature) == SpotElevation:
            self._append_spotElevation_derivative(feature, "SpotElevation")

        if isinstance(feature, Linker):
            self._append_linker(feature)

    def _append_spotElevation_derivative(self, feature, feature_type):
        """
        Appends a spotElevation derivative to this Object
        :param feature: location object
        :param feature_type: string representation of this object.
        """
        featurePm = kml.Placemark(NS,
                                  "{:.3f}".format(feature.feet),
                                  "{:.3f}".format(feature.feet))
        featurePm.geometry = Point(feature.longitude, feature.latitude)
        if not self.spotElevation_wkt.get(feature_type +
                                          featurePm.geometry.wkt):
            self.spotElevation_wkt[feature_type +
                                   featurePm.geometry.wkt] = True
            if feature_type == "Saddle":
                featurePm.styleUrl = "#saddle"
                featurePm.description = "Saddle"
                self.saddles.append(featurePm)
            if feature_type == "Summit":
                featurePm.styleUrl = "#summit"
                featurePm.description = "Summit"
                self.summits.append(featurePm)
            if feature_type == "RunOff":
                featurePm.styleUrl = "#runoff"
                featurePm.description = "RunOff"
                self.runOffs.append(featurePm)
            if feature_type == "SpotElevation":
                featurePm.styleUrl = "#spotelevation"
                featurePm.description = "SpotElevation"
                self.spotElevations.append(featurePm)

    def _append_linker(self, linker):
        """
        Append linker object to to this Object
        :param linker: :class:`Linker`
        """
        linkerPm = kml.Placemark(NS)
        saddle = Point(linker.saddle.longitude, linker.saddle.latitude)
        summit = Point(linker.summit.longitude, linker.summit.latitude)
        linkerPm.geometry = LineString([saddle,
                                        summit])
        if not self.linkers_wkt.get(linkerPm.geometry.wkt):
            self.linkers_wkt[linkerPm.geometry.wkt] = True
            self.linkers.append(linkerPm)

    def generateDocument(self):
        """
        Generates KML document of locations in this object.
        :return: kml Document
        """
        if not self.documentName:
            self.documentName =\
                "PyProm Document {}".format(str(datetime.datetime.now()))

        kml_doc = kml.Document(ns=NS,
                               name=self.documentName)
        kml_doc.append_style(SADDLE_STYLE)
        kml_doc.append_style(SUMMIT_STYLE)
        kml_doc.append_style(BASIN_SADDLE_STYLE)
        kml_doc.append_style(RUNOFF_STYLE)
        kml_doc.append_style(SPOTELEVATION_STYLE)

        if self.saddles._features:
            self.logger.info("Saddles: {}".format(len(self.saddles._features)))
            kml_doc.append(self.saddles)
        if self.summits._features:
            self.logger.info("Summits: {}".format(len(self.summits._features)))
            kml_doc.append(self.summits)
        if self.spotElevations._features:
            self.logger.info("Spot Elevations: {}".format(len(
                self.spotElevations._features)))
            kml_doc.append(self.spotElevations)
        if self.runOffs._features:
            self.logger.info("RunOffs: {}".format(len(self.runOffs._features)))
            kml_doc.append(self.runOffs)
        if self.linkers._features:
            self.logger.info("Linkers: {}".format(len(self.linkers._features)))
            kml_doc.append(self.linkers)
        return kml_doc

    def generateKML(self):
        """
        Produces KML string of this Writer Object.
        :return: string representation of KML
        """
        k = kml.KML()
        k.append(self.generateDocument())
        return k.to_string(prettyprint=True)

    def write(self):
        """
        Write KML file.
        """
        output = open(self.filename, "w")
        output.write(self.generateKML())
        output.close()
        self.logger.info("KML File Written: {}".format(self.filename))
