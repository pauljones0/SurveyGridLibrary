class LatLongCorners:
    def __init__(self, se=None, sw=None, nw=None, ne=None):
        self.south_east = se
        self.south_west = sw
        self.north_west = nw
        self.north_east = ne

    @property
    def count(self):
        return sum(1 for corner in [self.south_east, self.south_west, self.north_west, self.north_east] if corner is not None)
