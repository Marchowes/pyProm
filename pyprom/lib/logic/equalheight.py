"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict

from ..locations.base_gridpoint import BaseGridPoint
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
    masterGridPoint = BaseGridPoint(x, y)
    exploredEqualHeight = defaultdict(dict)
    exploredEqualHeight[x][y] = True
    perimeterPointHash = defaultdict(dict)
    toBeAnalyzed = [masterGridPoint]
    analyzed = []
    perimeterMapEdge = []
    x_mapEdge = {0: True, datamap.max_x: True}
    y_mapEdge = {0: True, datamap.max_y: True}

    # Loop until pool of equalHeight neighbors has been exhausted.
    edge = False
    while toBeAnalyzed:
        gridpoint = toBeAnalyzed.pop()
        analyzed.append(gridpoint)
        neighbors = datamap.iterateDiagonal(gridpoint.x, gridpoint.y)
        # Determine if edge or not.
        if not edge:
            if x_mapEdge.get(gridpoint.x) or y_mapEdge.get(gridpoint.y):
                edge = True
        for _x, _y, ele in neighbors:
            if exploredEqualHeight[_x].get(_y):
                continue
            if ele == elevation:
                toBeAnalyzed.append(BaseGridPoint(_x, _y))
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
            exploredEqualHeight[_x][_y] = True
    return MultiPoint(analyzed,
                      elevation, datamap,
                      perimeter=Perimeter(
                          pointIndex=perimeterPointHash,
                          mapEdge=edge,
                          mapEdgePoints=perimeterMapEdge)
                      )
