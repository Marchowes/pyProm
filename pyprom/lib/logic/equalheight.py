"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict

from ..containers.multipoint import MultiPoint
from ..containers.perimeter import Perimeter

from typing import TYPE_CHECKING, List, Set
if TYPE_CHECKING:
    from pyprom import DataMap
    from pyprom._typing.type_hints import (
        Numpy_X, Numpy_Y, 
        Elevation, 
        XY, 
        XY_Elevation
    )


def equalHeightBlob(
        datamap: DataMap, 
        x: Numpy_X, y: Numpy_Y, 
        elevation: Elevation
    ):
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
    masterGridPoint: XY_Elevation = (x, y, elevation)
    exploredEqualHeight: Set[XY] = set()
    memberPoint: List[XY] = list()
    _add_member_point(x, y, exploredEqualHeight, memberPoint)

    perimeterPointHash = defaultdict(dict)
    perimeterPoints = list()
    toBeAnalyzed: List[XY_Elevation] = [masterGridPoint]
    perimeterMapEdge: Set[XY_Elevation] = set()
    multipointEdges: List[XY_Elevation] = []

    if datamap.is_map_edge(x, y):
        multipointEdges.append((x, y, elevation))

    # Loop until pool of equalHeight neighbors has been exhausted.
    edge = False
    while toBeAnalyzed:
        gridPoint = toBeAnalyzed.pop()
        neighbors = datamap.iterateFull(gridPoint[0], gridPoint[1])
        # Determine if edge or not.
        if not edge:
            if datamap.is_map_edge(gridPoint[0], gridPoint[1]):
                edge = True
        for _x, _y, elevation in neighbors:
            if elevation is None or elevation == datamap.nodata:
                continue
            elif elevation == masterGridPoint[2] and not (_x,_y) in exploredEqualHeight:
                branch = (_x, _y, elevation)
                _add_member_point(_x, _y, exploredEqualHeight, memberPoint)
                if datamap.is_map_edge(_x, _y):
                    multipointEdges.append((_x, _y, elevation))
                toBeAnalyzed.append(branch)
            # If elevation > master grid point, stash away as
            # a perimeter point. Only keep track of edgepoints
            # higher!

            elif elevation != masterGridPoint[2]:
                if not perimeterPointHash[_x].get(_y, False):
                    if elevation > masterGridPoint[2]:
                        _add_perimeter_point((_x, _y, elevation), perimeterPointHash, perimeterPoints)
                    if datamap.is_map_edge(_x, _y):
                        perimeterMapEdge.add((_x, _y, elevation))
    return (
        MultiPoint(
            memberPoint,
            masterGridPoint[2],
            datamap,
            perimeter=Perimeter(
                pointList=perimeterPoints,
                pointIndex=perimeterPointHash,
                datamap=datamap,
                mapEdge=edge,
                mapEdgePoints=list(perimeterMapEdge))
            ),
        multipointEdges
    )

def _add_member_point(
        x: Numpy_X, y: Numpy_X, 
        explored_set: Set[XY], 
        list: List[XY]
    ) -> None:
    """
    Adds point to list and to hash
    """
    xy = (x,y)
    explored_set.add(xy)
    list.append(xy)

def _add_perimeter_point(
        xy_elevation: XY_Elevation, 
        hash, 
        list
    ):
    """
    Adds point to list and to hash
    :param x: x coordinate
    :param y: y coordinate
    :param hash: hash to add to
    :param list: list to add to
    :return:
    """
    hash[xy_elevation[0]][xy_elevation[1]] = xy_elevation
    list.append(xy_elevation)