"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for storing Saddle data.
"""

import math
from collections import defaultdict
from dijkstar import Graph, find_path
from .spot_elevation import SpotElevation
from .base_gridpoint import BaseGridPoint
from ..containers.multipoint import MultiPoint
from ..containers.gridpoint import GridPointContainer
from ..containers.linker import isLinker
from ..containers.base_self_iterable import BaseSelfIterable
from ..util import randomString


class Saddle(SpotElevation):
    """
    | Saddle object stores relevant saddle data.
    | A Saddle is by definition a point, or set of equal height points
    | (MultiPoint) which have at least 2 non contiguous sets of points
    | around the Perimeter that are higher than the point or Multipoint.
    | These are called "High Shores". A Saddle is a Child object of
    | :class:`pyprom.lib.locations.spot_elevation.SpotElevation`
    |
    | Examples:
    |
    | Single Point Saddle:
    |     ``v------high shore``
    | ``[0][2][0]``
    | ``[0][1][0]   [1] = Saddle``
    | ``[0][3][0]``
    |     ``^------high shore``
    |
    | MultiPoint Saddle:
    |     ``v--------high shore``
    | ``[0][2][0][0]``
    | ``[0][1][1][0]  [1][1] = Saddle``
    | ``[0][3][0][0]``
    |     ``^-----high shore``
    |
    """

    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        """
        :param latitude: latitude in dotted decimal
        :type latitude: int, float
        :param longitude: longitude in dotted decimal
        :type longitude: int, float
        :param elevation: elevation in meters
        :type elevation: int, float
        :param multiPoint: MultiPoint object
        :type multiPoint: :class:`pyprom.lib.containers.multipoint.MultiPoint`,
         None
        :param highShores: list of GridPointContainers representing a highShore
        :type highShores:
         list(:class:`pyprom.lib.containers.gridPoint.GridPointContainer`)
        :param bool edge: Does this :class:`Saddle` have an edge
         Effect?
        :param str id: kwarg for id
        :param list children: list of child Saddles. These are :class:`Saddle`
         derived from this :class:`Saddle`
        :param parent: Parent saddle These are :class:`Saddle`
         which from this :class:`Saddle` is derived.
        :param bool singleSummit: kwarg for Saddles disqualified for being
         linked to a Single Summit.
        :param bool basinSaddle: kwarg for Saddles disqualified for being
         a Basin Saddle.
        :param list basinSaddleAlternatives: kwarg for Saddles which are
         basin saddles of equivalent height
         :type basinSaddleAlternatives: list(:class:`Saddle`)
        :param bool disqualified: kwarg for a generic disqualified Saddle.
        """
        super(Saddle, self).__init__(latitude, longitude,
                                     elevation, *args, **kwargs)
        self.multiPoint = kwargs.get('multiPoint', [])
        self.highShores = kwargs.get('highShores', [])
        self.id = kwargs.get('id', 'sa:' + randomString())
        # List of linkers to summits
        self.summits = []
        # If this is set, this saddle has spun out another
        # Saddle with less data. (for instance, if its an edge effect)
        self.parent = kwargs.get('parent', None)  # Parent
        # Saddles that have been spawned off of this one.
        self.children = kwargs.get('children', [])
        # All Edges lead to One summit.
        self.singleSummit = kwargs.get('singleSummit', False)
        # redundant saddle, but too low.
        self.basinSaddle = kwargs.get('basinSaddle', False)
        # alternative basin saddles
        self.basinSaddleAlternatives = \
            kwargs.get('basinSaddleAlternatives', [])
        # Non specific disqualification
        self._disqualified = kwargs.get('disqualified', None)
        self.lprBoundary = []

    def addSummitLinker(self, linker):
        """
        Add a :class:`pyprom.lib.containers.linker.Linker` to this Saddle.
        This in effect links a :class:`pyprom.lib.locations.summit.Summit`
        to this Saddle.

        :param linker: linker to add.
        :type linker: :class:`pyprom.lib.containers.linker.Linker`
        """
        isLinker(linker)
        self.summits.append(linker)

    def feature_neighbors(self):
        """
        :return: returns all linked Summits.
         This is, in effect, an interface.
        :rtype: list(:class:`pyprom.lib.locations.summit.Summit`)
        """
        return [feature.summit for feature in self.summits]

    @property
    def domains(self):
        """
        :return: list of SummitDomains associated with this Saddle
        """
        return [l.summit.domain for l in self.summits if l.summit.domain]


    @property
    def neighbors(self, filterDisqualified=True):
        """
        neighbors will return all neighboring saddles by way of the
        connected summit.
        This function will filter out redundant neighbors.

        :param bool filterDisqualified: Filter out disqualified linkers.
        :return: list of unique neighboring saddles by way of
         neighboring summits excluding self.
        :rtype: list(:class:`Saddle`)
        """
        neighborSet = set(self.all_neighbors(filterDisqualified))
        neighborSet.discard(self)
        return list(neighborSet)

    def all_neighbors(self, filterDisqualified=True):
        """
        all_neighbors will return all neighboring saddles by way of the
        connected summit.
        This function deliberately makes no effort to filter out redundant
        neighbors.

        :param bool filterDisqualified: Filter out disqualified linkers.
        :return: list of neighboring saddles by way of neighboring summits.
        :rtype: list(:class:`Saddle`)
        """
        neighbors = []
        if filterDisqualified:
            [neighbors.extend(linker.saddles_connected_via_summit())
                for linker in self.summits if not linker.disqualified]
        else:
            [neighbors.extend(linker.saddles_connected_via_summit(
                skipDisqualified=False))
                for linker in self.summits]
        return neighbors

    def high_shore_shortest_path(self, datamap):
        """
        Finds the two closest opposing high shore points.
        This follows a path inside the saddle.
        Also returns the midpoint.

        :param datamap: Datamap required for distance calculations.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: HS1, HS2, Midpoint
        """
        bsi = BaseSelfIterable()
        bsi.points = []
        if self.multiPoint:
            bsi.points.extend(self.multiPoint.points)
        else:
            gp = self.toGridPoint(datamap)
            bsi.points.append((gp.x, gp.y))

        for hs in self.highShores:
            bsi.points.extend(hs)

        bsi.pointIndex = defaultdict(dict)
        for point in bsi.points:
            bsi.pointIndex[point[0]][point[1]] = point

        neighborHash = {}

        for point in bsi.points:
            neighborHash[point] = [nei for nei in bsi.iterNeighborDiagonal(point)]

        graph = Graph()
        for local, remotes in neighborHash.items():
            for remote in remotes:
                graph.add_edge(local, remote, datamap.distance(local, remote))
        all_shortest = []
        for us_hs in self.highShores[0]:
            shortest_length = None
            for them_hs in self.highShores[1]:
                path = find_path(graph, us_hs, them_hs)
                if shortest_length:
                    if path.total_cost < shortest_length.total_cost:
                        shortest_length = path
                else:
                    shortest_length = path
            all_shortest.append(shortest_length)

        overall_shortest = None
        for link in all_shortest:
            if overall_shortest:
                if link.total_cost < overall_shortest.total_cost:
                    overall_shortest = link
            else:
                overall_shortest = path

        return overall_shortest.nodes[0], overall_shortest.nodes[-1],\
               overall_shortest.nodes[math.floor(len(overall_shortest.nodes)/2)]

    @property
    def summits_set(self):
        """
        :return: set of linked Summits
        :rtype: set(:class:`pyprom.lib.locations.summit.Summit`)
        """
        return set([x.summit for x in self.summits])

    @property
    def disqualified(self):
        """
        :return: if any values that indicate disqualification are set,
         return True.
        :rtype: bool
        """
        # Allow for a manual override from user.
        if self._disqualified in [True, False]:
            return self._disqualified
        else:
            return self.singleSummit | self.basinSaddle

    @disqualified.setter
    def disqualified(self, value):
        """
        :param bool value: Override Saddle disqualification
        """
        self._disqualified = value

    def disqualify_self_and_linkers(self, basinSaddle=False,
                                    singleSummit=False):
        """
        Disqualify this :class:`Saddle` and linked
        :class:`pyprom.lib.containers.linker.Linker` s

        :param bool basinSaddle: set basinSaddle
        :param bool singleSummit: set singleSummit
        """
        if basinSaddle:
            self.basinSaddle = basinSaddle
        if singleSummit:
            self.singleSummit = singleSummit
        if not (basinSaddle | singleSummit):
            self._disqualified = True
        for linker in self.summits:
            linker.disqualified = True

    def emancipate(self):
        """
        Emancipate disassociates this saddle from its parent :class:`Saddle`
        """
        if self.parent:
            self.parent.children = \
                [x for x in self.parent.children if x != self]
            self.parent = None

    def disown_children(self):
        """
        disown_children disassociates this saddle from all child
         :class:`Saddle`
        """
        for child in self.children:
            child.emancipate()
        self.children = []

    def soft_delete(self):
        """
        Soft deletes this Saddle, that is, disassociates itself
        from other saddle attributes
        """
        if self.children:
            self.disown_children()
        if self.parent:
            self.emancipate()
        if self.basinSaddleAlternatives:
            for bsa in self.basinSaddleAlternatives:
                bsa.basinSaddleAlternatives =\
                    [x for x in bsa.basinSaddleAlternatives if x != self]
        self.basinSaddleAlternatives = []
        self.disqualify_self_and_linkers()

    def to_dict(self, referenceById=True):
        """
        Create the dictionary representation of this object.

        :param bool referenceById: reference Summits by ID.
        :return: dict() representation of :class:`Saddle`
        :rtype: dict()
        """
        to_dict = {'lat': self.latitude,
                   'lon': self.longitude,
                   'ele': self.elevation,
                   'edge': self.edgeEffect,
                   'edgepoints': self.edgePoints,
                   'id': self.id}
        if self.singleSummit:
            to_dict['singleSummit'] = self.singleSummit
        if self.basinSaddle:
            to_dict['basinSaddle'] = self.basinSaddle
        if self._disqualified:
            to_dict['disqualified'] = self._disqualified
        if self.multiPoint:
            to_dict['multipoint'] = self.multiPoint.to_dict()
        if self.highShores:
            to_dict['highShores'] = self.highShores
        # These values are not unloaded by from_dict()
        if referenceById:
            to_dict['children'] =\
                [x.id for x in self.children]  # saddles by ID
            to_dict['summits'] =\
                [x.id for x in self.summits]  # linker by ID
            if self.parent:
                to_dict['parent'] = self.parent.id
            if self.basinSaddleAlternatives:
                to_dict['basinSaddleAlternatives'] =\
                    [x.id for x in self.basinSaddleAlternatives] # saddle id
        return to_dict

    @classmethod
    def from_dict(cls, saddleDict, datamap=None):
        """
        Create this object from dictionary representation

        :param dict saddleDict: dict representation of this object.
        :param datamap: Datamap to build this object from.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
        :return: a new Saddle object.
        :rtype: :class:`Saddle`
        """
        ###########
        # The following attributes cannot be loaded here becasue they require
        # reference IDs which can only be provided at the container level:
        #
        # parent
        # children
        # basinSaddleAlternatives
        ###########

        lat = saddleDict['lat']
        long = saddleDict['lon']
        elevation = saddleDict['ele']
        edge = saddleDict['edge']
        edgePoints = [tuple(pt) for pt in saddleDict['edgepoints']]
        id = saddleDict['id']
        singleSummit = saddleDict.get('singleSummit', False)
        basinSaddle = saddleDict.get('basinSaddle', False)
        disqualified = saddleDict.get('disqualified', None)

        multipoint = saddleDict.get('multipoint', [])
        if multipoint:
            multipoint = MultiPoint.from_dict(multipoint, datamap=datamap)
        highshores = []
        incoming_hs = saddleDict.get('highShores', [])
        if incoming_hs:
            for hss in incoming_hs:
                hsx = []
                for hs in hss:
                    hsx.append(tuple(hs))
                highshores.append(hsx)

        return cls(lat, long, elevation,
                   multiPoint=multipoint,
                   highShores=highshores,
                   edge=edge,
                   edgePoints=edgePoints,
                   id=id,
                   singleSummit=singleSummit,
                   basinSaddle=basinSaddle,
                   disqualified=disqualified)

    def __hash__(self):
        """
        hash takes into account the lat, long, and elevation of the saddle
        As well as a hash of all the highShores. This is a costly calculation
        and should probably be avoided if possible.

        :return: Hash representation of this object
        :rtype: str
        """
        masterHash = super(SpotElevation, self).__hash__()
        pointsTuple = tuple(self.highShores)
        return hash((masterHash, hash(pointsTuple)))

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<Saddle> lat {} long {} {}ft {}m MultiPoint {}".format(
            self.latitude,
            self.longitude,
            self.feet,
            self.elevation,
            bool(self.multiPoint))

    __unicode__ = __str__ = __repr__


def isSaddle(saddle):
    """
    Check if passed in object is a :class:`Saddle`

    :param saddle: object under scrutiny
    :raises: TypeError if other not of :class:`Saddle`
    """
    if not isinstance(saddle, Saddle):
        raise TypeError("Expected Saddle Object.")
