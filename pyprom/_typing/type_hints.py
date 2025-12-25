from typing import Tuple, Generator

NUMPY_X = int
NUMPY_Y = int

Elevation = float
LATITUDE_Y = float
LONGITUDE_X = float
LatLon = Tuple[LATITUDE_Y, LONGITUDE_X]

XY_ELEVATION_TUPLE = Tuple[NUMPY_X, NUMPY_Y, Elevation]
XY_ELEVATION_GENERATOR = Generator[NUMPY_X, NUMPY_Y, Elevation]

XY_COORD = Tuple[NUMPY_X, NUMPY_Y]


DecimalDegrees = float