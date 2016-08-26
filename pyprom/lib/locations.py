"""
This lib contains objects for storing various geographic data.
"""
from collections import defaultdict


class BaseCoordinate(object):
    """
    Base Coordinate, intended to be inherited from. This contains
    basic lat/long
    """
    def __init__(self, latitude, longitude, *args, **kwargs):
        self.latitude = latitude
        self.longitude = longitude

    def __eq__(self, other):
        return [self.latitude, self.longitude] ==\
               [other.latitude, other.longitude]

    def __ne__(self, other):
        return [self.latitude, self.longitude] !=\
               [other.latitude, other.longitude]

    def __hash__(self):
        return hash((self.latitude, self.longitude))

    def __repr__(self):
        return "<BaseCoordinate> lat {} long {}".format(self.latitude,
                                                        self.longitude)

    __unicode__ = __str__ = __repr__


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

    def __eq__(self, other):
        return [self.latitude, self.longitude, self.elevation] ==\
               [other.latitude, other.longitude, other.elevation]

    def __ne__(self, other):
        return [self.latitude, self.longitude, self.elevation] != \
               [other.latitude, other.longitude, other.elevation]

    def __hash__(self):
        return hash((self.latitude, self.longitude, self.elevation))

    def __repr__(self):
        return "<SpotElevation> lat {} long {} El {}".format(self.latitude,
                                                             self.longitude,
                                                             self.feet)

    __unicode__ = __str__ = __repr__


class Summit(SpotElevation):
    """
    Summit object stores relevant summit data.
    """
    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        super(Summit, self).__init__(latitude, longitude,
                                     elevation, *args, **kwargs)
        self.multiPoint = kwargs.get('multiPoint', None)

    def __repr__(self):
        return "<Summit> lat {} long {} El {}".format(self.feet,
                                                      self.latitude,
                                                      self.longitude)

    __unicode__ = __str__ = __repr__


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

    def __repr__(self):
        return "<SpotElevationContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__


class BaseGridPoint(object):
    def __init__(self, x, y):
        """
        Basic Gridpoint.
        :param x: x coordinate
        :param y: y coordinate
        """
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return "<BaseGridPoint> x: {}, y: {}".format(self.x, self.y)

    __unicode__ = __str__ = __repr__


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

    def __eq__(self, other):
        return [self.x, self.y, self.elevation] ==\
               [other.x, other.y, other.elevation]

    def __ne__(self, other):
        return [self.x, self.y, self.elevation] !=\
               [other.x, other.y, other.elevation]

    def __repr__(self):
        return "<GridPoint> x: {}, y: {}, elevation(m); {}".\
               format(self.x,
                      self.y,
                      self.elevation)

    __unicode__ = __str__ = __repr__


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
            nonEqualNeighborList = list()
            equalNeighborList = list()
            for _x, _y, elevation in neighbors:
                if elevation != self.elevation:
                    nonEqualNeighborList.append(GridPoint(_x, _y, elevation))
                elif elevation == self.elevation:
                    equalNeighborList.append(GridPoint(_x, _y, elevation))

            if nonEqualNeighborList:
                edgeObjectList.append(EdgePoint(gridpoint.x,
                                                gridpoint.y,
                                                self.elevation,
                                                nonEqualNeighborList,
                                                equalNeighborList))
        return edgeObjectList

    def findShores(self):
        """
        Function will find all shores along pond-like blob. and add all
        discontigous shore points as lists within the returned list.
        This is needed for finding Islands.
        :return: List of lists of `GridPoint` representing a Shore
        """
        edge = self.findEdge()
        # Flatten list and find unique members.
        shorePoints = list(set([val for sublist in
                           [x.nonEqualNeighbors for x in edge]
                           for val in sublist]))

        # For Optimized Lookups on larger lists.
        shoreIndex = defaultdict(list)
        for shorePoint in shorePoints:
            shoreIndex[shorePoint.x].append(shorePoint.y)
        purgedIndex = defaultdict(list)

        # initialize the shoreList and its index.
        shoreList = list()
        shoreList.append(list())
        listIndex = 0

        # Grab some shorePoint to start with.
        masterGridPoint = shorePoints[0]
        toBeAnalyzed = [masterGridPoint]

        # toBeAnalyzed preloaded with the first point in the shorePoints list.
        # First Act is to pop a point from toBeAnalyzed, and analyze it's
        # orthogonal neighbors for shorePoint members and add them to the
        # toBeAnalyzed list. These points are also added to a purgedIndex,
        # as well as dropped from shoreIndex.
        # Once neighbors are depleted, a new point is pulled from the
        # shorePoints list the list index is incremented and its neighbors are
        # analyzed until shorePoints is depleted.

        while True:
            if not toBeAnalyzed:
                if shorePoints:
                    listIndex += 1
                    shoreList.append(list())
                    toBeAnalyzed = [shorePoints[0]]
            if not toBeAnalyzed:
                break
            try:
                gridPoint = toBeAnalyzed.pop()
            except:
                return shoreList

            if gridPoint.y not in purgedIndex[gridPoint.x]:
                shorePoints.remove(gridPoint)
                shoreIndex[gridPoint.x].remove(gridPoint.y)
                purgedIndex[gridPoint.x].append(gridPoint.y)
                shoreList[listIndex].append(gridPoint)
            else:
                continue
            neighbors = self.analyzeData.iterateOrthogonal(gridPoint.x,
                                                           gridPoint.y)
            for _x, _y, elevation in neighbors:
                candidate = GridPoint(_x, _y, elevation)
                if candidate.y in shoreIndex[candidate.x]:
                    toBeAnalyzed.append(candidate)
        return shoreList

    @property
    def pointsLatLong(self):
        """
        :return: List of All blob points with lat/long instead of x/y
        """
        return [BaseCoordinate(
                self.analyzeData.datamap.x_position_latitude(coord.x),
                self.analyzeData.datamap.y_position_longitude(coord.y))
                for coord in self.points]

    def __repr__(self):
        return "<Multipoint> elevation(m): {}, points {}". \
            format(self.elevation,
                   len(self.points))

    __unicode__ = __str__ = __repr__


class EdgePoint(GridPoint):
    """
    An Edge point, to be used in conjunction with MultiPoints.
    This keeps track of non equal height neighbors and their elevation
    :param x: x coordinate
    :param y: y coordinate
    :param elevation: elevation in meters
    :param nonEqualNeighbors: list of GridPoints that are non equal in height
           in comparison to the EdgePoint.
    :param equalNeighbors: list of GridPoints that are equal in height
           in comparison to the EdgePoint.
    """
    def __init__(self, x, y, elevation, nonEqualNeighbors, equalNeighbors):
        super(EdgePoint, self).__init__(x, y, elevation)
        self.nonEqualNeighbors = nonEqualNeighbors
        self.equalNeighbors = equalNeighbors

    def __repr__(self):
        return "<EdgePoint> ele(m): {}, #Eq Points {}, #NonEq Points {}".\
            format(self.elevation,
                   len(self.equalNeighbors),
                   len(self.nonEqualNeighbors))

    __unicode__ = __str__ = __repr__
