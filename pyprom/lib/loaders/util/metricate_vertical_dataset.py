"""
pyProm: Copyright Marc Howes 2016 - 2025.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from osgeo import gdal
from pyprom.lib import constants

def convert_dataset_vertical_units_from_feet_to_meters(
        dataset: gdal.Dataset,
        band_index: int = 1
    ) -> gdal.Dataset:
    """
    Converts the Vertical units in this dataset to Meters.
    """        
    raster_band = dataset.GetRasterBand(band_index)

    # As of GDAL 3.9 the recognized units are
    # m, metre, metre, ft, foot, US survey foot
    # see docs https://gdal.org/_/downloads/en/release-3.9/pdf/ pp118
    
    projection = dataset.GetProjection()
    geotransform = dataset.GetGeoTransform()

    # Convert stupid units to Metric.
    raster_array = raster_band.ReadAsArray()
    raster_array_meters = raster_array * constants.METERS_PER_FOOT

    # Make sure we set our unit type as 'm' just in case someone reads this later.
    raster_array_meters.SetUnitType('m')

    mem_driver = gdal.GetDriverByName('MEM')
    metric_vertical_dataset = mem_driver.Create(
        '', 
        dataset.RasterXSize, 
        dataset.RasterYSize, 
        1, 
        raster_band.DataType
    )
    metric_vertical_dataset.SetGeoTransform(geotransform)
    metric_vertical_dataset.SetProjection(projection)
    metric_vertical_dataset.GetRasterBand(band_index).WriteArray(raster_array_meters)
    
    return metric_vertical_dataset
