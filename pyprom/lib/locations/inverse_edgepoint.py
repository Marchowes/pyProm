"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing InverseEdgePoint
type location objects. InverseEdgepoints are for the outside edge
of a multipoint. Analogous to a Shore
"""
from .gridpoint import GridPoint


class InverseEdgePoint(GridPoint):
    """
    A Shore point, to be used in conjunction with :class:`EdgePoint`.
    This keeps track shorePoints and their neighboring :class:`EdgePoint`s.
    :param x: x coordinate
    :param y: y coordinate
    :param elevation: elevation in meters
    :param edgePoints: list of EdgePoints.
    :param inverseEdgePointNeighbors: list of neighboring
     :class:`InverseEdgePoint`
    """
    def __init__(self, x, y, elevation, edgePoints=[],
                 inverseEdgePointNeighbors=[]):
        super(InverseEdgePoint, self).__init__(x, y, elevation)
        self.edgePoints = edgePoints
        self.inverseEdgePointNeighbors = inverseEdgePointNeighbors

    def addEdge(self, edgepoint):
        self.edgePoints.append(edgepoint)

    def __repr__(self):
        return ("<InverseEdgePoint> x: {}, y: {}, ele(m): {},"
                " #EdgePoints {}, #InverseEdgePointNeighbors {}".
                format(self.x,
                       self.y,
                       self.elevation,
                       len(self.edgePoints),
                       len(self.inverseEdgePointNeighbors)))

    __unicode__ = __str__ = __repr__
