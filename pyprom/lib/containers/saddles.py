"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Saddle
type location objects.
"""

from .spot_elevation import SpotElevationContainer
from ..logic.internal_saddle_network import InternalSaddleNetwork
from ..locations.saddle import Saddle, isSaddle


class SaddlesContainer(SpotElevationContainer):
    """
    Container for Saddles.
    Allows for various list transformations.
    """

    def __init__(self, saddleList):
        """
        :param saddleList: list of :class:`Saddle`s
        """
        if len([x for x in saddleList if not isinstance(x, Saddle)]):
            raise TypeError("saddleList passed to SaddlesContainer"
                            " can only contain Saddle objects.")
        super(SaddlesContainer, self).__init__(saddleList)

    def rebuildSaddles(self, datamap):
        """
        Uses the saddles contained in this container and rebuilds any saddle
        which contains greater than 2 high edges as (n-1) new saddles where n
        is the number of high edges. The old saddle is tossed out unless it
        is an edge effect saddle, in which it is kept and disqualified.
        Saddles with 2 high edges are added back in. This in effect deals
        with waterbodies.
        :return: :class:`SaddlesContainer` (new)
        """
        new_saddles = list()
        for saddle in self.points:
            # insufficient highEdges. Re-add to the list an move on.
            if len(saddle.highShores) < 2:
                new_saddles.append(saddle)
                continue
            nw = InternalSaddleNetwork(saddle, datamap)
            new_saddles += nw.generate_child_saddles()
            # If its an edgeEffect, we need to disqualify it and stash that
            # away for later.
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

    def append(self, saddle):
        """
        Append a saddle to the container.
        :param saddle: :class:`Saddle`
        """
        isSaddle(saddle)
        self.points.append(saddle)

    def to_dict(self):
        """
        :return: dict() representation of :class:`SaddlesContainer`
        """
        return {'saddles': [x.to_dict() for x in self.points]}

    @classmethod
    def from_dict(cls, saddleContainerDict, datamap=None):
        """
        Load this object and child objects from a dict.
        :param saddleContainerDict: dict() representation of this object.
        :param datamap: :class:`Datamap`
        :return:
        """
        saddles = []
        saddleHash = dict()
        for saddle in saddleContainerDict['saddles']:
            saddleObj = Saddle.from_dict(saddle, datamap)
            saddles.append(saddleObj)
            saddleHash[saddleObj.id] = saddleObj
        saddlesContainer = cls(saddles)
        for saddle in saddleContainerDict['saddles']:
            children = saddle.get('children', None)
            if children:
                for child in children:
                    saddleHash[saddle['id']].children.append(saddleHash[child])
            parent = saddle.get('parent', None)
            if parent:
                saddleHash[saddle['id']].parent = saddleHash[parent]
        return saddlesContainer

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<SaddlesContainer> {} Objects".format(len(self.points))

    def __setitem__(self, idx, saddle):
        """
        :param idx: index
        :param saddle: :class:`Saddle`
        :return: :class:`Saddle`
        """
        isSaddle(saddle)
        self.points[idx] = saddle

    __unicode__ = __str__ = __repr__
