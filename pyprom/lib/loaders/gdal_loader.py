"""
pyProm: Copyright 2025.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import pyproj
import logging
from pathlib import Path

from osgeo import gdal
from .util.metricate_vertical_dataset import convert_dataset_vertical_units_to_meters
from .util.warp_to_geographic import warp_to_geographic


    

class BaseLoader:
    """
    Base class for data loaders.
    """
    filename: Path
    logger: logging.Logger

    def __init__(self, filename: str) -> None:
        """
        :param str filename: name of file to be loaded.
        """
        self.filename = Path(filename).expanduser()
        self.logger = logging.getLogger('{}'.format(__name__))
        if not self.filename.exists():
            raise OSError("File does not exist or uses unfamiliar formatting.")

class GDALLoader(BaseLoader):
    """
    Load Geospatial files using GDAL.

    Performs some minor reprojections and unit conversions.
    This ensures data present in the DataMap is always consistent.
    """
    source_gdal_dataset: gdal.Dataset
    gdal_dataset: gdal.Dataset

    def __init__(self, filename: str) -> None:
        super().__init__(filename)
        self.source_gdal_dataset = gdal.Open(self.filename)
        self.gdal_dataset = convert_dataset_vertical_units_to_meters(
            warp_to_geographic(self.source_gdal_dataset)
        )



    #def to_datamap()
