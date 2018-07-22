"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing PerimeterPoint
type location objects. PerimeterPoints are for the outside edge
of a multipoint. Analogous to a Shore
"""
from .gridpoint import GridPoint


class PerimeterPoint(GridPoint):
    """
    A Shore point, to be used in conjunction with :class:`EdgePoint`.
    This keeps track shorePoints and their neighboring :class:`EdgePoint`s.
    :param x: x coordinate
    :param y: y coordinate
    :param elevation: elevation in meters
    :param edgePoints: list of EdgePoints.
    :param perimeterPointNeighbors: list of neighboring
     :class:`PerimeterPoint`
    """
    def __init__(self, x, y, elevation, edgePoints=[],
                 perimeterPointNeighbors=[]):
        super(PerimeterPoint, self).__init__(x, y, elevation)
        self.edgePoints = edgePoints
        self.perimeterPointNeighbors = perimeterPointNeighbors

    def addEdge(self, edgepoint):
        self.edgePoints.append(edgepoint)

    def __repr__(self):
        return ("<PerimeterPoint> x: {}, y: {}, ele(m): {},"
                " #EdgePoints {}, #PerimeterPointNeighbors {}".
                format(self.x,
                       self.y,
                       self.elevation,
                       len(self.edgePoints),
                       len(self.perimeterPointNeighbors)))

    __unicode__ = __str__ = __repr__
