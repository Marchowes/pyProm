"""
We need this utility to be seperate becasue of circular dependencies.
"""


def findExtremities(points):
    """
    :param points: list of GridPoint type objects
    :return: Dict of N,S,E,W extremities
    """
    N = S = E = W = list([points[0]])
    for point in points:
        if point.x < N[0].x:
            N = [point]
        elif point.x == N[0].x:
            N.append(point)
        if point.x > S[0].x:
            S = [point]
        elif point.x == S[0].x:
            S.append(point)
        if point.y > E[0].y:
            E = [point]
        elif point.y == E[0].y:
            E.append(point)
        if point.y < W[0].y:
            W = [point]
        elif point.y == W[0].y:
            W.append(point)
    return {'N': N, 'S': S, 'E': E, 'W': W}
