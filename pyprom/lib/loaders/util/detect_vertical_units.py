"""
pyProm: Copyright Marc Howes 2016 - 2025.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

import numpy as np
from osgeo import gdal, osr

from pyprom.lib import constants 
from typing import Literal, Tuple



def detect_vertical_unit(
        gdal_dataset: gdal.Dataset,
        band_index: int = 1,
        sample_size: int = 100_000
    ) -> Tuple[constants.Units, constants.Confidence]:
    """
    Attempt to determine vertical units for a raster band.
    """

    band = gdal_dataset.GetRasterBand(band_index)

    # Retrieve Authoritative units from band.
    band_unit = band.GetUnitType()
    if band_unit:
        band_unit = band_unit.lower()
        if band_unit in constants.GDAL_METERS:
            return constants.Units.METERS, constants.Confidence.HIGH
        if band_unit in constants.GDAL_FEET:
            return constants.Units.FEET, constants.Confidence.HIGH

    # If we didn't find any Authoritative units, see if linear units can give us a hint.
    wkt = gdal_dataset.GetProjection()
    if wkt:
        srs = osr.SpatialReference(wkt=wkt)

        if srs.IsGeographic():
            # Horizontal degrees → vertical unknown
            pass
        else:
            unit_name = srs.GetLinearUnitsName().lower()
            unit_factor = srs.GetLinearUnits()

            if abs(unit_factor - 1.0) < 1e-9:
                return constants.Units.METERS, constants.Confidence.MEDIUM

            if abs(unit_factor - constants.METERS_PER_FOOT) < 1e-6:
                return constants.Units.FEET, constants.Confidence.MEDIUM

    # If all else fails try a heuristic?
    nodata = band.GetNoDataValue()

    # Read a subsample to avoid loading huge rasters
    xsize = band.XSize
    ysize = band.YSize

    step = max(1, int(np.sqrt((xsize * ysize) / sample_size)))

    arr = band.ReadAsArray(
        xoff=0, yoff=0,
        xsize=xsize, ysize=ysize,
        buf_xsize=xsize // step,
        buf_ysize=ysize // step
    ).astype("float64")

    if nodata is not None:
        arr = arr[arr != nodata]

    if arr.size == 0:
        return constants.Units.UNKNOWN, constants.Confidence.LOW

    vmin = np.nanpercentile(arr, 1)
    vmax = np.nanpercentile(arr, 99)

    # Very coarse heuristics. These are jank and should be avoided.
    value_range = vmax - vmin

    if value_range > 8_900:
        # Taller than everest in meters, yeah, thats feet
        return constants.Units.FEET, constants.Confidence.MEDIUM
    # Eh, it's probably meters. but who knows.
    return constants.Units.METERS, constants.Confidence.LOW