from SurveyGridLibrary.CoordinateConversionException import CoordinateConversionException
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.FederalPermitSystem import FederalPermitSystem

class FederalPermitSystemConverter:
    """
    Converts Federal Permit System coordinates to Latitude/Longitude.
    Based on the logic from the original C# implementation.
    """

    @staticmethod
    def to_lat_long(fps):
        """
        Converts a FederalPermitSystem object to a LatLongCoordinate object.

        Args:
            fps: An object representing the Federal Permit System coordinate with attributes:
                 lat_degrees (int): Latitude degrees.
                 lat_minutes (int): Latitude minutes within the degree block.
                 lon_degrees (int): Longitude degrees (assumed positive West).
                 lon_minutes (int): Longitude minutes within the degree block.
                 section (int): Section number (1-100).
                 unit (str): Unit character ('A' through 'P').

        Returns:
            LatLongCoordinate: The corresponding latitude and longitude.

        Raises:
            CoordinateConversionException: If conversion fails due to invalid input.
        """
        try:
            # Determine latitude offset based on the section's row (1-10)
            # Section numbers run 1-10 bottom to top within a column.
            modulo_section_latitude = fps.section % 10
            if modulo_section_latitude == 0:
                modulo_section_latitude = 10 # Section 10, 20, ..., 100 are in the 10th row
            latitude_section_offset_minutes = modulo_section_latitude - 1 # 0 to 9 minutes offset

            # Every section row is 1 minute tall. Add offset to base minutes.
            lat_minutes_total = float(fps.lat_minutes + latitude_section_offset_minutes)

            # Determine longitude offset based on the section's column (1-10/8/6)
            # Integer division gives the column index (0-based)
            # e.g., Section 1-10 -> col 0, 11-20 -> col 1, ...
            remain_section_longitude_index = (fps.section -1) // 10 # 0-based column index

            # Get the width of one section column in minutes
            section_minute_width = FederalPermitSystemConverter._section_minute_factor(fps.lat_degrees)

            # Calculate base longitude minutes + offset for the section column
            lon_minutes_total = float(fps.lon_minutes + (remain_section_longitude_index * section_minute_width))

            # Map Unit ('A'-'P') to 4x4 grid offsets (x, y) within the section
            # Grid starts bottom-left: A(0,0), B(1,0)... D(3,0), H(0,1)... P(0,3)
            unit_offsets = {
                'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'D': (3, 0),
                'H': (0, 1), 'G': (1, 1), 'F': (2, 1), 'E': (3, 1), # Note reversed order E-H in row 1
                'I': (0, 2), 'J': (1, 2), 'K': (2, 2), 'L': (3, 2),
                'P': (0, 3), 'O': (1, 3), 'N': (2, 3), 'M': (3, 3)  # Note reversed order M-P in row 3
            }

            if fps.unit not in unit_offsets:
                raise CoordinateConversionException(f"Unit '{fps.unit}' is out of range ('A'-'P') for conversion.")

            x, y = unit_offsets[fps.unit]

            # Add unit offsets. Each unit is 1/4 of a section dimension.
            # Latitude: Section is 1 minute tall, unit adds 0, 0.25, 0.5, or 0.75 minutes.
            lat_minutes_total += y * (1.0 / 4.0)
            # Longitude: Section width varies (section_minute_width), unit adds fraction of that width.
            lon_minutes_total += x * (section_minute_width / 4.0)

            # Convert degrees + total minutes to decimal degrees
            # Assume input lon_degrees/lon_minutes are positive West,
            # so final longitude should be negative.
            lat_decimal = fps.lat_degrees + lat_minutes_total / 60.0
            lon_decimal = -(fps.lon_degrees + lon_minutes_total / 60.0)

            # Assuming LatLongCoordinate takes decimal degrees (latitude, longitude).
            # The C# version passed degrees and minutes separately to its constructor.
            # This implementation calculates the final decimal degrees before construction.
            return LatLongCoordinate(lat_decimal, lon_decimal)

        except Exception as e:
            # Catch potential errors (e.g., attribute errors if fps is wrong type)
            # and re-raise as a domain-specific exception.
            raise CoordinateConversionException(f"Error converting FederalPermitSystem to LatLongCoordinate: {e}", e)


    @staticmethod
    def _section_minute_factor(lat_degrees):
        """
        Calculates the width of a section column in minutes of longitude based on latitude.
        This depends on the total number of sections in the grid block (60, 80, or 100).

        Args:
            lat_degrees (int): The latitude degrees.

        Returns:
            float: The width of one section column in minutes of longitude.

        Raises:
            CoordinateConversionException: If the section count for the latitude is invalid.
            NotImplementedError: If FederalPermitSystem.section_count is not implemented.
        """
        try:
            # This external function needs to be implemented based on FPS grid rules.
            # It determines if the block containing lat_degrees has 60, 80, or 100 sections wide.
            section_count = FederalPermitSystem.section_count(lat_degrees)
        except AttributeError:
             raise NotImplementedError("FederalPermitSystem.section_count(lat_degrees) is not defined.")
        except Exception as e:
             raise CoordinateConversionException(f"Error getting section count for latitude {lat_degrees}: {e}", e)


        # Grid blocks are 30' wide above 70 degrees latitude, 15' wide below 70 degrees.
        # The section width depends on this block width and the number of sections (columns).

        if lat_degrees >= 70:
            # Grid area is 30 minutes wide (longitude)
            if section_count == 60:
                # 30' / 6 columns = 5.0' per section column
                return 5.0
            elif section_count == 80:
                 # 30' / 8 columns = 3.75' per section column
                return 3.75
            elif section_count == 100:
                 # 30' / 10 columns = 3.0' per section column
                return 3.0
            else:
                raise CoordinateConversionException(f"Invalid section count {section_count} for latitude >= 70.")
        else:
            # Grid area is 15 minutes wide (longitude)
            if section_count == 60:
                 # 15' / 6 columns = 2.5' per section column
                return 2.5
            elif section_count == 80:
                 # 15' / 8 columns = 1.875' per section column
                return 1.875
            elif section_count == 100:
                 # 15' / 10 columns = 1.5' per section column
                return 1.5
            else:
                raise CoordinateConversionException(f"Invalid section count {section_count} for latitude < 70.")

