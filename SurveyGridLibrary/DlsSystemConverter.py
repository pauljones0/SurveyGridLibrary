import math
from CoordinateConversionException import CoordinateConversionException
from LatLongCoordinate import LatLongCoordinate
from DlsSurveyCoordinateProvider import DlsSurveyCoordinateProvider
from LatLongCorners import LatLongCorners
from DlsSystem import DlsSystem

class DlsSystemConverter:
    SectionHeightInDegrees = 0.014398614
    TownshipHeightInDegrees = 0.087300101772
    BaseLatitude = 48.99978996
    Meridians = [-97.45788889, -102, -106, -110.00506248, -114.00191933, -118.00020192, -122, -122.761]

    @staticmethod
    def to_lat_long(dls: DlsSystem) -> LatLongCoordinate:
        """Converts a DlsSystem object to a LatLongCoordinate."""
        dls_boundary = DlsSurveyCoordinateProvider().boundary_markers(dls.section, dls.township, dls.range, dls.meridian)
        if dls_boundary is None or dls_boundary.count == 0:
            raise CoordinateConversionException("Invalid dls location for conversion to lat long")

        if dls_boundary.count == 4:
            return DlsSystemConverter.interpolate4_point(dls.legal_subdivision, dls_boundary)
        else:
            raise CoordinateConversionException(f"lookup returned {dls_boundary.count} points")

    @staticmethod
    def from_lat_long_coordinate(coordinate: LatLongCoordinate) -> DlsSystem | None:
        """Finds the best fit DlsSystem for a given LatLongCoordinate."""
        inferred_trs = DlsSystemConverter.try_infer_township_for_lat_long_coordinate(coordinate)
        if inferred_trs is None:
            return None

        meridian, range_val, township = inferred_trs
        markers = DlsSurveyCoordinateProvider().township_markers(township, range_val, meridian)
        if markers is None:
            return None

        best_distance = float('inf')
        best_dls = None

        for section in range(1, 37):
            dls_boundary = markers[section - 1]
            if dls_boundary is None or dls_boundary.count == 0:
                continue

            for legal_subdivision in range(1, 17):
                if dls_boundary.count == 4:
                    test_distance = coordinate.relative_distance_to(DlsSystemConverter.interpolate4_point(legal_subdivision, dls_boundary))
                else:
                    test_distance = float('inf')

                if test_distance < best_distance:
                    best_distance = test_distance
                    best_dls = DlsSystem(legal_subdivision, section, township, range_val, meridian)

        return best_dls

    @staticmethod
    def try_infer_township_for_lat_long_coordinate(coordinate: LatLongCoordinate) -> tuple[int, int, int] | None:
        """
        Makes a best guess at the Township, Range, and Meridian containing the coordinate.
        Returns a tuple (meridian, range, township) on success, None on failure.
        """
        longitude = coordinate.longitude
        if longitude > DlsSystemConverter.Meridians[0] or longitude < DlsSystemConverter.Meridians[-1]:
            raise CoordinateConversionException("Longitude is out of range of supported Meridians")

        mrd = 0
        for k in range(1, 8):
            if longitude <= DlsSystemConverter.Meridians[k - 1] and longitude > DlsSystemConverter.Meridians[k]:
                mrd = k
                break

        if mrd == 0:
            return None

        twp_float = (coordinate.latitude - DlsSystemConverter.BaseLatitude) / DlsSystemConverter.TownshipHeightInDegrees + 1
        if twp_float <= 0:
            return None
        twp = int(math.floor(twp_float))

        township_width_in_degrees = 6 * DlsSystemConverter.get_section_width_in_degrees(twp)
        meridian_longitude = DlsSystemConverter.Meridians[mrd - 1]
        rng_float = (longitude - meridian_longitude) / township_width_in_degrees + 1
        if rng_float <=0:
            return None
        rng = int(math.floor(rng_float))

        return mrd, rng, twp

    @staticmethod
    def get_section_width_in_degrees(twp: int) -> float:
        """Calculates the estimated geodetic width of a section at a given township."""
        return DlsSystemConverter.interpolate(10, -0.02255, 80, -0.026093, twp)

    @staticmethod
    def interpolate4_point(legal_subdivision: int, geo_list: LatLongCorners) -> LatLongCoordinate:
        """Interpolates the center LatLongCoordinate of an LSD within a section defined by 4 corners."""
        if geo_list.south_east is None or geo_list.south_west is None or \
           geo_list.north_west is None or geo_list.north_east is None:
            return LatLongCoordinate.origin()

        lat = [[geo_list.south_west.latitude, geo_list.south_east.latitude],
               [geo_list.north_west.latitude, geo_list.north_east.latitude]]
        lng = [[geo_list.south_west.longitude, geo_list.south_east.longitude],
               [geo_list.north_west.longitude, geo_list.north_east.longitude]]
        return DlsSystemConverter.bilinear_interpolate(legal_subdivision, lat, lng)

    @staticmethod
    def bilinear_interpolate(lsd: int, lat: list[list[float]], lng: list[list[float]]) -> LatLongCoordinate:
        """Performs bilinear interpolation to find coordinates within a quadrilateral."""
        x_coords = [0.875, 0.625, 0.375, 0.125, 0.125, 0.375, 0.625, 0.875, 0.875, 0.625, 0.375, 0.125, 0.125, 0.375, 0.625, 0.875]
        y_coords = [0.125, 0.125, 0.125, 0.125, 0.375, 0.375, 0.375, 0.375, 0.625, 0.625, 0.625, 0.625, 0.875, 0.875, 0.875, 0.875]

        xp = x_coords[lsd - 1]
        yp = y_coords[lsd - 1]

        lat_west_edge = DlsSystemConverter.interpolate(0, lat[0][0], 1, lat[1][0], yp)
        lat_east_edge = DlsSystemConverter.interpolate(0, lat[0][1], 1, lat[1][1], yp)
        latitude = DlsSystemConverter.interpolate(0, lat_west_edge, 1, lat_east_edge, xp)

        lng_south_edge = DlsSystemConverter.interpolate(0, lng[0][0], 1, lng[0][1], xp)
        lng_north_edge = DlsSystemConverter.interpolate(0, lng[1][0], 1, lng[1][1], xp)
        longitude = DlsSystemConverter.interpolate(0, lng_south_edge, 1, lng_north_edge, yp)

        return LatLongCoordinate(latitude, longitude)

    @staticmethod
    def interpolate(x0: float, y0: float, x1: float, y1: float, z: float) -> float:
        """Linear interpolation: finds y value at point z between (x0, y0) and (x1, y1)."""
        if x0 == x1:
            return y0
        return (z - x1) * y0 / (x0 - x1) + (z - x0) * y1 / (x1 - x0)
