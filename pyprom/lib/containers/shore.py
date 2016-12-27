"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing GridPoint
type location objects in a Shore Context.
"""

from .base_gridpoint import BaseGridPointContainer


class ShoreContainer(BaseGridPointContainer):
    """
    Container for Shore Segments.
    """
    def __init__(self, gridPointList, mapEdge=False):
        super(ShoreContainer, self).__init__(gridPointList)
        self.mapEdge = mapEdge
