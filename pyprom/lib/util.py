from __future__ import division
import math

def dottedDecimaltoDegrees(coordinate):
    minute, second = divmod(coordinate*3600,60)
    degree, minute = divmod(minute, 60)
    return degree, minute, second

def degreesToDottedDecimal(deg, mnt=0, sec=0):
    """
    Accepts dms and converts to dd
    """
    return float("{0:.10f}".format(deg + (mnt / 60) + (sec / 3600)))

def longitudeArcSec(longitude):
    """
    Accepts longitude in dotted decimal notation, and returns 
    Arcsecond distance in meters.
    """
    return math.cos(math.radians(longitude))*30.87