"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""


DOMAIN_EXTENSION = ".dom"

# Unit Conversion Constants

METERS_PER_FOOT = 0.3048
METERS_PER_SURVEY_FOOT = 0.3048006096

FEET_PER_METER = 1/METERS_PER_FOOT
SURVEY_FEET_PER_METER = 1/METERS_PER_FOOT

FEET_PER_MILE = 5280

GDAL_METERS = ('m', 'metre', 'meter',)
GDAL_FEET = ('ft', 'foot', 'feet',)
GDAL_SURVEY_FOOT = ('us survey foot', 'US survey foot', 'us-ft',)