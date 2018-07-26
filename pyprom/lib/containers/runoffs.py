"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Saddle
type location objects.
"""

from .saddles import SaddlesContainer
from ..locations.runoff import Runoff


class RunoffsContainer(SaddlesContainer):
    """
    Container for Saddles.
    Allows for various list transformations.
    """
    def __init__(self, runoffList):
        """
        :param runoffList: list of :class:`Runoff`s
        """
        if len([x for x in runoffList if not isinstance(x, Runoff)]):
            raise TypeError("runoffList passed to RunoffsContainer"
                            " can only contain Runoff objects.")
        super(RunoffsContainer, self).__init__(runoffList)

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<RunoffsContainer> {} Objects".format(len(self.points))


    __unicode__ = __str__ = __repr__