# Example Usage (requires FederalPermitSystem and LatLongCoordinate classes)
# if __name__ == '__main__':
#     # Assumes FederalPermitSystem takes (lat_deg, lat_min, lon_deg, lon_min, section, unit)
#     # Assumes FederalPermitSystem.section_count is implemented
#     class MockFederalPermitSystem:
#         def __init__(self, lat_deg, lat_min, lon_deg, lon_min, sec, unit):
#             self.lat_degrees = lat_deg
#             self.lat_minutes = lat_min
#             self.lon_degrees = lon_deg
#             self.lon_minutes = lon_min
#             self.section = sec
#             self.unit = unit
#
#         @staticmethod
#         def section_count(lat_degrees):
#             # Dummy implementation for example
#             if 49 <= lat_degrees < 58: return 100 # NWT blocks often 100
#             if 58 <= lat_degrees < 70: return 80  # NWT blocks often 80
#             if lat_degrees >= 70: return 60 # Arctic blocks often 60
#             return 100 # Default assumption for others
#
#     # Replace MockFederalPermitSystem with actual FederalPermitSystem
#     FederalPermitSystem = MockFederalPermitSystem
#
#     # Example from some documentation (verify correctness)
#     # FPS: 65°10' 123°00' Section 58, Unit J -> Should be approx Lat 65.229 Lon -123.234
#     fps_coord = FederalPermitSystem(lat_deg=65, lat_min=10, lon_deg=123, lon_min=0, sec=58, unit='J')
#     lat_long = FederalPermitSystemConverter.to_lat_long(fps_coord)
#     print(f"FPS: {fps_coord.lat_degrees}°{fps_coord.lat_minutes}' {fps_coord.lon_degrees}°{fps_coord.lon_minutes}' Sec {fps_coord.section} Unit {fps_coord.unit}")
#     # Assuming LatLongCoordinate has a __str__ or __repr__ method
#     print(f"LatLong: {lat_long}")
