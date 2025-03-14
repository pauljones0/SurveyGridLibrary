import math
from SurveyGridLibrary.BcNtsGridSystem import BcNtsGridSystem
from SurveyGridLibrary.DlsSystem import DlsSystem

class LatLongCoordinate:
    def __init__(self, latitude, longitude):
        self._latitude = latitude
        self._longitude = longitude

    @staticmethod
    def from_radians(latitude_radians, longitude_radians):
        return LatLongCoordinate(math.degrees(latitude_radians), math.degrees(longitude_radians))

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    def clone(self):
        return LatLongCoordinate(self._latitude, self._longitude)

    def equals(self, other):
        if not isinstance(other, LatLongCoordinate):
            return False
        return math.isclose(self._latitude, other._latitude, abs_tol=1e-9) and math.isclose(self._longitude, other._longitude, abs_tol=1e-9)

    def get_hash_code(self):
        return hash((self._latitude, self._longitude))

    def to_string(self):
        return self.to_string_format("g")

    def to_string_format(self, format):
        return self.to_string_format_provider(format, None)

    def to_string_format_provider(self, format, format_provider):
        if not format:
            format = "g"

        if format == "DD MM.MMM":
            degrees_lat = int(self._latitude)
            degrees_lon = int(self._longitude)
            return f"{degrees_lat} {(self._latitude - degrees_lat) * 60.0:.3f}, {degrees_lon} {(self._longitude - degrees_lon) * 60.0:.3f}"

        if format == "d":
            return f"{self._latitude}°, {self._longitude}°"

        if format == "g":
            return f"{self._latitude:.6f}, {self._longitude:.6f}"

        raise ValueError(f"Unsupported format string '{format}'")

    def to_convertible_string(self):
        return f"{self._latitude},{self._longitude}"

    def to_degrees_minutes(self):
        lat_deg = int(self._latitude)
        lat_min = (self._latitude - lat_deg) * 60.0
        lon_deg = int(self._longitude)
        lon_min = (self._longitude - lon_deg) * 60.0
        return f"{lat_deg}° {lat_min:.3f}', {lon_deg}° {lon_min:.3f}'"

    def to_degrees_minutes_seconds(self):
        lat_deg = int(self._latitude)
        lat_min = int((self._latitude - lat_deg) * 60.0)
        lat_sec = (self._latitude - lat_deg - lat_min / 60.0) * 3600.0
        lon_deg = int(self._longitude)
        lon_min = int((self._longitude - lon_deg) * 60.0)
        lon_sec = (self._longitude - lon_deg - lon_min / 60.0) * 3600.0
        return f"{lat_deg}° {lat_min}' {lat_sec:.2f}\", {lon_deg}° {lon_min}' {lon_sec:.2f}\""

    @staticmethod
    def from_convertible_string(convertible_string):
        parts = convertible_string.split(',')
        if len(parts) != 2:
            raise ValueError("Invalid convertible string format")
        return LatLongCoordinate(float(parts[0]), float(parts[1]))

    def direction_to(self, other):
        if not isinstance(other, LatLongCoordinate):
            raise ValueError("Other must be a LatLongCoordinate")
        d_lon = math.radians(other._longitude - self._longitude)
        lat1 = math.radians(self._latitude)
        lat2 = math.radians(other._latitude)
        y = math.sin(d_lon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
        return (math.degrees(math.atan2(y, x)) + 360) % 360

    def distance_to(self, other):
        if not isinstance(other, LatLongCoordinate):
            raise ValueError("Other must be a LatLongCoordinate")
        lat1 = math.radians(self._latitude)
        lon1 = math.radians(self._longitude)
        lat2 = math.radians(other._latitude)
        lon2 = math.radians(other._longitude)
        d_lat = lat2 - lat1
        d_lon = lon2 - lon1
        a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371.0 * c

    def sphere_distance_to(self, other):
        if not isinstance(other, LatLongCoordinate):
            raise ValueError("Other must be a LatLongCoordinate")
        lat1 = math.radians(self._latitude)
        lon1 = math.radians(self._longitude)
        lat2 = math.radians(other._latitude)
        lon2 = math.radians(other._longitude)
        d_lat = lat2 - lat1
        d_lon = lon2 - lon1
        a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371.0 * c

    def relative_distance_to(self, other):
        if not isinstance(other, LatLongCoordinate):
            raise ValueError("Other must be a LatLongCoordinate")
        return self.sphere_distance_to(other)

    def great_circle_angle(self, other):
        if not isinstance(other, LatLongCoordinate):
            raise ValueError("Other must be a LatLongCoordinate")
        lat1 = math.radians(self._latitude)
        lon1 = math.radians(self._longitude)
        lat2 = math.radians(other._latitude)
        lon2 = math.radians(other._longitude)
        d_lon = lon2 - lon1
        y = math.sin(d_lon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
        return math.degrees(math.atan2(y, x))

    @staticmethod
    def from_decimal_degrees(latitude, longitude):
        return LatLongCoordinate(latitude, longitude)

    def to_bc_nts_grid_system(self):
        return BcNtsGridSystem.to_lat_long(self)

    def to_dls_system(self):
        return DlsSystem.to_lat_long(self)
