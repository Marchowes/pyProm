from pyprom.lib import constants 
from typing import Tuple, Generator, Literal

Numpy_X = int
Numpy_Y = int

Elevation = float
Latitude_X = float
Longitude_Y = float
LatLon = Tuple[Latitude_X, Longitude_Y]

XY_Elevation = Tuple[Numpy_X, Numpy_Y, Elevation]
XY_Elevation_Generator = Generator[Numpy_X, Numpy_Y, Elevation]

XY = Tuple[Numpy_X, Numpy_Y]

DecimalDegrees = float
