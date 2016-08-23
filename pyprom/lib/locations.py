"""
This lib contains objects for storing various geographic data.
"""


class BaseCoordinate(object):
    """
    Base Coordinate, intended to be inherited from. This contains
    basic lat/long
    """
    def __init__(self, latitude, longitude, *args, **kwargs):
        self.latitude = latitude
        self.longitude = longitude


class SpotElevation(BaseCoordinate):
    """
    SpotElevation -- Intended to be inherited from. lat/long/elevation
    """
    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        super(SpotElevation, self).__init__(latitude, longitude)
        self.elevation = elevation
        self.candidate = kwargs.get('edge', None)

    @property
    def feet(self):
        return self.elevation * 3.2808


class Summit(SpotElevation):
    """
    Summit object stores relevant summit data.
    """
    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        super(Summit, self).__init__(latitude, longitude,
                                     elevation, *args, **kwargs)
        self.multiPoint = kwargs.get('multiPoint', None)

    def __str__(self):
        return "Summit El {} lat {} long {}".format(self.feet,
                                                    self.latitude,
                                                    self.longitude)


class SpotElevationContainer(object):
    def __init__(self, spotElevationList):
        self.points = spotElevationList

    def rectangle(self, lat1, long1, lat2, long2):
        """
        For the purpose of gathering all points in a rectangle of
        (lat1, long1) - (lat2, long2)
        :param lat1:  latitude of point 1
        :param long1: longitude of point 1
        :param lat2:  latitude of point 2
        :param long2: longitude of point 2
        :return: list of all points in that between
        (lat1, long1) - (lat2, long2)
        """
        upperlat = max(lat1, lat2)
        upperlong = max(long1, long2)
        lowerlat = min(lat1, lat2)
        lowerlong = min(long1, long2)
        return [x for x in self.points if lowerlat < x.latitude < upperlat and
                lowerlong < x.longitude < upperlong]

    def elevationRange(self, lower=None, upper=100000):
        """
        :param lower: lower limit in feet
        :param upper: upper limit in feet
        :return: list of all points in range between lower and upper
        """
        return [x for x in self.points if x.feet > lower and x.feet < upper]

    def elevationRangeMetric(self, lower=None, upper=100000):
        """
        :param lower: lower limit in Meters
        :param upper: upper limit in Meters
        :return: list of all points in range between lower and upper
        """
        return [x for x in self.points if x.elevation > lower and
                x.elevation < upper]


class BaseGridPoint(object):
    def __init__(self, x, y):
        """
        Basic Gridpoint.
        :param x: x coordinate
        :param y: y coordinate
        """
        self.x = x
        self.y = y


class GridPoint(BaseGridPoint):
    def __init__(self, x, y, elevation):
        """
        A basic gridpoint. This maps an elevation to an X,Y coordinate.
        :param x: x coordinate
        :param y: y coordinate
        :param elevation: elevation in meters
        """
        super(GridPoint, self).__init__(x, y)
        self.elevation = elevation


class MultiPoint(object):
    """
    :param points: list of BaseGridPoint objects
    :param elevation: elevation in meters
    :param analyzeData: AnalyzeData object.
    """
    def __init__(self, points, elevation, analyzeData):
        self.points = points  # BaseGridPoint Object.
        self.elevation = elevation
        self.analyzeData = analyzeData  # data analysis object.

    def findEdge(self):
        """
        Finds all points in a blob that have non-equal neighbors.
        :return: list of EdgePoint objects.
        """
        edgeObjectList = list()
        for gridpoint in self.points:
            neighbors = self.analyzeData.iterateDiagonal(gridpoint.x,
                                                         gridpoint.y)
            edgeList = list()
            for _x, _y, elevation in neighbors:
                if elevation != self.elevation:
                    edgeList.append(GridPoint(_x, _y, elevation))
            if edgeList:
                edgeObjectList.append(EdgePoint(gridpoint.x,
                                                gridpoint.y,
                                                self.elevation,
                                                edgeList))
        return edgeObjectList

    @property
    def pointsLatLong(self):
        """
        :return: List of All blob points with lat/long instead of x/y
        """
        return [BaseCoordinate(
                self.analyzeData.datamap.x_position_latitude(coord.x),
                self.analyzeData.datamap.y_position_longitude(coord.y))
                for coord in self.points]


class EdgePoint(GridPoint):
    """
    An Edge point, to be used in conjunction with MultiPoints.
    This keeps track of non equal height neighbors and their elevation
    :param x: x coordinate
    :param y: y coordinate
    :param elevation: elevation in meters
    :param nonEqualNeighbors: list of GridPoints that are non equal in height
           in comparison to the EdgePoint.
    """
    def __init__(self, x, y, elevation, nonEqualNeighbors):
        super(EdgePoint, self).__init__(x, y, elevation)
        self.nonEqualNeighbors = nonEqualNeighbors
