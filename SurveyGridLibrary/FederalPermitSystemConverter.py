from SurveyGridLibrary.CoordinateConversionException import CoordinateConversionException
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate

class FederalPermitSystemConverter:
    @staticmethod
    def to_lat_long(federal_permit_system):
        try:
            lat = federal_permit_system.lat_degrees + federal_permit_system.lat_minutes / 60.0
            lon = federal_permit_system.lon_degrees + federal_permit_system.lon_minutes / 60.0
            return LatLongCoordinate(lat, -lon)
        except Exception as e:
            raise CoordinateConversionException("Error converting FederalPermitSystem to LatLongCoordinate", e)

    @staticmethod
    def section_minute_factor(section):
        if section < 1 or section > 100:
            raise ValueError("Section must be in the range 1-100")
        return (section - 1) * 0.6
