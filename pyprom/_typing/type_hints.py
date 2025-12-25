from typing import Tuple, Generator

NUMPY_X = int
NUMPY_Y = int

Elevation = float
LATITUDE_X = float
LONGITUDE_Y = float
LatLon = Tuple[LATITUDE_X, LONGITUDE_Y]

XY_ELEVATION_TUPLE = Tuple[NUMPY_X, NUMPY_Y, Elevation]
XY_ELEVATION_GENERATOR = Generator[NUMPY_X, NUMPY_Y, Elevation]

XY_COORD = Tuple[NUMPY_X, NUMPY_Y]


DecimalDegrees = float