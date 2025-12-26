"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""
from enum import Enum

DOMAIN_EXTENSION = ".dom"

# Unit Conversion Constants

METERS_PER_FOOT = 0.3048
METERS_PER_SURVEY_FOOT = 0.3048006096

FEET_PER_METER = 1/METERS_PER_FOOT
SURVEY_FEET_PER_METER = 1/METERS_PER_FOOT

FEET_PER_MILE = 5280

# PyProm Units

class Units(str, Enum):
    FEET = "FEET"
    METERS = "METERS"
    UNKNOWN = "UNKNOWN"

class Confidence(str, Enum):
    HIGH = 2
    MEDIUM = 1
    LOW = 0

# GDAL Unit Names
GDAL_METERS = ("m", "meter", "metre", "meters", "metres")
GDAL_FEET = ("ft", "feet", "foot", "us_survey_foot", "us-ft", "us survey foot", "US survey foot")

