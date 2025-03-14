import gzip
import struct
from collections import namedtuple

from survey_grid_library.lat_long_coordinate import LatLongCoordinate
from survey_grid_library.lat_long_corners import LatLongCorners

class DlsSurveyCoordinateProvider:
    _instance = None
    _pad_lock = object()

    def __new__(cls):
        if cls._instance is None:
            with cls._pad_lock:
                if cls._instance is None:
                    cls._instance = super(DlsSurveyCoordinateProvider, cls).__new__(cls)
                    cls._instance._offsets = {}
                    cls._instance.load_data()
        return cls._instance

    def load_data(self):
        township_data_bytes = 1154
        township_count = 15583

        resource_name = "survey_grid_library/coordinates.gz"
        with gzip.open(resource_name, 'rb') as resource_stream:
            while True:
                buffer = resource_stream.read(township_data_bytes)
                if not buffer:
                    break

                key = struct.unpack('H', buffer[:2])[0]
                township = struct.unpack('f' * 288, buffer[2:])
                self._offsets[key] = township

        if len(self._offsets) != township_count:
            raise Exception(f"Embedded manifest resource {resource_name}, did not contain expected number of townships, got {len(self._offsets)} expected {township_count}.")

    def township_markers(self, township, range, meridian):
        key = (meridian << 13) | (range << 7) | township
        if key not in self._offsets:
            return None

        township_floats = self._offsets[key]
        corners = []
        for offset in range(0, 288, 8):
            se = self.lat_long_coordinate(township_floats, offset + 0)
            sw = self.lat_long_coordinate(township_floats, offset + 2)
            nw = self.lat_long_coordinate(township_floats, offset + 4)
            ne = self.lat_long_coordinate(township_floats, offset + 6)
            corners.append(LatLongCorners(se, sw, nw, ne))
        return corners

    def township_boundary(self, township, range, meridian):
        key = (meridian << 13) | (range << 7) | township
        if key not in self._offsets:
            return None

        township_floats = self._offsets[key]
        se, sw, ne, nw = None, None, None, None

        for i in range(0, 144, 2):
            lat = township_floats[i]
            lon = township_floats[i + 1]

            if lat == 0 and lon == 0:
                continue

            if se is None or (lat < se.latitude and lon > se.longitude):
                se = LatLongCoordinate(lat, lon)
            if sw is None or (lat < sw.latitude and lon < sw.longitude):
                sw = LatLongCoordinate(lat, lon)
            if ne is None or (lat > ne.latitude and lon > ne.longitude):
                ne = LatLongCoordinate(lat, lon)
            if nw is None or (lat > nw.latitude and lon < nw.longitude):
                nw = LatLongCoordinate(lat, lon)

        return LatLongCorners(se, sw, nw, ne)

    def boundary_markers(self, section, township, range, meridian):
        key = (meridian << 13) | (range << 7) | township
        if key not in self._offsets:
            return None

        township_floats = self._offsets[key]
        offset = (section - 1) * 8

        se = self.lat_long_coordinate(township_floats, offset)
        sw = self.lat_long_coordinate(township_floats, offset + 2)
        nw = self.lat_long_coordinate(township_floats, offset + 4)
        ne = self.lat_long_coordinate(township_floats, offset + 6)

        return LatLongCorners(se, sw, nw, ne)

    @staticmethod
    def lat_long_coordinate(township_floats, offset):
        lat = township_floats[offset]
        lon = township_floats[offset + 1]
        if lat == 0 and lon == 0:
            return None
        return LatLongCoordinate(lat, lon)
