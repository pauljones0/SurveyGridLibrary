import csv
import gzip
import struct
import sys
from typing import Optional, Generator, Any

# Assuming dls_section_row.py and interpolator.py are in the same directory or accessible
from dls_section_row import DlsSectionRow 
import interpolator

# --- Configuration ---
INPUT_CSV_PATH = "DLSSections.csv"
OUTPUT_GZ_PATH = "coordinates.gz"
# 'H' for unsigned short (2 bytes), 'f' for float (4 bytes)
# '>' denotes big-endian. Choose based on consumer requirements.
# C# BinaryWriter default is typically little-endian ('<'), but big-endian is common for network/cross-platform.
KEY_FORMAT = '>H' # Format for the packed key (ushort)
COORD_FORMAT = '>f' # Format for each coordinate (float)
# ---------------------

def safe_float(value: Optional[str]) -> float:
    """Convert string to float, returning 0.0 for None or empty strings."""
    if value is None or value == '':
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def safe_int(value: Optional[str], field_name: str) -> int:
    """Convert string to int, raising ValueError for invalid or missing values."""
    if value is None or value == '':
         raise ValueError(f"Missing or empty value for required field: {field_name}")
    try:
        return int(value)
    except (ValueError, TypeError):
         raise ValueError(f"Invalid integer value '{value}' for field: {field_name}")

def read_dls_sections(filename: str) -> Generator[dict[str, Any], None, None]:
    """
    Reads the DLSSections CSV file row by row.

    Assumes the CSV file has a header row matching the expected field names 
    (Meridian, Range, Township, Section, SELat, SELon, etc.).
    """
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as infile:
            # Adjust dialect/parameters if needed based on exact CSV format
            reader = csv.DictReader(infile)
            # Check for required header columns (optional but good practice)
            required_headers = ['Meridian', 'Range', 'Township', 'Section']
            if not all(h in reader.fieldnames for h in required_headers):
                missing = [h for h in required_headers if h not in reader.fieldnames]
                raise ValueError(f"CSV missing required headers: {missing}")
            
            yield from reader
    except FileNotFoundError:
        print(f"Error: Input file not found at {filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file {filename}: {e}", file=sys.stderr)
        sys.exit(1)

