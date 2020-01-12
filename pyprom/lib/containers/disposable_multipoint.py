"""
pyProm: Copyright 2019.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

class DisposableMultipoint:
    """
    DisposableMultipoint is a Multipoint object used temporarily
    while discovering Summit Domains.

    In essence, this is a flat MultiPoint encountered during a walk.
    """

    def __init__(self, entryPoint, multiPoint, externalHash=None):
        self.entrypoints = [entryPoint]
        self.multiPoint = multiPoint

        if externalHash:
            for point in multiPoint.points:
                externalHash[point[0]][point[1]] = self

    def findClosestHighEdge(self, point):
        """
        :param point: (x, y) tuple.
        :return: closest (x, y) tuple coordinate.
        """


