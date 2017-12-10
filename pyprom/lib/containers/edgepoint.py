"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing EdgePoint
type location objects.
"""


class EdgePointContainer(object):
    """
    Container for :class:`EdgePoint` type lists.
    Allows for various list transformations.
    :param edgePointList: list of :class:`EdgePoint` to self.points
    :param edgePointIndex: {X: { Y: :class:`EdgePoint`}} passing this will
    automatically generate self.points

    """
    def __init__(self, edgePointList=None,
                 edgePointIndex=None,
                 datamap=None):
        super(EdgePointContainer, self).__init__()
        if edgePointIndex:
            self.edgePointIndex = edgePointIndex
            self.points = [v[1] for x, y in self.edgePointIndex.items()
                           for v in y.items()]
        if edgePointList:
            self.points = edgePointList
        self.datamap = datamap

    def __repr__(self):
        return "<EdgePointContainer> {} Objects".format(len(self.points))

    def __iter__(self):
        for edgePoint in self.points:
            yield edgePoint

    __unicode__ = __str__ = __repr__
