"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing GridPoint
type location objects.
"""

from .base_gridpoint import BaseGridPointContainer
from ..location_util import findExtremities


class GridPointContainer(BaseGridPointContainer):
    """
    Container for GridPoint type lists.
    Allows for various list transformations and functions.
    """
    def __init__(self, gridPointList):
        super(GridPointContainer, self).__init__(gridPointList)

    def findExtremities(self):
        return findExtremities(self.points)

    def __repr__(self):
        return "<GridPointContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__
