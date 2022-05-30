"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains logic for performing breadth first search on
contiguous point sets on a cartesian grid.
"""
from collections import defaultdict

class BreadthFirstSearch:
    def __init__(self,
                 pointList=None,
                 pointIndex=None,
                 datamap=None)
        """
        :param list pointList: list(tuple(x,y,z))
        """
        self.datamap = datamap
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

