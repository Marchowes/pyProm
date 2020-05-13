"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

def highest(points):
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