import unittest
from DlsSystem import DlsSystem, ParseOptions
from LatLongCoordinate import LatLongCoordinate
from CoordinateParseException import CoordinateParseException

class TestDlsSystem(unittest.TestCase):

    def test_to_lat_long_1(self):
        lat_long = DlsSystem(4, 11, 82, 4, 6).to_lat_long()
        self.assertAlmostEqual(lat_long.latitude, 56.08892, delta=0.00001)
        self.assertAlmostEqual(lat_long.longitude, -118.519378662109, delta=0.00001)

    def test_to_lat_long_2(self):
        lat_long = DlsSystem.to_lat_long(DlsSystem(4, 11, 82, 4, 6))
        self.assertAlmostEqual(lat_long.latitude, 56.08892, delta=0.00001)
        self.assertAlmostEqual(lat_long.longitude, -118.519378662109, delta=0.00001)

    def test_ctor(self):
        dls_system = DlsSystem(4, 11, 82, 4, 6)
        self.assertEqual(dls_system.direction, 'W')
        self.assertEqual(dls_system.legal_subdivision, 4)
        self.assertEqual(dls_system.meridian, 6)
        self.assertEqual(dls_system.quarter, "SW")
        self.assertEqual(dls_system.township, 82)
        self.assertEqual(dls_system.range, 4)
        self.assertEqual(dls_system.section, 11)

    def test_direction_via_parse(self):
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
        self.assertAlmostEqual(ll.latitude, 49.354435, delta=0.000001)
        self.assertAlmostEqual(ll.longitude, -114.524994, delta=0.000001)

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
        self.assertFalse(a == "some string")
        self.assertTrue(a != "some string")

    def test_inequality(self):
        a = DlsSystem(8, 36, 23, 1, 5)
        b = DlsSystem(8, 36, 23, 1, 4)
        self.assertFalse(a == b)
        self.assertTrue(a != b)
        self.assertFalse(a.equals(b))
        self.assertFalse(b.equals(a))

    def test_hash_code(self):
        a = DlsSystem(8, 36, 23, 1, 5)
        self.assertEqual(a.get_hash_code(), a.get_hash_code())
        b = DlsSystem(8, 36, 23, 1, 5)
        self.assertEqual(a.get_hash_code(), b.get_hash_code())
        c = DlsSystem(8, 36, 23, 1, 4)
        self.assertNotEqual(a.get_hash_code(), c.get_hash_code())

    def test_valid_construction(self):
        a = DlsSystem(16, 36, 127, 34, 6)
        self.assertIsNotNone(a)
        b = DlsSystem(1, 1, 1, 1, 1)
        self.assertIsNotNone(b)
        c = DlsSystem(1, 1, 1, 34, 1)
        self.assertIsNotNone(c)

    def test_invalid_construction_lsd(self):
        invalid_values = [0, 17]
        for lsd in invalid_values:
            with self.subTest(lsd=lsd):
                with self.assertRaises(ValueError):
                    DlsSystem(lsd, 1, 1, 1, 1)

    def test_invalid_construction_section(self):
        invalid_values = [0, 37]
        for section in invalid_values:
            with self.subTest(section=section):
                with self.assertRaises(ValueError):
                    DlsSystem(1, section, 1, 1, 1)

    def test_invalid_construction_township(self):
        invalid_values = [0, 128]
        for township in invalid_values:
            with self.subTest(township=township):
                with self.assertRaises(ValueError):
                    DlsSystem(1, 1, township, 1, 1)

    def test_invalid_construction_range(self):
        invalid_values = [0, 35]
        for range_val in invalid_values:
            with self.subTest(range=range_val):
                with self.assertRaises(ValueError):
                    DlsSystem(1, 1, 1, range_val, 1)
                with self.assertRaises(ValueError):
                    DlsSystem(1, 1, 1, range_val, 2)

    def test_invalid_construction_meridian(self):
        invalid_values = [0, 7]
        for meridian in invalid_values:
            with self.subTest(meridian=meridian):
                with self.assertRaises(ValueError):
                    DlsSystem(1, 1, 1, 1, meridian)

    def test_parse_valid(self):
        test_cases = [
            ("04-11-082-04W6", DlsSystem(4, 11, 82, 4, 6)),
            ("04 11 082 04W6", DlsSystem(4, 11, 82, 4, 6)),
            ("4/11/82/4W6", DlsSystem(4, 11, 82, 4, 6)),
            (" 4/11/82/4W6 ", DlsSystem(4, 11, 82, 4, 6)),
            ("100/04-11-082-04W6/0", DlsSystem(4, 11, 82, 4, 6)),
            ("13-01-075-01W5", DlsSystem(13, 1, 75, 1, 5)),
            ("13-01-075-01 W5", DlsSystem(13, 1, 75, 1, 5)),
            ("13-01-075-01W 5", DlsSystem(13, 1, 75, 1, 5)),
            ("13-01-075-01 W 5", DlsSystem(13, 1, 75, 1, 5)),
            ("13-1-75-1W5", DlsSystem(13, 1, 75, 1, 5)),
            ("13-1-75-1W5M", DlsSystem(13, 1, 75, 1, 5)),
            ("13-1-75-1W5GARBAGE", DlsSystem(13, 1, 75, 1, 5)),
            ("PREFIX/13-1-75-1W5", DlsSystem(13, 1, 75, 1, 5)),
            ("06-21-019-15W4", DlsSystem(6, 21, 19, 15, 4)),
            ("A6-21-019-15W4", DlsSystem(6, 21, 19, 15, 4)),
            ("B06-21-019-15W4", DlsSystem(6, 21, 19, 15, 4)),
            ("16-36-126-30W6", DlsSystem(16, 36, 126, 30, 6)),
            ("01-01-001-01W1", DlsSystem(1, 1, 1, 1, 1)),
            ("01-01-001-34W1", DlsSystem(1, 1, 1, 34, 1)),
            ("01-01-001-30W2", DlsSystem(1, 1, 1, 30, 2)),
            ("04-11-082-04WP", DlsSystem(4, 11, 82, 4, 1)),
        ]
        for location_str, expected_dls in test_cases:
            with self.subTest(location=location_str):
                dls = DlsSystem.parse(location_str)
                self.assertEqual(dls, expected_dls)

    def test_parse_valid_quarters(self):
        test_cases = [
            ("SW-12-065-04W4", DlsSystem(6, 12, 65, 4, 4)),
            (" NW 12 65 4 W 4 ", DlsSystem(11, 12, 65, 4, 4)),
            ("NE/12/65/4W4M", DlsSystem(10, 12, 65, 4, 4)),
            ("SE-1-1-1W1", DlsSystem(7, 1, 1, 1, 1)),
        ]
        options = {ParseOptions.ALLOW_QUARTERS}
        for location_str, expected_dls in test_cases:
            with self.subTest(location=location_str):
                dls = DlsSystem.parse(location_str, options=options)
                self.assertEqual(dls, expected_dls)

    def test_parse_invalid(self):
        invalid_locations = [
            None,
            "",
            " ",
            "garbage",
            "04-11-082-04",
            "04-11-082-04X6",
            "04-11-082-04W",
            "04-11-082-04W9",
            "04-11-082-04W0",
            "04-11-082-31W2",
            "04-11-082-0W2",
            "04-11-082-35W1",
            "04-11-000-04W1",
            "04-11-127-04W1",
            "04-00-082-04W1",
            "04-37-082-04W1",
            "00-11-082-04W1",
            "17-11-082-04W1",
            "XX-11-082-04W1",
            "04-11-082",
            "04-11-082-XXW1",
            "04-11-XX-04W1",
            "04-XX-082-04W1",
            "SE-12-065-04W4",
            "04-11-082-04E1",
        ]
        for location_str in invalid_locations:
            with self.subTest(location=location_str):
                with self.assertRaises(CoordinateParseException):
                    DlsSystem.parse(location_str)

    def test_parse_invalid_quarters_option(self):
        options = {ParseOptions.ALLOW_QUARTERS}
        invalid_locations = [
            "XX-12-065-04W4",
            "NorthWest-12-065-04W4",
        ]
        for location_str in invalid_locations:
            with self.subTest(location=location_str):
                with self.assertRaises(CoordinateParseException):
                    DlsSystem.parse(location_str, options=options)

    def test_to_string(self):
        dls = DlsSystem(4, 11, 82, 4, 6)
        self.assertEqual(str(dls), "04-11-082-04W6")
        self.assertEqual(dls.to_string(), "04-11-082-04W6")

        dls_padded = DlsSystem(1, 1, 1, 1, 1)
        self.assertEqual(str(dls_padded), "01-01-001-01W1")
        self.assertEqual(dls_padded.to_string(), "01-01-001-01W1")

    def test_repr(self):
        dls = DlsSystem(4, 11, 82, 4, 6)
        expected_repr = "DlsSystem(legal_subdivision=4, section=11, township=82, range=4, meridian=6)"
        self.assertEqual(repr(dls), expected_repr)

if __name__ == '__main__':
    unittest.main()
