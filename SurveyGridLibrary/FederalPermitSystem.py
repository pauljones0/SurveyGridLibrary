import operator  # Required for hash calculation

from CoordinateParseException import CoordinateParseException
from FederalPermitSystemConverter import FederalPermitSystemConverter

class FederalPermitSystem:
    """
    Represents a location within the Canadian Federal Permit System grid.

    Based on the regulations described in the C# version. Latitude and longitude
    refer to the northeast corner of a permit grid area.
    """
    def __init__(self, unit, section, lat_degrees, lat_minutes, lon_degrees, lon_minutes):
        """
        Initializes a new FederalPermitSystem instance.

        Args:
            unit (str): The unit identifier (A-P). Case-insensitive.
            section (int): The section number (1-100, 1-80, or 1-60 depending on latitude).
            lat_degrees (int): Latitude degrees of the NE corner (40-85).
            lat_minutes (int): Latitude minutes of the NE corner (0, 10, 20, 30, 40, 50).
            lon_degrees (int): Longitude degrees of the NE corner (42-141). West longitude is expected as positive.
            lon_minutes (int): Longitude minutes of the NE corner (0, 15, 30, 45 south of 70; 0, 30 north of 70).
        """
        if not isinstance(unit, str) or len(unit) != 1:
             raise ValueError("Unit must be a single character.")

        unit_upper = unit.upper()
        if not ('A' <= unit_upper <= 'P'):
            raise ValueError("Unit must be 'A' through 'P'")

        if not (40 <= lat_degrees < 85): # Note: C# range is 40-85, but SectionCount covers up to 84 implicitly. Upper bound exclusive here.
             raise ValueError("Latitude degrees must be between 40 and 84.")
        if lat_minutes not in [0, 10, 20, 30, 40, 50]:
            raise ValueError("Latitude minutes must be in the series [0, 10, 20, 30, 40, 50].")

        if not (42 <= lon_degrees <= 141):
            raise ValueError("Longitude degrees must be between 42 and 141.")

        if lat_degrees < 70:
            if lon_minutes not in [0, 15, 30, 45]:
                raise ValueError("Longitude minutes must be in the series [0, 15, 30, 45] south of 70.")
        else: # lat_degrees >= 70
            if lon_minutes not in [0, 30]:
                 raise ValueError("Longitude minutes must be in the series [0, 30] north of 70.")

        max_section = FederalPermitSystem.section_count(lat_degrees)
        if not (1 <= section <= max_section):
            raise ValueError(f"Section must be between 1 and {max_section} for latitude {lat_degrees}.")


        # Store longitude internally as negative west, matching C#
        self._lon_degrees = -lon_degrees

        self.unit = unit_upper
        self.section = section
        self.lat_degrees = lat_degrees
        self.lat_minutes = lat_minutes
        self.lon_minutes = lon_minutes

    @property
    def lon_degrees(self):
        """Gets the west longitude degrees (always positive)."""
        return -self._lon_degrees

    @staticmethod
    def section_count(lat_degrees):
        """Determines the number of sections in a grid area based on latitude."""
        if (40 <= lat_degrees < 60) or (70 <= lat_degrees < 75):
            return 100
        elif (60 <= lat_degrees < 68) or (75 <= lat_degrees < 78):
            return 80
        elif (68 <= lat_degrees < 70) or (78 <= lat_degrees < 85): # C# allows 85 here
             return 60
        else:
             # This case should theoretically not be hit due to constructor validation,
             # but included for robustness matching C# implicit behaviour if validation was bypassed.
             # C# returns default 100 if lat doesn't fall in ranges, Python will raise error earlier.
             raise ValueError(f"Latitude {lat_degrees} is outside the defined ranges for section counts.")


    def to_lat_long(self):
        """
        Converts this Federal Permit System location to a LatLongCoordinate.

        Requires the FederalPermitSystemConverter class to be implemented.
        """
        # Assuming FederalPermitSystemConverter.to_lat_long handles the conversion logic
        return FederalPermitSystemConverter.to_lat_long(self)

    def __eq__(self, other):
        """Checks if two FederalPermitSystem objects are equal."""
        if not isinstance(other, FederalPermitSystem):
            return NotImplemented
        return (self.unit == other.unit and
                self.section == other.section and
                self.lat_degrees == other.lat_degrees and
                self.lat_minutes == other.lat_minutes and
                self._lon_degrees == other._lon_degrees and # Compare internal negative longitude
                self.lon_minutes == other.lon_minutes)

    def __ne__(self, other):
        """Checks if two FederalPermitSystem objects are not equal."""
        return not self == other

    def __hash__(self):
        """Calculates the hash code for the FederalPermitSystem object."""
        # Mimicking the C# XOR hashing approach
        return operator.xor(hash(self.lon_minutes),
               operator.xor(hash(self._lon_degrees), # Hash internal negative longitude
               operator.xor(hash(self.lat_minutes),
               operator.xor(hash(self.lat_degrees),
               operator.xor(hash(self.section),
                            hash(self.unit))))))

    @staticmethod
    def parse(location):
        """
        Parses a string representation into a FederalPermitSystem object.
        Expected format: U-SS-DDMM-dddmm (e.g., L-55-7030-13600)

        Args:
            location (str): The string to parse.

        Returns:
            FederalPermitSystem: The parsed object.

        Raises:
            CoordinateParseException: If the string format is invalid.
        """
        if location is None:
            raise CoordinateParseException("Can not parse a null location.")

        location = location.strip()
        if not location:
            raise CoordinateParseException("Can not parse an empty location.")

        parts = location.split('-')

        if len(parts) != 4:
            raise CoordinateParseException("Location must have 4 parts separated by hyphens (e.g., U-SS-DDMM-dddmm).")

        if len(parts[0]) != 1:
            raise CoordinateParseException("Unit part must have length 1.")
        if len(parts[1]) != 2:
            raise CoordinateParseException("Section part must have length 2.")
        if len(parts[2]) != 4:
            raise CoordinateParseException("Latitude part must have length 4 (DDMM).")
        if len(parts[3]) != 5:
            raise CoordinateParseException("Longitude part must have length 5 (dddmm).")

        unit = parts[0][0] # Already checked length is 1

        try:
            section = int(parts[1])
            lat_degrees = int(parts[2][0:2])
            lat_minutes = int(parts[2][2:4])
            lon_degrees = int(parts[3][0:3])
            lon_minutes = int(parts[3][3:5])
        except ValueError as e:
            raise CoordinateParseException(f"Error parsing numeric parts: {e}")

        # The constructor will perform the final validation on ranges etc.
        return FederalPermitSystem(unit, section, lat_degrees, lat_minutes, lon_degrees, lon_minutes)

    def __str__(self):
        """
        Returns the string representation in the format U-SS-DDMM-dddmm.
        """
        # Access the public property lon_degrees which returns the positive value
        return f"{self.unit}-{self.section:02d}-{self.lat_degrees:02d}{self.lat_minutes:02d}-{self.lon_degrees:03d}{self.lon_minutes:02d}"

    # Add __repr__ for better debugging representation
    def __repr__(self):
        return (f"FederalPermitSystem(unit='{self.unit}', section={self.section}, "
                f"lat_degrees={self.lat_degrees}, lat_minutes={self.lat_minutes}, "
                f"lon_degrees={self.lon_degrees}, lon_minutes={self.lon_minutes})")
