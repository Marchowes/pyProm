### pyProm v0.0.2


This library is still under development. Do not expect full functionality, or documentation until release 1.0.0

pyProm
======

The purpose of PyProm is to load Surface datasets for discovery of Summit, Saddles (cols),
Prominence, and data manipulation/parsing of those datapoints. The goal is the take in a number of
different data formats, as well as produce a number of different result formats, including common
ones like KML.

pyProm is written in Python, which is a fairly accessible language to most people. My hope is once 
a stable, and well documented version can be produced, others can add features as they see fit.

This library is inspired by [WinProm](https://github.com/edwardearl/winprom), by the late [Edward Earl](http://peakbagger.com/climber/climber.aspx?cid=601), as well as the number of websites
which make use of similiarly derived data, such as [LoJ](listsofjohn.com) and [peakbagger](peakbagger.com)

More About Prominence and Surface Network Analysis
--------------------------------------------------

* [http://www.surgent.net/highpoints/prominence.html](http://www.surgent.net/highpoints/prominence.html)
* [http://www.peaklist.org/theory/theory.html](http://www.peaklist.org/theory/theory.html)
* [https://en.m.wikipedia.org/wiki/Topographic_prominence](https://en.m.wikipedia.org/wiki/Topographic_prominence#Wet_prominence_and_dry_prominence)

Datasources
-----------
* 1 ArcSecond SRTM Data [#1](https://dds.cr.usgs.gov/srtm/version1/United_States_1arcsec/1arcsec/) [#2](https://dds.cr.usgs.gov/srtm/version2_1/SRTM1/)
* [DEM type data] (http://viewer.nationalmap.gov/basic/#productGroupSearch) Start with Elevation Products (3DEP) - 1/3 arc-second DEM [More info](http://www.digitalpreservation.gov/formats/fdd/fdd000281.shtml)

Installation
------------
Why?? Why are you installing this??? It's nowhere near done.

Download zip from github, or clone.
Go to extraction directory and run `*pip install -e .`


Trouble Getting GDAL installed?
-------------------------------
The GDAL (Geo Data Abstration Layer) package for Python is a thin wrapper over a much larger binary package.

This produces a number of installation problems that can't always be easily dealt with with package managers
and thus may need manual intervention.

[First try this](http://www.sarasafavi.com/installing-gdalogr-on-ubuntu.html)
Gdal still giving you trouble? [Try this](http://gis.stackexchange.com/questions/9553/installing-gdal-and-ogr-for-pythonround)
More resources:
https://pypi.python.org/pypi/GDAL/
https://github.com/OSGeo/gdal
http://www.gdal.org/formats_list.html



