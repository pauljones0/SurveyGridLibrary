import unittest
import math
from LatLongCoordinate import LatLongCoordinate
from ReferenceEllipsoid import ReferenceEllipsoid
from BcNtsGridSystem import BcNtsGridSystem
from DlsSystem import DlsSystem
from Angle import Angle

class TestLatLongCoordinate(unittest.TestCase):

    def test_construct_dms(self):
        lat_long_coordinate = LatLongCoordinate.from_degrees_minutes_seconds(50, 3, 4, 100, 1, 2)
        self.assertAlmostEqual(lat_long_coordinate.latitude, 50.0511111, places=7)
        self.assertAlmostEqual(lat_long_coordinate.longitude, 100.0172222, places=7)

    def test_construct_dm(self):
        lat_long_coordinate = LatLongCoordinate.from_degrees_minutes(50, 3, 100, 1)
        self.assertAlmostEqual(lat_long_coordinate.latitude, 50.05, places=7)
        self.assertAlmostEqual(lat_long_coordinate.longitude, 100.0166667, places=7)

    def test_from_radians(self):
        lat_long_coordinate = LatLongCoordinate.from_radians(math.pi, math.pi)
        self.assertEqual(lat_long_coordinate.latitude, 90)
        self.assertEqual(lat_long_coordinate.longitude, 0)
        self.assertAlmostEqual(lat_long_coordinate.radians_lat, math.pi / 2, places=6)
        self.assertAlmostEqual(lat_long_coordinate.radians_lon, 0, places=6)

    def test_clone(self):
        lat_long_coordinate = LatLongCoordinate(50, 100)
        cloned = lat_long_coordinate.clone()
        self.assertIsNot(lat_long_coordinate, cloned)
        self.assertTrue(lat_long_coordinate.equals(cloned))

    def test_equality(self):
        a = LatLongCoordinate(1, 10)
        b = LatLongCoordinate(1, 10)
        self.assertTrue(a.equals(b))
        self.assertTrue(b.equals(a))

    def test_inequality(self):
        a = LatLongCoordinate(1, 10)
        b = LatLongCoordinate(2, 10)
        c = LatLongCoordinate(1, 11)
        self.assertFalse(a.equals(b))
        self.assertFalse(b.equals(a))
        self.assertFalse(a.equals(c))

    def test_hash_code(self):
        self.assertEqual(LatLongCoordinate(1, 10).get_hash_code(), LatLongCoordinate(1, 10).get_hash_code())

    def test_to_string_formats(self):
        a = LatLongCoordinate(1.234567, 10.765432)
        self.assertEqual(a.to_string(), "1.234567, 10.765432")
        self.assertEqual(a.to_string_format("g"), "1.234567, 10.765432")
        self.assertEqual(a.to_string_format("dm"), "N1 14.074 E10 45.926")
        self.assertEqual(a.to_string_format("dms"), 'N1° 14\' 4.4" E10° 45\' 55.6"')
        self.assertEqual(a.to_string_format("dd"), "N001.234567 E010.765432")
        self.assertEqual(a.to_string_format("sd"), "1.234567 10.765432")
        self.assertEqual(a.to_string_format("wkt"), "POINT(010.765432 001.234567)")

        b = LatLongCoordinate(-1.234567, 10.765432)
        self.assertEqual(b.to_string(), "-1.234567, 10.765432")
        self.assertEqual(b.to_string_format("dm"), "S1 14.074 E10 45.926")
        self.assertEqual(b.to_string_format("dms"), 'S1° 14\' 4.4" E10° 45\' 55.6"')
        self.assertEqual(b.to_string_format("dd"), "S001.234567 E010.765432")
        self.assertEqual(b.to_string_format("sd"), "-1.234567 10.765432")
        self.assertEqual(b.to_string_format("wkt"), "POINT(010.765432 S001.234567)")

        c = LatLongCoordinate(1.234567, -10.765432)
        self.assertEqual(c.to_string(), "1.234567, -10.765432")
        self.assertEqual(c.to_string_format("dm"), "N1 14.074 W10 45.926")
        self.assertEqual(c.to_string_format("dms"), 'N1° 14\' 4.4" W10° 45\' 55.6"')
        self.assertEqual(c.to_string_format("dd"), "N001.234567 W010.765432")
        self.assertEqual(c.to_string_format("sd"), "1.234567 -10.765432")
        self.assertEqual(c.to_string_format("wkt"), "POINT(W010.765432 001.234567)")

        d = LatLongCoordinate(-1.234567, -10.765432)
        self.assertEqual(d.to_string(), "-1.234567, -10.765432")
        self.assertEqual(d.to_string_format("dm"), "S1 14.074 W10 45.926")
        self.assertEqual(d.to_string_format("dms"), 'S1° 14\' 4.4" W10° 45\' 55.6"')
        self.assertEqual(d.to_string_format("dd"), "S001.234567 W010.765432")
        self.assertEqual(d.to_string_format("sd"), "-1.234567 -10.765432")
        self.assertEqual(d.to_string_format("wkt"), "POINT(W010.765432 S001.234567)")

    def test_from_convertible(self):
        lat_long_coordinate = LatLongCoordinate.from_convertible_string("-1, -10")
        self.assertEqual(lat_long_coordinate.latitude, -1)
        self.assertEqual(lat_long_coordinate.longitude, -10)
        lat_long_coordinate = LatLongCoordinate.from_convertible_string(" -1.5 , -10.5 ")
        self.assertAlmostEqual(lat_long_coordinate.latitude, -1.5)
        self.assertAlmostEqual(lat_long_coordinate.longitude, -10.5)

    def test_parse(self):
        lat_long_coordinate = LatLongCoordinate.parse("n 54 30 w 100 15")
        self.assertAlmostEqual(lat_long_coordinate.latitude, 54.5, places=7)
        self.assertAlmostEqual(lat_long_coordinate.longitude, -100.25, places=7)

        lat_long_coordinate = LatLongCoordinate.parse("N54 30 W100 15")
        self.assertAlmostEqual(lat_long_coordinate.latitude, 54.5, places=7)
        self.assertAlmostEqual(lat_long_coordinate.longitude, -100.25, places=7)

        lat_long_coordinate = LatLongCoordinate.parse("54 30 -100 15")
        self.assertAlmostEqual(lat_long_coordinate.latitude, 54.5, places=7)
        self.assertAlmostEqual(lat_long_coordinate.longitude, -100.25, places=7)

        with self.assertRaises(ValueError):
            LatLongCoordinate.parse("N50 33 08.352 W114 01 29.74")

    def test_from_decimal_degrees(self):
        lat_long_coordinate = LatLongCoordinate.from_decimal_degrees("N54.5 W100.25")
        self.assertAlmostEqual(lat_long_coordinate.latitude, 54.5, places=7)
        self.assertAlmostEqual(lat_long_coordinate.longitude, -100.25, places=7)

        lat_long_coordinate = LatLongCoordinate.from_decimal_degrees(" N 54.5 W 100.25 ")
        self.assertAlmostEqual(lat_long_coordinate.latitude, 54.5, places=7)
        self.assertAlmostEqual(lat_long_coordinate.longitude, -100.25, places=7)

        with self.assertRaises(ValueError):
            LatLongCoordinate.from_decimal_degrees("54.5 W100.25")
        with self.assertRaises(ValueError):
            LatLongCoordinate.from_decimal_degrees("N54.5 100.25")

    def test_to_bc_nts_grid_system(self):
        coordinate = LatLongCoordinate(54, -112)
        bc = coordinate.to_bc_nts_grid_system()
        self.assertIsNotNone(bc)

    def test_direction_to(self):
        a = LatLongCoordinate(30, 30)
        b = LatLongCoordinate(30, 30)
        c = LatLongCoordinate(0, 0)
        self.assertAlmostEqual(a.direction_to(b), 0, places=4)
        self.assertAlmostEqual(b.direction_to(a), 0, places=4)

        expected_a_to_c_deg = math.degrees(3.903035)
        expected_c_to_a_deg = math.degrees(0.7614422)
        self.assertAlmostEqual(a.direction_to(c), expected_a_to_c_deg, places=4)
        self.assertAlmostEqual(c.direction_to(a), expected_c_to_a_deg, places=4)

    def test_distance_to(self):
        a = LatLongCoordinate(30, 30)
        b = LatLongCoordinate(40, 31)
        distance = a.distance_to(b, ReferenceEllipsoid.WGS84)
        self.assertAlmostEqual(distance, 1113141.546, places=3)

    def test_sphere_distance_to(self):
        a = LatLongCoordinate(30, 30)
        b = LatLongCoordinate(40, 31)
        distance = a.sphere_distance_to(b)
        self.assertAlmostEqual(distance, 1116900.0741790, places=7)

    def test_great_circle_angle(self):
        a = LatLongCoordinate(30, 30)
        b = LatLongCoordinate(40, 31)
        angle_rad = LatLongCoordinate.great_circle_angle(a, b)
        self.assertAlmostEqual(math.degrees(angle_rad), 10.033284074692, places=8)

    def test_bc_geographic_system1(self):
        a = LatLongCoordinate(51, -114)
        nts = a.to_bc_nts_grid_system()
        self.assertIsNotNone(nts)

    def test_bc_geographic_system2(self):
        coordinate = LatLongCoordinate(54, -115)
        nts = coordinate.to_bc_nts_grid_system()
        self.assertIsNotNone(nts)

    def test_dls_system_near_fifth(self):
        coordinate = LatLongCoordinate(51, -114)
        dls = LatLongCoordinate.from_coordinate_to_dls_system(coordinate)
        self.assertIsNotNone(dls)

    def test_dls_system2(self):
        coordinate = LatLongCoordinate(54, -115)
        dls = coordinate.to_dls_system()
        self.assertIsNotNone(dls)

if __name__ == '__main__':
    unittest.main()
