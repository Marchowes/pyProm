"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

Base object for containers which are have member points of (x,y) tuples
which are self iterable.
"""

from collections import defaultdict
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from pyprom._typing.type_hints import (
        XY_Elevation, 
        XY_Elevation_Generator,
        XY_Elevation_Fast_Dict
    )

FULL_SHIFT_LIST = (
    (-1, 0), (-1, 1), 
    (0, 1), 
    (1, 1), (1, 0), (1, -1),
    (0, -1), 
    (-1, -1)
)
ORTHOGONAL_SHIFT_LIST = (
    (-1, 0), (0, 1), (1, 0), (0, -1)
)
DIAGONAL_SHIFT_LIST = (
    (-1, 1), (1, 1), (1, -1), (-1, -1)
)
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

    __slots__ = ['points', 'pointIndex']

    points: List[XY_Elevation]
    pointIndex: XY_Elevation_Fast_Dict

    def __init__(self,
            pointList:List[XY_Elevation] | None = None,
            pointIndex: XY_Elevation_Fast_Dict | None = None
        ):

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

    def iterNeighborFull(self, point: XY_Elevation) -> XY_Elevation_Generator:
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

    def iterNeighborOrthogonal(self, point: XY_Elevation) -> XY_Elevation_Generator:
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

    def iterNeighborOrthogonalDiagonal(self, point: XY_Elevation) -> XY_Elevation_Generator:
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
