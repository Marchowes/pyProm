"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing Vertex_Links
used in Saddle highPerimeterNeighborhoods Tree Calculations.
"""

import sys


class Feature_Verticies:
    """
    Feature_Verticies object stores Feature_Verticies data.
    :class:`pyprom.lib.locations.vertex_link.Vertex_Link`
    connect a vertex from one feature to a vertex from another.
    This class stores a list of those.

    It's best to think of this as a polygon whose verticies are
    stored in `self.vertex_linkers[:].local` and those verticies
    are all all linked to foreign verticies
    """

    __slots__ = ['index', 'vertex_linkers']

    def __init__(self, index, vertex_linkers):
        """
        :param int index: index of feature
        :param list vertex_linkers: list of Vertex_Links
        :type vertex_linkers:
         list(:class:`pyprom.lib.locations.vertex_link.Vertex_Link`)
        """
        self.index = index
        self.vertex_linkers = vertex_linkers

    def shortest_link(self, ignored_link_index={}):
        """
        shortest_link returns the shortest link found in `self.vertex_linkers`
        but ignores any links connecting to a foreign index container in
        `ignored_link_index`

        :param ignored_link_index: index of links to ignore.
        :type ignored_link_index: {idx: bool}
        :return: vertex link
        :rtype: :class:`pyprom.lib.locations.vertex_link.Vertex_Link`
        """
        shortest_distance = sys.maxsize
        shortest = None
        for link in self.vertex_linkers:
            # ignoring this one? Move along.
            if ignored_link_index.get(link.remote_container.index, None):
                continue
            if link.distance < shortest_distance:
                shortest_distance = link.distance
                shortest = link
        return shortest

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<Feature_Verticies> {} ".format(
            self.vertex_linkers)

    __unicode__ = __str__ = __repr__
