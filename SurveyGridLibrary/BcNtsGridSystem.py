import re
from CoordinateParseException import CoordinateParseException
from LatLongCoordinate import LatLongCoordinate
from BcNtsGridSystemConverter import BcNtsGridSystemConverter

class BcNtsGridSystem:
    def __init__(self, quarter_unit, unit, block, series, map_area, sheet):
        if not isinstance(quarter_unit, str) or len(quarter_unit) != 1 or not ('A' <= quarter_unit.upper() <= 'D'):
            raise ValueError("Quarter unit must be a single character in the range A-D")
        if not isinstance(unit, int) or not (1 <= unit <= 100):
            raise ValueError("Unit must be an integer in the range 1-100")
        if not isinstance(block, str) or len(block) != 1 or not ('A' <= block.upper() <= 'L'):
            raise ValueError("Block must be a single character in the range A-L")
        if not isinstance(series, int) or not (82 <= series <= 114):
            raise ValueError("Series must be an integer in the range 82-114")
        if not isinstance(map_area, str) or len(map_area) != 1 or not ('A' <= map_area.upper() <= 'P'):
            raise ValueError("Map Area must be a single character in the range A-P")
        if not isinstance(sheet, int) or not (1 <= sheet <= 16):
            raise ValueError("Sheet must be an integer in the range 1-16")

        self.quarter_unit = quarter_unit.upper()
        self.unit = unit
        self.block = block.upper()
        self.series = series
        self.map_area = map_area.upper()
        self.sheet = sheet

    def __eq__(self, other):
        """Checks equality between two BcNtsGridSystem objects."""
        if not isinstance(other, BcNtsGridSystem):
            # Return NotImplemented to allow other types to handle comparison
            return NotImplemented
        return (self.quarter_unit == other.quarter_unit and
                self.unit == other.unit and
                self.block == other.block and
                self.series == other.series and
                self.map_area == other.map_area and
                self.sheet == other.sheet)

    def __hash__(self):
        """Generates a hash code for the BcNtsGridSystem object."""
        # Use a tuple of the attributes for hashing
        return hash((self.quarter_unit, self.unit, self.block, self.series, self.map_area, self.sheet))

    def __str__(self):
        """Returns the string representation of the BcNtsGridSystem object. Format: Q-UUU-B/SSS-M-SS"""
        # Use f-string formatting with padding
        return f"{self.quarter_unit}-{self.unit:03d}-{self.block}/{self.series:03d}-{self.map_area}-{self.sheet:02d}"

    @staticmethod
    def parse(location):
        """Parses a string representation of a BC NTS location into a BcNtsGridSystem object."""
        if location is None:
            raise CoordinateParseException("Cannot parse a null location.")

        location_trimmed = location.strip().upper() # Standardize input
        if not location_trimmed:
            raise CoordinateParseException("Cannot parse an empty location.")

        # Split the location string by '/' or ''. Allows flexibility in separators.
        fields = re.split(r'[\/]', location_trimmed)

        first_half_str = ""
        second_half_str = ""

        if len(fields) == 1:
            # Handle cases where the primary separator '/' or '' might be missing,
            # but components are delimited differently (e.g., spaces or dashes).
            # The split_location method attempts to segment these.
            list_parts = list(BcNtsGridSystem.split_location(fields[0])) # Consume generator immediately
            # C# logic joins parts differently based on count, we replicate this behavior.
            if len(list_parts) == 6:
                # Standard expected case Q-U-B-S-M-S without '/'
                first_half_str = "-".join(list_parts[:3]) # Q-U-B
                second_half_str = "-".join(list_parts[3:]) # S-M-S
            elif len(list_parts) == 7:
                 # Allows for an optional 'exception' part like 'EX-Q-U-B'
                 # C# logic joins first 4 for first half:
                first_half_str = "-".join(list_parts[:4]) # EX-Q-U-B
                second_half_str = "-".join(list_parts[4:]) # S-M-S
            else:
                # If split_location couldn't derive 6 or 7 parts, the format is unexpected.
                raise CoordinateParseException(f"Could not parse BC NTS location from single part: '{fields[0]}'. Expected 6 or 7 components after splitting.")
        elif len(fields) == 2:
            # Standard case with '/' or '' separator: Q-U-B / S-M-S
            first_half_str = fields[0].strip()
            second_half_str = fields[1].strip()
        else:
            # More than one '/' or '' is invalid.
            raise CoordinateParseException("Location has too many parts separated by '/' or '\'.")

        # --- Parse the second half: Series-MapArea-Sheet ---
        second_parts = list(BcNtsGridSystem.split_location(second_half_str)) # Consume generator
        if len(second_parts) < 3:
            raise CoordinateParseException(f"BC NTS second part '{second_half_str}' must have at least Series-MapArea-Sheet.")

        # Parse Series (Integer 82-114)
        series_str = second_parts[0]
        try:
            series = int(series_str)
        except ValueError:
            raise CoordinateParseException(f"Series '{series_str}' is not a valid integer.")
        # Defined valid series values (Use a set for efficient 'in' check)
        valid_series = {82, 83, 92, 93, 94, 102, 103, 104}
        if series not in valid_series:
            # Provide sorted list in error message for clarity
            raise CoordinateParseException(f"Series {series} must be one of {sorted(list(valid_series))}.")

        # Parse Map Area (Char A-P)
        map_area_str = second_parts[1]
        if len(map_area_str) != 1:
            raise CoordinateParseException(f"Map Area '{map_area_str}' is an invalid length, expected one character.")
        map_area = map_area_str[0]
        # Fix common OCR/typing mistakes (0 -> O, 1 -> I) consistent with C#
        if map_area == '0': map_area = 'O'
        if map_area == '1': map_area = 'I'
        if not ('A' <= map_area <= 'P'):
            raise CoordinateParseException(f"Map Area '{map_area}' must be in the range A to P.")

        # Parse Map Sheet (Integer 1-16)
        sheet_str = second_parts[2]
        # Fix common mistake (I -> 1) consistent with C#
        if sheet_str == "I": sheet_str = "1"
        try:
            map_sheet = int(sheet_str)
        except ValueError:
             raise CoordinateParseException(f"Map Sheet '{sheet_str}' is not a valid integer.")
        if not (1 <= map_sheet <= 16):
            raise CoordinateParseException(f"Map Sheet {map_sheet} must be between 1 and 16.")

        # --- Parse the first half: [Exception]-QuarterUnit-Unit-Block ---
        # Note: C# parses right-to-left implicitly. We split then reverse for similar logic.
        first_parts = list(BcNtsGridSystem.split_location(first_half_str)) # Consume generator
        if len(first_parts) < 3:
            # Need at least Q, U, B
            raise CoordinateParseException(f"BC NTS first part '{first_half_str}' must have at least QuarterUnit-Unit-Block.")

        # Reverse list to process from right-to-left conceptually (Block, Unit, Quarter, [Exception])
        first_parts.reverse()

        # Parse Block (Char A-L) - Expected at index 0 after reverse
        block_str = first_parts[0]
        if len(block_str) != 1:
            raise CoordinateParseException(f"Block '{block_str}' is invalid, expected one character.")
        block = block_str[0]
        # Fix common mistake (1 -> I) consistent with C#
        if block == '1': block = 'I'
        if not ('A' <= block <= 'L'):
            raise CoordinateParseException(f"Block '{block}' must be from A to L.")

        # Parse Unit (Integer 1-100) - Expected at index 1 after reverse
        unit_str = first_parts[1]
        try:
            unit = int(unit_str)
        except ValueError:
            raise CoordinateParseException(f"Unit '{unit_str}' is not a valid integer.")
        if not (1 <= unit <= 100):
            raise CoordinateParseException(f"Unit {unit} must be in the range 1 to 100.")

        # Parse Quarter Unit (Char A-D) - Expected at index 2 or 3 after reverse
        # C# logic: Checks index 2 unless count is 4 AND index 2 looks like an exception (isalpha)
        quarter_part_index = 2 # Default index for Quarter after reversing [Block, Unit, Quarter]

        # Check if there might be an "exception" component before the quarter, similar to C# logic
        # If 4 parts exist [Block, Unit, Exception?, Quarter?] and part at index 2 is alphabetic -> Quarter is at index 3
        if len(first_parts) == 4 and first_parts[2] and first_parts[2].isalpha():
             quarter_part_index = 3 # Assume Quarter is the 4th element (index 3)

        # Validate index exists before accessing
        if quarter_part_index >= len(first_parts):
             raise CoordinateParseException(f"Could not find Quarter Unit component in '{first_half_str}'.")

        q_str = first_parts[quarter_part_index]
        if not q_str:
            # Segment exists but is empty? Invalid.
            raise CoordinateParseException("Quarter Unit component cannot be empty.")

        # Take the last character as the quarter unit (handles cases like 'CA' -> 'A') consistent with C#
        quarter = q_str[-1]
        if not ('A' <= quarter <= 'D'):
            raise CoordinateParseException(f"Quarter '{quarter}' (from '{q_str}') must be from A to D.")

        # Successfully parsed all components, create the object
        return BcNtsGridSystem(quarter, unit, block, series, map_area, map_sheet)

    @staticmethod
    def split_location(location_part):
        """
        Splits a part of the location string (e.g., 'D-96-H' or '94-A-15')
        into its alpha and numeric components, discarding separators.
        Yields each component (e.g., 'D', '96', 'H').
        """
        # Tracks the type of the current character sequence ('D' for digit, 'L' for letter, 'S' for separator/other)
        current_block_type = 'S' # Start as separator type
        buffer = '' # Accumulates current component

        for char in location_part:
            char_type = 'S' # Default to separator
            if '0' <= char <= '9':
                char_type = 'D' # Digit
            elif 'A' <= char <= 'Z': # Check against uppercase alphabet
                char_type = 'L' # Letter

            # If the type changes (e.g., from Letter to Digit, Digit to Separator, etc.)
            # and the buffer has content, yield the completed component.
            if char_type != current_block_type:
                if buffer:
                    yield buffer
                    buffer = '' # Reset buffer
                current_block_type = char_type # Update the current type

            # Add character to buffer only if it's a letter or digit
            if char_type == 'D' or char_type == 'L':
                buffer += char
            # Separators ('S') are effectively skipped (not added to buffer)

        # After loop, yield any remaining content in the buffer
        if buffer:
            yield buffer

    def to_lat_long(self) -> LatLongCoordinate:
        """
        Converts this BC NTS grid system object to an approximate LatLongCoordinate.
        Requires the BcNtsGridSystemConverter class.
        """
        # Delegates the conversion logic to the specialized converter class
        return BcNtsGridSystemConverter.to_lat_long(self)

    # Note: The C# had a second static ToLatLong method. In Python, a static method
    # can be called via the class (BcNtsGridSystem.static_to_lat_long(...)) or an
    # instance (instance.static_to_lat_long(...)), but having a separate static
    # method duplicating the instance method's call isn't typically necessary unless
    # there's a specific reason. The instance method `to_lat_long` serves the primary purpose.
    # If an explicit static version is needed, it could be:
    # @staticmethod
    # def static_to_lat_long(system: 'BcNtsGridSystem') -> LatLongCoordinate:
    #     """Static method to convert a BC NTS grid object to LatLongCoordinate."""
    #     return BcNtsGridSystemConverter.to_lat_long(system)

