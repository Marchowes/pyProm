from __future__ import division

def dottedDecimaltoDegrees(coordinate):
    minute, second = divmod(coordinate*3600,60)
    degree, minute = divmod(minute, 60)
    return degree, minute, second

def degreesToDottedDecimal(deg, mnt, sec):
    return float("%.5f" % (deg + (mnt / 60) + (sec / 3600)))