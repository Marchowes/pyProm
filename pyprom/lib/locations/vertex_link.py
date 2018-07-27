"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a location class for storing a Vertex_Link
used in Saddle highShores Tree Calculations.
"""


class Vertex_Link(object):
    """
    Vertex_Link connects a vertex (:class`GridPoint`) from one feature to
    a vertex from another
    """

    def __init__(self, localPoint, remotePoint,
                 distance, remote_container=None):
        """
        :param localPoint: relative (local) GridPoint (vertex)
        :param remotePoint: relative (remote) GridPoint (vertex)
        :param distance: distance between points.
        :param remote_container: :class:`Feature_Verticies`
        """
        self.local = localPoint
        self.remote = remotePoint
        self.distance = distance
        self.remote_container = remote_container

    def _remote_container_idx(self):
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
