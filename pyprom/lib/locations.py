"""
This lib contains objects for storing various geographic data.
"""
import logging

from collections import defaultdict, Counter
from location_util import findExtremities


class _Base(object):
    def __init__(self):
        self.logger = logging.getLogger('pyProm.{}'.format(__name__))


class BaseCoordinate(object):
    """
    Base Coordinate, intended to be inherited from. This contains
    basic lat/long
    """
    def __init__(self, latitude, longitude, *args, **kwargs):
        super(BaseCoordinate, self).__init__()
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
        try:
            return self.elevation * 3.2808
        except:
            return None

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
        return "<Summit> lat {} long {} El {} MultiPoint {}".format(
            self.latitude,
            self.longitude,
            self.feet,
            bool(self.multiPoint))

    __unicode__ = __str__ = __repr__


class Saddle(SpotElevation):
    """
    Saddle object stores relevant saddle data.
    """
    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        super(Saddle, self).__init__(latitude, longitude,
                                     elevation, *args, **kwargs)
        self.multiPoint = kwargs.get('multiPoint', None)

    def __repr__(self):
        return "<Saddle> lat {} long {} El {} MultiPoint {}".format(
            self.latitude,
            self.longitude,
            self.feet,
            bool(self.multiPoint))

    __unicode__ = __str__ = __repr__


class SpotElevationContainer(_Base):
    """
    Container for Spot Elevation type lists.
    Allows for various list transformations.
    """
    def __init__(self, spotElevationList):
        super(SpotElevationContainer, self).__init__()
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

    def byType(self, string):
        """
        :param string: Object type (as String). ex: Saddle, Summit
        :return: SpotElevationContainer of objects by type.
        """
        name = string.upper()
        return SpotElevationContainer([x for x in self.points
                                       if type(x).__name__.upper() == name])

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
        super(BaseGridPoint, self).__init__()
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

    def toSpotElevation(self, analysis):
        return SpotElevation(analysis.datamap.x_position_latitude(self.x),
                             analysis.datamap.y_position_longitude(self.y),
                             self.elevation)

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


class BaseGridPointContainer(_Base):
    """
    Base Grid Point Container.
    """
    def __init__(self, gridPointList):
        super(BaseGridPointContainer, self).__init__()
        self.points = gridPointList

    def __hash__(self):
        return hash(tuple(sorted([x.x for x in self.points])))

    def __eq__(self, other):
        return sorted([x.x for x in self.points]) == \
               sorted([x.x for x in other.points])

    def __ne__(self, other):
        return sorted([x.x for x in self.points]) == \
               sorted([x.x for x in other.points])

    def __repr__(self):
        return "<BaseGridPointContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__


class GridPointContainer(BaseGridPointContainer):
    """
    Container for GridPoint type lists.
    Allows for various list transformations and functions.
    """

    def __init__(self, gridPointList):
        super(GridPointContainer, self).__init__(gridPointList)

    def findExtremities(self):
        return findExtremities(self.points)

    def __repr__(self):
        return "<GridPointContainer> {} Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__


class Island(BaseGridPointContainer):
    """
    Island Object accepts a list of shore points, and a MultiPoint object
    which is a Pond-type object. points are calculated in fillIn()
    """
    def __init__(self, shoreGridPointList, analyzeData, pondElevation):
        super(Island, self).__init__(shoreGridPointList)
        self.shoreGridPointList = self.points[:]
        self.pondElevation = pondElevation
        self.analyzeData = analyzeData
        self.fillIn()
        self.mapEdge = self.findMapEdge()

    def findMapEdge(self):
        """
        :return: list of SpotElevation Points along the map Edge.
        """
        mapEdge = list()
        for point in self.points:
            if point.x == 0 or point.x ==\
                    self.analyzeData.self.analyzeData.max_x:
                mapEdge.append(point.toSpotElevation(self.analyzeData))
            if point.y == 0 or point.y ==\
                    self.analyzeData.self.analyzeData.max_y:
                mapEdge.append(point.toSpotElevation(self.analyzeData))
        return mapEdge

    def fillIn(self):
        """
        Function uses shore GridPoints and water body elevation to find all
        points on island. Object "points" are then replaced with GridPoints
        found.
        """

        # Grabs first point (which is a shore) and prefills in hashes
        toBeAnalyzed = [self.points[0]]
        islandHash = defaultdict(list)
        islandHash[toBeAnalyzed[0].x].append(toBeAnalyzed[0].x)
        islandGridPoints = toBeAnalyzed[:]

        # Find all points not at pond-level.
        while toBeAnalyzed:
            gridPoint = toBeAnalyzed.pop()
            neighbors = self.analyzeData.iterateDiagonal(gridPoint.x,
                                                         gridPoint.y)
            for _x, _y, elevation in neighbors:

                if elevation != self.pondElevation and _y not in\
                                islandHash[_x]:
                    branch = GridPoint(_x, _y, elevation)
                    islandHash[_x].append(_y)
                    toBeAnalyzed.append(branch)
                    islandGridPoints.append(branch)
        self.points = islandGridPoints

    def __repr__(self):
        return "<Island> {} Point Objects".format(len(self.points))

    __unicode__ = __str__ = __repr__


