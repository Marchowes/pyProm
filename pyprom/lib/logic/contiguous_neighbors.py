"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict

def contiguous_neighbors(points, datamap):
    """
    :param points: list of (x, y, ele) points
    :param datamap: datamap
    :return: Finds all contigous blocks of neighboring points.
     Returns list of these contiguous blocks.
    """
    # strip out elevation.
    points = set(points)
    neighborsList = list()
    while points:
        stack = [points.pop()]
        neighbors = list([stack[0]])
        neighborsList.append(neighbors)
        while stack:
            # Grab a point from the stack.
            point = stack.pop()
            for x, y, el in datamap.iterateFull(point[0], point[1]):
                pt = (x, y, el)
                # is this neighbor a member of our pointlist still?
                if pt in points:
                    stack.append(pt)
                    points.remove(pt)
                    neighbors.append(pt)
    return neighborsList


# def contiguous_neighbors(points, datamap):
#     explored = defaultdict(dict)
#     highLists = list()
#     for point in points:
#         if explored[point[0]].get(point[1], False):
#             continue
#         if point[2] > elevation:
#             toBeAnalyzed = [point]
#             highList = list()
#             while True:
#                 if not toBeAnalyzed:
#                     highLists.append(highList)
#                     break
#                 else:
#                     gridPoint = toBeAnalyzed.pop()
#                 if not explored[gridPoint[0]].get(gridPoint[1], False):
#                     highList.append(gridPoint)
#                     neighbors = [x for x in
#                                  self.iterNeighborDiagonal(gridPoint)
#                                  if x[2] > elevation and
#                                  not explored[x[0]].get(x[1], False)]
#                     toBeAnalyzed += neighbors
#                     explored[gridPoint[0]][gridPoint[1]] = True
#         else:
#             explored[point[0]][point[1]] = True
#     return [GridPointContainer(x) for x in highLists]

def touching_neighborhoods(list_of_point_lists, datamap):
    """
    todo: inefficient, fix.
    :param list_of_point_lists:
    :param datamap:
    :return:
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







