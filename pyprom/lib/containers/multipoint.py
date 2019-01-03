"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Multipoint
type location objects as well as a number of functions.
"""

from ..locations.base_coordinate import BaseCoordinate
from ..locations.base_gridpoint import isBaseGridPoint, BaseGridPoint
from ..locations.gridpoint import GridPoint
from .perimeter import Perimeter


class MultiPoint:
    """A MultiPoint Container. This is a special kind of feature which contains
    multiple :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`s.
    These points are all of equal elevation and neighbor each other
    Orthogonally or Diagonally.
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
    |      [5][5][5]
    |         [5]   <- Without Perimeter
    |      [5]
    |
    |
    |   [4][3][4][6][4]
    |   [3]         [6] <- Just the Perimeter.
    |   [2][3]   [6][3]
    |   [3]   [4][3]
    |   [6][7][6]
    """

    def __init__(self, points, elevation, datamap,
                 perimeter=None):
        """
        :param points: list of BaseGridPoint objects. These are the inside
            points that make up a Multipoint.
        :type points:
         list(:class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`)
        :param elevation: elevation in meters
        :type elevation: int, float
        :param datamap: datamap which this MultiPoint uses.
        :type datamap: :class:`Datamap` object.
        :param perimeter: :class:`MultiPoint` Perimeter.  These are the points
         that make up the orthogonally/diagonally connected border of the
         multipoint outside of the multipoint.
        :type perimeter: :class:`Perimeter` object.
        """
        super(MultiPoint, self).__init__()
        self.points = points  # BaseGridPoint Objects.
        self.elevation = elevation
        self.datamap = datamap  # data analysis object.
        self.perimeter = perimeter

    def to_dict(self):
        """
        :return: dict() representation of :class:`MultiPoint`
        """
        multiPointDict = dict()
        multiPointDict['points'] = [x.to_dict() for x in self.points]
        multiPointDict['perimeter'] = self.perimeter.to_dict()
        multiPointDict['elevation'] = self.elevation
        return multiPointDict

    @classmethod
    def from_dict(cls, multiPointDict, datamap=None):
        """
        Creates a new :class:`MultiPoint` from the dict() representation.

        :param multiPointDict: dict() representation of this
         :class:`MultiPoint`.
        :param datamap: datamap which this MultiPoint uses.
        :type datamap: :class:`Datamap` object.
        :return: new Multipoint object.
        :rtype: :class:`MultiPoint`
        """
        points = [BaseGridPoint(x['x'], x['y'])
                  for x in multiPointDict['points']]
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
        return [BaseCoordinate(*self.datamap.xy_to_latlong(coord.x, coord.y))
                for coord in self.points]

    def append(self, point):
        """
        Add a BaseGridPoint to this container.

        :param point: BaseGridPoint to add.
        :type point: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :raises: TypeError if point not of
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        """
        isBaseGridPoint(point)
        self.points.append(point)

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
        closestDistance = gridPoint.distance(self.points[0])
        closest = self.points[0]
        for point in self.points[1:]:
            distance = gridPoint.distance(point)
            # well, can't get closer than that. mark it and bail.
            if distance == 0:
                closest = point
                break
            if distance < closestDistance:
                closest = point
                closestDistance = distance
        gp = GridPoint(closest.x, closest.y, self.elevation)
        if asSpotElevation:
            return gp.toSpotElevation(self.datamap)
        return gp

    def __len__(self):
        """
        :return: number of items in self.points
        :rtype: int
        """
        return len(self.points)

    def __setitem__(self, idx, point):
        """
        Gives MultiPoint list like set capabilities

        :param int idx: index value
        :param point: BaseGridPoint for setitem.
        :type point: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :raises: TypeError if point not of :class:`BaseGridPoint`
        """
        isBaseGridPoint(point)
        self.points[idx] = point

    def __getitem__(self, idx):
        """
        Gives MultiPoint list like get capabilities

        :param int idx: index value
        :return: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
         self.point at idx
        """
        return self.points[idx]

    def __eq__(self, other):
        """
        Determines if MultiPoint is equal to another.

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
        Determines if MultiPoint is not equal to another.

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
        :return: self.points as iterator
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

    __unicode__ = __str__ = __repr__


def _isMultiPoint(mp):
    """
    Check if passed in object is a :class:`MultiPoint`

    :param mp: object under scrutiny
    :raises: TypeError if other not of :class:`MultiPoint`
    """
    if not isinstance(mp, MultiPoint):
        raise TypeError("MultiPoint expected")
