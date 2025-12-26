from osgeo import gdal, osr

def warp_to_geographic(dataset: gdal.Dataset) -> gdal.Dataset:
    """
    Reprojects our data to 4326.

    Args:
        dataset (gdal.Dataset): dataset to reproject.
        epsg_code (int | None, optional): Target EPSG code. Defaults to 4326.

    Returns:
        gdal.Dataset: reprojected dataset.
    """

    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(4326)
    target_wkt = target_srs.ExportToWkt()

    # Warp our raster to conform to 4326
    mem_driver = gdal.GetDriverByName('MEM')
    return gdal.Warp(
        '',
        dataset,
        format='MEM',
        dstSRS=target_wkt,
        resampleAlg=gdal.GRA_Bilinear
    )