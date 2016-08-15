from __future__ import division

import numpy
from locations import *



class AnalyzeData(object):
    def __init__(self, datamap):
        """
        :param datamap: `DataMap` object.
        """
        self.datamap = datamap
        self.data = self.datamap.numpy_map
        self.size = self.data.size
        self.edge = False
        self.equalNeighbor = False        
        self.span_longitude = self.datamap.span_longitude
        self.span_latitude = self.datamap.span_latitude
        self.cardinalGrid = dict()
        # Relative Grid Hash -- in case we ever want to use this feature...
        for cardinality in ['N','S','E','W']:
            self.cardinalGrid[cardinality] = candidateGridHash(cardinality, 3)



    def analyze(self):
        """
        Analyze Routine.
        Looks for summits, and returns a list of summits
        FUTURE: Analysis for Cols, as well as capability of chasing equal height neighbors.
        """
        iterator = numpy.nditer(self.data, flags=['multi_index'])
        locationObjects = list()
        index = 0
        #Iterate through numpy grid, and keep track of gridpoint coordinates.
        while not iterator.finished:
            x, y = iterator.multi_index
            self.elevation = iterator[0]

            #Quick Progress Meter. Needs refinement,
             index += 1
            if not index%100000:
                print "{}/{} - {}%".format(index, self.size, index/self.size)
            
            #Check for summit
            feature = self._summit(x, y)
            #Add summit object to list if it exists
            if feature:
                featureObjects.append(location)
            #Reset variables, and go to next gridpoint.
            self.edge = False
            self.equalNeighbor = False
            iterator.iternext()
        return featureObjects        



    def _summit(self, x, y):
        """
        Summit Scanning Function. This recieves an x,y grid point coordinate and
        determines if it is a summit coordinate or not.
        """

        def analyze_summit():
            """
            Helper for Summit Analysis. Returns True or False.
            """
            neighbor = self.iterateDiagonal(x,y)
            for degree, elevation in neighbor:
                if elevation > self.elevation:
                    return False
                if elevation == self.elevation:
                    self.equalNeighbor = True
            return True              

        #Returns nothing if the summit analysis is negative.
        if not analyze_summit():
            return
     

        # avg_elevation_hash = dict()
        # for cardinality in ['N','S','E','W']:
        #     elevationStore=[]
        #     for shift in self.cardinalGrid[cardinality]:
        #         try:
        #             elevationStore.append(self.data[x+shift[0]][y+shift[1]])
        #         except:
        #             pass
        #     #avg_elevation_hash[cardinality] = numpy.mean(elevationStore)
        #     if numpy.mean(elevationStore) > self.elevation:
        #         return
        ####print "FOUND SUFFICIENT: {}, {}, {}".format(self.datamap.x_position_latitude(x), self.datamap.y_position_longitude(y), self.elevation)  
        ####print "Neighbors are:{} - {}".format(self.elevation, [y1 for x1,y1 in self.iterateDiagonal(x,y)])     

        #Implicitly returns summit object if nothign fails.
        return Summit(self.datamap.x_position_latitude(x), self.datamap.y_position_longitude(y),
                      self.elevation, edge=self.edge, equalNeighbor=self.equalNeighbor)  
     
    def iterateDiagonal(self, x,y):
        """
        generator returns 8 closest neighbors to a raster grid location, that is,
        all points touching including the diagonals.
        """
        degreeMap = {'_0': [0,-1], 
                     '_45': [1,-1],
                     '_90': [1,0],
                     '_135':[1,1],
                     '_180': [0,1],
                     '_225': [-1,1],
                     '_270': [-1,0],
                     '_315': [-1,-1]}
        for degree, shift in degreeMap.items():
            _x = x+shift[0]
            _y = y+shift[1]
            if 0 < _x < self.span_latitude-1 and 0 < _y < self.span_longitude-1:
                yield degree, self.data[_x,_y]
            else:
                yield degree, None                    

                
    def iterateOrthogonal(self,x,y):
        """
        generator returns 4 closest neighbors to a raster grid location, that is,
        all points touching excluding the diagonals.
        """        
        degreeMap = {'_0': [0,-1], 
                     '_90': [1,0],
                     '_180': [0,1],
                     '_270': [-1,0]}
        for degree, shift in degreeMap.items():
            _x = x+shift[0]
            _y = y+shift[1]
            if 0 < _x < self.span_latitude-1 and 0 < _y < self.span_longitude-1:
                yield degree, self.data[_x,_y]
            else:
                yield degree, None  


def candidateGridHash(cardinality,resolution=1):
    """
    Returns a resolution x resolution relative grid based on cardinality.
    This is a helper and may be scrapped later on.
    """
    if not resolution%2:
        resolution+=1 #has to be odd.
    offset = int(numpy.median(range(resolution)))
    if cardinality.upper() == "N":
        return [[x,y] for x in range(-offset, offset+1) for y in range(-resolution, 0)]
    if cardinality.upper() == "E":
        return [[x,y] for x in range(1, resolution+1) for y in range(-offset, offset+1)]
    if cardinality.upper() == "S":
        return [[x,y] for x in range(-offset, offset+1) for y in range(1, resolution+1)]
    if cardinality.upper() == "W":
        return [[x,y] for x in range(-resolution, 0) for y in range(-offset, offset+1)]        
