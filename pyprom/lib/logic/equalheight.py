"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict

from ..locations.gridpoint import GridPoint
from ..locations.base_gridpoint import BaseGridPoint
from ..containers.multipoint import MultiPoint
from ..util import coordinateHashToXYTupleList
from ..containers.perimeter import Perimeter


def equalHeightBlob(datamap, x, y, elevation):
    """
    This function generates a
    :class:`pyprom.lib.containers.multipoint.MultiPoint`
    which contains a list of :class:`pyprom.lib.locations.gridpoint.GridPoint`
    of equal elevation which are diagonally & orthogonally connected.

    :param int x: x coordinate
    :param int y: y coordinate
    :param elevation: elevation to search neighbors for.
    :type elevation: int, float
    :return: MultiPoint Object containing all x,y coordinates and elevation
    :rtype: :class:`pyprom.lib.containers.multipoint.MultiPoint`
    """
    masterGridPoint = (x, y, elevation)
    exploredEqualHeight = defaultdict(dict)
    exploredEqualHeight[x][y] = True
    perimeterPointHash = defaultdict(dict)
    toBeAnalyzed = [masterGridPoint]
    shoreMapEdge = set()
    multipointEdges = []

    x_mapEdge = {0: True, datamap.max_x: True}
    y_mapEdge = {0: True, datamap.max_y: True}
    if x_mapEdge.get(x) or y_mapEdge.get(y):
        multipointEdges.append((x, y, elevation))

    # Loop until pool of equalHeight neighbors has been exhausted.
    edge = False
    while toBeAnalyzed:
        gridPoint = toBeAnalyzed.pop()
        neighbors = datamap.iterateFull(gridPoint[0], gridPoint[1])
        # Determine if edge or not.
        if not edge:
            if x_mapEdge.get(gridPoint[0]) or y_mapEdge.get(gridPoint[1]):
                edge = True
        for _x, _y, elevation in neighbors:
            if elevation is None or elevation == datamap.nodata:
                continue
            elif elevation == masterGridPoint[2] and\
                    not exploredEqualHeight[_x].get(_y, False):
                branch = (_x, _y, elevation)
                exploredEqualHeight[_x][_y] = True
                if x_mapEdge.get(_x) or y_mapEdge.get(_y):
                    multipointEdges.append((_x, _y, elevation))
                toBeAnalyzed.append(branch)
            # If elevation > master grid point, stash away as
            # a perimeter point. Only keep track of edgepoints
            # higher!

            elif elevation != masterGridPoint[2]:
                if not perimeterPointHash[_x].get(_y, False):
                    if elevation > masterGridPoint[2]:
                        perimeterPointHash[_x][_y] = (_x, _y, elevation)
                    if x_mapEdge.get(_x) or y_mapEdge.get(_y):
                        shoreMapEdge.add((_x, _y, elevation))
    return MultiPoint(coordinateHashToXYTupleList(exploredEqualHeight),
                      masterGridPoint[2], datamap,
                      perimeter=Perimeter(
                          pointIndex=perimeterPointHash,
                          datamap=datamap,
                          mapEdge=edge,
                          mapEdgePoints=list(shoreMapEdge))),\
        multipointEdges

def high_low_equal(x, y, elevation, datamap):
    point = (x, y, elevation)

    edgepoints = set() #equalheight edgepoints
    mapEdgePoints = set() #perimeter points which touch the map edge

    x_edge = (0, datamap.max_x)
    y_edge = (0, datamap.max_y)
    edge = False

    high = set()
    low = set()

    stack = list()
    stack.append(point)
    equal = set([point])
    tracker = set()

    while stack:
        point = stack.pop()
        tracker.add(point)
        for x, y, el in datamap.iterateFull(point[0], point[1]):
            pt = (x, y, el)
            if el == point[2]:
                if isinstance(equal, float):
                    print("what")
                equal.add(pt)
                if pt not in tracker:
                    stack.append(pt)
                if x in x_edge or y in y_edge:
                    edge = True
                    edgepoints.add(pt)
                continue

            if el > point[2]:
                high.add(pt)
            if el < point[2]:
                low.add(pt)
            if x in x_edge or y in y_edge:
                edge = True
                mapEdgePoints.add(pt)



    mp = MultiPoint(list(equal),
                    point[2], datamap,
                    perimeter=Perimeter(
                          pointList=list(high),
                          datamap=datamap,
                          mapEdge=edge,
                          mapEdgePoints=list(mapEdgePoints))), \
           list(edgepoints)
    return mp
