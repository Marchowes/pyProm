"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""


class BaseGridPointContainer(object):
    """
    Base Grid Point Container.
    """
    def __init__(self, gridPointList):
        """
        :param gridPointList: list of :class:`GridPoints`
        """
        super(BaseGridPointContainer, self).__init__()
        self.points = gridPointList

    def __hash__(self):
        return hash(tuple(sorted([x.x for x in self.points])))

    def __eq__(self, other):
        return sorted([x.x for x in self.points]) == \
               sorted([x.x for x in other.points])

    def __ne__(self, other):
        return sorted([x.x for x in self.points]) == \
               sorted([x.x for x in other.points])

    def __repr__(self):
        return "<BaseGridPointContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__
