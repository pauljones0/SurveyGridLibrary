from SurveyGridLibrary.CoordinateParseException import CoordinateParseException
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.FederalPermitSystemConverter import FederalPermitSystemConverter

class FederalPermitSystem:
    def __init__(self, unit, section, lat_degrees, lat_minutes, lon_degrees, lon_minutes):
        if unit not in 'ABCDEFGHIJKLMNOP':
            raise ValueError("Unit must be in the range A-P")
        if section < 1 or section > 100:
            raise ValueError("Section must be in the range 1-100")
        if lat_degrees < 0 or lat_degrees > 90:
            raise ValueError("Latitude degrees must be in the range 0-90")
        if lat_minutes < 0 or lat_minutes >= 60:
            raise ValueError("Latitude minutes must be in the range 0-59")
        if lon_degrees < 0 or lon_degrees > 180:
            raise ValueError("Longitude degrees must be in the range 0-180")
        if lon_minutes < 0 or lon_minutes >= 60:
            raise ValueError("Longitude minutes must be in the range 0-59")

        self.unit = unit
        self.section = section
        self.lat_degrees = lat_degrees
        self.lat_minutes = lat_minutes
        self.lon_degrees = lon_degrees
        self.lon_minutes = lon_minutes

    def to_lat_long(self):
        return FederalPermitSystemConverter.to_lat_long(self)

    def equals(self, other):
        if not isinstance(other, FederalPermitSystem):
            return False
        return self == other

    def get_hash_code(self):
        return hash((self.unit, self.section, self.lat_degrees, self.lat_minutes, self.lon_degrees, self.lon_minutes))

    def parse(location):
        if location is None:
            raise CoordinateParseException("Can not parse a null location.")

        if not location.strip():
            raise CoordinateParseException("Can not parse an empty location.")

        fields = location.upper().strip().split('/')
        if len(fields) != 2:
            raise CoordinateParseException("Location must have two fields separated by a '/'.")

        first_half, second_half = fields

        second_parts = second_half.split('-')
        if len(second_parts) != 3:
            raise CoordinateParseException("Second half must have three parts separated by '-'.")

        lat_degrees = int(second_parts[0])
        lat_minutes = int(second_parts[1])
        lon_degrees = int(second_parts[2])
        lon_minutes = int(second_parts[3])

        first_parts = first_half.split('-')
        if len(first_parts) != 2:
            raise CoordinateParseException("First half must have two parts separated by '-'.")

        unit = first_parts[0]
        section = int(first_parts[1])

        return FederalPermitSystem(unit, section, lat_degrees, lat_minutes, lon_degrees, lon_minutes)

    def to_string(self):
        return f"{self.unit}-{self.section:02}/{self.lat_degrees:02}-{self.lat_minutes:02}-{self.lon_degrees:03}-{self.lon_minutes:02}"
