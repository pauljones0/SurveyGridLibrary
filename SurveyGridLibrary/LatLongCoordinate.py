import math
from BcNtsGridSystem import BcNtsGridSystem
from DlsSystem import DlsSystem

class LatLongCoordinate:
    def __init__(self, latitude, longitude):
        # Clamp latitude to [-90, 90]
        self._latitude = max(min(latitude, 90), -90)
        # Emulate C# remainder for longitude with divisor 180 (truncates toward zero)
        self._longitude = longitude - 180 * int(longitude / 180)

    @staticmethod
    def from_radians(latitude_radians, longitude_radians):
        return LatLongCoordinate(math.degrees(latitude_radians), math.degrees(longitude_radians))

    @staticmethod
    def from_degrees_minutes(lat_degrees, lat_minutes, lon_degrees, lon_minutes):
        if lat_degrees > 0:
            latitude = lat_degrees + lat_minutes / 60.0
        else:
            latitude = lat_degrees - lat_minutes / 60.0
        if lon_degrees > 0:
            longitude = lon_degrees + lon_minutes / 60.0
        else:
            longitude = lon_degrees - lon_minutes / 60.0
        return LatLongCoordinate(latitude, longitude)

    @staticmethod
    def from_degrees_minutes_seconds(lat_degrees, lat_minutes, lat_seconds, lon_degrees, lon_minutes, lon_seconds):
        if lat_degrees > 0:
            latitude = lat_degrees + lat_minutes / 60.0 + lat_seconds / 3600.0
        else:
            latitude = lat_degrees - (lat_minutes / 60.0 + lat_seconds / 3600.0)
        if lon_degrees > 0:
            longitude = lon_degrees + lon_minutes / 60.0 + lon_seconds / 3600.0
        else:
            longitude = lon_degrees - (lon_minutes / 60.0 + lon_seconds / 3600.0)
        return LatLongCoordinate(latitude, longitude)

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
        if math.isnan(self._latitude) or math.isnan(self._longitude):
            return "NaN"
        if format == "dd":
            lat_str = f"{'N' if self._latitude >= 0 else 'S'}{abs(self._latitude):06.6f}"
            lon_str = f"{'E' if self._longitude >= 0 else 'W'}{abs(self._longitude):07.6f}"
            return f"{lat_str} {lon_str}"
        elif format == "dms":
            return self.to_degrees_minutes_seconds()
        elif format == "dm":
            return self.to_degrees_minutes()
        elif format == "sd":
            return f"{self._latitude:.6f} {self._longitude:.6f}"
        elif format == "wkt":
            return f"POINT({self._longitude:07.6f} {self._latitude:06.6f})"
        elif format == "g":
            return self.to_convertible_string()
        else:
            raise ValueError(f"Unsupported format string '{format}'")

    def to_convertible_string(self):
        return f"{self._latitude}, {self._longitude}"

    def to_degrees_minutes(self):
        lat_deg = int(abs(self._latitude))
        lon_deg = int(abs(self._longitude))
        lat_min = (abs(self._latitude) - lat_deg) * 60.0
        lon_min = (abs(self._longitude) - lon_deg) * 60.0
        return f"{'N' if self._latitude >= 0 else 'S'}{lat_deg} {lat_min:05.3f} {'E' if self._longitude >= 0 else 'W'}{lon_deg} {lon_min:05.3f}"

    def to_degrees_minutes_seconds(self):
        lat_deg = int(abs(self._latitude))
        lon_deg = int(abs(self._longitude))
        lat_min = int((abs(self._latitude) - lat_deg) * 60)
        lon_min = int((abs(self._longitude) - lon_deg) * 60)
        lat_sec = (abs(self._latitude) - lat_deg - lat_min / 60.0) * 3600.0
        lon_sec = (abs(self._longitude) - lon_deg - lon_min / 60.0) * 3600.0
        return f"{'N' if self._latitude >= 0 else 'S'}{lat_deg}° {lat_min}' {lat_sec:0.1f}\" {'E' if self._longitude >= 0 else 'W'}{lon_deg}° {lon_min}' {lon_sec:0.1f}\""

    def direction_to(self, other):
        if not isinstance(other, LatLongCoordinate):
            raise ValueError("Other must be a LatLongCoordinate")
        lat1 = math.radians(self._latitude)
        lon1 = math.radians(self._longitude)
        lat2 = math.radians(other._latitude)
        lon2 = math.radians(other._longitude)
        dlonW = math.remainder(lon2 - lon1, 2 * math.pi)
        dlonE = math.remainder(lon1 - lon2, 2 * math.pi)
        dphi = math.log(math.tan(lat2 / 2 + math.pi / 4) / math.tan(lat1 / 2 + math.pi / 4))
        if dlonW < dlonE:
            tc = math.atan2(-dlonW, dphi)
        else:
            tc = math.atan2(dlonE, dphi)
        tc = -tc
        if tc < 0:
            tc += 2 * math.pi
        return math.degrees(tc)

    def great_circle_angle(self, other):
        if not isinstance(other, LatLongCoordinate):
            raise ValueError("Other must be a LatLongCoordinate")
        lat1 = math.radians(self._latitude)
        lon1 = math.radians(self._longitude)
        lat2 = math.radians(other._latitude)
        lon2 = math.radians(other._longitude)
        cosine_angle = math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2)
        cosine_angle = max(-1, min(1, cosine_angle))
        return math.acos(cosine_angle)  # returns angle in radians

    def distance_to(self, other, ellipsoid=None):
        if not isinstance(other, LatLongCoordinate):
            raise ValueError("Other must be a LatLongCoordinate")
        # Vincenty's formula for ellipsoidal distance
        # Use WGS84 parameters if ellipsoid is not provided
        a = 6378137.0  # semi-major axis in meters
        b = 6356752.314245  # semi-minor axis in meters
        f = 1/298.257223563  # flattening
        lat1 = math.radians(self._latitude)
        lon1 = math.radians(self._longitude)
        lat2 = math.radians(other._latitude)
        lon2 = math.radians(other._longitude)
        L = lon2 - lon1
        U1 = math.atan((1 - f) * math.tan(lat1))
        U2 = math.atan((1 - f) * math.tan(lat2))
        sinU1 = math.sin(U1)
        cosU1 = math.cos(U1)
        sinU2 = math.sin(U2)
        cosU2 = math.cos(U2)
        lamb = L
        lambdaP = 2 * math.pi
        iterLimit = 20
        while abs(lamb - lambdaP) > 1e-12 and iterLimit > 0:
            sinLambda = math.sin(lamb)
            cosLambda = math.cos(lamb)
            sinSigma = math.sqrt((cosU2 * sinLambda) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2)
            if sinSigma == 0:
                return 0.0
            cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
            sigma = math.atan2(sinSigma, cosSigma)
            sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
            cosSqAlpha = 1 - sinAlpha ** 2
            cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha if cosSqAlpha != 0 else 0
            C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
            lambdaP = lamb
            lamb = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM ** 2)))
            iterLimit -= 1
        if iterLimit == 0:
            raise Exception("Formula failed to converge on solution.")
        uSq = cosSqAlpha * (a**2 - b**2) / (b**2)
        A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
        B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
        deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma * (-1 + 2 * cos2SigmaM ** 2) - B / 6 * cos2SigmaM * (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2SigmaM ** 2)))
        s = b * A * (sigma - deltaSigma)
        return round(s, 3)

    def sphere_distance_to(self, other):
        angle = self.great_circle_angle(other)  # in radians
        a = 6378137.0  # Use WGS84 semi-major axis as sphere radius in meters
        return angle * a

    def relative_distance_to(self, other):
        if not isinstance(other, LatLongCoordinate):
            raise ValueError("Other must be a LatLongCoordinate")
        lat1 = self._latitude
        lat2 = other._latitude
        lon1 = abs(self._longitude)
        lon2 = abs(other._longitude)
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        s1 = math.sin(d_lat / 2)
        s2 = math.sin(d_lon / 2)
        a_val = s1**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * s2**2
        c = math.atan2(math.sqrt(a_val), math.sqrt(1 - a_val))
        return c

    @staticmethod
    def from_convertible_string(convertible_string):
        parts = convertible_string.split(",")
        if len(parts) != 2:
            raise ValueError("Invalid convertible string format")
        return LatLongCoordinate(float(parts[0].strip()), float(parts[1].strip()))

    @staticmethod
    def from_decimal_degrees(dd):
        dd = dd.replace(" ", "").upper()
        if len(dd.strip()) == 0:
            raise ValueError("The lat/long must not be empty.")
        i = dd.find('N')
        if i == -1:
            raise ValueError("The latitude must have the 'N' or 'S' character.")
        j = dd.find('W')
        if j == -1 or j >= len(dd) - 1:
            raise ValueError("The longitude must have the 'E' or 'W' character.")
        try:
            lat = float(dd[i+1:j])
        except:
            raise ValueError("Invalid latitude format.")
        if lat < -90 or lat > 90:
            raise ValueError("Latitude must be in the range -90 to 90")
        try:
            lon = float(dd[j+1:])
        except:
            raise ValueError("Invalid longitude format.")
        if lon < -180 or lon > 180:
            raise ValueError("Longitude must be in the range -180 to 180")
        # Mimic C# by negating longitude
        return LatLongCoordinate(lat, -lon)

    def to_bc_nts_grid_system(self):
        # External: BcNtsGridSystem.to_lat_long should mimic C# BcNtsGridSystemConverter.FromLatLongCoordinates
        return BcNtsGridSystem.to_lat_long(self)

    def to_dls_system(self):
        # External: DlsSystem.to_lat_long should mimic C# DlsSystemConverter.FromLatLongCoordinate
        result = DlsSystem.to_lat_long(self)
        if result is None:
            raise Exception("Dls lookup failed")
        return result
