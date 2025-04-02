import re
from enum import Enum
from SurveyGridLibrary.CoordinateParseException import CoordinateParseException
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.FederalPermitSystem import FederalPermitSystem
from SurveyGridLibrary.BcNtsGridSystem import BcNtsGridSystem
from SurveyGridLibrary.DlsSystem import DlsSystem

class SurveySystemCode(Enum):
    """
    A one-character code in position 1 indicating the Survey System by which the well is located, and
    the set of location items that will follow in Identifier positions 4 – 15.
    """
    DOMINION_LAND_SURVEY = 1
    NATIONAL_TOPOGRAPHIC_SERIES = 2
    FEDERAL_PERMIT_SYSTEM = 3
    GEODETIC_COORDINATES = 4

class UniqueWellIdentifier:
    """
    Represents a Unique Well Identifier (UWI) used in various Canadian land survey systems.

    The UWI is a standard 16-character code defining the bottom hole location and significant drilling/completion events.
    The format and interpretation depend on the survey system indicated by the first character.

    DLS Example (Dominion Land Survey): 100143608517W600 (for location 14-36-85-17 W6)
    NTS Example (National Topographic Series): 200D096H094A1500 (for location d-96-H/94-A-15)

    See C# documentation for detailed breakdown of character positions for each system.
    """
    _UWI_LENGTH = 16

    # Private constructor, use the static parse method instead.
    def __init__(self, uwi_chars, survey_system):
        if not isinstance(uwi_chars, list) or len(uwi_chars) != self._UWI_LENGTH:
            raise ValueError("Internal error: uwi_chars must be a list of 16 characters.")
        if not isinstance(survey_system, SurveySystemCode):
             raise ValueError("Internal error: survey_system must be a SurveySystemCode enum member.")
        self._id = uwi_chars # Store as a list of characters, similar to char[]
        self._survey_system = survey_system

    @staticmethod
    def parse(uwi):
        """
        Parses a string representation of a Unique Well Identifier.

        Args:
            uwi (str): The 16-character UWI string.

        Returns:
            UniqueWellIdentifier: An instance representing the parsed UWI.

        Raises:
            CoordinateParseException: If the UWI string is invalid or uses an unsupported format.
            TypeError: If uwi is not a string.
            ValueError: If uwi is None.
        """
        if uwi is None:
            raise ValueError("UWI cannot be None.") # Match ArgumentNullException
        if not isinstance(uwi, str):
             raise TypeError("UWI must be a string.") # Added type check
        if not uwi: # Check for empty string after ensuring it's a string
            raise CoordinateParseException("UWI is null or empty.")
        if len(uwi) != UniqueWellIdentifier._UWI_LENGTH:
            raise CoordinateParseException(f"UWI must contain {UniqueWellIdentifier._UWI_LENGTH} characters.")

        first_char = uwi[0]
        uwi_chars = list(uwi) # Convert to list of chars for internal storage

        if first_char == '1':
            return UniqueWellIdentifier._parse_dls(uwi_chars)
        elif first_char == '2':
            return UniqueWellIdentifier._parse_nts(uwi_chars)
        elif first_char == '3':
            return UniqueWellIdentifier._parse_federal(uwi_chars)
        elif first_char == '4':
            return UniqueWellIdentifier._parse_geodetic(uwi_chars)
        else:
            raise CoordinateParseException("Expected UWI to start with '1', '2', '3', or '4'.")

    @staticmethod
    def _parse_geodetic(uwi_chars):
        # C# checks uwi[0] != '4' (already done in parse) and uwi[14] != '0'
        if uwi_chars[14] != '0':
            raise CoordinateParseException("The 15th character must be zero for Geodetic UWI.")
        return UniqueWellIdentifier(uwi_chars, SurveySystemCode.GEODETIC_COORDINATES)

    @staticmethod
    def _parse_federal(uwi_chars):
        # C# checks uwi[0] != '3' (already done in parse)
        # No check on character 15 in the C# _ParseFederal
        return UniqueWellIdentifier(uwi_chars, SurveySystemCode.FEDERAL_PERMIT_SYSTEM)

    @staticmethod
    def _parse_nts(uwi_chars):
        # C# checks uwi[0] != '2' (already done in parse)
        # C# comments out the check for uwi[1] != '0', but the description says it's always '0'.
        # Following C# code behavior by commenting out the check below.
        # If strict validation according to description is needed later, this can be uncommented.
        # if uwi_chars[1] != '0':
        #    raise CoordinateParseException("The second character must be zero for NTS UWI.")
        if uwi_chars[14] != '0':
            raise CoordinateParseException("The 15th character must be zero for NTS UWI.")
        return UniqueWellIdentifier(uwi_chars, SurveySystemCode.NATIONAL_TOPOGRAPHIC_SERIES)

    @staticmethod
    def _parse_dls(uwi_chars):
        # C# checks uwi[0] != '1' (already done in parse)
        # C# comments out the check for uwi[1] != '0', mentioning Sask wells. Following C# behavior.
        # if uwi_chars[1] != '0':
        #    raise CoordinateParseException("The second character must be zero for DLS UWI.")
        if uwi_chars[14] != '0':
            raise CoordinateParseException("The 15th character must be zero for DLS UWI.")
        return UniqueWellIdentifier(uwi_chars, SurveySystemCode.DOMINION_LAND_SURVEY)

    @property
    def survey_system(self):
        """Gets the survey system code for this UWI."""
        return self._survey_system

    @property
    def location_exception_code(self):
        """
        Gets the Location Exception Code (characters 2-3).
        - DLS: Indicates chronological sequence (0=first well, 2=second, etc.).
        - NTS: Indicates chronological sequence (0=first well, 2=second, etc.).
        - Federal: Not explicitly defined in C# comments for this property.
        - Geodetic: Not explicitly defined in C# comments for this property.
        """
        return "".join(self._id[1:3])

    @property
    def legal_survey_system(self):
        """Gets the legal survey system part of the UWI (characters 4-15)."""
        return "".join(self._id[3:15])

    @property
    def event_sequence_code(self):
        """
        Gets the Event Sequence Code (character 16).
        Indicates significant drilling/completion operations (0=initial, 2-9=subsequent events).
        """
        return self._id[15]

    def to_lat_long_coordinate(self):
        """
        Converts the UWI to a Latitude/Longitude coordinate.

        This requires the corresponding survey system classes (DlsSystem, BcNtsGridSystem, etc.)
        to be implemented with a `to_lat_long()` method.

        Returns:
            LatLongCoordinate: The calculated latitude and longitude.

        Raises:
            NotImplementedError: If conversion for the specific survey system is not implemented.
            CoordinateParseException: If the UWI components are invalid for conversion.
        """
        system = self.survey_system
        if system == SurveySystemCode.DOMINION_LAND_SURVEY:
            dls = self._extract_dls_system()
            # Assumes DlsSystem instance has a 'to_lat_long' method returning LatLongCoordinate
            return dls.to_lat_long()
        elif system == SurveySystemCode.GEODETIC_COORDINATES:
            # Assumes LatLongCoordinate can be constructed directly from lat/lon floats
            return self._geodetic_to_lat_long()
        elif system == SurveySystemCode.FEDERAL_PERMIT_SYSTEM:
            fps = self._extract_federal_permit_system()
            # Assumes FederalPermitSystem instance has a 'to_lat_long' method returning LatLongCoordinate
            return fps.to_lat_long()
        elif system == SurveySystemCode.NATIONAL_TOPOGRAPHIC_SERIES:
            nts = self._extract_bc_nts_grid_system()
            # Assumes BcNtsGridSystem instance has a 'to_lat_long' method returning LatLongCoordinate
            return nts.to_lat_long()
        else:
            # Should not happen if parse logic is correct, but defensive check.
            raise NotImplementedError(f"Lat/Long conversion not implemented for survey system: {system}")

    # These private extraction methods mirror the C# static private helpers,
    # but are instance methods here as they operate on self._id.
    # They assume the corresponding Python classes exist and can be instantiated
    # with the extracted values.

    def _extract_federal_permit_system(self):
        """
        Parses Federal Permit System components from the internal UWI characters.
        Assumes FederalPermitSystem(unit_char, section, lat_deg, lat_min, lon_deg, lon_min) exists.
        Expected constructor signature:
        FederalPermitSystem(unit: str, section: int, lat_deg: int, lat_min: int, lon_deg: int, lon_min: int)
        """
        try:
            unit = self._id[3]
            section = int("".join(self._id[4:6]))
            lat_degrees = int("".join(self._id[6:8]))
            lat_minutes = int("".join(self._id[8:10]))
            lon_degrees = int("".join(self._id[10:13]))
            lon_minutes = int("".join(self._id[13:15]))
            # Instantiate the external FederalPermitSystem class
            return FederalPermitSystem(unit, section, lat_degrees, lat_minutes, lon_degrees, lon_minutes)
        except (ValueError, IndexError) as e:
            raise CoordinateParseException(f"Invalid Federal Permit System UWI format: {e}")

    def _extract_bc_nts_grid_system(self):
        """
        Parses BC NTS Grid System components from the internal UWI characters.
        Assumes BcNtsGridSystem(quarter_unit, unit, block, series, map_area, sheet) exists.
        Expected constructor signature:
        BcNtsGridSystem(quarter_unit: str, unit: int, block: str, series: int, map_area: str, sheet: int)
        """
        try:
            quarter_unit = self._id[3]
            unit = int("".join(self._id[4:7]))
            block = self._id[7]
            series = int("".join(self._id[8:11]))
            map_area = self._id[11]
            sheet = int("".join(self._id[12:14]))
            # Instantiate the external BcNtsGridSystem class
            return BcNtsGridSystem(quarter_unit, unit, block, series, map_area, sheet)
        except (ValueError, IndexError) as e:
            raise CoordinateParseException(f"Invalid BC NTS Grid System UWI format: {e}")

    def _extract_dls_system(self):
        """
        Parses DLS System components from the internal UWI characters.
        Assumes DlsSystem(legal_subdivision, section, township, range, meridian) exists.
        Expected constructor signature (types are int, DlsSystem should handle conversion if needed):
        DlsSystem(legal_subdivision: int, section: int, township: int, range_val: int, meridian: int)
        """
        try:
            subdivision = int("".join(self._id[3:5]))
            section = int("".join(self._id[5:7]))
            township = int("".join(self._id[7:10]))
            range_val = int("".join(self._id[10:12]))
            # Direction self._id[12] is ignored in C# extraction, only meridian number is used
            meridian = int(self._id[13])
            # Instantiate the external DlsSystem class
            # Note: C# DlsSystem constructor takes bytes, Python int used here. Ensure DlsSystem handles this.
            return DlsSystem(subdivision, section, township, range_val, meridian)
        except (ValueError, IndexError) as e:
            raise CoordinateParseException(f"Invalid DLS UWI format: {e}")

    def _geodetic_to_lat_long(self):
        """
        Parses Lat/Long components from the internal Geodetic UWI characters.
        Assumes LatLongCoordinate(latitude, longitude) exists.
        Expected constructor signature: LatLongCoordinate(latitude: float, longitude: float)
        """
        try:
            # Format: 4xxLAT.XXX LON.XXX0E -> indices 3,4.5,6,7 for lat; 8,9,10.11,12,13 for lon
            # Example C# extraction implies: 4_ _ LAT _ _ _ LON _ _ _ _ _ _ 0 E
            # Chars:  0 1 2  3  4 5 6 7   8  9 10 11 12 13 14 15
            # C#: slat = "" + uwi._id[3] + uwi._id[4] + "." + uwi._id[5] + uwi._id[6] + uwi._id[7];
            # C#: slon = "" + uwi._id[8] + uwi._id[9] + uwi._id[10] + "." + uwi._id[11] + uwi._id[12] + uwi._id[13];
            lat_str = f"{self._id[3]}{self._id[4]}.{self._id[5]}{self._id[6]}{self._id[7]}"
            lon_str = f"{self._id[8]}{self._id[9]}{self._id[10]}.{self._id[11]}{self._id[12]}{self._id[13]}"

            lat = float(lat_str)
            lon = float(lon_str) # Assuming longitude is positive West based on C# code.
                                  # Standard GIS often uses negative West. Confirm convention if using externally.
                                  # No sign change is applied here, matching C# behavior.

            # Instantiate the external LatLongCoordinate class
            return LatLongCoordinate(lat, lon)
        except (ValueError, IndexError) as e:
             raise CoordinateParseException(f"Invalid Geodetic UWI format: {e}")


    def __eq__(self, other):
        """Checks if two UniqueWellIdentifier instances are equal."""
        if not isinstance(other, UniqueWellIdentifier):
            return NotImplemented # Use NotImplemented for comparisons with unrelated types
        # Compare survey system and the character list content
        return self._survey_system == other._survey_system and self._id == other._id

    def __hash__(self):
        """Returns a hash code for this instance."""
        # Combine hash of survey system and tuple representation of the ID list
        return hash((self._survey_system, tuple(self._id)))

    def __str__(self):
        """Returns the string representation of the UWI."""
        return "".join(self._id)

    def __repr__(self):
        """Returns a developer-friendly representation."""
        return f"UniqueWellIdentifier(uwi='{''.join(self._id)}', system={self._survey_system.name})"
