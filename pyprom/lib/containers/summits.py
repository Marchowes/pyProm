"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Summit
type location objects.
"""

from .spot_elevation import SpotElevationContainer
from ..locations.summit import Summit

class SummitsContainer(SpotElevationContainer):
    """
    Container for Summits.
    Allows for various list transformations.
    """
    def __init__(self, summitList):
        """
        :param summitList: list of :class:`Summit`s
        """
        if len([x for x in summitList if not isinstance(x, Summit)]):
            raise TypeError("summitList passed to SummitsContainer"
                            " can only contain Summit objects.")
        super(SummitsContainer, self).__init__(summitList)

    @property
    def summits(self):
        """
        Getter alias for summits
        :return: list() of summits (points)
        """
        return self.points



    def append(self, summit):
        """
        Add a summit to the container.
        :param summit: :class:`Summit`
        """
        _isSummit(summit)
        self.points.append(summit)

    def __setitem__(self, idx, summit):
        _isSummit(summit)
        self.points[idx] = summit

    def __repr__(self):
        return "<SummitsContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__


def _isSummit(summit):
    if not isinstance(summit, Summit):
        raise TypeError("SummitsContainer can only contain"
                        " Summit objects.")