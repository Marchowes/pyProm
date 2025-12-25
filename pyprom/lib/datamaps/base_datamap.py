"""
pyProm: Copyright Marc Howes, 2016 - 2025.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This file acts as the glue between the raster data loaded and the logic
used to analyze the map.
"""
from __future__ import annotations
import logging


from math import hypot
from shapely.geometry import Polygon
from numpy import array2string

from typing import TYPE_CHECKING, Tuple, Any
if TYPE_CHECKING:
    from pyprom._typing.type_hints import (
        Numpy_X, Numpy_Y, 
        XY_Elevation,
        XY_Elevation_Generator,
        DecimalDegrees,
        Elevation,
        XY
    )
    from osgeo import osr
    from numpy import NDArray


ARCSEC_DEG = 3600
ARCMIN_DEG = 60
FULL_SHIFT_LIST = (
        (-1, 0), (-1, 1), 
        (0, 1), 
        (1, 1), (1, 0), 
        (1, -1),
        (0, -1), 
        (-1, -1)
    )
ORTHOGONAL_SHIFT_LIST = (
        (-1, 0), (0, 1), (1, 0), (0, -1)
    )
DIAGONAL_SHIFT_LIST = (
    (-1, 1), (1, 1), (1, -1), (-1, -1)
)
FULL_SHIFT_ORTHOGONAL_DIAGONAL_LIST = ORTHOGONAL_SHIFT_LIST + DIAGONAL_SHIFT_LIST

class BaseDataMap:

    def coord_inbounds(self, x, y) -> bool:
        return (x >= 0 and x <= self.max_x) & (y >= 0 and y <= self.max_y)

    def iterateFull(self, x: Numpy_X, y: Numpy_Y) -> XY_Elevation_Generator:
        """
        Generator returns 8 closest neighbors to a raster grid location,
        that is, all points touching including the diagonals.

        :param int x: x coordinate in raster data.
        :param int y: y coordinate in raster data.
        """
        # 0, 45, 90, 135, 180, 225, 270, 315
        for shift in FULL_SHIFT_LIST:
            _x = x + shift[0]
            _y = y + shift[1]
            if self.coord_inbounds(_x, _y):
                yield _x, _y, float(self.numpy_array[_x, _y])
            else:
                yield _x, _y, self.nodata

    def iterateOrthogonal(self, x: Numpy_X, y: Numpy_Y) -> XY_Elevation_Generator:
        """
        Generator returns 4 closest neighbors to a raster grid location,
        that is, all points touching excluding the diagonals.

        :param int x: x coordinate in raster data.
        :param int y: y coordinate in raster data.
        """
        # 0, 90, 180, 270
        for shift in ORTHOGONAL_SHIFT_LIST:
            _x = x + shift[0]
            _y = y + shift[1]
            if self.coord_inbounds(_x, _y):
                yield _x, _y, float(self.numpy_array[_x, _y])
            else:
                yield _x, _y, self.nodata

    def iterateDiagonal(self, x: Numpy_X, y: Numpy_Y) -> XY_Elevation_Generator:
        """
        Generator returns 4 closest neighbors to a raster grid location,
        that is, all points touching excluding the orthogonals.

        :param int x: x coordinate in raster data.
        :param int y: y coordinate in raster data.
        """
        # 45, 135, 225, 315
        for shift in DIAGONAL_SHIFT_LIST:
            _x = x + shift[0]
            _y = y + shift[1]
            if self.coord_inbounds(_x, _y):
                yield _x, _y, float(self.numpy_array[_x, _y])
            else:
                yield _x, _y, self.nodata

    def steepestNeighbor(self, x: Numpy_X, y: Numpy_Y) -> XY_Elevation:
        """
        Finds neighbor with steepest slope

        :param int x: x coordinate in raster data.
        :param int y: y coordinate in raster data.
        :return: tuple(x, y) highest neighbor
        """
        steepest_slope = -1
        steepest_neighbor = None
        point_elevation = self.get(x, y)

        for _x, _y, elevation in self.iterateFull(x, y):
            if elevation is None or elevation < point_elevation:
                continue
            slope = (elevation-point_elevation)/hypot((x - _x)*self.res_x, (y - _y)*self.res_y)
            if steepest_slope < slope:
                if slope < 0:
                    continue
                steepest_neighbor = (_x, _y, elevation)
                steepest_slope = slope
        return steepest_neighbor

    def distance(self, us: XY, them: XY) -> DecimalDegrees:
        """
        :param us: Tuple(x, y)
        :param them: Tuple(x, y)
        :return: distance.
        """
        return hypot((us[0] - them[0]) * self.geotransform[1], (us[1] - them[1]) * self.geotransform[5])

    def get(self, x: Numpy_X, y: Numpy_Y) -> Elevation:
        """
        Gets elevation from numpy map, and converts units to Meters
        :param int x: x coordinate in raster data.
        :param int y: y coordinate in raster data.
        :return: float
        """
        return float(self.numpy_array[x, y])

    def is_map_edge(self, x: Numpy_X, y: Numpy_Y) -> bool:
        """
        Determine if x, y is on the map edge.
        """
        return x == 0 or y == 0 or x == self.max_x or y == self.max_y