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

    :param float coordinate: dd coordinate to convert.
    :return: degrees, minutes, seconds
    :rtype: int, int, int
    """
    degrees = int(coordinate)
    md = abs(coordinate - degrees) * 60
    minutes = int(md)
    seconds = (md - minutes) * 60
    return (degrees, minutes, seconds)


def degreesToDottedDecimal(deg, mnt=0, sec=0):
    """
    Accepts dms and converts to dd

    :param int deg: degrees
    :param int mnt: minutes
    :param int sec: seconds
    :return: dotted decimal format
    :rtype: float
    """
    return float(round(deg + (mnt / 60) + (sec / 3600), 6))


def coordinateHashToList(coordianteHash):
    """
    Converts a coordinateHash to a list of coordinates.

    :param coordianteHash: a hash using
     {x1:[y1:True,y2:True..],x1:[y1:True,y2:True..]} format
    :return: list coordinates [[x1,y1],[x1,y2]....]
    """
    return [[x, y] for x, _y in coordianteHash.items() for y, _ in _y.items()]


def coordinateHashToGridPointList(coordinateHash):
    """
    Converts a coordinateHash to a
    :class:`pyprom.lib.locations.gridpoint.GridPoint` list.

    :param dict coordinateHash: a hash using
     {x1:[y1:True,y2:True..],x1:[y1:True,y2:True..]} format
    :return: list of BaseGridPoint objects.
    """
    return [BaseGridPoint(x, y)
            for x, _y in coordinateHash.items() for y, _ in _y.items()]


def coordinateHashToXYTupleList(coordinateHash):
    """
    Converts a coordinateHash to a list of tuples

    :param dict coordinateHash: a hash using
     {x1:[y1:True,y2:True..],x1:[y1:True,y2:True..]} format
    :return: list of (x,y) tuples.
    """
    return [(x, y) for x, _y in coordinateHash.items() for y, _ in _y.items()]


def compressRepetetiveChars(string):
    """
    Accepts String like "HHLHHHLL" and removes continuous redundant chars
    "HLHL"

    :param str string: "H" and "L" string
    :return: condensed non repeating string.
    """
    return ''.join(ch for ch, _ in itertools.groupby(string))


def seconds_to_arcseconds(seconds):
    """
    Convert Seconds to Arc Seconds

    :param float seconds:
    :return: converts seconds into arcseconds.
    """
    return seconds * 3600


def arcseconds_to_seconds(arcseconds):
    """
    Convert Arc Seconds to Seconds.

    :param arcseconds:
    :return: converts arcseconds into seconds.
    """
    return arcseconds / 3600


def randomString(length=12):
    """
    Creates Random string.

    :param int length: string length
    :return: random string of length characters.
    """
    return ''.join(random.choice(
        string.ascii_lowercase +
        string.ascii_uppercase +
        string.digits) for _ in range(length))