# --- Example Usage (Optional - uncomment to run tests) ---
# if __name__ == '__main__':
#     test_locations = [
#         "D-96-H/94-A-15",   # Standard
#         "d-096-h/094-a-015", # Lowercase, padded numbers
#         "A-1-A/82-B-1",     # Min values
#         "D-100-L/104-P-16", # Max values
#         "C-50-F\93-G-10",  # Backslash separator
#         "B-25-J 092 K 05",  # Space separators (handled by split_location)
#         "D96H94A15",        # No separators (handled by split_location)
#         "A-10-C / 083-I-09",# Mixed spacing, fixed common errors (0->O, I->1, 1->I)
#         "B-011-1/103-0-I",  # Test error fixing (1->I, 0->O, I->1)
#         "CA-75-K/94-P-12"   # Quarter Unit with Exception 'C' (takes 'A')
#     ]
#
#     print("--- Parsing Tests ---")
#     for loc_str in test_locations:
#         try:
#             nts = BcNtsGridSystem.parse(loc_str)
#             print(f"Parsed '{loc_str}' -> {nts}")
#             # Test __eq__ and __hash__ implicitly by creating equivalent object
#             nts_direct = BcNtsGridSystem(nts.quarter_unit, nts.unit, nts.block, nts.series, nts.map_area, nts.sheet)
#             if nts != nts_direct:
#                  print(f"  ERROR: Equality check failed for {nts}")
#             if hash(nts) != hash(nts_direct):
#                  print(f"  ERROR: Hash check failed for {nts}")
#         except (CoordinateParseException, ValueError) as e:
#             print(f"Error parsing '{loc_str}': {e}")
#
#     print("--- Invalid Format Tests ---")
#     invalid_locations = [
#         None, "", "   ", "D-96-H/94-A-17", "D-101-H/94-A-15", "D-96-M/94-A-15",
#         "E-96-H/94-A-15", "D-96-H/95-A-15", "D-96-H/94-Q-15", "D-96-H/94-A",
#         "D-96/94-A-15", "D-96-H/94/A-15", "InvalidData"
#     ]
#     for loc_str in invalid_locations:
#          try:
#              BcNtsGridSystem.parse(loc_str)
#              print(f"ERROR: Parsed invalid location '{loc_str}' without error.")
#          except (CoordinateParseException, ValueError, TypeError) as e: # TypeError for None
#              print(f"Correctly failed parsing '{loc_str}': {type(e).__name__}")
#
#     # Note: To test to_lat_long(), you would need the BcNtsGridSystemConverter class defined.
#     # try:
#     #     nts_for_conversion = BcNtsGridSystem.parse("D-96-H/94-A-15")
#     #     lat_long = nts_for_conversion.to_lat_long()
#     #     print(f"Converted {nts_for_conversion} to Lat/Long: {lat_long}") # Requires LatLongCoordinate.__str__
#     # except NameError:
#     #      print("Skipping Lat/Long conversion test: BcNtsGridSystemConverter not defined.")
#     # except Exception as e:
#     #      print(f"Error during Lat/Long conversion test: {e}")
