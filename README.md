### pyProm v0.5.3

![pyProm](https://github.com/marchowes/pyProm/raw/master/images/pyProm-logo-500px.png "pyProm")

This library is still under development. Do not expect full functionality, or documentation until release 1.0.0

**Warning** There will be breaking changes to how domains are exported starting in 0.5.3

pyProm
======

Supported version of Python: Python 3

The purpose of PyProm is to have a fully scriptable API for loading Raster Data for discovery of Summits,
Saddles (cols), Prominence, Peak Parentage and all that good stuff. Anything you might want to be able to
manipulate can be manipulated in a scalable, scriptable manner. 

pyProm is written in Python, which is a fairly accessible language to most people. My master plan is once 
a stable, and well documented version can be produced, others can add features as they see fit. The
disadvantage of writing such a deeply customizable library in python is it is inherently slower and
consumes more memory (apalling so in some instances).

This library is inspired by [WinProm](https://github.com/edwardearl/winprom), by the late [Edward Earl](http://peakbagger.com/climber/climber.aspx?cid=601), as well as the number of websites
which make use of similiarly derived data, such as [LoJ](listsofjohn.com) and [peakbagger](peakbagger.com)

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
from dataexport import KMLfileWriter
import logging
logging.basicConfig(level=logging.DEBUG)

# Load your Datamap into your Domain
data = GDALLoader('YOURPATHHERE/N44W072.hgt')
domain = Domain(data)
domain.run()
# ^This will run the Saddle/Summit discovery, it'll take a while..

# Find all summits above 4000 feet
_4ks = domain.summits.elevationRange(4000)

# Write your fancy list of 4ks to a KML file
mykml = KMLfileWriter(_4ks, 'YOURPATHHERE/myfile.kml')
mykml.writeFile()

# Save your Domain
domain.write('YOURPATHHERE/mydomain.dom')

# Load your Domain you you don't need to wait forever for analysis.
newdomain = Domain(data)
newdomain.read('YOURPATHHERE/mydomain.dom')
```

Installation
------------
Warning! JSON data or saved Domains will almost certainly fail to load in future version. There WILL be breaking changes. You've been warned! (twice!)


Download zip from github, or clone.
Go to extraction directory and run `pip install -e .`
This will work with Python 3.4+

Trouble Getting GDAL installed?
-------------------------------
The GDAL (Geo Data Abstration Layer) package for Python is a thin wrapper over a much larger binary package.

This produces a number of installation problems that can't always be easily dealt with with package managers
and thus may need manual intervention.

[First try this](http://www.sarasafavi.com/installing-gdalogr-on-ubuntu.html)
Gdal still giving you trouble? [Try this](http://gis.stackexchange.com/questions/9553/installing-gdal-and-ogr-for-pythonround)
More resources:
* https://pypi.python.org/pypi/GDAL/
* https://github.com/OSGeo/gdal
* http://www.gdal.org/formats_list.html

If all else fails, I've had good luck getting it to work with conda. You're on your own with that one.



