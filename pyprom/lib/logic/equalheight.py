"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict

from ..locations.gridpoint import GridPoint
from ..containers.multipoint import MultiPoint
from ..util import coordinateHashToGridPointList
from ..containers.perimeter import Perimeter

def equalHeightBlob(datamap, x, y, elevation):
    """
    This function generates a list of coordinates that involve equal height
    :param x: x coordinate
    :param y: y coordinate
    :param elevation: elevation
    :return: Multipoint Object containing all x,y coordinates and elevation
    """

    masterGridPoint = GridPoint(x, y, elevation)
    exploredEqualHeight = defaultdict(dict)
    exploredEqualHeight[x][y] = True
    perimeterPointHash = defaultdict(dict)
    toBeAnalyzed = [masterGridPoint]

    # Loop until pool of equalHeight neighbors has been exhausted.
    edge = False
    while toBeAnalyzed:
        gridPoint = toBeAnalyzed.pop()
        neighbors = datamap.iterateDiagonal(gridPoint.x, gridPoint.y)
        # Determine if edge or not.
        if gridPoint.x in (datamap.max_x, 0) or gridPoint.y in \
                (datamap.max_y, 0):
            edge = True
        for _x, _y, elevation in neighbors:
            if elevation == masterGridPoint.elevation and\
                    not exploredEqualHeight[_x].get(_y, False):
                branch = GridPoint(_x, _y, elevation)
                exploredEqualHeight[_x][_y] = True
                toBeAnalyzed.append(branch)
            # If elevation >  master grid point, stash away as
            # a perimeter point. Only keep track of edgepoints
            # higher!
            elif elevation > masterGridPoint.elevation:
                if not perimeterPointHash[_x].get(_y, False):
                    perimeterPointHash[_x][_y] = \
                        GridPoint(_x, _y, elevation)
    return MultiPoint(coordinateHashToGridPointList(exploredEqualHeight),
                      masterGridPoint.elevation, datamap,
                      perimeter=Perimeter(
                          pointIndex=perimeterPointHash,
                          datamap=datamap, mapEdge=edge)
                      )
