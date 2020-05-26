"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

Base object for containers which are have member points of (x,y) tuples
which are self iterable.
"""

from collections import defaultdict

FULL_SHIFT_LIST = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                       (0, -1), (-1, -1))
ORTHOGONAL_SHIFT_LIST = ((-1, 0), (0, 1), (1, 0), (0, -1))
DIAGONAL_SHIFT_LIST = ((-1, 1), (1, 1), (1, -1), (-1, -1))
FULL_SHIFT_ORTHOGONAL_DIAGONAL_LIST = ORTHOGONAL_SHIFT_LIST + DIAGONAL_SHIFT_LIST

class BaseSelfIterable:
    """
    :param pointList: tuple(x, y, elevation) which make up the BaseSelfIterable.
    :type pointList:
    list(tuple(x, y, elevation))
    :param pointIndex: Members as a dict().
    :type pointIndex:
    dict({X: { Y: tuple(x, y, elevation)}}
    """
    def __init__(self,
                 pointList=None,
                 pointIndex=None):

        self.points = []
        if pointList and pointIndex:
            self.points = pointList
            self.pointIndex = pointIndex
            return
        if pointIndex:
            self.pointIndex = pointIndex
            self.points = [p for x, _y in self.pointIndex.items()
                           for y, p in _y.items()]
        if pointList:
            self.points = pointList
            self.pointIndex = defaultdict(dict)
            for point in self.points:
                self.pointIndex[point[0]][point[1]] = point

    def iterNeighborFull(self, point):
        """
        Iterate through diagonally and orthogonally neighboring
        tuple(x, y, ele) which are also members of this
        :class:`BaseSelfIterable`

        :param point: tuple(x, y, ele)
        :type point: tuple(x, y, ele)

        :return: tuple(x, y, ele)
        """
        for shift in FULL_SHIFT_LIST:
            x = point[0] + shift[0]
            y = point[1] + shift[1]
            if self.pointIndex[x].get(y, False):
                yield self.pointIndex[x].get(y, False)
            else:
                continue

    def iterNeighborOrthogonal(self, point):
        """
        Iterate through orthogonally neighboring
        tuple(x, y, ele) which are  also members of this
        :class:`BaseSelfIterable`

        :param point: tuple(x, y, ele)
        :type point: tuple(x, y, ele)

        :return: tuple(x, y, ele)
        """
        for shift in ORTHOGONAL_SHIFT_LIST:
            x = point[0] + shift[0]
            y = point[1] + shift[1]
            if self.pointIndex[x].get(y, False):
                yield self.pointIndex[x].get(y, False)
            else:
                continue

    def iterNeighborOrthogonalDiagonal(self, point):
        """
        Iterate through orthogonally, then diagonally neighboring
        tuple(x, y, ele) which are  also members of this
        :class:`BaseSelfIterable`

        :param point: tuple(x, y, ele)
        :type point: tuple(x, y, ele)

        :return: tuple(x, y, ele)
        """
        for shift in ORTHOGONAL_SHIFT_LIST:
            x = point[0] + shift[0]
            y = point[1] + shift[1]
            if self.pointIndex[x].get(y, False):
                yield self.pointIndex[x].get(y, False)
            else:
                continue
