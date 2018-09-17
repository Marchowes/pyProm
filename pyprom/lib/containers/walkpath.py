"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""
from ..locations.base_coordinate import BaseCoordinate
from ..locations.spot_elevation import SpotElevation
from ..locations.base_gridpoint import BaseGridPoint
from ..locations.gridpoint import GridPoint


class WalkPath:
    """WalkPath Container"""

    def __init__(self, points):
        """
        :param points: List of (X,Y) tuples.
        """
        self.points = points

    @property
    def path(self):
        """Returns the path as BaseCoordinates"""
        return self.baseCoordinate()

    def iterateBaseCoordinate(self):
        """
        Iterator for BaseCoordinate representation of the Walk Path.
        :return: :class:`BaseCoordinate`
        """
        for point in self.points:
            yield BaseCoordinate(point[0], point[1])

    def iterateSpotElevation(self, datamap):
        """
        Iterator for SpotElevation representation of the Walk Path.
        :param: :class:`Datamap` datamap used to look up elevation of point.
        :return: :class:`SpotElevation`
        """
        for point in self.points:
            x, y = datamap.latlong_to_xy(point[0], point[1])
            elevation = datamap.numpy_map[x, y]
            yield SpotElevation(point[0], point[1], elevation)

    def iterateBaseGridPoint(self, datamap):
        """
        Iterator for BaseGridPoint representation of the Walk Path.
        :param: :class:`Datamap` datamap used to look up elevation of point.
        :return: :class:`BaseGridPoint`
        """
        for point in self.points:
            x, y = datamap.latlong_to_xy(point[0], point[1])
            yield BaseGridPoint(x, y)

    def iterateGridPoint(self, datamap):
        """
        Iterator for GridPoint representation of the Walk Path.
        :param: :class:`Datamap` datamap used to look up elevation of point.
        :return: :class:`GridPoint`
        """
        for point in self.points:
            x, y = datamap.latlong_to_xy(point[0], point[1])
            elevation = datamap.numpy_map[x, y]
            yield GridPoint(x, y, elevation)

    def baseCoordinate(self):
        """
        :return: List of points as :class:`BaseCoordinate`
        """
        return [x for x in self.iterateBaseCoordinate()]

    def spotElevation(self, datamap):
        """
        :param: :class:`Datamap` datamap used to look up elevation of point.
        :return: List of points as :class:`SpotElevation`
        """
        return [x for x in self.iterateSpotElevation(datamap)]

    def baseGridPoint(self, datamap):
        """
        :param: :class:`Datamap` datamap used to look up elevation of point.
        :return: List of points as :class:`BaseGridPoint`
        """
        return [x for x in self.iterateBaseGridPoint(datamap)]

    def gridPoint(self, datamap):
        """
        :param: :class:`Datamap` datamap used to look up elevation of point.
        :return: List of points as :class:`GridPoint`
        """
        return [x for x in self.iterateGridPoint(datamap)]

    def to_dict(self):
        """
        :return: dict() representation of :class:`WalkPath`
        """
        to_dict = dict()
        to_dict['path'] = self.points
        return to_dict

    @classmethod
    def from_dict(cls, pathDict):
        """
        :return: :class:`WalkPath`
        """
        path = pathDict.get('path', [])
        pathTuples = []
        for point in path:
            pathTuples.append((point[0], point[1]))
        return cls(pathTuples)

    def __eq__(self, other):
        """
        Determines if :class:`WalkPath` is equal to another.
        :param other: :class:`WalkPath` to be compared against
        :return: bool of inequality
        """
        return self.points == other.points

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<WalkPath> {} Objects".format(len(self.points))
