Release History
---------------

0.3.7 (December 15, 2017)
+++++++++++++++++++++++++
* Optimizations for explored points 33 - 50% performance improvement

0.3.6 (December 10, 2017)
+++++++++++++++++++++++++
* Tore out old Dataloaders and replaced with a universal GDAL based solution
* Fixed the logger name.

0.3.5 (November 19, 2017)
+++++++++++++++++++++++++
* Added some unit tests
* Start of Divide tree objects
* Bug Fixes in Domains
* GZIP domain files
* Walks can disqualify invalid links, like links to single summits, and duplicate links which are not the highest.
* Fixed some imports.


0.3.0 (January 7, 2017)
+++++++++++++++++++++++
* Partial Walk Functionality
* Linker Objects
* JSON data improvements
* Domain Object as an easier entry point
* Saddle Analysis accuracy improvement
* Fixed Bug where X,Y to Lat/Long was rounding wrong
* Spot elevation objects can return UTM coordinates
* More clear names for X,Y to Lat/Long and vice versa

0.2.5 (January 1, 2017)
+++++++++++++++++++++++
* Complete rewrite of saddle analysis.
* 33% runtime improvement. 66% memory reduction.
* Overhauled Logic Process, Functions now more atomic
* Overhauled InverseEdgePoints
* Eliminated EdgePoints (keeping objects for later)
* Python 3 compatability
* Overhauled KML export for Python 3 compatability
* to_json to SpotElevation container
* Expunged old Pond/Island analysis in multipoints

0.2.1 (December 26, 2016)
+++++++++++++++++++++++++
* Radius Search for locations
* SpotElevationContainer filters all return new SpotElevationContainers
* Break Locations and container into their own files.
* Added BSD license.

0.2.0 (December 23, 2016)
+++++++++++++++++++++++++
* Fixed Edge Locator
* 100% accurate summit scan
* to_json for objects
* InverseEdgePoints used to calculate edge vectors
* iterator moved from analyze to datamap
* Saddles differentiate high/low edges (HighEdgeContainer)
* No longer return array types with numpy.
* Round comparisons
* Outside map bounds NoneType return supported
* Better roundings for internal types.

0.1.1 (November 3, 2016)
++++++++++++++++++++++++
* Improved EdgePoint collection
* Improved Shore tracing
* Added Edgepoints and InverseEdgePoints


0.1.0 (October 21, 2016)
++++++++++++++++++++++++
* Island/Pond Like Analysis
* Summit/Saddle Analysis
* Logging
* Documentation

0.0.2 (August 25, 2016)
+++++++++++++++++++++++
* Summit Analysis
* Common Base Features
* Location Types

0.0.1 (August 21, 2016)
+++++++++++++++++++++++
* Basic Setup Files


0.0.0 (August 2016)
+++++++++++++++++
* Initial Base Release
