"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from pyprom._typing.type_hints import XY_Elevation

def highest(
        points: List[XY_Elevation]
    ) -> List[XY_Elevation]:
    """
    :return: list of highest GridPoint objects found in this container
    :rtype: list(:class:`pyprom.lib.locations.gridpoint.GridPoint`)
    """
    high = points[0][2]
    highest = list()
    for gridPoint in points:
        if gridPoint[2] > high:
            high = gridPoint[2]
            highest = list()
            highest.append(gridPoint)
        elif gridPoint[2] == high:
            highest.append(gridPoint)
    return highest