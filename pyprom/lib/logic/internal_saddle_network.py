"""
pyProm: Copyright 2018

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains logic for calculating networks for links inside saddles.
This is a disposable object and is only intended for computation.
"""

import sys

from ..locations.gridpoint import GridPoint
from ..locations.vertex_link import Vertex_Link

from ..containers.feature_verticies import Feature_Verticies
from ..containers.gridpoint import GridPointContainer
from ..locations.saddle import Saddle
from .shortest_path_by_points import find_closest_points

from collections import defaultdict


class InternalSaddleNetwork(object):
    """
    InternalSaddleNetwork object for computing internal saddle networks.
    This is used for finding the center point of a saddle, and for
    breaking saddles with > 2 high edges into 2 high edge
    :class:`pyprom.lib.locations.saddle.Saddle`
    """

    def __init__(self, saddle, datamap):
        """
        :param saddle: saddle to build internal network for.
        :type saddle: :class:`pyprom.lib.locations.saddle.Saddle`
        :param datamap: datamap where this saddle resides.
        :type datamap: :class:`pyprom.lib.datamap.DataMap`
       """
        self.saddle = saddle
        self.datamap = datamap
        self.allVertexLinkers = []
        self.shortest_links = []

    def treeExploration(self, toBeExplored, toBeExploredIndex,
                        explored_nodes_index, first):
        """
        Loop until toBeExplored is exhausted. This continues until all
        conventionally accessible highPerimeterNeighborhoods are connected
        via Vertex Links.
        This loop works by looking at all `remote_container`s (a node)
        that are linked to the `node` under exploration. Whatever
        unexplored remote node has the node under exploration as it's
        shortest link is added to the toBeExplored queue and that
        :class:`pyprom.lib.locations.vertex_link.Vertex_Link`
        is added to the unordered `shortest_path` list.

        :param toBeExplored: list of Vertex Linkers to be explored
        :type toBeExplored:
         list(:class:`pyprom.lib.locations.vertex_link.Vertex_Link`)
        :param toBeExploredIndex: index of Vertex Linkers to be explored.
        :type toBeExploredIndex: dict(idx: bool)
        :param explored_nodes_index: index of explored Vertex Linkers..
        :type explored_nodes_index: dict(idx: bool)
        :param bool first: boolean value of if this is the first explored tree.
        """
        while toBeExplored:
            node = toBeExplored.pop(0)
            toBeExploredIndex[node.index] = False
            gotOne = False
            # Look at all the :class:``Vertex_link`s and find which remote
            # has this node as a shortest path.
            for link in node.vertex_linkers:
                # Already looked there, or already planning to? Skip.
                if explored_nodes_index.get(link.remote_container.index,
                                            None) or \
                        toBeExploredIndex.get(link.remote_container.index,
                                              None):
                    continue
                reverse_shortest = \
                    link.remote_container.shortest_link(
                        explored_nodes_index)
                # Does the shortest path from the remote lead back to
                # `node`? if so, add that Vertex_link to the
                # `shortest_links` list, and add that node
                # to the list of nodes to explore.
                if reverse_shortest and \
                        reverse_shortest.remote_container.index == node.index:
                    gotOne = True
                    toBeExplored.append(link.remote_container)
                    toBeExploredIndex[link.remote_container.index] = True
                    self.shortest_links.append(link)
            # if this is the first node explored, and this node isn't
            # the shortest link from any remotes, we'll use the shortest
            # link from this node instead.
            if not gotOne and first:
                shortest = node.shortest_link(explored_nodes_index)
                toBeExplored.append(shortest.remote_container)
                toBeExploredIndex[shortest.remote_container.index] = True
                self.shortest_links.append(shortest)
            explored_nodes_index[node.index] = True
            first = False
        return toBeExplored, toBeExploredIndex, explored_nodes_index, first

    def build_internal_tree(self):
        """
        This function builds an unordered list of links which connect all
        highPerimeterNeighborhoods (nodes) together. Stored in `self.shortest_links`
        """
        # Calculate all shortest paths.
        self.find_shortest_paths_between_high_perimeter_neighborhoods()
        # Index for keeping track of explored nodes.
        explored_nodes_index = dict()
        # Seed our toBeExplored list
        toBeExplored = [self.allVertexLinkers[0]]
        toBeExploredIndex = dict()
        first = True

        # The main loop for the tree building expression. Loop infinitely
        # until told to break. This is necessary to catch any nodes that
        # haven't been connected to the main tree.
        while True:
            toBeExplored, toBeExploredIndex, explored_nodes_index, first =\
                self.treeExploration(toBeExplored,
                                     toBeExploredIndex,
                                     explored_nodes_index,
                                     first)
            # if not every node is accounted for we need to analyze
            # those and add them to the tree.
            #
            # This is achieved by creating a :class:`GridPointContainer` of
            # all unexplored nodes and another :class:`GridPointContainer`
            # of all explored nodes, and find the shortest path between the
            # two sets. That `Vertex_Link` is then added to the list of
            # `shortest_links` and the node closest to the set of
            # explored node is seeded into `toBeExplored` and the entire
            # discovery loop is started again.
            if len(self.allVertexLinkers) > len(explored_nodes_index.items()):

                # Build out an index of unexplored nodes
                unexplored_nodes_index = dict()
                for node in self.allVertexLinkers:
                    if not explored_nodes_index.get(node.index, False):
                        unexplored_nodes_index[node.index] = True
                # build a list of unexplored nodes.
                unexplored_nodes = [x for x in self.allVertexLinkers
                                    if unexplored_nodes_index.get(x.index,
                                                                  False)]
                # tease out the shortest link between the unexplored nodes and
                # the explored nodes. Add that link to shortest_links and add
                # the node to `toBeExplored`
                shortest_distance = sys.maxsize
                shortest_link = None
                starting_point = None
                for node in unexplored_nodes:
                    shortest_distance_link =\
                        node.shortest_link(unexplored_nodes_index)
                    if shortest_distance_link.distance < shortest_distance:
                        shortest_distance = shortest_distance_link.distance
                        shortest_link = shortest_distance_link
                        starting_point = node
                self.shortest_links.append(shortest_link)
                toBeExplored.append(starting_point)
            # Everyone explored? GTFO.
            else:
                break

    def generate_child_saddles(self):
        """
        generate_child_saddles produces a list of saddles derived from
        saddle(`self`). This produces (N-1) saddles where N is the number
        of highPerimeterNeighborhoods in `self.saddles` These saddles. have their highPerimeterNeighborhoods
        consolidated as well as produce a centered mid point which is
        important for multipoint blobs, as well as multipoints with N > 2
        highPerimeterNeighborhoods.
        In the case of this Saddle having an EdgeEffect we need to preserve
        The original Saddle for its eventual joining with another datamap.
        In that case the new Saddles are marked as Children of the original
        saddle. And all Children mark the Original Saddle as their parent.
        The Parent Saddle is then disqualified from further analysis, but
        saved.

        :return: list of Saddles
        :rtype: list(:class:`pyprom.lib.locations.saddle.Saddle`)
        """
        # Gather all shortest links.
        self.build_internal_tree()
        saddles = []
        # For each Link, find the midpoint between the two points.
        # This will be the location of our Saddle. Convert this point to a
        # SpotElevation and create a Saddle Object using its lat/long/elev
        # set that saddle's highPerimeterNeighborhoods to GridPointContainers containing the
        # two points from the :class:`Vertex_Link`
        #
        # Finally if the saddle(`self`) has an edgeEffect, save it and mark
        # all new saddles as children and mark the parent on all new Saddles.
        for link in self.shortest_links:
            middlePoint = GridPoint(int(link.local[0] + link.remote[0]) / 2,
                                    int(link.local[1] + link.remote[1]) / 2,
                                    self.saddle.elevation)

            if self.saddle.multipoint:
                middleSpotElevation = \
                    self.saddle.multipoint.closestPoint(middlePoint,
                                                        asSpotElevation=True)
                newSaddle = Saddle(middleSpotElevation.latitude,
                                   middleSpotElevation.longitude,
                                   middleSpotElevation.elevation)
            else:
                newSaddle = Saddle(self.saddle.latitude,
                                   self.saddle.longitude,
                                   self.saddle.elevation)

            newSaddle.highPerimeterNeighborhoods = [[link.local],
                                                    [link.remote]]

            if self.saddle.edgeEffect:
                newSaddle.parent = self.saddle
                self.saddle.children.append(newSaddle)

            saddles.append(newSaddle)
        return saddles

    def find_shortest_paths_between_high_perimeter_neighborhoods(self):
        """
        find_shortest_paths_between_high_perimeter_neighborhoods iterates through all
        highPerimeterNeighborhoods of `self` and returns an ordered list of
        :class:`pyprom.lib.containers.feature_verticies.Feature_Verticies`
        which corresponds to the ordering of the
        highPerimeterNeighborhoods. These
        :class:`pyprom.lib.containers.feature_verticies.Feature_Verticies`
        contain :class:`pyprom.lib.locations.vertex_link.Vertex_Link`
        which link the shortest points between each highPerimeterNeighborhoods.

        :return: ordered list of Feature_Verticies
        :rtype:
         list(:class:`pyprom.lib.containers.feature_verticies.Feature_Verticies`)
        """
        # create X empty :class:`Feature_Verticies`
        for idx in range(len(self.saddle.highPerimeterNeighborhoods)):
            self.allVertexLinkers.append(Feature_Verticies(idx, []))
        nesteddict = lambda: defaultdict(nesteddict)
        # index holds the a tuple of (local closest, remote closest, distance)
        # indexed by [local][remote] in the hash.
        index = nesteddict()
        totalPerimeterNeighborhoods = len(self.saddle.highPerimeterNeighborhoods)
        # run through every index of every highPerimeterNeighborhood
        for outerIdx in range(totalPerimeterNeighborhoods - 1):
            for innerIdx in range(outerIdx + 1, totalPerimeterNeighborhoods):
                if index[outerIdx][innerIdx]:
                    continue
                # outer closest, inner closest, distance between
                outer, inner, distance = find_closest_points(self.saddle.highPerimeterNeighborhoods[innerIdx], self.saddle.highPerimeterNeighborhoods[outerIdx], self.datamap)

                # assign tuple to hash for local and remote so we don't
                # have to bother calculating twice.
                index[outerIdx][innerIdx] = (outer, inner, distance)
                index[innerIdx][outerIdx] = (inner, outer, distance)
        # fill in those :class:`Feature_Verticies` with the discovered links
        # stored in the index.
        for idx, data in index.items():
            for remoteNodeIdx, data in data.items():
                self.allVertexLinkers[idx].vertex_linkers.append(
                    Vertex_Link(data[0],
                                data[1],
                                data[2],
                                self.allVertexLinkers[remoteNodeIdx]))
