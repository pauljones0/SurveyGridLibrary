import re
from SurveyGridLibrary.CoordinateParseException import CoordinateParseException
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.DlsSystemConverter import DlsSystemConverter

# TODO: Consider using an Enum or constants for ParseOptions for better type safety and clarity, similar to C#.
# Example:
# from enum import Enum, Flag, auto
# class ParseOptions(Flag):
#     NONE = 0
#     ALLOW_QUARTERS = auto()
class ParseOptions:
    ALLOW_QUARTERS = "AllowQuarters" # Simple string-based option for now

class DlsSystem:
    def __init__(self, legal_subdivision, section, township, range, meridian):
        if not (1 <= legal_subdivision <= 16):
            raise ValueError("Legal sub division must be in the range 1-16")
        if not (1 <= section <= 36):
            raise ValueError("Section must be in the range 1-36")
        if not (1 <= township <= 127):
            raise ValueError("Township must be in the range 1-127")
        # Note: C# range validation differs slightly between constructor (1-34) and parser (1-30 or 1-34 based on meridian).
        # Sticking to C# constructor validation here. Parser validation is handled in parse().
        if not (1 <= range <= 34):
            raise ValueError("Range must be in the range 1-34")
        if not (1 <= meridian <= 6):
            raise ValueError("Meridian must be in the range 1-6")

        self.legal_subdivision = legal_subdivision
        self.section = section
        self.township = township
        self.range = range
        self.meridian = meridian
        # NOTE: Direction is currently hardcoded to West ('W') as East is not supported by the parser.
        self._direction = 'W'

    @property
    def quarter(self):
        """Gets the quarter section (NE, NW, SE, SW) based on the legal subdivision."""
        # QUARTERS map to lsd as follows:
        # 13|14 | 15|16      NW | NE
        # 12|11 | 10|09
        # -------------      ---------
        # 05|06 | 07|08      SW | SE
        # 04|03 | 02|01
        if self.legal_subdivision in [1, 2, 7, 8]:
            return "SE"
        if self.legal_subdivision in [3, 4, 5, 6]:
            return "SW"
        if self.legal_subdivision in [9, 10, 15, 16]:
            return "NE"
        if self.legal_subdivision in [11, 12, 13, 14]:
            return "NW"
        return None # Should not happen with valid LSD (1-16)

    @property
    def direction(self):
        """Gets the direction identifier ('W' or 'E'). Currently only 'W' is supported."""
        return self._direction

    def to_string(self):
        """Returns the standard string representation, e.g., 04-11-082-04W6"""
        return f"{self.legal_subdivision:02}-{self.section:02}-{self.township:03}-{self.range:02}{self.direction}{self.meridian}"

    @staticmethod
    def parse(location, options=None): # options can be a set or list containing ParseOptions flags/strings
        """
        Parses a string representation of a DLS location.
        e.g., "04-11-082-04W6", "SW-12-065-04W4", "100/04-11-082-04W6/0"
        Args:
            location (str): The DLS location string.
            options (set, optional): Parsing options, e.g., {ParseOptions.ALLOW_QUARTERS}. Defaults to None.
        Returns:
            DlsSystem: A new DlsSystem instance.
        Raises:
            CoordinateParseException: If the location string is invalid.
        """
        if location is None:
            raise CoordinateParseException("Cannot parse a null location.")

        location = location.strip()
        if not location:
            raise CoordinateParseException("Cannot parse an empty location.")

        location = location.upper()

        if location.endswith("M"): # Often included, e.g., W4M
            location = location[:-1]

        # Determine meridian direction ('W' or 'E') and value
        direction_index = location.rfind('W')
        if direction_index == -1:
            direction_index = location.rfind('E')
            if direction_index == -1:
                raise CoordinateParseException("DLS location must contain a direction specifier ('W' or 'E').")

        direction_char = location[direction_index]

        # Find the meridian number (digit or 'P' for Principal) following the direction
        mer_str = ""
        for char in location[direction_index + 1:]:
            if char.isdigit() or char == 'P':
                mer_str += char
            elif mer_str: # Stop if we found digits/P and then hit something else
                break
            # Ignore non-digit/non-P characters between direction and meridian number

        if not mer_str:
             raise CoordinateParseException(f"Could not find Meridian number after direction '{direction_char}'.")

        mer = 0
        if mer_str == 'P':
            mer = 1
        else:
            try:
                mer = int(mer_str)
            except ValueError:
                raise CoordinateParseException(f"Meridian '{mer_str}' is not a valid number.")

        # C# Parser vs Constructor validation discrepancy:
        # The original C# parser checks West Meridian 1-8, but the constructor restricts it to 1-6.
        # This Python code mimics the *parser's* validation logic.
        # Consider aligning C# constructor and parser validation if possible.
        if direction_char == 'W' and not (1 <= mer <= 8):
             raise CoordinateParseException("West Meridian must be in the range 1 to 8.")

        if direction_char == 'E':
             # TODO: Implement East Meridian support if needed. Requires DlsSystemConverter updates.
             raise CoordinateParseException("East Meridian is not supported.")

        # Extract the part before the direction specifier (contains LSD, Section, Township, Range)
        location_part = location[:direction_index]

        # Split the location part from right-to-left
        # Expected order after reversing: Range, Township, Section, LSD, [optional garbage]
        parts = list(DlsSystem._split_location_string(location_part))
        if len(parts) < 4:
            raise CoordinateParseException("DLS location must have at least Range, Township, Section, and LSD components.")

        # Parse components right-to-left for robustness
        try:
            rng = int(parts[0])
            # C# Parser Range validation based on Meridian
            if mer == 1 and not (1 <= rng <= 34): # Principal Meridian
                 raise CoordinateParseException(f"Range {rng} for Meridian {mer} must be between 1 and 34.")
            elif mer != 1 and not (1 <= rng <= 30): # Other Meridians
                 raise CoordinateParseException(f"Range {rng} for Meridian {mer} must be between 1 and 30.")
        except ValueError:
            raise CoordinateParseException(f"Range '{parts[0]}' is not a valid integer.")

        try:
            twp = int(parts[1])
            if not (1 <= twp <= 126): # C# uses 1-126 in parser
                 raise CoordinateParseException(f"Township {twp} must be between 1 and 126.")
        except ValueError:
            raise CoordinateParseException(f"Township '{parts[1]}' is not a valid integer.")

        try:
            sec = int(parts[2])
            if not (1 <= sec <= 36):
                 raise CoordinateParseException(f"Section {sec} must be between 1 and 36.")
        except ValueError:
            raise CoordinateParseException(f"Section '{parts[2]}' is not a valid integer.")

        # Parse Legal Subdivision (LSD) - can be number, quarter, or contain letters
        lsd_string = parts[3]
        lsd = 0
        try:
            # Try parsing as a direct number first
            lsd = int(lsd_string)
        except ValueError:
            # Not a simple number, check for quarters if allowed
            allow_quarters = options and (ParseOptions.ALLOW_QUARTERS in options)
            if allow_quarters:
                quarter_map = {"NW": 11, "NE": 10, "SW": 6, "SE": 7} # Center LSD for each quarter
                if lsd_string in quarter_map:
                    lsd = quarter_map[lsd_string]

            # If still not found, check if it contains a number (e.g., "A06", "B2")
            if lsd == 0:
                # Extract digits from the string
                digits = "".join(filter(str.isdigit, lsd_string))
                if digits:
                    try:
                       potential_lsd = int(digits)
                       # Check if the extracted number is a valid LSD
                       if 1 <= potential_lsd <= 16:
                           lsd = potential_lsd
                    except ValueError:
                        pass # Ignore if extracted digits don't form valid int

        if not (1 <= lsd <= 16):
             raise CoordinateParseException(f"Legal Subdivision '{lsd_string}' is not valid or must be between 1 and 16.")

        # Use the constructor validation ranges (tighter than parser for Meridian)
        return DlsSystem(lsd, sec, twp, rng, mer)

    @staticmethod
    def _split_location_string(location_str):
        """Helper to split the location string by non-alphanumeric separators, working right-to-left."""
        buff = ''
        for char in reversed(location_str):
            # Accumulate alphanumeric characters
            if char.isalnum():
                buff = char + buff
            else:
                # If we hit a separator and have accumulated something, yield it
                if buff:
                    yield buff
                    buff = ''
        # Yield any remaining buffer content after the loop
        if buff:
            yield buff

    def to_lat_long(self) -> LatLongCoordinate:
        """
        Converts this DLS location to Latitude/Longitude coordinates.
        Requires the DlsSystemConverter class.
        Returns:
            LatLongCoordinate: The calculated geographic coordinate.
        """
        # Calls the static method in the converter class.
        # Assumes DlsSystemConverter.py exists and has a 'to_lat_long' static method
        # corresponding to the C# 'DlsSystemConverter.ToLatLong'.
        return DlsSystemConverter.to_lat_long(self)

    # --- Equality and Hashing ---

    def equals(self, other):
        """Checks if this DlsSystem is equal to another object."""
        if not isinstance(other, DlsSystem):
            return False
        return self == other

    def get_hash_code(self):
        """Returns a hash code for this instance."""
        # Use a tuple of the immutable fields for hashing.
        return hash((self.legal_subdivision, self.section, self.township, self.range, self.meridian, self.direction))

    def __eq__(self, other):
        """Checks equality between two DlsSystem instances."""
        if not isinstance(other, DlsSystem):
            return NotImplemented # Use NotImplemented for comparisons with unrelated types
        return (self.legal_subdivision == other.legal_subdivision and
                self.section == other.section and
                self.township == other.township and
                self.range == other.range and
                self.meridian == other.meridian and
                self.direction == other.direction) # Added direction check

    def __ne__(self, other):
        """Checks inequality between two DlsSystem instances."""
        return not self.__eq__(other)

    def __str__(self):
        """Returns the standard string representation. Alias for to_string()."""
        return self.to_string()

    def __repr__(self):
        """Returns a detailed representation for debugging."""
        return (f"DlsSystem(legal_subdivision={self.legal_subdivision}, section={self.section}, "
                f"township={self.township}, range={self.range}, meridian={self.meridian})")
