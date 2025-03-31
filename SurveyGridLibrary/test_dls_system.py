import unittest
from SurveyGridLibrary.DlsSystem import DlsSystem
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.CoordinateParseException import CoordinateParseException

class TestDlsSystem(unittest.TestCase):

    def test_to_lat_long_1(self):
        lat_long = DlsSystem(4, 11, 82, 4, 6).to_lat_long()
        self.assertAlmostEqual(lat_long.latitude, 56.08892, places=5)
        self.assertAlmostEqual(lat_long.longitude, -118.519378662109, places=5)

    def test_to_lat_long_2(self):
        lat_long = DlsSystem.to_lat_long(DlsSystem(4, 11, 82, 4, 6))
        self.assertAlmostEqual(lat_long.latitude, 56.08892, places=5)
        self.assertAlmostEqual(lat_long.longitude, -118.519378662109, places=5)

    def test_ctor(self):
        dls_system = DlsSystem(4, 11, 82, 4, 6)
        self.assertEqual(dls_system.direction, 'W')
        self.assertEqual(dls_system.legal_subdivision, 4)
        self.assertEqual(dls_system.meridian, 6)
        self.assertEqual(dls_system.quarter, "SW")
        self.assertEqual(dls_system.township, 82)
        self.assertEqual(dls_system.range, 4)
        self.assertEqual(dls_system.section, 11)

    def test_direction(self):
        dls_system = DlsSystem.parse("04-11-082-04W6")
        self.assertEqual(dls_system.direction, 'W')
        self.assertEqual(dls_system.legal_subdivision, 4)
        self.assertEqual(dls_system.meridian, 6)
        self.assertEqual(dls_system.quarter, "SW")
        self.assertEqual(dls_system.township, 82)
        self.assertEqual(dls_system.range, 4)
        self.assertEqual(dls_system.section, 11)

    def test_conversion(self):
        ll = DlsSystem(7, 6, 5, 4, 5).to_lat_long()
        self.assertAlmostEqual(ll.latitude, 49.354435, places=6)
        self.assertAlmostEqual(ll.longitude, -114.524994, places=6)

    def test_ensure_relative(self):
        dls_west = DlsSystem(8, 36, 23, 1, 5)
        dls_east = DlsSystem(5, 33, 23, 29, 4)
        dls_north_west = DlsSystem(9, 36, 23, 1, 5)

        lat_west = dls_west.to_lat_long()
        lat_east = dls_east.to_lat_long()
        lat_north_west = dls_north_west.to_lat_long()
        self.assertTrue(lat_west.longitude < lat_east.longitude)

        lat_test = LatLongCoordinate(51, -114)
        a = lat_test.relative_distance_to(lat_west)
        b = lat_test.relative_distance_to(lat_east)
        c = lat_test.relative_distance_to(lat_north_west)

        self.assertTrue(b < a)
        self.assertTrue(b < c)

    def test_equality(self):
        a = DlsSystem(8, 36, 23, 1, 5)
        b = DlsSystem(8, 36, 23, 1, 5)
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        self.assertTrue(a.equals(b))
        self.assertTrue(b.equals(a))

    def test_inequality(self):
        a = DlsSystem(8, 36, 23, 1, 5)
        b = DlsSystem(8, 36, 23, 1, 4)
        self.assertFalse(a == b)
        self.assertTrue(a != b)
        self.assertFalse(a.equals(b))
        self.assertFalse(b.equals(a))

    def test_hash_code(self):
        self.assertEqual(hash(DlsSystem(8, 36, 23, 1, 5)), hash(DlsSystem(8, 36, 23, 1, 5)))

    def test_valid_construction(self):
        a = DlsSystem(16, 36, 127, 34, 6)
        self.assertIsNotNone(a)
        b = DlsSystem(1, 1, 1, 1, 1)
        self.assertIsNotNone(b)

    def test_invalid_construction_lsd(self):
        with self.assertRaises(ValueError):
            DlsSystem(0, 1, 1, 1, 1)
        with self.assertRaises(ValueError):
            DlsSystem(17, 1, 1, 1, 1)

    def test_invalid_construction_section(self):
        with self.assertRaises(ValueError):
            DlsSystem(1, 0, 1, 1, 1)
        with self.assertRaises(ValueError):
            DlsSystem(1, 37, 1, 1, 1)

    def test_invalid_construction_township(self):
        with self.assertRaises(ValueError):
            DlsSystem(1, 1, 0, 1, 1)
        with self.assertRaises(ValueError):
            DlsSystem(1, 1, 128, 1, 1)

    def test_invalid_construction_range(self):
        with self.assertRaises(ValueError):
            DlsSystem(1, 1, 1, 0, 1)
        with self.assertRaises(ValueError):
            DlsSystem(1, 1, 1, 35, 1)
        with self.assertRaises(ValueError):
            DlsSystem(1, 1, 1, 255, 1)

    def test_invalid_construction_meridian(self):
        with self.assertRaises(ValueError):
            DlsSystem(1, 1, 1, 1, 0)
        with self.assertRaises(ValueError):
            DlsSystem(1, 1, 1, 1, 7)

if __name__ == '__main__':
    unittest.main()
