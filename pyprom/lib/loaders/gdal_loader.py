"""
pyProm: Copyright Marc Howes 2016 - 2025.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from pathlib import Path

from osgeo import gdal
from .util.metricate_vertical_dataset import convert_dataset_vertical_units_to_meters
from .util.warp_to_geographic import warp_to_geographic
from pyprom.lib.datamaps.datamap import DataMap


class BaseLoader:
    """
    Base class for data loaders.
    """
    filename: Path

    def __init__(self, filename: str) -> None:
        """
        :param str filename: name of file to be loaded.
        """
        self.filename = Path(filename).expanduser()
        if not self.filename.exists():
            raise OSError("File does not exist or uses unfamiliar formatting.")

class GDALLoader(BaseLoader):
    """
    Load Geospatial files using GDAL.

    This loader performs two crucial functions:
    - Converts source data from whatever it is to WGS84 coordinate system.
    - Converts vertical units to meters.
    
    """
    source_gdal_dataset: gdal.Dataset
    gdal_dataset: gdal.Dataset

    def __init__(self, filename: str) -> None:
        super().__init__(filename)
        self.source_gdal_dataset = gdal.Open(self.filename)
        self.gdal_dataset = convert_dataset_vertical_units_to_meters(
            warp_to_geographic(self.source_gdal_dataset)
        )

    def to_datamap(self) -> DataMap:
        """
        Create a DataMap from this Loader
        """
        return DataMap.from_loader(self)
