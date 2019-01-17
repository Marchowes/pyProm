"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Summit
type location objects.
"""

from .spot_elevation import SpotElevationContainer
from ..locations.summit import Summit, isSummit


class SummitsContainer(SpotElevationContainer):
    """
    Container for Summits.
    Allows for various list transformations.
    """

    def __init__(self, summitList):
        """
        :param summitList: list of Summits which reside in this container.
        :type summitList: list(:class:`pyprom.lib.locations.summit.Summit`)
        :raises: TypeError if summitList contains non
         :class:`pyprom.lib.locations.summit.Summit` objects
        """
        if len([x for x in summitList if not isinstance(x, Summit)]):
            raise TypeError("summitList passed to SummitsContainer"
                            " can only contain Summit objects.")
        super(SummitsContainer, self).__init__(summitList)

    @property
    def summits(self):
        """
        Getter alias for `self.points`

        :return: All summits in this container.
        :rtype: list(:class:`pyprom.lib.locations.summit.Summit`)
        """
        return self.points

    def append(self, summit):
        """
        Append a :class:`pyprom.lib.locations.summit.Summit`
        to this container.

        :param summit: Summit to append.
        :type summit: :class:`pyprom.lib.locations.summit.Summit`
        :raises: TypeError if summit not of
         :class:`pyprom.lib.locations.summit.Summit`
        """
        isSummit(summit)
        self.points.append(summit)
        self.fast_lookup[summit.id] = summit

    def to_dict(self):
        """
        :return: dict() representation of :class:`SummitsContainer`
        """
        return {'summits': [x.to_dict() for x in self.points]}

    @classmethod
    def from_dict(cls, summitContainerDict, datamap=None):
        """
        Load this object and child objects from a dict.

        :param summitContainerDict: dict() representation of this object.
        :param datamap: datamap which MultiPoint style Saddles use.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: New SummitsContainer
        :rtype: :class:`SummitsContainer`
        """
        summits = []
        for summit in summitContainerDict['summits']:
            summits.append(Summit.from_dict(summit, datamap))
        summitsContainer = cls(summits)

        return summitsContainer

    def __setitem__(self, idx, summit):
        """
        Gives :class:`pyprom.lib.containers.summits.SummitsContainer`
        list like set capabilities

        :param int idx: index value
        :param summit: Summit to add.
        :type summit: :class:`pyprom.lib.locations.summit.Summit`
        :raises: TypeError if summit not of
         :class:`pyprom.lib.locations.summit.Summit`
        """
        isSummit(summit)
        self.points[idx] = summit

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<SummitsContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__
