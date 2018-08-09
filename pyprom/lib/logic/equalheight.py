"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict

from ..locations.gridpoint import GridPoint
from ..locations.base_gridpoint import BaseGridPoint
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
    shoreMapEdge = []
    multipointEdges = []

    x_mapEdge = {0: True, datamap.max_x: True}
    y_mapEdge = {0: True, datamap.max_y: True}
    if x_mapEdge.get(x) or y_mapEdge.get(y):
        multipointEdges.append(BaseGridPoint(x, y))

    # Loop until pool of equalHeight neighbors has been exhausted.
    edge = False
    while toBeAnalyzed:
        gridPoint = toBeAnalyzed.pop()
        neighbors = datamap.iterateDiagonal(gridPoint.x, gridPoint.y)
        # Determine if edge or not.
        if not edge:
            if x_mapEdge.get(gridPoint.x) or y_mapEdge.get(gridPoint.y):
                edge = True
        for _x, _y, elevation in neighbors:
            if elevation == masterGridPoint.elevation and\
                    not exploredEqualHeight[_x].get(_y, False):
                branch = GridPoint(_x, _y, elevation)
                exploredEqualHeight[_x][_y] = True
                if x_mapEdge.get(_x) or y_mapEdge.get(_y):
                    multipointEdges.append(BaseGridPoint(_x, y))
                toBeAnalyzed.append(branch)
            # If elevation > master grid point, stash away as
            # a perimeter point. Only keep track of edgepoints
            # higher!
            elif elevation != masterGridPoint.elevation:
                if not perimeterPointHash[_x].get(_y, False):
                    gp = GridPoint(_x, _y, elevation)
                    if elevation > masterGridPoint.elevation:
                        perimeterPointHash[_x][_y] = gp
                    if x_mapEdge.get(_x) or y_mapEdge.get(_y):
                        shoreMapEdge.append(gp)
    return MultiPoint(coordinateHashToGridPointList(exploredEqualHeight),
                      masterGridPoint.elevation, datamap,
                      perimeter=Perimeter(
                          pointIndex=perimeterPointHash,
                          datamap=datamap,
                          mapEdge=edge,
                          mapEdgePoints=shoreMapEdge)),\
        multipointEdges
