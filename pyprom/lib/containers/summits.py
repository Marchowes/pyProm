"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Summit
type location objects.
"""

from .spot_elevation import SpotElevationContainer

class SummitsContainer(SpotElevationContainer):
    """
    Container for Summits.
    Allows for various list transformations.
    """
    def __init__(self, summitList):
        """
        :param summitList: list of :class:`Summit`s
        """
        super(SummitsContainer, self).__init__(summitList)

    @property
    def summits(self):
        """
        Getter alias for summits
        :return: list() of summits (points)
        """
        return self.points

    def add(self, summit):
        """
        Add a summit to the container.
        :param summit: :class:`Summit`
        """
        self.points.append(summit)

    def __repr__(self):
        return "<SummitsContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__