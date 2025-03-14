class LatLongCorners:
    def __init__(self, se=None, sw=None, nw=None, ne=None):
        self.se = se
        self.sw = sw
        self.nw = nw
        self.ne = ne

    def count(self):
        return sum(1 for corner in [self.se, self.sw, self.nw, self.ne] if corner is not None)
