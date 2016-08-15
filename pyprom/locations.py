


class BaseCoordinate(object):
    def __init__(self, latitude, longitude, *args, **kwargs):
        self.latitude = latitude
        self.longitude = longitude

class SpotElevation(BaseCoordinate):
    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        super(SpotElevation, self).__init__(latitude, longitude)
        self.elevation = elevation
        self.candidate = kwargs.get('edge', None)

    @property
    def feet(self):
        return self.elevation * 3.2808

class Summit(SpotElevation):
    def __init__(self, latitude, longitude, elevation, *args, **kwargs):
        super(Summit, self).__init__(latitude, longitude, elevation, *args, **kwargs)
        self.equalNeighbor=kwargs.get('equalNeighbor', None)

    def __str__(self):
        return "Summit El {} lat {} long {}".format(self.feet, self.latitude, self.longitude)

