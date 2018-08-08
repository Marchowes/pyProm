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
    masterXY = (x, y)
    exploredEqualHeight = defaultdict(dict)
    exploredEqualHeight[x][y] = True
    perimeterPointHash = defaultdict(dict)
    toBeAnalyzed = [masterXY]
    perimeterMapEdge = []
    x_mapEdge = {0: True, datamap.max_x: True}
    y_mapEdge = {0: True, datamap.max_y: True}

    # Loop until pool of equalHeight neighbors has been exhausted.
    edge = False
    while toBeAnalyzed:
        x, y = toBeAnalyzed.pop()
        neighbors = datamap.iterateDiagonal(x, y)
        # Determine if edge or not.
        if not edge:
            if x_mapEdge.get(x) or y_mapEdge.get(y):
                edge = True
        for _x, _y, ele in neighbors:
            if ele == elevation and\
                    not exploredEqualHeight[_x].get(_y):
                branch = (_x, _y)
                exploredEqualHeight[_x][_y] = True
                toBeAnalyzed.append(branch)
            # If elevation >  master grid point, stash away as
            # a perimeter point. Only keep track of edgepoints
            # higher!
            elif ele != elevation:
                if not perimeterPointHash[_x].get(_y):
                    gp = GridPoint(_x, _y, ele)
                    if ele > elevation:
                        perimeterPointHash[_x][_y] = gp
                    if x_mapEdge.get(_x) or y_mapEdge.get(_y):
                        perimeterMapEdge.append(gp)
    return MultiPoint(coordinateHashToGridPointList(exploredEqualHeight),
                      elevation, datamap,
                      perimeter=Perimeter(
                          pointIndex=perimeterPointHash,
                          mapEdge=edge,
                          mapEdgePoints=perimeterMapEdge)
                      )
