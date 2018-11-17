Release History

0.6.0 (????)
++++++++++++
* More robustness in KMLWriter
* New features for BaseGridPoints, namely index() which returns the index at which that BaseGridpoint exists in the container, and distance() which calculates the distance (in points) from one BaseGridPoint to another.
* New linker functions for returning remote linkers via connected Summits or Saddles
* SpotElevationContainer object now support index()
* GridPointContainer now supports highest() and lowest()
* GridPoint now Hashable
* Summit and Saddle Objects now have Neighbor Finding functions

0.5.10 (September 17, 2018)
+++++++++++++++++++++++++++
* Fix bug in disqualify_lower_linkers()

0.5.9 (September 16, 2018)
++++++++++++++++++++++++++
* Rebuild the KMLFileWriter

0.5.8 (September 3, 2018)
+++++++++++++++++++++++++
* Fixed Bug within the walk function
* Improved equality operator in Linker object
* Cleaned up some of the progress displays.
* WalkPath from_dict converts to tuple.

0.5.7 (August 31, 2018)
+++++++++++++++++++++++
* Dockerized ipython terminal

0.5.6 (August 30, 2018)
+++++++++++++++++++++++
* Dockerized tests

0.5.5 (August 29, 2018)
+++++++++++++++++++++++
* Change Multipoint to default empty list
* add LPRboundary to saddle/summit objects.

0.5.4 (August 23, 2018)
+++++++++++++++++++++++
* Fix performance problems while reading domain files
* Add fast_lookup hash of various SpotElevationContainers.

0.5.3 (August 19, 2018)
+++++++++++++++++++++++
* to_dict() for all Domain child objects.
* from_dict() for all Domain child objects

0.5.2 (August 9, 2018)
++++++++++++++++++++++
* Track edgePoints inside SpotElevations.

0.5.1 (August 3, 2018)
++++++++++++++++++++++
* Track Walk path - introduces WalkPath container.
* Move walk() to Domain where it is more useful.
* Move disqualify_lower_linkers() to Domain.
* Move mark_redundant_linkers() to Domain.

0.5.0 (July 31, 2018)
+++++++++++++++++++++
* Elimination of InverseEdgePoints and InverseEdgePointContainer.
* Introduction of Perimeter as a replacement
* Very large addition of Unit tests
* Adding __getItems__, setItems, eq, ne, lt, repr and other magic functions to Container Objects.
* Made points from objects inherited from BaseGridPoint sortable
* Introduction of Runoffs, which are essentially saddles, but at the edge with a little looser restrictions.
* Elimination of "EdgePoints" and their container.

0.4.0 (January 11, 2018)
++++++++++++++++++++++++
* Walk now leverages equalHeightBlobs, but no longer keeps track of walk paths.
* Summits and Saddles now have thier own containers.
* Saddles can now have their high Shores reduced to a single point per shore and have their multipoint elements discarded while having their location set to the middle of those points.
* ..and saddles with > 2 highShores now ahve an internal network built for linking them all together and reducing thier size.
* logic.py is not feature_discovery.py
* equalHeightBlob is now in its own file in lib/logic/
* New Unit tests

0.3.9 (January 2, 2018)
+++++++++++++++++++++++
* Added __len__() function to SpotElevationContainer()
* Added neighbor iterators to GridPointContainers
* Added PseudoSummit finder within GridPointContainer.

0.3.8 (December 17, 2017)
+++++++++++++++++++++++++
* Fixed radius() function for Spot Elevation containers.
* Get nodata value and load appropriately. Considerable optimization.

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
+++++++++++++++++++
* Initial Base Release
