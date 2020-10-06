### pyProm

![pyProm](https://github.com/marchowes/pyProm/raw/master/images/pyProm-logo-500px.png "pyProm")

This library is still under development. Do not expect full functionality, or documentation until release 1.0.0

**Warning** There will be breaking changes to how DomainMaps are exported starting in 0.5.4. As this is an alpha
the concept of saving DomainMaps should never be considered stable.

pyProm
======

Supported version of Python: Python 3.8+

The purpose of PyProm is to have a fully scriptable API for loading Raster Data for discovery of Summits,
Saddles (cols), Prominence, Peak Parentage and all that good stuff. Anything you might want to be able to
manipulate can be manipulated in a scalable, scriptable manner. 

pyProm is written in Python, which is a fairly accessible language to most people. My master plan is once 
a stable, and well documented version can be produced, others can add features as they see fit. The
disadvantage of writing such a deeply customizable library in python is it is inherently slower and
consumes more memory (appalling so in some instances).

This library is inspired by [WinProm](https://github.com/edwardearl/winprom), by the late [Edward Earl](http://peakbagger.com/climber/climber.aspx?cid=601), as well as the number of websites
which make use of similiarly derived data, such as [LoJ](listsofjohn.com) and [peakbagger](peakbagger.com)

Read The Docs
--------------
Fancy pyProm Documentation derived from docstrings can be found on [readthedocs.io](http://pyprom.readthedocs.io)


More About Prominence and Surface Network Analysis
--------------------------------------------------

* [http://www.surgent.net/highpoints/prominence.html](http://www.surgent.net/highpoints/prominence.html)
* [http://www.peaklist.org/theory/theory.html](http://www.peaklist.org/theory/theory.html)
* [https://en.m.wikipedia.org/wiki/Topographic_prominence](https://en.m.wikipedia.org/wiki/Topographic_prominence#Wet_prominence_and_dry_prominence)

Datasources
-----------
* 1 ArcSecond SRTM Data [#1](https://dds.cr.usgs.gov/srtm/version1/United_States_1arcsec/1arcsec/), [#2](https://dds.cr.usgs.gov/srtm/version2_1/SRTM1/)
* [DEM type data] (http://viewer.nationalmap.gov/basic/#productGroupSearch) Start with Elevation Products (3DEP) - 1/3 arc-second DEM [More info](http://www.digitalpreservation.gov/formats/fdd/fdd000281.shtml)

Example(s)
----------
* Install pyProm
* [Download This](https://dds.cr.usgs.gov/srtm/version2_1/SRTM1/Region_06/N44W072.hgt.zip)
* Extract the zip file
In your favorite Python interpreter on a Unix system (I use `ipython` in `Linux`):

```
from dataload import GDALLoader
from domain import Domain
from lib.kmlwriter import KMLFileWriter
import logging
logging.basicConfig(level=logging.DEBUG)

# Load your Datamap into your Domain
data = GDALLoader('YOURPATHHERE/N44W072.hgt')
domainmap = DomainMap(data)
domainmap.run()
# ^ This will run the Saddle/RunOff/Summit discovery as well as saddle walk and saddle disqualifiers, it'll take a while..

# Find all summits above 4000 feet
_4ks = domainmap.summits.elevationRange(4000)

# Write your fancy list of 4ks to a KML file
mykml = KMLfileWriter('YOURPATHHERE/myfile.kml', features=_4ks')
mykml.writeFile()

# Save your Domain
domainmap.write('YOURPATHHERE/mydomain.dom')

# Load your DomainMap you you don't need to wait forever for analysis.
newDomain = DomainMap.read('YOURPATHHERE/mydomain.dom', data.datamap)
```

Installation
------------
Warning! Cbor data or saved Domains will almost certainly fail to load in future version. There WILL be breaking changes. You've been warned! (twice!)


Download zip from github, or clone.
Go to extraction directory and run `pip install -e .`
This will work with Python 3.4+

Trouble Getting GDAL installed?
-------------------------------
The GDAL (Geo Data Abstration Layer) package for Python must match the version of gdal installed on your system.

`gdalinfo --version`

You may have to manually install the proper version with pip3.
..or use conda..

Most common fix here:
https://gis.stackexchange.com/questions/28966/python-gdal-package-missing-header-file-when-installing-via-pip

Running Unit Tests
------------------
Unit tests can be run in two ways:

Your own local env:
`make test`

Inside a docker container:
`make test-docker`

Docker tests requires you to have docker installed on your system, and may require privilege escalation.
The advantage of running tests in docker is for dependency consistency.

Running pyprom inside Docker
----------------------------
As of 0.5.7 you can run pyprom inside a Docker container!

`make pyprom-docker`

Will put you inside an ipython instance.