class MultiPoint(_Base):
    """
    This is an "equal height" Multipoint storage container that
    provides a number of functions for analysis of these blob like
    locations. An Example of this would be a pond. This object in
    contains a list of all the points of this pond.
    :param points: list of BaseGridPoint objects
    :param elevation: elevation in meters
    :param analyzeData: AnalyzeData object.
    """
    def __init__(self, points, elevation, analyzeData,
                 edgePoints=None, inverseEdgePoints=None):
        super(MultiPoint, self).__init__()
        self.points = points  # BaseGridPoint Object.
        self.elevation = elevation
        self.analyzeData = analyzeData  # data analysis object.
        self.edgePoints = edgePoints
        self.inverseEdgePoints = inverseEdgePoints
        self.mapEdge = []

    def findExtremities(self):
        """
        Function will find all the points furthest N, S, E, W and
        return their X or Y values.
        :return: dict: {'N': x, 'S': x, 'E': y, 'W': y}
        """
        return findExtremities(self.findShores().points)

    def findMapEdge(self):
        """
        :return: list of :class:`SpotElevation` Points along the map Edge.
        That is, the edge of the dataset map.
        """
        mapEdge = list()
        for point in self.points:
            if point.x == 0 or point.x == self.analyzeData.max_x:
                newPoint = GridPoint(point.x, point.y, self.elevation)
                mapEdge.append(newPoint.toSpotElevation(self.analyzeData))
            if point.y == 0 or point.y == self.analyzeData.max_y:
                newPoint = GridPoint(point.x, point.y, self.elevation)
                mapEdge.append(newPoint.toSpotElevation(self.analyzeData))
        return mapEdge

    def findEdge(self):
        """
        Finds all points in a Equal Height Multipoint that have non-equal
        neighbors. Using the pond example, these are all the water points
        that border the shore
        :return: list of EdgePoint objects.
        """
        return self.edgePoints

    # Obsolete. Kept for debugging.
    def findShores(self, edge=None):
        """
        Function will find all shores along pond-like multipoint. and add all
        discontiguous shore points as lists within the returned list.
        This is needed for finding "Islands".
        :param: edge - A list of edges (can reduce redundant edge finds
         in certain cases.)
        :return: List of lists of `GridPoint` representing a Shore
        """
        if not edge:
            edge = self.findEdge()

        # Flatten list and find unique members.
        shorePoints = list(set([val for sublist in
                           [x.nonEqualNeighbors for x in edge.points]
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
        # First act is to pop a point from toBeAnalyzed, and analyze it's
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
        return [GridPointContainer(x) for x in shoreList]

    def findIslands(self):
        """
        findIslands runs through a list of shore lists and finds the
        extremities of each shorelist. The list with the most maximum
        relative extremity is considered the main pond shore. Everything
        else is implicity an Island .
        :return: List of Islands.
        """

        # First lets find the shores.
        shoreList = self.findShores()

        # Initialize Blank Values.
        N, S, E, W = (None for i in range(4))

        # Next, we find all the furthest extremities among all shore lists.
        # In theory, the only extremities that can occur for shorelines that
        # Don't belong to the main pond body are along the map edge.
        for index, shore in enumerate(shoreList):
            extremityHash = shore.findExtremities()
            if index == 0:
                N, S, E, W = ([shore] for i in range(4))
                continue
            if extremityHash['N'][0].x < N[0].findExtremities()['N'][0].x:
                N = [shore]
            elif extremityHash['N'][0].x == N[0].findExtremities()['N'][0].x:
                N.append(shore)
            if extremityHash['S'][0].x > S[0].findExtremities()['S'][0].x:
                S = [shore]
            elif extremityHash['S'][0].x == S[0].findExtremities()['S'][0].x:
                S.append(shore)
            if extremityHash['E'][0].y > E[0].findExtremities()['E'][0].y:
                E = [shore]
            elif extremityHash['E'][0].y == E[0].findExtremities()['E'][0].y:
                E.append(shore)
            if extremityHash['W'][0].y < W[0].findExtremities()['W'][0].y:
                W = [shore]
            elif extremityHash['W'][0].y == W[0].findExtremities()['W'][0].y:
                W.append(shore)

        # Now, lets flatten the list of cardinal extremities
        flatList = [val for sublist in [N, S, E, W] for val in sublist]
        counter = Counter(flatList)

        # In theory, the main pond shore should have the most extremities
        pondLike = counter.most_common(1)

        # Wow, what a piece of crap. I feel ashamed of the next 6 lines.
        if pondLike[0][0] < 4:
            raise Exception("Largest Pond does not have 4 max points."
                            " Something is horribly Wrong.")
        if len(pondLike) != 1:
            raise Exception("Equal number of extremities in pond?"
                            " How can that be?")

            pondLike = pondLike[0][0]

        # Find any map edges and add them to the Plain Blob Object mapEdge.
        self.mapEdge = self.findMapEdge()

        # Well, this probably isn't an island, so drop it from the list.
        shoreList.remove(pondLike)

        # Find any map edges for the island, and create Island Objects.
        islands = list()
        for island in shoreList:
            islands.append(Island(island.points,
                                  self.analyzeData,
                                  self.elevation))
        return islands

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
    :param nonEqualNeighbors: list of :class:`GridPoints` that are non equal
           in height in comparison to the :class:`EdgePoint`.
    :param equalNeighbors: list of :class:`GridPoint`s that are equal in
           height in comparison to the EdgePoint.
    """
    def __init__(self, x, y, elevation, nonEqualNeighbors, equalNeighbors):
        super(EdgePoint, self).__init__(x, y, elevation)
        self.nonEqualNeighbors = nonEqualNeighbors
        self.equalNeighbors = equalNeighbors

    def __repr__(self):
        return ("<EdgePoint> x: {}, y: {}, ele(m): {},"
                " #Eq Points {}, #NonEq Points {}".
                format(self.x,
                       self.y,
                       self.elevation,
                       len(self.equalNeighbors),
                       len(self.nonEqualNeighbors)))

    __unicode__ = __str__ = __repr__


class InverseEdgePoint(GridPoint):
    """
    A Shore point, to be used in conjunction with :class:`EdgePoint`.
    This keeps track shorePoints and their neighboring :class:`EdgePoint`s.
    :param x: x coordinate
    :param y: y coordinate
    :param elevation: elevation in meters
    :param edgePoints: list of EdgePoints.
    :param inverseEdgePointNeighbors: list of neighboring
     :class:`InverseEdgePoint`
    """
    def __init__(self, x, y, elevation, edgePoints,
                 inverseEdgePointNeighbors=[]):
        super(InverseEdgePoint, self).__init__(x, y, elevation)
        self.edgePoints = edgePoints
        self.inverseEdgePointNeighbors = inverseEdgePointNeighbors

    def addEdge(self, edgepoint):
        self.edgePoints.append(edgepoint)

    def orthogonalEdgePoints(self):
        """
        Returns all orthogonal edgePoints.
        :return:
        """
        return [x for x in self.iterateOrthogonalEdgePoint()]


    def iterateOrthogonalEdgePoint(self):
        """
        Iterate through all orthogonal Edgepoint Neighbors. these are UNORDERED
        :return:
        """
        shiftList = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        for point in self.edgePoints:
            if [sh for sh in shiftList if self.x + sh[0] == point.x and
                self.y + sh[1] == point.y]:
                yield point
            else:
                continue

    def __repr__(self):
        return ("<InverseEdgePoint> x: {}, y: {}, ele(m): {},"
                " #EdgePoints {}, #InverseEdgePointNeighbors {}".
                format(self.x,
                       self.y,
                       self.elevation,
                       len(self.edgePoints),
                       len(self.inverseEdgePointNeighbors)))

    __unicode__ = __str__ = __repr__


class EdgePointContainer(_Base):
    """
    Container for :class:`EdgePoint` type lists.
    Allows for various list transformations.
    :param edgePointList: list of :class:`EdgePoint` to self.points
    :param edgePointIndex: {X: { Y: :class:`EdgePoint`}} passing this will
    automatically generate self.points

    """
    def __init__(self, edgePointList=None,
                 edgePointIndex=None,
                 analyzeData=None):
        super(EdgePointContainer, self).__init__()
        if edgePointIndex:
            self.edgePointIndex = edgePointIndex
            self.points = [v[1] for x, y in self.edgePointIndex.items()
                           for v in y.items()]
        if edgePointList:
            self.points = edgePointList
        self.analyzeData = analyzeData

    def __repr__(self):
        return "<EdgePointContainer> {} Objects".format(len(self.points))

    def __iter__(self):
        for edgePoint in self.points:
            yield edgePoint

    __unicode__ = __str__ = __repr__


class InverseEdgePointContainer(_Base):
    """
    Container for :class:`InverseEdgePoint` type lists.
    Allows for various list transformations.
    :param inverseEdgePointList: list of :class:`InverseEdgePoint` to
     self.points
    :param inverseEdgePointIndex: {X: { Y: :class:`InverseEdgePoint`}} passing
    this will automatically generate self.points
    """
    def __init__(self, inverseEdgePointList=None,
                 inverseEdgePointIndex=None,
                 analyzeData=None):
        super(InverseEdgePointContainer, self).__init__()
        if inverseEdgePointIndex:
            self.inverseEdgePointIndex = inverseEdgePointIndex
            self.points = [v[1] for x, y in self.inverseEdgePointIndex.items()
                           for v in y.items()]
        if inverseEdgePointList:
            self.points = inverseEdgePointList
        self.analyzeData = analyzeData
        self.exemptPoints = defaultdict(list)

    def iterNeighborDiagonal(self, inverseEdgePoint):
        """
        Iterate through existing diagonal :class:`InverseEdgePoint`
        neighbors.
        :param inverseEdgePoint:
        """
        shiftList = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1],
                     [0, -1], [-1, -1]]
        for shift in shiftList:
            x = inverseEdgePoint.x+shift[0]
            y = inverseEdgePoint.y+shift[1]
            if self.inverseEdgePointIndex[x][y]:
                if 0 <= x <= self.analyzeData.max_x\
                        and 0 <= y <= self.analyzeData.max_y:
                    yield self.inverseEdgePointIndex[x][y]
            else:
                continue

    def iterNeighborOrthogonal(self, inverseEdgePoint):
        """
        Iterate through existing orthogonal :class:`InverseEdgePoint`
        neighbors.
        :param inverseEdgePoint:
        """

        shiftList = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        for shift in shiftList:
            x = inverseEdgePoint.x + shift[0]
            y = inverseEdgePoint.y + shift[1]
            if self.inverseEdgePointIndex[x][y]:
                if 0 <= x <= self.analyzeData.max_x \
                        and 0 <= y <= self.analyzeData.max_y:
                    yield self.inverseEdgePointIndex[x][y]
            else:
                continue

    def findLinear(self):
        """
        Returns a list of :class:`InverseEdgePoint`s in order.
        :return:
        """

        shoreContainers = list()
        self.exemptPoints = defaultdict(list)

        rounds = 0
        edge = list()
        two = list()

        # Find points with exactly one neighbor. These are edgepoints.
        # Subdivide these into two groups, edges and stubs.

        for point in (pt for pt in self.points):
            neighbors = [x for x in self.iterNeighborDiagonal(point)]
            if len(neighbors) == 1:
                if point.x in [self.analyzeData.max_x, 0] or\
                                point.y in [self.analyzeData.max_y, 0]:
                    edge.append(point)
            if len(neighbors) == 2:
                two.append(point)

        # order the points
        scanOrder = edge + two + self.points

        while True:
            rounds += 1
            for point in (pt for pt in scanOrder
                          if pt.y not in self.exemptPoints[pt.x]):
                neighbors = [x for x in self.iterNeighborDiagonal(point)]
                masterPoint = point

                if not len(neighbors):
                    shoreContainers.append(GridPointContainer([point]))
                    self.exemptPoints[point.x].append(point.y)
                    break

                firstPoint = neighbors[0]
                shoreContainers.append(GridPointContainer(
                    self.branchChaser(masterPoint,
                                      masterPoint,
                                      firstPoint)))
                break

            if not len([pt for pt in self.points if pt.y not in
                        self.exemptPoints[pt.x]]):
                return shoreContainers
            if rounds > 100:
                self.logger.info('Something broke in {}'.format(self))
                return shoreContainers

    def branchChaser(self, masterPoint, originalPoint, firstPoint):
        """
        Recursive function for chasing down inverse edge Branches
        :param masterPoint: Master point for this segment. This is
         passed all the way through.
        :param originalPoint: Original Point Branch under analysis.
        :param firstPoint: First point, this is a neighbor of the
         OriginalPoint and determines the direction of analysis travel.
        :return: ordered List of points.
        """

        lookbackPoint = originalPoint
        currentPoint = firstPoint

        orderedList = [originalPoint]

        while True:
            # First, we find all neighbors who are not the original point,
            # a lookback point, the master point, or an already analyzed point.

            neighbors = [pt for pt in self.iterNeighborDiagonal(currentPoint)
                         if pt not in [lookbackPoint,
                                       originalPoint,
                                       masterPoint]]
            neighbors = [pt for pt in neighbors
                         if pt.y not in self.exemptPoints[pt.x]]

            # More than one neighbor? We'll need to look back at the last
            # point and find how common neighbors we have.
            commonEdgeHash = defaultdict(list)
            if len(neighbors) > 1:
                for neighbor in neighbors:
                    commonEdgePoints =\
                        len(set(neighbor.edgePoints).
                            intersection(currentPoint.edgePoints))
                    commonEdgeHash[commonEdgePoints].append(neighbor)

                # Look for the neighbors with the most EdgePoints in common
                if len(commonEdgeHash[max(commonEdgeHash.keys())]) != 1:
                    level1CommonEdgeHash = defaultdict(list)
                    self.logger.debug("Highly unusual Branch "
                                               "Exception! on {}".format(self))
                    # a bunch of neighbors with no common EdgePoints? Lets
                    # look for common edges with the neighbors


                    # if max(commonEdgeHash.keys()) == 0:
                    #     for nei in commonEdgeHash[0]:
                    #         level1CommonEdgePoints = len(nei.edgePoints)
                    #         level1CommonEdgeHash[level1CommonEdgePoints].\
                    #             append(nei)
                    #
                    #     if len(level1CommonEdgeHash[max(
                    #             level1CommonEdgeHash.keys())]) != 1:
                    #         # Fucking hell, they're equal. Guess we'll just
                    #         # choose the first one anyways.
                    #         self.logger.debug("Highly unusual Branch "
                    #                           "Exception! on {}".format(self))
                    #         self.logger.debug(
                    #             "TroubleMakers {}".format(currentPoint))
                    #
                    orderedList += self.branchChaser(masterPoint,
                                                  currentPoint,
                                                  commonEdgeHash[max(
                                                  commonEdgeHash.keys())][0])
                    continue
                else:
                    # Follow the branch with the most common neighbors.
                    if currentPoint.y not in self.exemptPoints[currentPoint.x]:
                        self.exemptPoints[currentPoint.x].append(currentPoint.y)
                    orderedList += self.branchChaser(masterPoint,
                                                     currentPoint,
                                                     commonEdgeHash[max(
                                                       commonEdgeHash.keys())]
                                                          [0])
                    continue

            # Not exempt? Add to the ordered list.
            if currentPoint.y not in self.exemptPoints[currentPoint.x]:
                # Last modification in PR, delete this comment someday.
                self.exemptPoints[currentPoint.x].append(currentPoint.y)
                orderedList.append(currentPoint)

            if len(neighbors) == 0:
                # End of the line? return the ordered list.
                for point in orderedList:
                    self.exemptPoints[point.x].append(point.y)
                return orderedList

            # Just one neighbor? Okay, do this...
            lookbackPoint = currentPoint
            currentPoint = neighbors[0]

    def __repr__(self):
        return "<InverseEdgePointContainer>" \
               " {} Objects".format(len(self.points))

    def __iter__(self):
        for inverseEdgePoint in self.points:
            yield inverseEdgePoint

    __unicode__ = __str__ = __repr__
