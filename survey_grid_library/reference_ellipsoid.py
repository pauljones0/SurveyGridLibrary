class ReferenceEllipsoid:
    def __init__(self, semi_major_axis, semi_minor_axis, inverse_flattening):
        self.semi_major_axis = semi_major_axis
        self.semi_minor_axis = semi_minor_axis
        self.inverse_flattening = inverse_flattening

    WGS84 = None
    GRS80 = None
    CLARKE1866 = None

ReferenceEllipsoid.WGS84 = ReferenceEllipsoid(6378137, 6356752.314245, 1 / 298.257223563)
ReferenceEllipsoid.GRS80 = ReferenceEllipsoid(6378137, 6356752.3141, 1 / 298.257222101)
ReferenceEllipsoid.CLARKE1866 = ReferenceEllipsoid(6378206.4, 6356583.8, 1 / 294.978698214)
