import math
import numpy as np

class Angle:
    def __init__(self, radians):
        self.radians = radians

    @staticmethod
    def from_radians(radians):
        return Angle(radians)

    @staticmethod
    def from_degrees(degrees):
        return Angle(degrees * math.pi / 180.0)

    @property
    def degrees(self):
        return self.radians * 180.0 / math.pi

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
        return self.radians * (200.0 / math.pi)

    @property
    def milliradians(self):
        return self.radians * 1000.0

    def compare_to(self, obj):
        if obj is None:
            return 1
        if not isinstance(obj, Angle):
            raise ValueError("Object is not an Angle")
        return self.compare_to_angle(obj)

    def compare_to_angle(self, other):
        if self.radians > other.radians:
            return 1
        return -1 if self.radians < other.radians else 0

    def equals(self, other):
        return np.isclose(self.radians, other.radians)

    def get_hash_code(self):
        return hash(self.radians)

    def to_string(self):
        return self.to_string_format("g")

    def to_string_format(self, format):
        return self.to_string_format_provider(format, None)

    def to_string_format_provider(self, format, format_provider):
        if not format:
            format = "g"

        if format == "DD MM.MMM":
            degrees = int(self.degrees)
            return f"{degrees} {(self.degrees - degrees) * 60.0:.3f}"

        if format == "d":
            return f"{self.degrees}°"

        if format == "g":
            return f"{self.radians:.6f}"

        raise ValueError(f"Unsupported format string '{format}'")
