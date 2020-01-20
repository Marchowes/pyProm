"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import logging
import os
import datetime
from fastkml import kml, styles

from .locations.summit import Summit
from .locations.saddle import Saddle
from .locations.runoff import Runoff
from ..domain import Domain
from .locations.spot_elevation import SpotElevation
from .containers.spot_elevation import SpotElevationContainer
from .containers.summit_domain import SummitDomain

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

    def __init__(self, outputFileName, documentName=None, features=[], noFeatureDescription=False):
        """
        :param str outputFileName: Full path and for output file.
        :param str documentName: Name of root document.
        :param features: list of containers or locations OR a container.
        :type features: list, :class:`pyprom.lib.containers.spot_elevation.SpotElevationContainer`
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
        self.runoffs = kml.Folder(NS,
                                  name="Runoffs",
                                  description="Runoff Folder")
        self.spotElevations = kml.Folder(NS,
                                         name="SpotElevations",
                                         description="SpotElevation Folder")
        self.summitDomains = kml.Folder(NS,
                                         name="SummitDomains",
                                         description="SummitDomain Folder")

        self.noFeatureDescription = noFeatureDescription

        # This must be the last value set in __init__()
        if features:
            self.extend(features)

    def extend(self, features):
        """
        Extend extends features onto this KMLFileWriter.
        This is intended for lists of locations, or location containers.

        :param features: list of features, or container
        :type features: list, :class:`pyprom.lib.containers.spot_elevation.SpotElevationContainer`
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
            return

        if isinstance(feature, Summit):
            self._append_spotElevation_derivative(feature, "Summit")
            return

        if isinstance(feature, Runoff):
            self._append_spotElevation_derivative(feature, "RunOff")
            return

        elif isinstance(feature, Saddle):
            if feature.disqualified:
                self._append_spotElevation_derivative(feature, "BasinSaddle")
            else:
                self._append_spotElevation_derivative(feature, "Saddle")
            return

        if type(feature) == SpotElevation:
            self._append_spotElevation_derivative(feature, "SpotElevation")
            return

        if isinstance(feature, Linker):
            self._append_linker(feature)
            return

        if isinstance(feature, Domain):
            self.extend(feature.linkers)
            self.extend(feature.saddles)
            self.extend(feature.summits)
            self.extend(feature.runoffs)
            self.extend(feature.summit_domains)
            return

        if isinstance(feature, SummitDomain):
            self._append_summit_domain(feature)
            return

        raise Exception("Did not find any valid Datatypes to append."
                        " Try extend?")

    def _append_summit_domain(self, feature):
        featurePm = kml.Placemark(NS,
                                  "{:.3f}".format(feature.summit.feet),
                                  "{:.3f}".format(feature.summit.feet))
        featurePm.geometry = feature.shape
        self.summitDomains.append(featurePm)


    def _append_spotElevation_derivative(self, feature, feature_type):
        """
        Appends a spotElevation derivative to this Object

        :param feature: location object
        :param str feature_type: string representation of this object.
        """

        featurePm = kml.Placemark(NS,
                                  "{:.3f}".format(feature.feet),
                                  "{:.3f}".format(feature.feet))
        featurePm.geometry = feature.shape
        if not self.spotElevation_wkt.get(feature_type +
                                          featurePm.geometry.wkt):
            self.spotElevation_wkt[feature_type +
                                   featurePm.geometry.wkt] = True
            if not self.noFeatureDescription:
                featurePm.description = \
                    " {} {}\n {} meters\n {} feet\n {}\n".format(
                    feature.latitude, feature.longitude,
                    feature.elevation, feature.feet, feature_type)
            if feature_type == "BasinSaddle":
                featurePm.styleUrl = "#basinsaddle"
                self.saddles.append(featurePm)
            elif feature_type == "Saddle":
                featurePm.styleUrl = "#saddle"
                self.saddles.append(featurePm)
            elif feature_type == "Summit":
                featurePm.styleUrl = "#summit"
                self.summits.append(featurePm)
            elif feature_type == "RunOff":
                featurePm.styleUrl = "#runoff"
                self.runoffs.append(featurePm)
            elif feature_type == "SpotElevation":
                featurePm.styleUrl = "#spotelevation"
                self.spotElevations.append(featurePm)

    def _append_linker(self, linker):
        """
        Append linker object to to this Object

        :param linker: :class:`Linker`
        """
        linkerPm = kml.Placemark(NS)
        linkerPm.geometry = linker.shape
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
        if self.runoffs._features:
            self.logger.info("RunOffs: {}".format(len(self.runoffs._features)))
            kml_doc.append(self.runoffs)
        if self.linkers._features:
            self.logger.info("Linkers: {}".format(len(self.linkers._features)))
            kml_doc.append(self.linkers)
        if self.summitDomains._features:
            self.logger.info("SummitDomains: {}".format(len(
                self.summitDomains._features)))
            kml_doc.append(self.summitDomains)
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
        Write KML data to file.
        """
        output = open(self.filename, "w")
        output.write(self.generateKML())
        output.close()
        self.logger.info("KML File Written: {}".format(self.filename))
