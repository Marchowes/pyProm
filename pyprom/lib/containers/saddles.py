"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Saddle
type location objects.
"""

from .spot_elevation import SpotElevationContainer

class SaddlesContainer(SpotElevationContainer):
    """
    Container for Saddles.
    Allows for various list transformations.
    """
    def __init__(self, saddleList):
        """
        :param saddleList: list of :class:`Saddle`s
        """
        super(SaddlesContainer, self).__init__(saddleList)

    def rebuildSaddles(self, datamap):
        """
        :return:
        """
        new_saddles = list()
        for saddle in self.points:
            # insufficient highEdges. Re-add to the list an move on.
            if len(saddle.highShores) < 2:
                new_saddles.append(saddle)
                continue

            new_saddles += saddle.generate_child_saddles(datamap)
            # If its an edgeEffect, we need to disqualify it and stash that away for later.
            if saddle.edgeEffect:
                saddle.disqualified = True
                new_saddles.append(saddle)
        return SaddlesContainer(new_saddles)

    @property
    def saddles(self):
        """
        Getter alias for saddles
        :return: list() of saddles (points)
        """
        return self.points

    def add(self, saddle):
        """
        Add a saddle to the container.
        :param saddle: :class:`Saddle`
        """
        self.points.append(saddle)

    def __repr__(self):
        return "<SaddlesContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__

