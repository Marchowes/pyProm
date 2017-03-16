import sys
import logging
import zipfile
import os.path
python_version = sys.version_info.major

if python_version == 2:
    import urllib
else:
    import urllib.request


def getTestZip():
    """
    Python 2 and 3 compatible helper function for pulling down the
    desired test data.
    """

    logger = logging.getLogger('pyProm.{}'.format(__name__))
    domain = "https://dds.cr.usgs.gov"
    path = "srtm/version2_1/SRTM1/Region_06"
    nh_north = "N44W072"
    hgtsuffix = ".hgt"
    suffix = ".hgt.zip"
    nh_north_zip = nh_north+suffix
    tmp = "/tmp"
    destination = "{}/{}".format(tmp,nh_north+suffix)

    extracted = tmp+"/"+nh_north+hgtsuffix

    fullPath = ("/".join([domain, path, nh_north_zip]))

    if not os.path.isfile(extracted):
        logger.info("Downloading {} to {}".format(nh_north_zip, destination))

        if python_version == 2:
            urllib.urlretrieve(fullPath, destination)
        else:
            urllib.request.urlretrieve(fullPath, destination)

        logger.info("Extracting {} to {}".format(destination, extracted))
        zip_ref = zipfile.ZipFile(destination, 'r')
        zip_ref.extractall(tmp)
        zip_ref.close()
    else:
        logger.info("Already have {}".format(extracted))