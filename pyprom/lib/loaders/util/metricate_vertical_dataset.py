from osgeo import gdal
from pyprom.lib import constants

def convert_dataset_vertical_units_to_meters(dataset: gdal.Dataset) -> gdal.Dataset:
    """
    Converts the Vertical units in this dataset to Meters.
    """        
    raster_band = dataset.GetRasterBand(1)

    # As of GDAL 3.9 the recognized units are
    # m, metre, metre, ft, foot, US survey foot
    # see docs https://gdal.org/_/downloads/en/release-3.9/pdf/ pp118
    vertical_unit = raster_band.GetUnitType()
    # Already meters? Bail.
    if vertical_unit in constants.GDAL_METERS:
        return dataset
    
    projection = dataset.GetProjection()
    geotransform = dataset.GetGeoTransform()

    # Convert stupid units to Metric.
    raster_array = raster_band.ReadAsArray()
    if vertical_unit in constants.GDAL_FEET:
        raster_array_meters = raster_array * constants.METERS_PER_FOOT
    elif vertical_unit in constants.GDAL_SURVEY_FOOT:
        raster_array_meters = raster_array * constants.METERS_PER_SURVEY_FOOT
    else:
        raise Exception(f"Could not recognize units. {vertical_unit}")

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
    metric_vertical_dataset.GetRasterBand(1).WriteArray(raster_array_meters)
    
    return metric_vertical_dataset
