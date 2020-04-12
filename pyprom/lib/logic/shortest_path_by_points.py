"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""
import sys

from _collections import defaultdict
from ..containers.base_self_iterable import BaseSelfIterable
from dijkstar import Graph, find_path


def high_shore_shortest_path(point, flat_area_points, highShores, datamap):
    # needs to include perimeter in full path
    bsi = BaseSelfIterable()
    bsi.points = flat_area_points

    for hs in highShores:
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

    shortest_length = None
    for them in highShores:
        for them_hs in them:
            path = find_path(graph, point, them_hs)
            if shortest_length:
                if path.total_cost < shortest_length.total_cost:
                    shortest_length = path
            else:
                shortest_length = path
    closest = shortest_length.nodes[-1]
    return closest



def findClosestPoints(us, them, datamap):
    """
    """
    myClosest = None
    theirClosest = None
    closest_distance = sys.maxsize
    # Loop through all points in `us`
    for myPoint in us:
        # Loop through all points in `them`
        for theirPoint in them:
            distance = datamap.distance(myPoint, theirPoint)
            # if this is the shortest, set it as such.
            if distance < closest_distance:
                myClosest = myPoint
                theirClosest = theirPoint
                closest_distance = distance
    return myClosest, theirClosest, closest_distance


def findClosestPointsByDistance(us, them, datamap):
    """
    """
    closest = dict()
    # Loop through all points in `us`
    for myPoint in us:
        closest_distance = sys.maxsize
        # Loop through all points in `them`
        for theirPoint in them:
            distance = datamap.distance(myPoint, theirPoint)
            # if this is the shortest, set it as such.
            if distance < closest_distance:
                closest[myPoint] = theirPoint
                closest_distance = distance
    return closest

