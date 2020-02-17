"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict

def contiguous_neighbors(points, datamap ):
    """
    :param points: list of (x, y, ele) points
    :param datamap: datamap
    :return: Finds all contigous blocks of neighboring points.
     Returns list of these contiguous blocks.
    """
    points = set(points)
    neighborsList = list()
    while points:
        stack = [points.pop()]
        neighbors = list(stack[0])
        neighborsList.append(neighbors)
        while stack:
            # Grab a point from the stack.
            point = stack.pop()
            for _x, _y, _el in datamap.iterateFull(point[0], point[1]):
                pt = (_x, _y, _el)
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