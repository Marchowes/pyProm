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
from ..locations.gridpoint import GridPoint
from ..containers.gridpoint import GridPointContainer


class SaddlesContainer(SpotElevationContainer):
    """
    Container for Saddles.
    Allows for various list transformations.
    """

    def __init__(self, saddleList):
        """
        :param saddleList: list of Saddle objects to reside in this container.
        :type saddleList: list(:class:`pyprom.lib.locations.saddle.Saddle`)
        """
        if len([x for x in saddleList if not isinstance(x, Saddle)]):
            raise TypeError("saddleList passed to SaddlesContainer"
                            " can only contain Saddle objects.")
        super(SaddlesContainer, self).__init__(saddleList)

    def rebuildSaddles(self, datamap):
        """
        Uses the saddles contained in this container and rebuilds any saddle
        which contains >= 2 high edges as (n-1) new saddles where n
        is the number of high edges. The old saddle is tossed out unless it
        is an edge effect saddle, in which it is kept and disqualified.
        Saddles with 2 high edges are added back in. This in effect deals
        with waterbodies and other similiar features.

        :param datamap: datamap to use while rebuilding.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: New SaddlesContainer
        :rtype: :class:`SaddlesContainer`
        """
        new_saddles = list()
        for saddle in self.points:
            # insufficient highEdges. Re-add to the list an move on.
            if len(saddle.highShores) < 2:
                new_saddles.append(saddle)
                continue
            # More than 2 high shores? build the network.
            if len(saddle.highShores) > 2:
                nw = InternalSaddleNetwork(saddle, datamap)
                new_saddles += nw.generate_child_saddles()
            # if we've just got 2 high shores, find all the highest points in
            # the highShores, and find the midpoint between the first two if
            # its a multipoint
            if len(saddle.highShores) == 2:
                highShores = []
                for highShore in saddle.highShores:
                    highShores.append(GridPointContainer(highShore.highest))

                # if multipoint use first of each of the highest high shores
                # and find the mid point for both. Then find the point within
                # the multipoint that is closest to that midpoint. Disregard
                # high shores.
                if saddle.multiPoint:
                    hs0, hs1, distance =\
                        saddle.highShores[0].findClosestPoints(
                            saddle.highShores[1])
                    # find the middle GP for the 2 closest opposing shore
                    # points.
                    # Note, in some cases this might be outside the multipoint
                    middleGP = GridPoint(int((hs0.x +
                                             hs1.x) / 2),
                                         int((hs0.y +
                                             hs1.y) / 2),
                                         saddle.elevation)
                    # reconcile any points which might be outside the
                    # multipoint by finding the closest point inside the
                    # multipoint.
                    middleSpotElevation =\
                        saddle.multiPoint.closestPoint(middleGP,
                                                       asSpotElevation=True)
                    newSaddle = Saddle(middleSpotElevation.latitude,
                                       middleSpotElevation.longitude,
                                       middleSpotElevation.elevation)
                # if not multipoint, just use that point.
                else:
                    newSaddle = Saddle(saddle.latitude,
                                       saddle.longitude,
                                       saddle.elevation)

                newSaddle.highShores = [GridPointContainer(highShores[0]),
                                        GridPointContainer(highShores[1])]
                new_saddles.append(newSaddle)
                if saddle.edgeEffect:
                    newSaddle.parent = saddle
                    saddle.children.append(newSaddle)
            # If its an edgeEffect, we need to disqualify it and stash that
            # away for later.
            if saddle.edgeEffect:
                saddle.disqualified = True
                new_saddles.append(saddle)

        return SaddlesContainer(new_saddles)

    @property
    def saddles(self):
        """
        Getter alias for self.points

        :return: all Saddles in the container
        :rtype: list
        """
        return self.points

    def append(self, saddle):
        """
        Append a :class:`pyprom.lib.locations.saddle.Saddle` to this container.

        :param saddle: Saddle to append.
        :type saddle: :class:`pyprom.lib.locations.saddle.Saddle`
        :raises: TypeError if not of type
         :class:`pyprom.lib.locations.saddle.Saddle`
        """
        isSaddle(saddle)
        self.points.append(saddle)
        self.fast_lookup[saddle.id] = saddle

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
        :param datamap: datamap which MultiPoint style Saddles use.
        :type datamap: :class:`Datamap` object.
        :return: New SaddlesContainer
        :rtype: :class:`SaddlesContainer`
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

    @property
    def disqualified(self):
        """
        :return: list of all disqualified
         :class:`pyprom.lib.locations.saddle.Saddle` in this container.
        :rtype: list(:class:`pyprom.lib.locations.saddle.Saddle`)
        """
        return [x for x in self.points if x.disqualified]

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<SaddlesContainer> {} Objects".format(len(self.points))

    def __setitem__(self, idx, saddle):
        """
        Gives :class:`SaddlesContainer` list like set capabilities

        :param int idx: index
        :param saddle: Saddle object to add.
        :type saddle: :class:`pyprom.lib.locations.saddle.Saddle`
        """
        isSaddle(saddle)
        self.points[idx] = saddle

    __unicode__ = __str__ = __repr__
