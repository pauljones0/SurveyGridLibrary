import math
from survey_grid_library.angle import Angle
from survey_grid_library.coordinate_conversion_exception import CoordinateConversionException
from survey_grid_library.bc_nts_grid_system_converter import BcNtsGridSystemConverter
from survey_grid_library.dls_system_converter import DlsSystemConverter

class LatLongCoordinate:
    Origin = None

    MinLatitude = -90
    MaxLatitude = 90
    MinLongitude = -180
    MaxLongitude = 180

    def __init__(self, latitude, longitude):
        self._latitude = max(min(latitude, self.MaxLatitude), self.MinLatitude)
        self._longitude = longitude % self.MaxLongitude

    @staticmethod
    def from_radians(lat_radians, long_radians):
        return LatLongCoordinate(math.degrees(lat_radians), math.degrees(long_radians))

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

        if format == "dd":
            return f"{'N' if self._latitude >= 0 else 'S'}{abs(self._latitude):.6f} {'E' if self._longitude >= 0 else 'W'}{abs(self._longitude):.6f}"

        if format == "dms":
            return self.to_degrees_minutes_seconds()

        if format == "dm":
            return self.to_degrees_minutes()

        if format == "sd":
            return f"{self._latitude:.6f} {self._longitude:.6f}"

        if format == "wkt":
            return f"POINT({self._longitude:.6f} {self._latitude:.6f})"

        if format == "g":
            return self.to_convertible_string()

        raise ValueError(f"Invalid format specifier '{format}'")

    def to_convertible_string(self):
        return f"{self._latitude}, {self._longitude}"

    def to_degrees_minutes(self):
        lat_degrees = int(self._latitude)
        lat_minutes = (self._latitude - lat_degrees) * 60

        lng_degrees = int(self._longitude)
        lng_minutes = (self._longitude - lng_degrees) * 60

        return f"{'N' if self._latitude >= 0 else 'S'}{abs(lat_degrees)} {lat_minutes:.3f} {'E' if self._longitude >= 0 else 'W'}{abs(lng_degrees)} {lng_minutes:.3f}"

    def to_degrees_minutes_seconds(self):
        lat_degrees = int(self._latitude)
        lat_minutes = int((self._latitude - lat_degrees) * 60)
        lat_seconds = (self._latitude - lat_degrees) * 3600 - lat_minutes * 60

        lng_degrees = int(self._longitude)
        lng_minutes = int((self._longitude - lng_degrees) * 60)
        lng_seconds = (self._longitude - lng_degrees) * 3600 - lng_minutes * 60

        return f"{'N' if self._latitude >= 0 else 'S'}{abs(lat_degrees)}° {lat_minutes}' {lat_seconds:.1f}\" {'E' if self._longitude >= 0 else 'W'}{abs(lng_degrees)}° {lng_minutes}' {lng_seconds:.1f}\""

    @staticmethod
    def from_convertible_string(convertible_string):
        tokens = convertible_string.split(',')
        if len(tokens) != 2:
            tokens = convertible_string.split(' ')

        if len(tokens) != 2:
            raise ValueError(f"Invalid lat long string '{convertible_string}'")
        lat_value = tokens[0].strip()
        long_value = tokens[1].strip()
        return LatLongCoordinate(float(lat_value), float(long_value))

    def direction_to(self, destination):
        lat1 = math.radians(self._latitude)
        lon1 = math.radians(self._longitude)
        lat2 = math.radians(destination.latitude)
        lon2 = math.radians(destination.longitude)

        dlon_w = (lon2 - lon1) % (2 * math.pi)
        dlon_e = (lon1 - lon2) % (2 * math.pi)
        dphi = math.log(math.tan(lat2 / 2 + math.pi / 4) / math.tan(lat1 / 2 + math.pi / 4))
        tc = (math.atan2(-dlon_w, dphi) if dlon_w < dlon_e else math.atan2(dlon_e, dphi)) % (2 * math.pi)

        tc = -tc
        angle = Angle.from_radians(tc)
        if angle.radians < 0:
            angle = Angle.from_radians(angle.radians + 2 * math.pi)

        return angle

    def distance_to(self, p2, ellipsoid):
        p1 = self

        transverse_radius = ellipsoid.semi_major_axis
        conjugate_radius = ellipsoid.semi_minor_axis
        flattening = ellipsoid.inverse_flattening

        l = math.radians(p2.longitude - p1.longitude)
        u1 = math.atan((1 - flattening) * math.tan(math.radians(p1.latitude)))
        u2 = math.atan((1 - flattening) * math.tan(math.radians(p2.latitude)))
        sin_u1 = math.sin(u1)
        cos_u1 = math.cos(u1)
        sin_u2 = math.sin(u2)
        cos_u2 = math.cos(u2)

        lambda_ = l
        lambda_p = 2 * math.pi
        limit = 20

        cos2_sigma_m = 0.0
        cos_sigma = 0.0
        cos_sq_alpha = 0.0
        sigma = 0.0
        sin_sigma = 0.0
        while abs(lambda_ - lambda_p) > 1e-12 and limit > 0:
            sin_lambda = math.sin(lambda_)
            cos_lambda = math.cos(lambda_)
            sin_sigma = math.sqrt((cos_u2 * sin_lambda) ** 2 + (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lambda) ** 2)
            if sin_sigma == 0:
                return 0

            cos_sigma = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lambda
            sigma = math.atan2(sin_sigma, cos_sigma)
            sin_alpha = cos_u1 * cos_u2 * sin_lambda / sin_sigma
            cos_sq_alpha = 1 - sin_alpha ** 2
            cos2_sigma_m = cos_sigma - 2 * sin_u1 * sin_u2 / cos_sq_alpha

            if math.isnan(cos2_sigma_m):
                cos2_sigma_m = 0

            c = flattening / 16 * cos_sq_alpha * (4 + flattening * (4 - 3 * cos_sq_alpha))
            lambda_p = lambda_
            lambda_ = l + (1 - c) * flattening * sin_alpha * (sigma + c * sin_sigma * (cos2_sigma_m + c * cos_sigma * (-1 + 2 * cos2_sigma_m ** 2)))
            limit -= 1

        if limit == 0:
            raise Exception("Formula failed to converge on solution.")

        u_sq = cos_sq_alpha * (transverse_radius ** 2 - conjugate_radius ** 2) / (conjugate_radius ** 2)
        a = 1 + u_sq / 16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
        b = u_sq / 1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
        delta_sigma = b * sin_sigma * (cos2_sigma_m + b / 4 * (cos_sigma * (-1 + 2 * cos2_sigma_m ** 2) - b / 6 * cos2_sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos2_sigma_m ** 2)))
        s = conjugate_radius * a * (sigma - delta_sigma)

        return round(s, 3)

    def sphere_distance_to(self, destination):
        radius_of_earth = 6378137.0
        return self.great_circle_angle(self, destination).radians * radius_of_earth

    def relative_distance_to(self, geo):
        lat2 = geo.latitude
        lat1 = self.latitude
        lon2 = abs(geo.longitude)
        lon1 = abs(self.longitude)

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        s1 = math.sin(dlat / 2)
        s2 = math.sin(dlon / 2)
        a = s1 ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * s2 ** 2
        c = math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return c

    @staticmethod
    def great_circle_angle(p1, p2):
        d = math.acos(math.sin(math.radians(p1.latitude)) * math.sin(math.radians(p2.latitude)) + math.cos(math.radians(p1.latitude)) * math.cos(math.radians(p2.latitude)) * math.cos(math.radians(p1.longitude) - math.radians(p2.longitude)))
        return Angle.from_radians(d)

    @staticmethod
    def from_decimal_degrees(dd):
        dd = dd.replace(" ", "").upper()
        if not dd:
            raise ValueError("The lat/long must not be empty.")

        i = dd.find('N')
        if i == -1:
            raise ValueError("The latitude must have the 'N' or 'S' character.")

        j = dd.find('W')
        if j == -1 or j >= len(dd) - 1:
            raise ValueError("The longitude must have the 'E' or 'W' character.")

        latitude = float(dd[i + 1:j - 1])
        if latitude < LatLongCoordinate.MinLatitude or latitude > LatLongCoordinate.MaxLatitude:
            raise ValueError(f"Latitude must be in the range {LatLongCoordinate.MinLatitude} to {LatLongCoordinate.MaxLatitude}")

        longitude = float(dd[j + 1:])
        if longitude < LatLongCoordinate.MinLongitude or longitude > LatLongCoordinate.MaxLongitude:
            raise ValueError(f"Longitude must be in the range {LatLongCoordinate.MinLongitude} to {LatLongCoordinate.MaxLongitude}")

        return LatLongCoordinate(latitude, -longitude)

    def to_bc_nts_grid_system(self):
        return BcNtsGridSystemConverter.from_lat_long_coordinates(self)

    def to_dls_system(self):
        dls = DlsSystemConverter.from_lat_long_coordinate(self)
        if dls is None:
            raise CoordinateConversionException("Dls lookup failed")
        return dls

LatLongCoordinate.Origin = LatLongCoordinate(0, 0)