def process_coordinates():
    """
    Reads DLS section data from CSV, processes coordinates (interpolating 
    where necessary), and writes the results to a compressed binary file.
    
    Output Format (coordinates.gz):
    - Compressed using gzip.
    - Contains records in sequence.
    - Each township starts with a Key (ushort, big-endian by default).
    - Followed by 36 Section coordinate blocks.
    - Each coordinate block consists of 8 floats (SELat, SELon, SWLat, SWLon, 
      NWLat, NWLon, NELat, NELon), written sequentially (big-endian by default).
    """
    print(f"Starting to create {OUTPUT_GZ_PATH} from {INPUT_CSV_PATH}...")

    expected_section_counter = 0
    last_key = 0 # Use 0 as initial value, assuming 0 is not a valid packed key

    try:
        # Use gzip.open for writing compressed data directly
        with gzip.open(OUTPUT_GZ_PATH, 'wb', compresslevel=1) as outfile: # compresslevel=1 for fastest
            
            # Use enumerate to get a row index (starting from 1 for data rows)
            for row_index, row_dict in enumerate(read_dls_sections(INPUT_CSV_PATH), start=1):
                try:
                    # --- Data Extraction and Validation ---
                    meridian = safe_int(row_dict.get('Meridian'), 'Meridian')
                    range_val = safe_int(row_dict.get('Range'), 'Range') # Renamed from 'range'
                    township = safe_int(row_dict.get('Township'), 'Township')
                    section = safe_int(row_dict.get('Section'), 'Section')

                    # Check section sequence
                    if section != expected_section_counter % 36 + 1:
                        raise ValueError(f"Unexpected section number. Expected {expected_section_counter % 36 + 1}, got {section} "
                                         f"for M={meridian}, R={range_val}, T={township}")

                    # --- Key Calculation and Writing ---
                    # Key: 000 | 000000 | 0000000 (Meridian | Range | Township)
                    key = (meridian << 13) | (range_val << 7) | township
                    if key != last_key:
                        # Pack key as unsigned short (2 bytes), big-endian
                        outfile.write(struct.pack(KEY_FORMAT, key))
                        last_key = key

                    # --- Coordinate Block Processing ---
                    block = [
                        safe_float(row_dict.get('SELat')), safe_float(row_dict.get('SELon')),
                        safe_float(row_dict.get('SWLat')), safe_float(row_dict.get('SWLon')),
                        safe_float(row_dict.get('NWLat')), safe_float(row_dict.get('NWLon')),
                        safe_float(row_dict.get('NELat')), safe_float(row_dict.get('NELon')),
                    ]

                    # Count valid corners (pairs with non-zero lat or lon)
                    count = 4
                    if block[0] == 0.0 and block[1] == 0.0: count -= 1
                    if block[2] == 0.0 and block[3] == 0.0: count -= 1
                    if block[4] == 0.0 and block[5] == 0.0: count -= 1
                    if block[6] == 0.0 and block[7] == 0.0: count -= 1

                    # --- Coordinate Validation (Pre-Interpolation) ---
                    # Winding order checks (ensure coordinates are generally sensible)
                    if block[0] != 0.0 and block[6] != 0.0 and block[0] > block[6]: # SE Lat > NE Lat
                        raise ValueError("Bad Coords: SE Lat > NE Lat")
                    if block[2] != 0.0 and block[4] != 0.0 and block[2] > block[4]: # SW Lat > NW Lat
                        raise ValueError("Bad Coords: SW Lat > NW Lat")
                    if block[1] != 0.0 and block[3] != 0.0 and block[1] < block[3]: # SE Lon < SW Lon
                        raise ValueError("Bad Coords: SE Lon < SW Lon")
                    if block[7] != 0.0 and block[5] != 0.0 and block[7] < block[5]: # NE Lon < NW Lon
                        raise ValueError("Bad Coords: NE Lon < NW Lon")
                    
                    # --- Interpolation ---
                    if count > 0 and count < 4:
                        if count == 1:
                            block = interpolator.interpolate1(township, block)
                        elif count == 2:
                            block = interpolator.interpolate2(township, block)
                        elif count == 3:
                            block = interpolator.interpolate3(block)

                    # --- Coordinate Validation (Post-Interpolation) ---
                    if count > 0:
                        # Check for zeros after interpolation (shouldn't happen if interpolation worked)
                        if any(coord == 0.0 for coord in block):
                            raise ValueError("Interpolated block has unexpected zero coordinate")
                        # Check latitude order again
                        if block[0] > block[6] or block[2] > block[4]:
                             raise ValueError("Interpolated block has flipped latitude values")
                        # Check longitude order again
                        if block[1] < block[3] or block[7] < block[5]:
                             raise ValueError("Interpolated block has flipped longitude values")

                    # --- Writing Coordinates ---
                    # Pack 8 floats, big-endian
                    outfile.write(struct.pack(COORD_FORMAT * 8, *block))
                    
                    expected_section_counter += 1

                except (ValueError, TypeError, KeyError) as e:
                    # Add more context to errors from specific rows using the enumerated index
                    print(f"Error processing data row {row_index} (M={row_dict.get('Meridian')}, R={row_dict.get('Range')}, T={row_dict.get('Township')}, S={row_dict.get('Section')}): {e}", file=sys.stderr)
                    sys.exit(1)
                except Exception as e: # Catch other unexpected errors
                    # Use the enumerated index here as well
                    print(f"Unexpected error processing data row {row_index}: {e}", file=sys.stderr)
                    sys.exit(1)

    except IOError as e:
        print(f"Error writing to output file {OUTPUT_GZ_PATH}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e: # Catch other unexpected errors during file handling
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    print("Done.")

if __name__ == "__main__":
    process_coordinates() 