


class BaseCoordinate(object):
    def __init__(self, latitude, longitude, *args, **kwargs):
        self.latitude = latitude
        self.longitude = longitude

class SpotElevation(BaseCoordinate):
    def __init__(self, latitude, longitude, elevation):
        super(SpotElevation, self).__init__(latitude, longitude)
        self.elevation = elevation

    @property
    def feet(self):
        return self.elevation * 3.2808

class Summit(SpotElevation):
    def __init__(self, latitude, longitude, elevation):
        super(Summit, self).__init__(latitude, longitude, elevation)

