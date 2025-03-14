class ReferenceEllipsoid:
    def __init__(self, semi_major_axis, semi_minor_axis, flattening, inverse_flattening):
        self.semi_major_axis = semi_major_axis
        self.semi_minor_axis = semi_minor_axis
        self.flattening = flattening
        self.inverse_flattening = inverse_flattening
