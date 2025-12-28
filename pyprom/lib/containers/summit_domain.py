"""
pyProm: Copyright 2019.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""
from __future__ import annotations

from shapely.ops import unary_union

from ..locations.base_coordinate import BaseCoordinate
from ..locations.spot_elevation import SpotElevation
from ..locations.base_gridpoint import BaseGridPoint
from ..locations.gridpoint import GridPoint

from typing import TYPE_CHECKING, List, Self, Dict, Generator
if TYPE_CHECKING:
    from pyprom._typing.type_hints import XY_Elevation
    from pyprom import DataMap
    from pyprom.lib.locations.saddle import Saddle
    from pyprom.lib.locations.summit import Summit
    from pyprom.lib.containers.saddles import SaddlesContainer
    from pyprom.lib.containers.summits import SummitsContainer
    from shapely.geometry.base import BaseGeometry

class SummitDomain:
    """
    SummitDomain Container.
    A SummitDomain is an unordered list of (X,Y) coordinates which represents
    all points along all directly ascending paths to a summit.
    """

    __slots__ = ['datamap', 'points', 'summit', 'saddles']

    def __init__(self, 
            datamap: DataMap, 
            summit: Summit, 
            saddles: List[Saddle], 
            points: List[XY_Elevation]
        ):
        """
        :param datamap: Datamap associated with this :class:`SummitDomain`
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :param summit: Summit for which this domain is connected
        :type summit: :class:`pyprom.lib.locations.summit.Summit`)
        :param saddles: list of Saddles
        :type saddles: :list(:class:`pyprom.lib.locations.saddle.Saddle`)
        :param points: List of (x, y, elevation) tuples. A point
        is a non summit, non saddle member of this domain along
        a non descending path from a
        :class:`pyprom.lib.locations.saddle.Saddle` to the
        :class:`pyprom.lib.locations.summit.Summit`
        :type points: list(tuple(x, y, elevation))
        """
        self.datamap = datamap
        self.points = points
        self.summit = summit
        self.saddles = saddles

    @property
    def members(self) -> List[BaseCoordinate]:
        """
        Returns the members as BaseCoordinates

        :return: List of points as
         :class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`
        :rtype:
         list(:class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`)
        """
        return self.baseCoordinate()

    def append(self, 
            point: XY_Elevation, 
            externalHash: Dict[int, Dict[int, SummitDomain]] = None
        ) -> None:
        """
        Appends a point to this container. Adds coordinate to
         externalHash if supplied.
        :param point: (x, y, elevation) to append.
        :param externalHash: defaultDict This is a fast lookup
         {x: {y : SummitDomain}} used by the caller.
        """
        self.points.append(point)
        if externalHash != None:
            externalHash[point[0]][point[1]] = self

    def extend(self, 
            points: XY_Elevation, 
            externalHash: Dict[int, Dict[int, SummitDomain]] = None
        ) -> None:
        """
        Extends points to this container. Adds coordinates to
         externalHash if supplied.
        :param points: [(x, y, elevation)] to extend.
        :param externalHash: defaultDict This is a fast lookup
         {x: {y : SummitDomain}} used by the caller.
        """
        for point in points:
            self.append(point, externalHash)

    def remove_saddle(self, saddle: Saddle):
        """
        Removes Saddle from this SummitDomain.
        :param saddle: Saddle to remove from this SaddleDomain.
        :type saddle: :class:`pyprom.lib.location.saddle.Saddle`
        """
        self.saddles = [x for x in self.saddles if x != saddle]

    def iterateBaseCoordinate(self) -> Generator[BaseCoordinate]:
        """
        Iterator for BaseCoordinate representation of the Walk Path.

        :return: Basecoordinate along path.
        :rtype: :class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`
        """
        for point in self.points:
            yield BaseCoordinate(point[0], point[1])

    def iterateSpotElevation(self) -> Generator[SpotElevation]:
        """
        Iterator for SpotElevation representation of the Walk Path.

        :return: SpotElevation along path.
        :rtype: :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        """
        for point in self.points:
            lat, long = self.datamap.xy_to_latlon(point[0], point[1])
            elevation = self.datamap.get(point[0], point[1])
            yield SpotElevation(lat, long, elevation)

    def iterateBaseGridPoint(self) -> Generator[BaseGridPoint]:
        """
        Iterator for BaseGridPoint representation of the Walk Path.

        :return: BaseGridPoint along path
        :rtype: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        """
        for point in self.points:
            x, y = self.datamap.latlong_to_xy(point[0], point[1])
            yield BaseGridPoint(x, y)

    def iterateGridPoint(self) -> Generator[GridPoint]:
        """
        Iterator for GridPoint representation of the Walk Path.

        :param datamap: Datamap used to look up elevation of point.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: GridPoint along path
        :rtype: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        for point in self.points:
            elevation = self.datamap.get(point[0], point[1])
            yield GridPoint(point[0], point[1], elevation)

    def baseCoordinate(self) -> List[BaseCoordinate]:
        """
        :return: List of points as
         :class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`
        :rtype:
         list(:class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`)
        """
        return [x for x in self.iterateBaseCoordinate()]

    def spotElevation(self) -> List[SpotElevation]:
        """
        :return: List of points as
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        :rtype:
         list(:class:`pyprom.lib.locations.spot_elevation.SpotElevation`)
        """
        return [x for x in self.iterateSpotElevation()]

    def baseGridPoint(self) -> List[BaseGridPoint]:
        """
        :return: List of points as
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :rtype:
         list(:class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`)
        """
        return [x for x in self.iterateBaseGridPoint()]

    def gridPoint(self) -> List[GridPoint]:
        """
        :return: List of points as
         :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :rtype: list(:class:`pyprom.lib.locations.gridpoint.GridPoint`)
        """
        return [x for x in self.iterateGridPoint()]

    def to_dict(self) -> dict:
        """
        Create the dictionary representation of this object.
        Summits and Saddles are ALWAYS referenced by ID.
        :return: dict() representation of :class:`SummitDomain`
        :rtype: dict()
        """
        to_dict = dict()
        to_dict['points'] = self.points

        # Summits and saddles are only reference by ID
        to_dict['saddles'] = [x.id for x in self.saddles]
        to_dict['summit'] = self.summit.id
        return to_dict

    @classmethod
    def from_dict(cls, 
            summitDomainDict: dict, 
            saddlesContainer: SaddlesContainer,
            summitsContainer: SummitsContainer, 
            datamap: DataMap
        ) -> Self:
        """
        Create this object from dictionary representation

        :param dict summitDomainDict: dict() representation of this object.
        :param saddlesContainer: SaddlesContainer to use to assign member saddles.
        :param summitsContainer: SummitsContainer to use to assign member summits.
        :param datamap: Datamap associated with this object.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: a new SummitDomain
        :rtype: :class:`SummitDomain`
        """
        points = summitDomainDict.get('points', [])
        points = [tuple(x) for x in points]
        saddles = [saddlesContainer.fast_lookup[x] for x in summitDomainDict['saddles']]
        summit = summitsContainer.fast_lookup[summitDomainDict['summit']]

        # make sure to assign this summit domain to that summit.
        sd = cls(datamap, summit, saddles, points)
        summit.domain = sd
        return sd

    @property
    def shape(self) -> BaseGeometry:
        """
        Produces :class:`shapely.geometry.polygon.Polygon` of this
         :class:`SummitDomain`. This shape only includes member points, not
         summits, saddles, or linkers.

        :return: :class:`shapely.geometry.polygon.Polygon` of
         this :class:`SummitDomain`
        """
        return unary_union([self.datamap.point_geom(point[0], point[1])
                            for point in self.points])

    def __eq__(self, other: Self) -> bool:
        return (self.summit == other.summit and
                sorted(self.saddles) == sorted(other.saddles) and
                sorted(self.points) == sorted(other.points))

    def __hash__(self) -> int:
        """
        :return: Hash representation of this object
        We only care about the summit.
        """
        return self.summit.__hash__()


    def __repr__(self) -> str:
        """
        :return: String representation of this object
        """
        return "<SummitDomain> Of {} - {} points".format(self.summit, len(self.points))