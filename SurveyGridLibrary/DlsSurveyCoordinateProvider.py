import gzip
import struct
from typing import List, Optional, Dict, Tuple, TypeVar, Type

from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.LatLongCorners import LatLongCorners

# Define a generic type variable for the singleton pattern
T = TypeVar('T', bound='DlsSurveyCoordinateProvider')

class DlsSurveyCoordinateProvider:
    """
    Provides access to Dominion Land Survey (DLS) corner coordinates.

    This class loads coordinate data from a compressed file and allows querying
    for township boundaries, section markers, and township markers based on
    township, range, and meridian identifiers. It implements the singleton
    pattern to ensure only one instance loads the data.

    Note: Unlike the C# version which loads data from an embedded assembly
    resource, this Python version loads data from a file path specified in
    `load_data`. Ensure the `coordinates.gz` file is accessible at the
    expected path relative to where the script is run or adjust the path
    accordingly.
    """
    _instance: Optional['DlsSurveyCoordinateProvider'] = None
    _pad_lock = object()
    _offsets: Dict[int, Tuple[float, ...]]

    def __new__(cls: Type[T]) -> T:
        """Creates or returns the singleton instance of the class."""
        if cls._instance is None:
            with cls._pad_lock:
                # Double-check locking
                if cls._instance is None:
                    cls._instance = super(DlsSurveyCoordinateProvider, cls).__new__(cls)
                    cls._instance._offsets = {}
                    cls._instance.load_data()
        return cls._instance

    def load_data(self) -> None:
        """
        Loads township coordinate data from a compressed file.

        Reads a gzipped file containing township data, unpacks it, and stores
        it in memory keyed by a composite key derived from meridian, range,
        and township numbers.

        Raises:
            FileNotFoundError: If the coordinate data file cannot be found.
            Exception: If the loaded data does not contain the expected number
                       of townships.
        """
        township_data_bytes = 1154  # Size of data block for one township (2 byte key + 288 * 4 byte floats)
        township_count = 15583      # Expected number of townships in the data file
        floats_per_township = 288   # 36 sections * 4 corners * 2 floats (lat, long)

        # Assumes 'coordinates.gz' is in a 'SurveyGridLibrary' subdirectory
        # relative to the execution path. Adjust if necessary.
        resource_name = "SurveyGridLibrary/coordinates.gz"
        try:
            with gzip.open(resource_name, 'rb') as resource_stream:
                while True:
                    buffer = resource_stream.read(township_data_bytes)
                    if not buffer:
                        break
                    if len(buffer) < township_data_bytes:
                        # Handle potentially incomplete read at EOF, though gzip.open
                        # should ideally handle this. This check guards against corruption.
                        print(f"Warning: Read incomplete buffer of size {len(buffer)} from {resource_name}, expected {township_data_bytes}. Stopping.")
                        break

                    # Key: ushort (2 bytes), little-endian '<'
                    # Value: 288 floats (4 bytes each), little-endian '<'
                    key = struct.unpack('<H', buffer[:2])[0]
                    # Ensure the buffer slice is correct size for unpacking
                    township_float_bytes = buffer[2:]
                    if len(township_float_bytes) == floats_per_township * 4:
                         township_tuple = struct.unpack(f'<{floats_per_township}f', township_float_bytes)
                         self._offsets[key] = township_tuple
                    else:
                        print(f"Warning: Incorrect data size for township key {key}. Expected {floats_per_township * 4} bytes, got {len(township_float_bytes)}. Skipping.")


        except FileNotFoundError:
            raise FileNotFoundError(f"Coordinate data file not found at {resource_name}. Please ensure the file exists and the path is correct.")

        if len(self._offsets) != township_count:
            # This exception matches the C# version's behavior.
            raise Exception(f"Data file {resource_name} did not contain the expected number of townships. Loaded {len(self._offsets)}, expected {township_count}.")

    def township_markers(self, township: int, range_val: int, meridian: int) -> Optional[List[LatLongCorners]]:
        """
        Returns the SE, SW, NW, NE corners for all 36 sections within a township.

        Args:
            township: The township number (typically 1-126).
            range_val: The range number (typically 1-34).
            meridian: The meridian number (W4, W5, W6, etc., represented numerically, e.g., 4, 5, 6).

        Returns:
            A list of LatLongCorners objects, one for each section (1-36),
            or None if the township data is not found. The list index corresponds
            to (section_number - 1).
        """
        key = (meridian << 13) | (range_val << 7) | township
        if key not in self._offsets:
            return None

        township_floats = self._offsets[key]
        corners = []
        num_sections = 36
        floats_per_section = 8 # SE(lat,lon), SW(lat,lon), NW(lat,lon), NE(lat,lon)
        total_floats = num_sections * floats_per_section # Should be 288

        # Check if the retrieved float tuple has the expected length
        if len(township_floats) != total_floats:
             print(f"Warning: Unexpected number of floats ({len(township_floats)}) for township key {key}. Expected {total_floats}. Returning potentially incomplete data.")
             # Decide how to handle this - return partial data, None, or raise error?
             # For now, proceed but limit loop to available data.
             total_floats = len(township_floats)


        for offset in range(0, total_floats, floats_per_section):
            # Ensure we don't read past the end of the available floats
            if offset + floats_per_section > len(township_floats):
                break

            se = self.lat_long_coordinate(township_floats, offset + 0)
            sw = self.lat_long_coordinate(township_floats, offset + 2)
            nw = self.lat_long_coordinate(township_floats, offset + 4)
            ne = self.lat_long_coordinate(township_floats, offset + 6)
            corners.append(LatLongCorners(se, sw, nw, ne))
        return corners

    def township_boundary(self, township: int, range_val: int, meridian: int) -> Optional[LatLongCorners]:
        """
        Calculates the extreme outer boundary corners (SE, SW, NW, NE) for a given township.

        It iterates through all coordinate pairs in the township data to find the
        points that define the overall extent.

        Args:
            township: The township number.
            range_val: The range number.
            meridian: The meridian number.

        Returns:
            A LatLongCorners object representing the extreme boundary, or None
            if the township data is not found.
        """
        key = (meridian << 13) | (range_val << 7) | township
        if key not in self._offsets:
            return None

        township_floats = self._offsets[key]
        se: Optional[LatLongCoordinate] = None
        sw: Optional[LatLongCoordinate] = None
        ne: Optional[LatLongCoordinate] = None
        nw: Optional[LatLongCoordinate] = None

        # Iterate through all coordinate pairs (latitude, longitude)
        # There are 288 floats total, so 144 pairs.
        # The loop range should go up to 288 (exclusive) with a step of 2.
        for i in range(0, len(township_floats), 2):
            lat = township_floats[i]
            # Check bounds before accessing i+1
            if i + 1 >= len(township_floats):
                break # Avoid index out of bounds if float count is odd (shouldn't happen)
            lon = township_floats[i + 1]

            # Skip invalid coordinates (0, 0 often indicates missing data point)
            if lat == 0.0 and lon == 0.0:
                continue

            current_coord = LatLongCoordinate(lat, lon)

            # Update SE: minimum latitude, maximum longitude
            if se is None or (lat < se.latitude) or (lat == se.latitude and lon > se.longitude):
                 # Simplified logic based on C#: find min lat, then max lon among those with min lat seems complex.
                 # The C# logic: `lat < se.Value.Latitude && lon > se.Value.Longitude` seems potentially flawed
                 # as it requires *both* lower latitude and greater longitude simultaneously.
                 # Let's assume the intent is to find the point furthest South-East.
                 # A common way is min lat, max lon, but let's try to match C# logic first, then revise if needed.
                 # Sticking to C# logic:
                 if se is None or (lat < se.latitude and lon > se.longitude): # Requires strictly smaller lat AND strictly greater lon
                    se = current_coord
                 # Re-evaluating standard boundary finding might be better:
                 # if se is None or lat < se.latitude or (lat == se.latitude and lon > se.longitude):
                 #    se = current_coord

            # Update SW: minimum latitude, minimum longitude
            if sw is None or (lat < sw.latitude) or (lat == sw.latitude and lon < sw.longitude):
                 # C# logic: `lat < sw.Value.Latitude && lon < sw.Value.Longitude`
                 if sw is None or (lat < sw.latitude and lon < sw.longitude):
                    sw = current_coord
                 # Standard logic:
                 # if sw is None or lat < sw.latitude or (lat == sw.latitude and lon < sw.longitude):
                 #    sw = current_coord


            # Update NE: maximum latitude, maximum longitude
            if ne is None or (lat > ne.latitude) or (lat == ne.latitude and lon > ne.longitude):
                 # C# logic: `lat > ne.Value.Latitude && lon > ne.Value.Longitude`
                 if ne is None or (lat > ne.latitude and lon > ne.longitude):
                    ne = current_coord
                 # Standard logic:
                 # if ne is None or lat > ne.latitude or (lat == ne.latitude and lon > ne.longitude):
                 #    ne = current_coord

            # Update NW: maximum latitude, minimum longitude
            if nw is None or (lat > nw.latitude) or (lat == nw.latitude and lon < nw.longitude):
                 # C# logic: `lat > nw.Value.Latitude && lon < nw.Value.Longitude`
                 if nw is None or (lat > nw.latitude and lon < nw.longitude):
                    nw = current_coord
                 # Standard logic:
                 # if nw is None or lat > nw.latitude or (lat == nw.latitude and lon < nw.longitude):
                 #    nw = current_coord

        # It seems the C# logic for finding boundary corners might be slightly unconventional.
        # The standard approach is typically min/max latitude combined with min/max longitude.
        # The conditions like `lat < se.Value.Latitude && lon > se.Value.Longitude` might miss
        # the true corner if no single point satisfies both conditions relative to the current candidate.
        # For now, I've kept the direct translation of the C# logic commented alongside standard logic.
        # If boundary results seem incorrect, revisiting this logic is recommended.

        return LatLongCorners(se, sw, nw, ne)


    def boundary_markers(self, section: int, township: int, range_val: int, meridian: int) -> Optional[LatLongCorners]:
        """
        Returns the SE, SW, NW, NE corner coordinates for a specific section within a township.

        Args:
            section: The section number (1-36).
            township: The township number.
            range_val: The range number.
            meridian: The meridian number.

        Returns:
            A LatLongCorners object containing the coordinates for the specified
            section's corners, or None if the township or section data is not found.
        """
        if not (1 <= section <= 36):
             raise ValueError("Section number must be between 1 and 36.")

        key = (meridian << 13) | (range_val << 7) | township
        if key not in self._offsets:
            return None

        township_floats = self._offsets[key]
        floats_per_section = 8
        offset = (section - 1) * floats_per_section

        # Check if the calculated offset is valid for the loaded float data
        if offset + floats_per_section > len(township_floats):
             print(f"Warning: Calculated offset for section {section} is out of bounds for township key {key}. Available floats: {len(township_floats)}, required: {offset + floats_per_section}. Section data may be missing.")
             return None # Or handle differently, e.g., return partial corners if possible?


        # Extract coordinates using the static helper method
        se = self.lat_long_coordinate(township_floats, offset + 0)
        sw = self.lat_long_coordinate(township_floats, offset + 2)
        nw = self.lat_long_coordinate(township_floats, offset + 4)
        ne = self.lat_long_coordinate(township_floats, offset + 6)

        return LatLongCorners(se, sw, nw, ne)

    @staticmethod
    def lat_long_coordinate(township_floats: Tuple[float, ...], offset: int) -> Optional[LatLongCoordinate]:
        """
        Extracts a LatLongCoordinate from the township float tuple at a given offset.

        Args:
            township_floats: The tuple of floats representing coordinate data for a township.
            offset: The starting index in the tuple for the latitude value. Longitude
                    is expected at offset + 1.

        Returns:
            A LatLongCoordinate object if the latitude and longitude at the offset
            are non-zero, otherwise None. Returns None if offset is out of bounds.
        """
        # Check bounds to prevent IndexError
        if offset < 0 or offset + 1 >= len(township_floats):
            return None # Offset out of bounds

        lat = township_floats[offset]
        lon = township_floats[offset + 1]

        # Treat (0.0, 0.0) as an invalid or missing coordinate
        if lat == 0.0 and lon == 0.0:
            return None
        return LatLongCoordinate(lat, lon)
