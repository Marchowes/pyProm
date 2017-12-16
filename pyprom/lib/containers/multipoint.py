"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Multipoint
type location objects as well as a number of functions.
"""
import json
from ..locations.base_coordinate import BaseCoordinate


class MultiPoint(object):
    """
    This is an "equal height" Multipoint storage container that
    provides a number of functions for analysis of these blob like
    locations. An Example of this would be a pond. This object in
    contains a list of all the points of this pond.
    :param points: list of BaseGridPoint objects
    :param elevation: elevation in meters
    :param datamap: :class:`Datamap` object.
    :param edgePoints: :class:`EdgePointContainer` object
    :param inverseEdgePoints: :class:`InverseEdgePointContainer` object
    """
    def __init__(self, points, elevation, datamap,
                 edgePoints=None, inverseEdgePoints=None):
        super(MultiPoint, self).__init__()
        self.points = points  # BaseGridPoint Object.
        self.elevation = elevation
        self.datamap = datamap  # data analysis object.
        self.edgePoints = edgePoints
        self.inverseEdgePoints = inverseEdgePoints
        self.mapEdge = []

    def to_dict(self, verbose=True):
        """
        :param verbose: returns extra data like `InverseEdgePoint`
        and `EdgePoint` (future)
        :return: list of dicts.
        """
        plist = list()
        for point in self.points:
            pdict = dict()
            pdict['gridpoint'] = point.to_dict()
            lat, long = self.datamap.xy_to_latlong(point.x, point.y)
            pdict['coordinate'] = \
                BaseCoordinate(lat, long).to_dict()
            plist.append(pdict)
        return plist

    def to_json(self, verbose=False, prettyprint=True):
        """
        :param prettyprint: human readable,
         but takes more space when written to a file.
        :param verbose: returns extra data like `InverseEdgePoint`
        and `EdgePoint` (future)
        :return: json data
        """
        if prettyprint:
            return json.dumps(self.to_dict(verbose=verbose), sort_keys=True,
                              indent=4, separators=(',', ': '))
        else:
            return json.dumps(self.to_dict(verbose=verbose))

    @property
    def pointsLatLong(self):
        """
        :return: List of All blob points with lat/long instead of x/y
        """
        return [BaseCoordinate(*self.datamap.xy_to_latlong(coord.x, coord.y))
                for coord in self.points]

    def __repr__(self):
        return "<Multipoint> elevation(m): {}, points {}". \
            format(self.elevation,
                   len(self.points))

    __unicode__ = __str__ = __repr__
