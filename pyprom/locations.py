class BaseCoordinate(object):
    """
    Base Coordinate, intended to be inherited from. This contains
    basic lat/long
    """
    def __init__(self, latitude, longitude, *args, **kwargs):
        self.latitude = latitude
        self.longitude = longitude

class SpotElevation(BaseCoordinate):
    """
    SpotElevation -- Intended to be inherited from. lat/long/elevation
    """
    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        super(SpotElevation, self).__init__(latitude, longitude)
        self.elevation = elevation
        self.candidate = kwargs.get('edge', None)

    @property
    def feet(self):
        return self.elevation * 3.2808

class Summit(SpotElevation):
    """
    Summit object stores relevant summit data.
    """
    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        super(Summit, self).__init__(latitude, longitude, elevation, *args, **kwargs)
        self.multiPoint=kwargs.get('multiPoint', None)

    def __str__(self):
        return "Summit El {} lat {} long {}".format(self.feet, self.latitude, self.longitude)

class MultiPoint(object):
    """
    Multipoint objects contain a list of raster coordinates as
    well as an elevation
    """
    def __init__(self, points, elevation):
        self.points = points
        self.elevation = elevation

