"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Multipoint
type location objects as well as a number of functions.
"""

from math import hypot
from collections import defaultdict
from dijkstar import Graph, find_path
from .base_self_iterable import BaseSelfIterable
from ..locations.base_coordinate import BaseCoordinate
from ..locations.base_gridpoint import  BaseGridPoint
from ..locations.gridpoint import GridPoint
from .perimeter import Perimeter


class MultiPoint(BaseSelfIterable):
    """
    | A MultiPoint Container. This is a special kind of feature which contains
    | multiple :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`s.
    | These points are all of equal elevation and neighbor each other
    | Orthogonally or Diagonally.
    |
    |   [4][3][4][6][4]
    |   [3][5][5][5][6]
    |   [2][3][5][6][3]
    |   [3][5][4][3]
    |   [6][7][6]
    |
    |   In the above example, all [5] points represent a valid MultiPoint.
    |   All non [5] points are Perimeter Points, that is, they neighbor
    |   MultiPoint members Diagonally or Orthogonally.
    |
    | ``[5][5][5]``
    |    ``[5]   <- Without Perimeter``
    | ``[5]``
    |
    |
    | ``[4][3][4][6][4]``
    | ``[3]         [6] <- Just the Perimeter.``
    | ``[2][3]   [6][3]``
    | ``[3]   [4][3]``
    | ``[6][7][6]``
    """

    def __init__(self, points, elevation, datamap,
                 perimeter=None):
        """
        :param points: list of
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint` objects.
         These are the inside points that make up a Multipoint.
        :type points:
         list(:class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`)
        :param elevation: elevation in meters
        :type elevation: int, float
        :param datamap: datamap which this MultiPoint uses.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :param perimeter: Perimeter of MultiPoint. These are the points
         that make up the orthogonally/diagonally connected border of the
         multipoint outside of the multipoint.
        :type perimeter: :class:`pyprom.lib.containers.perimeter.Perimeter`
        """
        self.points = points  # BaseGridPoint Objects.
        self.elevation = elevation
        self.datamap = datamap  # data analysis object.
        self.perimeter = perimeter

    def to_dict(self):
        """
        Create the dictionary representation of this object.

        :return: dict() representation of :class:`MultiPoint`
        :rtype: dict()
        """
        multiPointDict = dict()
        multiPointDict['points'] = self.points
        multiPointDict['perimeter'] = self.perimeter.to_dict()
        multiPointDict['elevation'] = self.elevation
        return multiPointDict

    @classmethod
    def from_dict(cls, multiPointDict, datamap=None):
        """
        Create this object from dictionary representation

        :param multiPointDict: dict() representation of this
         :class:`MultiPoint`.
        :param datamap: datamap which this MultiPoint uses.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: a new Multipoint.
        :rtype: :class:`MultiPoint`
        """
        points = [(pt[0], pt[1]) for pt in multiPointDict['points']]
        perimeter = Perimeter.from_dict(multiPointDict['perimeter'], datamap)
        elevation = multiPointDict['elevation']
        return cls(points, elevation, datamap, perimeter=perimeter)

    @property
    def pointsLatLong(self):
        """
        Returns list() of Container
        :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint` as
        :class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`

        :return: List of All blob points with lat/long instead of x/y
        :rtype:
         list(:class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`)
        """
        return [BaseCoordinate(*self.datamap.xy_to_latlong(coord[0], coord[1]))
                for coord in self.points]

    def append(self, point):
        """
        Add a BaseGridPoint to this container.

        :param point: BaseGridPoint or tuple to add.
        :type point: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :type point: tuple
        :raises: TypeError if point not of :class:`BaseGridPoint` or tuple
        :raises: Exception if tuple length != 2
        """
        incoming = self._check_and_return_incoming_point_type(point)
        self.points.append(incoming)


    def closestPoint(self, gridPoint, asSpotElevation=False):
        """
        Returns the closest point in this container to the GridPoint passed in.

        :param gridPoint: GridPoint to check.
        :type gridPoint: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :param bool asSpotElevation: If True, returns SpotElevation object.
        :return: GridPoint if asSpotElevation == False
         SpotElevation if asSpotElevation == True
        :rtype :class:`pyprom.lib.locations.gridpoint.GridPoint`,
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        """
        distanceCalc = lambda themX, themY, usX, usY: hypot((themX - usX),
                                                        (themY - usY))
        themX, themY = gridPoint.x, gridPoint.y
        closestDistance = distanceCalc(themX, themY, *self.points[0])
        closest = self.points[0]
        for point in self.points[1:]:
            distance = distanceCalc(themX, themY, point[0], point[1])
            # well, can't get closer than that. mark it and bail.
            if distance == 0:
                closest = point
                break
            if distance < closestDistance:
                closest = point
                closestDistance = distance
        gp = GridPoint(closest[0], closest[1], self.elevation)
        if asSpotElevation:
            return gp.toSpotElevation(self.datamap)
        return gp

    def closestHighPerimeterPoint(self, gridPoint, asSpotElevation=False):
        """
        Returns the closest point in this container to the GridPoint passed in.

        :param gridPoint: GridPoint to check.
        :type gridPoint: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :param bool asSpotElevation: If True, returns SpotElevation object.
        :return: GridPoint if asSpotElevation == False
         SpotElevation if asSpotElevation == True
        :rtype :class:`pyprom.lib.locations.gridpoint.GridPoint`,
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        """
        distanceCalc = lambda themX, themY, usX, usY: hypot((themX - usX),
                                                            (themY - usY))
        themX, themY = gridPoint[0], gridPoint[1]

        highPerimeters = self.perimeter.findHighEdges(self.elevation)
        if not highPerimeters:
            return None
        closest = highPerimeters[0][0]
        closestDistance = distanceCalc(themX, themY, closest[0], closest[1])

        for highPerimeter in highPerimeters:
            for point in highPerimeter:
                distance = distanceCalc(themX, themY, point[0], point[1])
                # well, can't get closer than that. mark it and bail.
                if distance == 0:
                    closest = point
                    break
                if distance < closestDistance:
                    closest = point
                    closestDistance = distance
        if asSpotElevation:
            gp = GridPoint(closest[0], closest[1], closest[2])
            return gp.toSpotElevation(self.datamap)
        return closest

    def internal_neighbor_map(self):

        self.pointIndex = defaultdict(dict)
        for point in self.points:
            self.pointIndex[point[0]][point[1]] = point

        neighborHash = {}

        for point in self.points:
            neighborHash[point] = [nei for nei in self.iterNeighborDiagonal(point)]
        return neighborHash

    def closest_high_edge_to_internal_points(self):
        bsi = BaseSelfIterable()
        bsi.points = []
        bsi.points.extend(self.points)

        all_high_edges = self.perimeter.findHighPerimeter(self.elevation)
        bsi.points.extend(all_high_edges)

        bsi.pointIndex = defaultdict(dict)
        for point in bsi.points:
            bsi.pointIndex[point[0]][point[1]] = point

        neighborHash = {}

        for point in bsi.points:
            neighborHash[point] = [nei for nei in bsi.iterNeighborDiagonal(point)]

        graph = Graph()
        for local, remotes in neighborHash.items():
            for remote in remotes:
                graph.add_edge(local, remote, self.datamap.distance(local, remote))


        closest_dict = dict() # {self.point: closest_hs}

        for point in self.points:
            shortest_length = None
            for hs in all_high_edges:
                path = find_path(graph, point, hs)
                if shortest_length:
                    if path.total_cost < shortest_length.total_cost:
                        shortest_length = path
                else:
                    shortest_length = path
            closest_dict[point] = shortest_length.nodes[-1]
        return closest_dict


    def points_with_elevation(self):
        return [(x[0], x[1], self.elevation) for x in self.points]

    def __len__(self):
        """
        :return: number of items in `self.points`
        :rtype: int
        """
        return len(self.points)

    def __setitem__(self, idx, point):
        """
        Gives MultiPoint list like set capabilities

        :param int idx: index value
        :param point: BaseGridPoint or tuple for setitem.
        :type point: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :type point: tuple()
        """
        incoming = self._check_and_return_incoming_point_type(point)
        self.points[idx] = incoming

    def __getitem__(self, idx):
        """
        Gives MultiPoint list like get capabilities

        :param int idx: index value
        :return: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
         self.point at idx
        """
        return BaseGridPoint.from_tuple(self.points[idx])

    def __eq__(self, other):
        """
        Determines if this object is equal to another.

        :param other: other :class:`MultiPoint` to check.
        :type: :class:`MultiPoint`
        :return: equality
        :rtype: bool
        :raises: TypeError if other not of :class:`MultiPoint`
        """
        _isMultiPoint(other)
        return sorted([x for x in self.points]) == \
            sorted([x for x in other.points])

    def __ne__(self, other):
        """
        Determines if this object is not equal to another.

        :param other: other :class:`MultiPoint` to check.
        :type: :class:`MultiPoint`
        :return: inequality
        :rtype: bool
        :raises: TypeError if other not of :class:`MultiPoint`
        """
        _isMultiPoint(other)
        return sorted([x for x in self.points]) != \
            sorted([x for x in other.points])

    def __iter__(self):
        """
        :return: `self.points` as iterator
        """
        for point in self.points:
            yield point

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<Multipoint> elevation(m): {}, points {}". \
            format(self.elevation,
                   len(self.points))

    def _check_and_return_incoming_point_type(self, point):
        """
        Make sure incoming point type is a tuple with length 2, or explicitly a
        :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`

        :param point: tuple, or
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint
        :raises: TypeError if point not of
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint` or tuple
        :raises: Exception if tuple length != 2
        :return: tuple(x,y)
        """
        if isinstance(point, BaseGridPoint):
            incoming = point.to_tuple()
        elif isinstance(point, tuple):
            incoming = point
        else:
            raise TypeError("point must be tuple, or BaseGridPoint. Got: {}".format(type(point)))
        if len(incoming) != 2:
            raise Exception("tuple must have length of 2, or object must be BaseGridPoint and not inherited type.")
        return incoming

    __unicode__ = __str__ = __repr__


def _isMultiPoint(mp):
    """
    Check if passed in object is a :class:`MultiPoint`

    :param mp: object under scrutiny
    :raises: TypeError if other not of :class:`MultiPoint`
    """
    if not isinstance(mp, MultiPoint):
        raise TypeError("MultiPoint expected")
