import math

class Angle:
    def __init__(self, radians):
        self._radians = radians

    @staticmethod
    def from_radians(radians):
        return Angle(radians)

    @staticmethod
    def from_degrees(degrees):
        return Angle(math.radians(degrees))

    @property
    def radians(self):
        return self._radians

    @property
    def degrees(self):
        return math.degrees(self._radians)

    @property
    def minutes(self):
        degrees = self.degrees
        if degrees < 0.0:
            return (degrees - math.ceil(degrees)) * 60.0
        return (degrees - math.floor(degrees)) * 60.0

    @property
    def seconds(self):
        degrees = self.degrees
        if degrees < 0.0:
            a = (degrees - math.ceil(degrees)) * 60.0
            return (a - math.ceil(a)) * 60.0
        d = (degrees - math.floor(degrees)) * 60.0
        return (d - math.floor(d)) * 60.0

    @property
    def gradians(self):
        return self._radians * (200.0 / math.pi)

    @property
    def milliradians(self):
        return self._radians * 1000.0

    def compare_to(self, obj):
        if obj is None:
            return 1
        if not isinstance(obj, Angle):
            raise ValueError("Object is not an Angle")
        return self.compare_to_angle(obj)

    def compare_to_angle(self, other):
        if self._radians > other._radians:
            return 1
        return -1 if self._radians < other._radians else 0

    def equals(self, other):
        if not isinstance(other, Angle):
            return False
        return math.isclose(self._radians, other._radians, abs_tol=1e-9)

    def __eq__(self, other):
        if not isinstance(other, Angle):
            return False
        return self.equals(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_hash_code(self):
        return hash(self._radians)

    def to_string(self):
        return self.to_string_format("g")

    def to_string_format(self, format):
        return self.to_string_format_provider(format, None)

    def to_string_format_provider(self, format, format_provider):
        if not format:
            format = "g"

        if format == "DD MM.MMM":
            degrees = int(self.degrees)
            minutes = (self.degrees - degrees) * 60.0
            return f"{degrees:02d} {minutes:06.3f}"

        if format == "d":
            return f"{self.degrees:.0f}°"

        if format == "g":
            return f"{self._radians:.6f}"

        raise ValueError(f"Unsupported format string '{format}'")
