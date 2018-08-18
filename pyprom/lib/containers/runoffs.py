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
    Container for Runoffs.
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

    def to_dict(self):
        """
        :return: dict() representation of :class:`RunoffsContainer`
        """
        return {'runoffs': [x.to_dict() for x in self.points]}

    @classmethod
    def from_dict(cls, runoffContainerDict, datamap=None):
        """
        Load this object and child objects from a dict.
        :param runoffsContainerDict: dict() representation of this object.
        :param datamap: :class:`Datamap`
        :return:
        """
        runoffs = []
        for runoff in runoffContainerDict['runoffs']:
            runoffs.append(Runoff.from_dict(runoff, datamap))
        runoffsContainer = cls(runoffs)

        return runoffsContainer

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<RunoffsContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__
