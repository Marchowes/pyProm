"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from pyprom.lib.containers.gridpoint import GridPointContainer
from pyprom.lib.containers.multipoint import MultiPoint
from pyprom.lib.locations.base_gridpoint import BaseGridPoint
from pyprom.lib.locations.gridpoint import GridPoint
from pyprom.lib.locations.saddle import Saddle

def generate_MultiPoint(x, y, xSpan, ySpan,
                        datamap, elevation,
                        excludeBGPC = []):
    """
    Generate a rectangular MultiPoint, with the ability to exclude
    points.
    :param x: upper x coordinate
    :param y: upper y coordinate
    :param xSpan: span on x axis
    :param ySpan:  span on y axis
    :param datamap: :class:`Datamap`
    :param elevation: elevation
    :param excludeBGPC: [BaseGridPointContainer, BaseGridPointContainer...]
     points to remove from MultiPoint
    :return: :class:`MultiPoint`
    """

    mpBlock = []
    for xx in range(x, x+xSpan):
        for yy in range(y, y+ySpan):
            # leave these ones out, they're our islands.
            mpBlock.append(BaseGridPoint(xx, yy))
    mp = MultiPoint(mpBlock, elevation, datamap)
    for excluded in excludeBGPC:
        for point in excluded.points:
            mp.points.remove(point)
    return mp

def generate_multiPoint_saddle(x, y, xSpan, ySpan,
                               datamap, elevation,
                               islands = [],
                               perimeterHighShores = 1):
    """
    Generate a rectangular MultiPoint Saddle, with the ability to exclude
    points (islands). and generate highShores on the Perimeter.
    :param x: upper x coordinate
    :param y: upper y coordinate
    :param xSpan: span on x axis
    :param ySpan:  span on y axis
    :param datamap: :class:`Datamap`
    :param elevation: elevation
    :param islands: [BaseGridPointContainer, BaseGridPointContainer...]
     islands to remove from multipoint. islands will be elevation of mp +1
     DO NOT MAKE AN ISLAND MORE THAN 2 POINTS WIDE. This function is
     not designed to be smart in any way.
    :param perimeterHighShores: number of perimeter highShores to make up.
    :return: :class:`MultiPoint`
    """

    mp = generate_MultiPoint(x, y, xSpan, ySpan,
                             datamap, elevation,
                             excludeBGPC = islands)

    saddle = Saddle(x, y, elevation)
    saddle.multiPoint = mp

    islandGPCs = []
    for island in islands:
        islandGridPoints = []
        for islandPoint in island:
            islandGridPoints.append(GridPoint(islandPoint.x,
                                              islandPoint.y,
                                              elevation + 1))
        islandGPCs.append(GridPointContainer(islandGridPoints))

    highShoresPerimeter = []
    # Dumb highShore generator. One point along y axis. Since
    # this is for testing, make sure not to set `perimeterHighShores`
    # to more than the ySpan + 2. Again, this is dumb.
    for highShoreIdx in range(perimeterHighShores):
        hs = GridPoint(x - 1, y - 1 + highShoreIdx, elevation + 1)
        highShoresPerimeter.append(GridPointContainer([hs]))
    saddle.highShores = islandGPCs + highShoresPerimeter
    return saddle








