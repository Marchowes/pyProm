"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing EdgePoint
type location objects. Edgepoints are for the inside edge
of a multipoint
"""
from .gridpoint import GridPoint


class EdgePoint(GridPoint):
    """
    An Edge point, to be used in conjunction with MultiPoints.
    This keeps track of non equal height neighbors and their elevation
    :param x: x coordinate
    :param y: y coordinate
    :param elevation: elevation in meters
    :param nonEqualNeighbors: list of :class:`GridPoints` that are non equal
           in height in comparison to the :class:`EdgePoint`.
    :param equalNeighbors: list of :class:`GridPoint`s that are equal in
           height in comparison to the EdgePoint.
    """
    def __init__(self, x, y, elevation, nonEqualNeighbors, equalNeighbors):
        super(EdgePoint, self).__init__(x, y, elevation)
        self.nonEqualNeighbors = nonEqualNeighbors
        self.equalNeighbors = equalNeighbors

    def __repr__(self):
        return ("<EdgePoint> x: {}, y: {}, ele(m): {},"
                " #Eq Points {}, #NonEq Points {}".
                format(self.x,
                       self.y,
                       self.elevation,
                       len(self.equalNeighbors),
                       len(self.nonEqualNeighbors)))

    __unicode__ = __str__ = __repr__
