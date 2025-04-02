import unittest
from DlsSurveyCoordinateProvider import DlsSurveyCoordinateProvider
from LatLongCoordinate import LatLongCoordinate
import time

class TestDlsMarkerProvider(unittest.TestCase):

    def test_load_performance(self):
        start = time.time()
        provider = DlsSurveyCoordinateProvider()
        self.assertIsNotNone(provider)
        end = time.time() - start
        print("provider load time=", end * 1000)

    def test_iterate_all_townships(self):
        i = 0
        provider = DlsSurveyCoordinateProvider()
        for meridian in range(1, 7):
            for range_ in range(1, 35):
                for township in range(1, 128):
                    markers = provider.township_boundary(township, range_, meridian)
                    if markers is not None:
                        i += 1
        self.assertEqual(15583, i)

    def test_verify_first_marker(self):
        markers = DlsSurveyCoordinateProvider().boundary_markers(1, 1, 1, 1)
        self.assertIsNotNone(markers)
        self.assertIsNotNone(markers.south_east)
        coordinate = markers.south_east
        self.assertAlmostEqual(49.000801086426, coordinate.latitude, delta=0.0000001)
        self.assertAlmostEqual(-97.459770202637, coordinate.longitude, delta=0.0000001)

    def test_verify_last_marker(self):
        markers = DlsSurveyCoordinateProvider().boundary_markers(36, 78, 15, 6)
        self.assertIsNotNone(markers)
        self.assertIsNotNone(markers.north_east)
        coordinate = markers.north_east
        self.assertAlmostEqual(55.8103638, coordinate.latitude, delta=0.000001)
        self.assertAlmostEqual(-120.172646, coordinate.longitude, delta=0.000001)

    def test_assert_markers_match_known(self):
        markers = DlsSurveyCoordinateProvider().boundary_markers(6, 1, 30, 3)
        self.assertIsNotNone(markers.south_east)
        self.assertAlmostEqual(48.9997524, markers.south_east.latitude, delta=0.000001)
        self.assertAlmostEqual(-109.991165, markers.south_east.longitude, delta=0.000001)
        self.assertIsNotNone(markers.south_west)
        self.assertAlmostEqual(48.99978247, markers.south_west.latitude, delta=0.000001)
        self.assertAlmostEqual(-110.00480669, markers.south_west.longitude, delta=0.000001)
        self.assertIsNotNone(markers.north_east)
        self.assertAlmostEqual(49.014183, markers.north_east.latitude, delta=0.000001)
        self.assertAlmostEqual(-109.9911499, markers.north_east.longitude, delta=0.000001)
        self.assertIsNotNone(markers.north_west)
        self.assertAlmostEqual(49.0142335, markers.north_west.latitude, delta=0.000001)
        self.assertAlmostEqual(-110.00480651, markers.north_west.longitude, delta=0.000001)

    def test_invalid_section_marker(self):
        markers = DlsSurveyCoordinateProvider().boundary_markers(127, 127, 127, 127)
        self.assertIsNone(markers)

    def test_known_township_markers(self):
        markers = DlsSurveyCoordinateProvider().township_boundary(23, 29, 4)
        self.assertIsNotNone(markers)

if __name__ == '__main__':
    unittest.main()
