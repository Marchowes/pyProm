"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a location class for storing a Vertex_Link
used in Saddle highPerimeterNeighborhoods Tree Calculations.
"""


class Vertex_Link:
    """
    Vertex_Link connects a vertex
    :class:`pyprom.lib.locations.gridpoint.GridPoint` from one feature to
    a vertex from another. These are used in Internal Saddle Networks.
    """

    __slots__ = ['local', 'remote', 'distance', 'remote_container']

    def __init__(self, localPoint, remotePoint,
                 distance, remote_container=None):
        """
        :param localPoint: relative (local) GridPoint (vertex)
        :type localPoint: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :param remotePoint: relative (remote) GridPoint (vertex)
        :type remotePoint: :class:`pyprom.lib.locations.gridpoint.GridPoint`
        :param distance: distance between points.
        :type distance: int, float
        :param remote_container: Remote linked vertex container.
        :type remote_container:
         :class:`pyprom.lib.containers.feature_verticies.Feature_Verticies`
        """
        self.local = localPoint
        self.remote = remotePoint
        self.distance = distance
        self.remote_container = remote_container

    def _remote_container_idx(self):
        """
        :return: index of remove_container
        :rtype: int, "None"
        """
        if self.remote_container:
            return self.remote_container.index
        else:
            return "None"

    def __repr__(self):
        """
        :return: String representation of this object
        """
        return "<Vertex_Link> local {} remote {} " \
            "distance {} remote_container_idx {}".format(
                self.local,
                self.remote,
                self.distance,
                self._remote_container_idx())

    __unicode__ = __str__ = __repr__
