import unittest
from SurveyGridLibrary.BcNtsGridSystem import BcNtsGridSystem
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.CoordinateParseException import CoordinateParseException

class TestBcNtsGridSystem(unittest.TestCase):

    def test_equality(self):
        a = BcNtsGridSystem('B', 1, 'L', 93, 'F', 10)
        b = BcNtsGridSystem('B', 1, 'L', 93, 'F', 10)
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        self.assertTrue(a.equals(b))
        self.assertTrue(b.equals(a))

    def test_inequality(self):
        a = BcNtsGridSystem('B', 1, 'L', 93, 'F', 10)
        b = BcNtsGridSystem('A', 1, 'L', 93, 'F', 10)
        self.assertFalse(a == b)
        self.assertTrue(a != b)
        self.assertFalse(a.equals(b))
        self.assertFalse(b.equals(a))

    def test_hash_code(self):
        self.assertEqual(hash(BcNtsGridSystem('B', 1, 'L', 93, 'F', 10)),
                         hash(BcNtsGridSystem('B', 1, 'L', 93, 'F', 10)))

    def test_properties(self):
        a = BcNtsGridSystem('B', 1, 'L', 93, 'F', 10)
        self.assertEqual('L', a.block)
        self.assertEqual('F', a.map_area)
        self.assertEqual('B', a.quarter_unit)
        self.assertEqual(93, a.series)
        self.assertEqual(10, a.sheet)
        self.assertEqual(1, a.unit)

    def test_to_string(self):
        self.assertEqual("B-001-L/093-F-10", BcNtsGridSystem('B', 1, 'L', 93, 'F', 10).to_string())

    def test_parse(self):
        a = BcNtsGridSystem('B', 1, 'L', 93, 'F', 10)
        b = BcNtsGridSystem.parse("B-001-L/093-F-10")
        self.assertTrue(a == b)

    def test_to_lat_long_1(self):
        coordinate = BcNtsGridSystem.to_lat_long(BcNtsGridSystem('A', 1, 'J', 93, 'P', 8))
        self.assertAlmostEqual(55.41875, coordinate.latitude, places=5)
        self.assertAlmostEqual(-120.128128, coordinate.longitude, places=6)

    def test_from_lat_long(self):
        ll = LatLongCoordinate(49.354435, -114.524994)
        nts_grid_system = ll.to_bc_nts_grid_system()
        self.assertEqual("C-022-H/082-G-07", nts_grid_system.to_string())

    def test_to_lat_long_2(self):
        coordinate = BcNtsGridSystem('A', 1, 'J', 93, 'P', 8).to_lat_long()
        self.assertAlmostEqual(55.41875, coordinate.latitude, places=5)
        self.assertAlmostEqual(-120.128128, coordinate.longitude, places=6)

    def test_valid_construction(self):
        a = BcNtsGridSystem('D', 100, 'L', 114, 'P', 16)
        self.assertIsNotNone(a)
        b = BcNtsGridSystem('a', 1, 'a', 82, 'a', 1)
        self.assertIsNotNone(b)

    def test_invalid_construction_quarter(self):
        with self.assertRaises(ValueError):
            BcNtsGridSystem('E', 100, 'L', 114, 'P', 16)
        with self.assertRaises(ValueError):
            BcNtsGridSystem('0', 100, 'L', 114, 'P', 16)

    def test_invalid_construction_unit(self):
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 0, 'L', 114, 'P', 16)
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 255, 'L', 114, 'P', 16)

    def test_invalid_construction_block(self):
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 100, 'M', 114, 'P', 16)
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 100, '0', 114, 'P', 16)

    def test_invalid_construction_series(self):
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 100, 'L', 81, 'P', 16)
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 100, 'L', 115, 'P', 16)
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 100, 'L', 255, 'P', 16)

    def test_invalid_construction_map_area(self):
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 100, 'L', 114, 'Q', 16)
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 100, 'L', 114, '0', 16)

    def test_invalid_construction_sheet(self):
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 100, 'L', 114, 'P', 0)
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 100, 'L', 114, 'P', 17)
        with self.assertRaises(ValueError):
            BcNtsGridSystem('a', 100, 'L', 114, 'P', 255)

if __name__ == '__main__':
    unittest.main()
