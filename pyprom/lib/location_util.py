"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

We need this utility to be seperate becasue of circular dependencies.
"""
import math


def longitudeArcSec(longitude):
    """
    Accepts longitude in dotted decimal notation, and returns
    Arcsecond distance in meters.
    """
    return math.cos(math.radians(longitude))*30.87
