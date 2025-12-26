"""
pyProm: Copyright Marc Howes 2016 - 2025.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from pathlib import Path

from osgeo import gdal
from .util.metricate_vertical_dataset import convert_dataset_vertical_units_from_feet_to_meters
from .util.warp_to_geographic import warp_to_geographic
from .util.detect_vertical_units import detect_vertical_unit
from pyprom.lib.datamaps.datamap import DataMap
from pyprom.lib.constants import Units, Confidence

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

    def __init__(self,
            filename: str,
            band_index: int = 1,
            force_vertical_units: Units | None = None,
            gdal_min_vertical_unit_condence: Confidence = Confidence.MEDIUM
        ) -> None:
        """
        Create Dataload and provide any necessary overrides.

        Args:
            filename (str): Our path.
            band_index (int, optional): The Raster band. This is
                almost always band 1.
            force_vertical_units (Units | None, optional): If GDAL can't 
                figure out the vertical units, you must provide.
            gdal_min_vertical_unit_condence (Confidence, optional): We 
                use a function to determine the vertical units. it has
                a variety of confidence levels. Defaults to Confidence.MEDIUM.

        """
        super().__init__(filename)
        self.source_gdal_dataset = gdal.Open(self.filename)

        # We need to make some considerations for Vertical units.
        # pyProm expects all data to come in with metric units, so if our
        # source data is NOT in metric units, we need to change that.
        # Sometimes GDAL will fail to figure out the vertical units, so we have to
        # offer users an opportunity to provide and override.
        if force_vertical_units:
            units = force_vertical_units
        else:
            units, confidence = detect_vertical_unit(self.source_gdal_dataset, band_index)
            if confidence < gdal_min_vertical_unit_condence or units == Units.UNKNOWN:
                raise Exception("Couldn't confidently determine Vertical Units. Try manual override if known")
        if units != Units.METERS:
            self.gdal_dataset = convert_dataset_vertical_units_from_feet_to_meters(self.source_gdal_dataset, band_index)    
        else:
            self.gdal_dataset = self.source_gdal_dataset

        # pyprom also expects data to be geographic (that is, lat/lon or WGS84)
        self.gdal_dataset = warp_to_geographic(self.source_gdal_dataset)

    def to_datamap(self) -> DataMap:
        """
        Create a DataMap from this Loader
        """
        return DataMap.from_loader(self)
