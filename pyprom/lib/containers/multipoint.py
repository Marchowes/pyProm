"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Multipoint
type location objects as well as a number of functions.
"""
import json

from ..locations.base_coordinate import BaseCoordinate
from ..locations.base_gridpoint import isBaseGridPoint, BaseGridPoint
from .perimeter import Perimeter

class MultiPoint:
    """MultiPoint Container"""

    def __init__(self, points, elevation, datamap,
                 perimeter=None):
        """
        This is an "equal height" Multipoint storage container that
        provides a number of functions for analysis of these blob like
        locations. An Example of this would be a pond. This object in
        contains a list of all the points of this pond.
        :param points: list of BaseGridPoint objects. These are the inside
            points that make up a Multipoint.
        :param elevation: elevation in meters
        :param datamap: :class:`Datamap` object.
        :param perimeter: :class:`Perimeter` object.
            These are the points that make up the border of the multipoint
            outside of the multipoint.
        """
        super(MultiPoint, self).__init__()
        self.points = points  # BaseGridPoint Objects.
        self.elevation = elevation
        self.datamap = datamap  # data analysis object.
        self.perimeter = perimeter

    def to_json(self, prettyprint=True):
        """
        :param prettyprint: human readable,
         but takes more space when written to a file.
        :return: json data
        """
        if prettyprint:
            return json.dumps(self.to_dict(), sort_keys=True,
                              indent=4, separators=(',', ': '))
        else:
            return json.dumps(self.to_dict())

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
        :param multiPointDict: dict() representation of this object.
        :param datamap: :class:`Datamap`
        :return: :class:`MultiPoint`
        """
        points = [BaseGridPoint(x['x'], x['y']) for x in multiPointDict['points']]
        perimeter = Perimeter.from_dict(multiPointDict['perimeter'], datamap)
        elevation = multiPointDict['elevation']
        return cls(points, elevation, datamap, perimeter=perimeter)

    @property
    def pointsLatLong(self):
        """
        :return: List of All blob points with lat/long instead of x/y
        """
        return [BaseCoordinate(*self.datamap.xy_to_latlong(coord.x, coord.y))
                for coord in self.points]

    def append(self, point):
        """
        Add a BaseGridPoint to the container.
        :param point: :class:`BaseGridPoint`
        :raises: TypeError if point not of :class:`BaseGridPoint`
        """
        isBaseGridPoint(point)
        self.points.append(point)

    def __len__(self):
        """
        :return: integer - number of items in self.points
        """
        return len(self.points)

    def __setitem__(self, idx, point):
        """
        Gives MultiPoint list like set capabilities
        :param idx: index value
        :param point: :class:`BaseGridPoint`
        :raises: TypeError if point not of :class:`BaseGridPoint`
        """
        isBaseGridPoint(point)
        self.points[idx] = point

    def __getitem__(self, idx):
        """
        Gives MultiPoint list like get capabilities
        :param idx: index value
        :return: :class:`GridPoint` self.point at idx
        """
        return self.points[idx]

    def __eq__(self, other):
        """
        Determines if MultiPoint is equal to another.
        :param other: :class:`MultiPoint`
        :return: bool of equality
        :raises: TypeError if other not of :class:`MultiPoint`
        """
        _isMultiPoint(other)
        return sorted([x for x in self.points]) == \
            sorted([x for x in other.points])

    def __ne__(self, other):
        """
        :param other: :class:`MultiPoint`
        :return: bool of inequality
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
    :param mp: object under scrutiny
    :raises: TypeError if other not of :class:`MultiPoint`
    """
    if not isinstance(mp, MultiPoint):
        raise TypeError("MultiPoint expected")
