"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""


DOMAIN_EXTENSION = ".dom"

# Unit Conversion Constants

METERS_TO_FEET = 0.3048
METERS_TO_SURVEY_FOOT = 0.3048006096

FEET_TO_METERS = 1/METERS_TO_FEET
SURVEY_FOOT_TO_METERS = 1/METERS_TO_FEET

FEET_IN_MILES = 5280

GDAL_METERS = ('m', 'metre', 'meter',)
GDAL_FEET = ('ft', 'foot', 'feet',)
GDAL_SURVEY_FOOT = ('us survey foot', 'US survey foot', 'us-ft',)