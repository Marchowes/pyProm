"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""
import sys

from ..containers.base_self_iterable import BaseSelfIterable
from dijkstar import Graph, find_path
from scipy.spatial import KDTree
from math import hypot
import numpy as np


def high_perimeter_neighborhood_shortest_path(point, flat_area_points, highPerimeterNeighborhoods, datamap):
    """
    Finds the shortest path from point

    :param tuple point: (x, y, ele)
    :param list flat_area_points: list(tuple(x, y, ele))
    :param highPerimeterNeighborhoods: list(list(tuple(x, y, ele))) list of
     lists of high perimeter neighborhoods.
    :param datamap: Datamap to calculate distance.
    :return:
    """
    # needs to include perimeter in full path
    pts = flat_area_points

    for hs in highPerimeterNeighborhoods:
        pts.extend(hs)
    bsi = BaseSelfIterable(pointList=pts)

    neighborHash = {}

    for point in bsi.points:
        neighborHash[point] = [nei for nei in bsi.iterNeighborFull(point)]

    graph = Graph()
    for local, remotes in neighborHash.items():
        for remote in remotes:
            graph.add_edge(local, remote, datamap.distance(local, remote))

    shortest_length = None
    # todo: inefficient. Maybe we can do a breadth first algorithm which searches
    # todo: for the first encountered member of a destination set, rather than this clumsy dijkstra nonesense.
    for them in highPerimeterNeighborhoods:
        for them_hs in them:
            path = find_path(graph, point, them_hs)
            if shortest_length:
                if path.total_cost < shortest_length.total_cost:
                    shortest_length = path
            else:
                shortest_length = path
    closest = shortest_length.nodes[-1]
    return closest

def closest_points_between_sets_brute_force(us, them, datamap):
    """
    Returns closest points from two different sets of coordinates
    as well as their distance. Uses brute brute force method,
    best for smaller sets.

    :param us: list(tuple(x,y,ele))
    :param them: list(tuple(x,y,ele))
    :param datamap: Datamap to calculate distance.
    :return: closest from us, Closest from them, distance
    :rtype: Tuple(x,y,ele), Tuple(x,y,ele), float
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


def closest_point_by_distance_brute_force(us, them):
    """
    For all points in us, find the closest point in them.
    Uses brute force method, best for smaller sets.

    :param us: list(tuple(x,y,ele))
    :param them: list(tuple(x,y,ele))
    :return: {(x,y,ele): (x,y,ele)}
    """
    closest = dict()
    # Loop through all points in `us`
    for myPoint in us:
        closest_distance = sys.maxsize
        # Loop through all points in `them`
        for theirPoint in them:
            distance = hypot((myPoint[0] - theirPoint[0]), (myPoint[1] - theirPoint[1]))
            # if this is the shortest, set it as such.
            if distance < closest_distance:
                closest[myPoint] = theirPoint
                closest_distance = distance
    return closest

def closest_points_between_sets_kdtree(us, them, datamap):
    """
    Returns closest points from two different sets of coordinates
    as well as their distance. Uses brute KDTree method, best for larger sets.

    :param us: list(tuple(x,y,ele))
    :param them: list(tuple(x,y,ele))
    :param datamap: Datamap to calculate distance.
    :return: closest from us, Closest from them, distance
    :rtype: Tuple(x,y,ele), Tuple(x,y,ele), float
    """
    # Strip elevation
    us2d = [(x[0], x[1]) for x in us]
    them2d = [(x[0], x[1]) for x in them]
    kdtree = KDTree(us2d)
    dists = kdtree.query(them2d)
    idx = np.argmin(dists[0])
    theirs = them[idx]
    ours = us[dists[1][idx]]
    return ours, theirs, datamap.distance(ours, theirs)

def closest_point_by_distance_kdtree(us, them):
    """
    For all points in us, find the closest point in them.
    Uses KDTree method, best for larger sets.

    :param us: list(tuple(x,y,ele))
    :param them: list(tuple(x,y,ele))
    :return: {(x,y,ele): (x,y,ele)}
    """
    closest = dict()
    us2d = [(x[0], x[1]) for x in us]
    them2d = [(x[0], x[1]) for x in them]
    kdtree = KDTree(them2d)
    dists = kdtree.query(us2d)
    for idx in range(len(dists[0])):
        closest[us[idx]] = them[dists[1][idx]]
    return closest


def find_closest_points(us, them, datamap):
    """
    Returns closest points from two different sets of coordinates
    as well as their distance.
    Includes branch logic for dividing up work. Brute
    force is faster for smaller sets, KDTree is faster for larger.

    :param us: list(tuple(x,y,ele))
    :param them: list(tuple(x,y,ele))
    :param datamap: Datamap to calculate distance.
    :return: closest from us, Closest from them, distance
    :rtype: Tuple(x,y,ele), Tuple(x,y,ele), float
    """

    if len(us) + len(them) < 100:
        return closest_points_between_sets_brute_force(us, them, datamap)
    else:
        return closest_points_between_sets_kdtree(us, them, datamap)

def find_closest_point_by_distance_map(us, them):
    """
    For all points in us, find the closest point in them.

    Returns map of {us: them(closest)} for all members of us.

    Includes branch logic for dividing up work. Brute
    force is faster for smaller sets, KDTree is faster for larger.

    :param us: list(tuple(x,y,ele))
    :param them: list(tuple(x,y,ele))
    :return: {(x,y,ele): (x,y,ele)}
    """

    if len(us) + len(them) < 100:
        return closest_point_by_distance_brute_force(us, them)
    else:
        return closest_point_by_distance_kdtree(us, them)


