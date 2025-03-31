class ReferenceEllipsoid:
    def __init__(self, semi_major_axis, semi_minor_axis, inverse_flattening):
        self.semi_major_axis = semi_major_axis
        self.semi_minor_axis = semi_minor_axis
        self.inverse_flattening = inverse_flattening

    Wgs84 = None
    Grs80 = None
    Clarke1866 = None

ReferenceEllipsoid.Wgs84 = ReferenceEllipsoid(6378137, 6356752.314245, 1 / 298.257223563)
ReferenceEllipsoid.Grs80 = ReferenceEllipsoid(6378137, 6356752.3141, 1 / 298.257222101)
ReferenceEllipsoid.Clarke1866 = ReferenceEllipsoid(6378206.4, 6356583.8, 1 / 294.978698214)
