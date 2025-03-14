import math
from SurveyGridLibrary.CoordinateConversionException import CoordinateConversionException
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.DlsSurveyCoordinateProvider import DlsSurveyCoordinateProvider
from SurveyGridLibrary.LatLongCorners import LatLongCorners
from SurveyGridLibrary.DlsSystem import DlsSystem

class DlsSystemConverter:
    SectionHeightInDegrees = 0.014398614
    TownshipHeightInDegrees = 0.087300101772
    BaseLatitude = 48.99978996
    Meridians = [-97.45788889, -102, -106, -110.00506248, -114.00191933, -118.00020192, -122, -122.761]

    @staticmethod
    def to_lat_long(dls):
        dls_boundary = DlsSurveyCoordinateProvider().boundary_markers(dls.section, dls.township, dls.range, dls.meridian)
        if dls_boundary is None or dls_boundary.count == 0:
            raise CoordinateConversionException("Invalid dls location for conversion to lat long")

        if dls_boundary.count == 4:
            return DlsSystemConverter.interpolate4_point(dls.legal_subdivision, dls_boundary)
        else:
            raise CoordinateConversionException(f"lookup returned {dls_boundary.count} points")

    @staticmethod
    def from_lat_long_coordinate(coordinate):
        if not DlsSystemConverter.try_infer_township_for_lat_long_coordinate(coordinate):
            return None

        meridian, range, township = DlsSystemConverter.try_infer_township_for_lat_long_coordinate(coordinate)
        markers = DlsSurveyCoordinateProvider().township_markers(township, range, meridian)
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
                    best_dls = DlsSystem(legal_subdivision, section, township, range, meridian)

        return best_dls

    @staticmethod
    def try_infer_township_for_lat_long_coordinate(coordinate):
        longitude = coordinate.longitude
        if longitude > DlsSystemConverter.Meridians[0] or longitude < DlsSystemConverter.Meridians[-1]:
            raise CoordinateConversionException("Meridian is out of range")

        mrd = 0
        for k in range(1, 8):
            if longitude <= DlsSystemConverter.Meridians[k - 1] and longitude > DlsSystemConverter.Meridians[k]:
                mrd = k
                break

        if mrd == 0:
            return False

        twp = math.floor((coordinate.latitude - DlsSystemConverter.BaseLatitude) / DlsSystemConverter.TownshipHeightInDegrees) + 1
        if twp <= 0:
            return False

        township_width_in_degrees = 6 * DlsSystemConverter.get_section_width_in_degrees(twp)
        meridian_longitude = DlsSystemConverter.Meridians[mrd - 1]
        rng = math.floor((longitude - meridian_longitude) / township_width_in_degrees) + 1

        return mrd, rng, twp

    @staticmethod
    def get_section_width_in_degrees(twp):
        return DlsSystemConverter.interpolate(10, -0.02255, 80, -0.026093, twp)

    @staticmethod
    def interpolate4_point(legal_subdivision, geo_list):
        if geo_list.south_east is None or geo_list.south_west is None or geo_list.north_west is None or geo_list.north_east is None:
            return LatLongCoordinate.origin()

        lat = [[geo_list.south_west.latitude, geo_list.south_east.latitude], [geo_list.north_west.latitude, geo_list.north_east.latitude]]
        lng = [[geo_list.south_west.longitude, geo_list.south_east.longitude], [geo_list.north_west.longitude, geo_list.north_east.longitude]]
        return DlsSystemConverter.bilinear_interpolate(legal_subdivision, lat, lng)

    @staticmethod
    def bilinear_interpolate(lsd, lat, lng):
        x = [0.875, 0.625, 0.375, 0.125, 0.125, 0.375, 0.625, 0.875, 0.875, 0.625, 0.375, 0.125, 0.125, 0.375, 0.625, 0.875]
        xp = x[lsd - 1]
        y = [0.125, 0.125, 0.125, 0.125, 0.375, 0.375, 0.375, 0.375, 0.625, 0.625, 0.625, 0.625, 0.875, 0.875, 0.875, 0.875]
        yp = y[lsd - 1]

        xa = DlsSystemConverter.interpolate(0, lat[0][0], 1, lat[1][0], yp)
        xb = DlsSystemConverter.interpolate(0, lat[0][1], 1, lat[1][1], yp)
        latitude = DlsSystemConverter.interpolate(0, xa, 1, xb, xp)

        ya = DlsSystemConverter.interpolate(0, lng[0][0], 1, lng[0][1], xp)
        yb = DlsSystemConverter.interpolate(0, lng[1][0], 1, lng[1][1], xp)
        longitude = DlsSystemConverter.interpolate(0, ya, 1, yb, yp)

        return LatLongCoordinate(latitude, longitude)

    @staticmethod
    def interpolate(x0, y0, x1, y1, z):
        return (z - x1) * y0 / (x0 - x1) + (z - x0) * y1 / (x1 - x0)
