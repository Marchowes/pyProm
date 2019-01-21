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
    """
    WalkPath Container.
    A Walk path is an ordered list of (X,Y) coordinates which creates a path.
    """

    def __init__(self, points):
        """
        :param points: List of (X,Y) tuples. making a path
        :type points: list(tuple(int, int))
        """
        self.points = points

    @property
    def path(self):
        """
        Returns the path as BaseCoordinates

        :return: List of points as
         :class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`
        :rtype:
         list(:class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`)
        """
        return self.baseCoordinate()


    def iterateBaseCoordinate(self):
        """
        Iterator for BaseCoordinate representation of the Walk Path.

        :return: Basecoordinate along path.
        :rtype: :class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`
        """
        for point in self.points:
            yield BaseCoordinate(point[0], point[1])

    def iterateSpotElevation(self, datamap):
        """
        Iterator for SpotElevation representation of the Walk Path.

        :param datamap: Datamap used to look up elevation of point.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: SpotElevation along path.
        :rtype: :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        """
        for point in self.points:
            x, y = datamap.latlong_to_xy(point[0], point[1])
            elevation = datamap.numpy_map[x, y]
            yield SpotElevation(point[0], point[1], elevation)

    def iterateBaseGridPoint(self, datamap):
        """
        Iterator for BaseGridPoint representation of the Walk Path.

        :param datamap: Datamap used to look up elevation of point.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: BaseGridPoint along path
        :rtype: :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        """
        for point in self.points:
            x, y = datamap.latlong_to_xy(point[0], point[1])
            yield BaseGridPoint(x, y)

    def iterateGridPoint(self, datamap):
        """
        Iterator for GridPoint representation of the Walk Path.

        :param datamap: Datamap used to look up elevation of point.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: GridPoint along path
        :rtype: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        """
        for point in self.points:
            x, y = datamap.latlong_to_xy(point[0], point[1])
            elevation = datamap.numpy_map[x, y]
            yield GridPoint(x, y, elevation)

    def baseCoordinate(self):
        """
        :return: List of points as
         :class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`
        :rtype:
         list(:class:`pyprom.lib.locations.base_coordinate.BaseCoordinate`)
        """
        return [x for x in self.iterateBaseCoordinate()]

    def spotElevation(self, datamap):
        """
        :param datamap: Datamap used to look up elevation of point.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: List of points as
         :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
        :rtype:
         list(:class:`pyprom.lib.locations.spot_elevation.SpotElevation`)
        """
        return [x for x in self.iterateSpotElevation(datamap)]

    def baseGridPoint(self, datamap):
        """
        :param datamap: Datamap used to look up elevation of point.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: List of points as
         :class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`
        :rtype:
         list(:class:`pyprom.lib.locations.base_gridpoint.BaseGridPoint`)
        """
        return [x for x in self.iterateBaseGridPoint(datamap)]

    def gridPoint(self, datamap):
        """
        :param datamap: Datamap used to look up elevation of point.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: List of points as
         :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :rtype: list(:class:`pyprom.lib.locations.gridpoint.GridPoint`)
        """
        return [x for x in self.iterateGridPoint(datamap)]

    def to_dict(self):
        """
        Create the dictionary representation of this object.

        :return: dict() representation of :class:`WalkPath`
        :rtype: dict()
        """
        to_dict = dict()
        to_dict['path'] = self.points
        return to_dict

    @classmethod
    def from_dict(cls, pathDict):
        """
        Create this object from dictionary representation

        :param dict pathDict: dict() representation of this object.
        :return: a new WalkPath
        :rtype: :class:`WalkPath`
        """
        path = pathDict.get('path', [])
        pathTuples = []
        for point in path:
            pathTuples.append((point[0], point[1]))
        return cls(pathTuples)

    def __eq__(self, other):
        """
        Determines if this object is equal to another.

        :param other: :class:`WalkPath` to be compared against
        :type other: :class:`WalkPath`
        :return: equality
        :rtype: bool
        """
        return self.points == other.points

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<WalkPath> {} Objects".format(len(self.points))
