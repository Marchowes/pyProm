"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Summit
type location objects.
"""

from .spot_elevation import SpotElevationContainer
from ..locations.summit import Summit, isSummit

from typing import TYPE_CHECKING, List, Self
if TYPE_CHECKING:
    from pyprom.lib.locations.summit import Summit
    from pyprom import DataMap


class SummitsContainer(SpotElevationContainer):
    """
    Container for Summits.
    Allows for various list transformations.
    """

    def __init__(self, summitList: List[Summit]):
        """
        :param summitList: list of Summits which reside in this container.
        :type summitList: list(:class:`pyprom.lib.locations.summit.Summit`)
        :raises: TypeError if summitList contains non
         :class:`pyprom.lib.locations.summit.Summit` objects
        """
        if len([x for x in summitList if not isinstance(x, Summit)]):
            raise TypeError("summitList passed to SummitsContainer"
                            " can only contain Summit objects.")
        super().__init__(summitList)

    @property
    def summits(self) -> List[Summit]:
        """
        Getter alias for `self.points`

        :return: All summits in this container.
        :rtype: list(:class:`pyprom.lib.locations.summit.Summit`)
        """
        return self.points

    def append(self, summit: Summit) -> None:
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

    def extend(self, summits: List[Summit]) -> None:
        """
        Extend a list of :class:`pyprom.lib.locations.summit.Summit
        to this container.

        :param summits: list of Saddles to append.
        :type list(summits):
         list(:class:`pyprom.lib.locations.summit.Summit`)
        :raises: TypeError if point not of
         :class:`pyprom.lib.locations.summit.Summit'
        """
        for su in summits:
            isSummit(su)
        self.points.extend(summits)
        for su in summits:
            self.fast_lookup[su.id] = su

    def to_dict(self) -> dict:
        """
        Create the dictionary representation of this object.

        :return: dict() representation of :class:`SummitsContainer`
        :rtype: dict()
        """
        return {'summits': [x.to_dict() for x in self.points]}

    @classmethod
    def from_dict(cls, 
            summitContainerDict: dict, 
            datamap: DataMap | None = None
        ) -> Self:
        """
        Create this object from dictionary representation

        :param summitContainerDict: dict() representation of this object.
        :param datamap: datamap which MultiPoint style Saddles use.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: a new SummitsContainer
        :rtype: :class:`SummitsContainer`
        """
        summits = []
        for summit in summitContainerDict['summits']:
            summits.append(Summit.from_dict(summit, datamap))
        summitsContainer = cls(summits)

        return summitsContainer

    @property
    def multipoints(self) -> List[Summit]:
        """
        Returns list of all multipoint
         :class:`pyprom.lib.locations.summit.Summit` within container

        :return: list(:class:`pyprom.lib.locations.summit.Summit`)
        """
        return [pt for pt in self.points if pt.multipoint]

    def __setitem__(self, idx: int, summit: Summit):
        """
        Gives SummitsContainer list like set capabilities

        :param int idx: index value
        :param summit: Summit to add.
        :type summit: :class:`pyprom.lib.locations.summit.Summit`
        :raises: TypeError if summit not of
         :class:`pyprom.lib.locations.summit.Summit`
        """
        isSummit(summit)
        self.points[idx] = summit

    def __repr__(self) -> str:
        """
        :return: String representation of this object
        """
        return "<SummitsContainer> {} Objects".format(len(self.points))

    __str__ = __repr__
