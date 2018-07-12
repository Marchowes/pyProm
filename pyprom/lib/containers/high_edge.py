"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a container class for storing EdgePoint
type location objects.
"""


class HighEdgeContainer(object):
    """
    Container for High Edge Lists -- Specifically for the purpose of storing
     high edge sections around Saddles.

    The object takes a gridPoint container which represents all Perimeter
    points around a point. And breaks it down into distinct highEdge regions.

    :param shore: :class:`GridPointCointer`
    :param blobElevation: elevation (m) of blob.
    """
    def __init__(self, shore, blobElevation):
        # list of list of high edges.
        self._highPoints = list()
        highEdgePoints = list()
        first = True
        firstPoint = shore.points[0]
        for shorePoint in shore.points:
            if shorePoint.elevation > blobElevation:
                highEdgePoints.append(shorePoint)
                self.summitLike = False
            elif shorePoint.elevation < blobElevation:
                if first:
                    first = False
                if highEdgePoints:
                    self._highPoints.append(highEdgePoints)
                    highEdgePoints = list()
            # If its elevation = None (map edge) and we're
            # on a string of highs...
            if not shorePoint.elevation and highEdgePoints:
                highEdgePoints.append(shorePoint)
        if first:
            if highEdgePoints:
                self._highPoints.append(highEdgePoints)
            return
        else:
            # Do we have a queue of highpoints and was the first one
            # also high? but we're not on the initial high string?
            # then we need to string them together.
            if highEdgePoints\
                    and firstPoint.elevation > blobElevation\
                    and not first:
                self._highPoints[0] = \
                     highEdgePoints + self._highPoints[0]
            elif highEdgePoints:
                self._highPoints.append(highEdgePoints)

    @property
    def highPoints(self):
        return self._highPoints

    def __repr__(self):
        return "<HighEdgeContainer> {} Lists".format(len(self.highPoints))

    __unicode__ = __str__ = __repr__
