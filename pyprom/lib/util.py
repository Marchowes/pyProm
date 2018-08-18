"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""
import random
import itertools
import string

from .locations.base_gridpoint import BaseGridPoint

def dottedDecimaltoDegrees(coordinate):
    """
    Converts dotted Decimal coordinate to a DMS
    :param coordinate:
    :return: degree, minute, second
    """
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
    :param coordianteHash: a hash using
    {x1:[y1:True,y2:True..],x1:[y1:True,y2:True..]} format
    :return: list coordinates [[x1,y1],[x1,y2]....]
    """
    return [[x, y] for x, _y in coordianteHash.items() for y, _ in _y.items()]


def coordinateHashToGridPointList(coordianteHash):
    """
    :param coordianteHash: a hash using
    {x1:[y1:True,y2:True..],x1:[y1:True,y2:True..]} format
    :return: list of BaseGridPoint objects.
    """
    return [BaseGridPoint(x, y)
            for x, _y in coordianteHash.items() for y, _ in _y.items()]


def compressRepetetiveChars(string):
    """
    Accepts String like "HHLHHHLL" and removes continuous redundant chars
    "HLHL"
    :param string:
    :return:
    """
    return ''.join(ch for ch, _ in itertools.groupby(string))


def seconds_to_arcseconds(seconds):
    """
    :param seconds:
    :return: converts seconds into arcseconds.
    """
    return seconds * 3600


def arcseconds_to_seconds(arcseconds):
    """
    :param arcseconds:
    :return: converts arcseconds into seconds.
    """
    return arcseconds / 3600

def randomString(length=12):
    """
    :param length: string length
    :return: string
    """
    return ''.join(random.choice(
        string.ascii_lowercase +
        string.ascii_uppercase +
        string.digits) for _ in range(length))