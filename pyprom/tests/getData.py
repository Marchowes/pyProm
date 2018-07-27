"""
pyProm: Copyright 2017.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import logging
import zipfile
import os.path
import urllib.request


def gettestzip():
    """Function is for pulling down the desired test data."""
    logger = logging.getLogger('pyProm.{}'.format(__name__))
    domain = "https://dds.cr.usgs.gov"
    path = "srtm/version2_1/SRTM1/Region_06"
    nh_north = "N44W072"
    hgtsuffix = ".hgt"
    suffix = ".hgt.zip"
    nh_north_zip = nh_north + suffix
    tmp = "/tmp"
    destination = "{}/{}".format(tmp, nh_north + suffix)

    extracted = tmp + "/" + nh_north + hgtsuffix

    fullPath = ("/".join([domain, path, nh_north_zip]))

    if not os.path.isfile(extracted):
        logger.info("Downloading {} to {}".format(nh_north_zip, destination))
        urllib.request.urlretrieve(fullPath, destination)

        logger.info("Extracting {} to {}".format(destination, extracted))
        zip_ref = zipfile.ZipFile(destination, 'r')
        zip_ref.extractall(tmp)
        zip_ref.close()
    else:
        logger.info("Already have {}".format(extracted))
