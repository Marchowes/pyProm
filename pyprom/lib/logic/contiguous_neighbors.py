"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict
from typing import TYPE_CHECKING, List, Dict
if TYPE_CHECKING:
    from pyprom._typing.type_hints import XY_Elevation
    from pyprom import DataMap

OFFSETS = (-1, 0, 1)


def contiguous_neighbors(
        points: List[XY_Elevation]
    ) -> List[List[XY_Elevation]]:
    """
    Consumes a list of (x, y, ele) points. finds which points neighbor
    each other diagonally or orthogonally.

    This works by looking at full X, Y numpy slices

    :param points: list of (x, y, ele) points
    :param datamap: datamap
    :return: Finds all contiguous blocks of neighboring points.
        Returns list of these contiguous blocks.
    """
    points = set(points)
    lookup = defaultdict(dict)
    for pt in points:
        lookup[pt[0]][pt[1]] = pt[2]
    neighborsList = list()
    while points:
        stack = [points.pop()]
        lookup[stack[0][0]][stack[0][1]] = None
        neighbors = list([stack[0]])
        neighborsList.append(neighbors)
        while stack:
            # Grab a point from the stack.
            point = stack.pop()
            for offset_x in OFFSETS:
                x_val = point[0] + offset_x
                x_axis = lookup[x_val]
                if not x_axis or x_val < 0:
                    continue
                for offset_y in OFFSETS:
                    y_val = point[1] + offset_y
                    if y_val < 0:
                        continue
                    el = x_axis.get(y_val, None)
                    if el is not None:
                        pt = (x_val, y_val, el)
                        stack.append(pt)
                        points.remove(pt)
                        lookup[pt[0]][pt[1]] = None
                        neighbors.append(pt)
    return neighborsList

def touching_neighborhoods(
        list_of_point_lists: List[List[XY_Elevation]],
        datamap: DataMap
    ) -> Dict[int, List[int]]:
    """
    Consumes list of point lists and which lists touch.

    THis works by looking at the list index from the passed
    in from list_of_point_lists. What is returned follows
    the following format:
    Example:
    {0: [2, 4], 1: [3, 2]})
    {my_idx: [touching_neighborhood_1_idx, ...]}
    :param list list_of_point_lists: list(list(tuple(x, y, ele)))
    :param datamap: datamap
    """
    touching_neighborhoods = defaultdict(list)

    tracker = []
    lookup = defaultdict(dict)
    for idx, pt_list in enumerate(list_of_point_lists):
        for pt in pt_list:
            lookup[pt[0]][pt[1]] = idx
    for us, pt_list in enumerate(list_of_point_lists):
        for pt in pt_list:
            for x, y, el in datamap.iterateFull(pt[0], pt[1]):
                if lookup[x].get(y, None):
                    them = lookup[x][y]
                    if us == them:
                        continue
                    if (us, them) not in tracker:
                        tracker.extend([(them, us), (us, them)])
                        touching_neighborhoods[us].append(them)
    return touching_neighborhoods
