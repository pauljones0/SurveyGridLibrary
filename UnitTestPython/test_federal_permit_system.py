import unittest
from SurveyGridLibrary.FederalPermitSystem import FederalPermitSystem
from SurveyGridLibrary.CoordinateParseException import CoordinateParseException

class TestFederalPermitSystem(unittest.TestCase):

    def test_equality(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        b = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        self.assertTrue(a.equals(b))
        self.assertTrue(b.equals(a))

    def test_inequality(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        b = FederalPermitSystem('A', 55, 70, 30, 136, 0)
        self.assertFalse(a == b)
        self.assertTrue(a != b)
        self.assertFalse(a.equals(b))
        self.assertFalse(b.equals(a))

    def test_hash_code(self):
        self.assertEqual(hash(FederalPermitSystem('L', 55, 70, 30, 136, 0)),
                         hash(FederalPermitSystem('L', 55, 70, 30, 136, 0)))

    def test_properties(self):
        federal_permit_system = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        self.assertEqual('L', federal_permit_system.unit)
        self.assertEqual(55, federal_permit_system.section)
        self.assertEqual(70, federal_permit_system.lat_degrees)
        self.assertEqual(30, federal_permit_system.lat_minutes)
        self.assertEqual(-136, federal_permit_system.lon_degrees)
        self.assertEqual(0, federal_permit_system.lon_minutes)

    def test_to_string(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        self.assertEqual("L-55-7030-13600", a.to_string())
        a = FederalPermitSystem('L', 1, 70, 30, 136, 0)
        self.assertEqual("L-01-7030-13600", a.to_string())
        a = FederalPermitSystem('L', 1, 70, 30, 99, 0)
        self.assertEqual("L-01-7030-09900", a.to_string())

    def test_parse(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        b = FederalPermitSystem.parse("L-55-7030-13600")
        self.assertTrue(a == b)

    def test_to_lat_long_1(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        lat_long = FederalPermitSystem.to_lat_long(a)
        self.assertAlmostEqual(70.5749969482422, lat_long.latitude, places=5)
        self.assertAlmostEqual(-136.287506103516, lat_long.longitude, places=6)

    def test_to_lat_long_2(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        lat_long = a.to_lat_long()
        self.assertAlmostEqual(70.5749969482422, lat_long.latitude, places=5)
        self.assertAlmostEqual(-136.287506103516, lat_long.longitude, places=6)

    def test_valid_construction(self):
        a = FederalPermitSystem('A', 1, 40, 0, 42, 0)
        self.assertIsNotNone(a)
        b = FederalPermitSystem('P', 100, 85, 50, 141, 0)
        self.assertIsNotNone(b)

    def test_invalid_construction_unit(self):
        with self.assertRaises(ValueError):
            FederalPermitSystem('9', 1, 40, 0, 42, 0)
        with self.assertRaises(ValueError):
            FederalPermitSystem('Q', 1, 40, 0, 42, 0)

    def test_invalid_construction_section(self):
        with self.assertRaises(ValueError):
            FederalPermitSystem('A', 0, 40, 0, 42, 0)
        with self.assertRaises(ValueError):
            FederalPermitSystem('A', 101, 40, 0, 42, 0)

    def test_invalid_construction_lat_degrees(self):
        with self.assertRaises(ValueError):
            FederalPermitSystem('A', 1, 39, 0, 42, 0)
        with self.assertRaises(ValueError):
            FederalPermitSystem('A', 1, 86, 0, 42, 0)

    def test_invalid_construction_lat_minutes(self):
        with self.assertRaises(ValueError):
            FederalPermitSystem('A', 1, 40, 61, 42, 0)

    def test_invalid_construction_lon_degrees(self):
        with self.assertRaises(ValueError):
            FederalPermitSystem('A', 1, 40, 0, 41, 0)
        with self.assertRaises(ValueError):
            FederalPermitSystem('A', 1, 40, 0, 142, 0)

    def test_invalid_construction_lon_minutes(self):
        with self.assertRaises(ValueError):
            FederalPermitSystem('A', 1, 40, 0, 42, 61)

if __name__ == '__main__':
    unittest.main()
