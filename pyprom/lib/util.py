from __future__ import division
from locations import BaseGridPoint
import itertools
import math


def dottedDecimaltoDegrees(coordinate):
    minute, second = divmod(coordinate * 3600, 60)
    degree, minute = divmod(minute, 60)
    return degree, minute, second


def degreesToDottedDecimal(deg, mnt=0, sec=0):
    """
    Accepts dms and converts to dd
    """
    return float(round(deg + (mnt / 60) + (sec / 3600), 6))


def coordinateHashToList(coordianteHash):
    """
    :param coordianteHash: a hash using {x1:[y1,y2..],x1:[y1,y2..]} format
    :return: list coordinates [[x1,y1],[x1,y2]....]
    """
    return [[x, y] for x, _y in coordianteHash.items() for y in _y]


def coordinateHashToGridPointList(coordianteHash):
    """
    :param coordianteHash: a hash using {x1:[y1,y2..],x1:[y1,y2..]} format
    :return: list of BaseGridPoint objects.
    """
    return [BaseGridPoint(x, y)
            for x, _y in coordianteHash.items() for y in _y]


def compressRepetetiveChars(string):
    """
    Accepts String like "HHLHHHLL" and removes continuous redundant chars
    "HLHL"
    :param string:
    :return:
    """
    return ''.join(ch for ch, _ in itertools.groupby(string))
