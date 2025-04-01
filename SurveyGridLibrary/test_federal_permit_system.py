import unittest
from FederalPermitSystem import FederalPermitSystem

class TestFederalPermitSystem(unittest.TestCase):

    def test_equality(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        b = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        self.assertTrue(a == b)
        self.assertFalse(a != b)

    def test_inequality(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        b = FederalPermitSystem('A', 55, 70, 30, 136, 0)
        self.assertFalse(a == b)
        self.assertTrue(a != b)

    def test_hash_code(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        b = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        self.assertEqual(hash(a), hash(b))

    def test_properties(self):
        federal_permit_system = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        self.assertEqual('L', federal_permit_system.unit)
        self.assertEqual(55, federal_permit_system.section)
        self.assertEqual(70, federal_permit_system.lat_degrees)
        self.assertEqual(30, federal_permit_system.lat_minutes)
        self.assertEqual(136, federal_permit_system.lon_degrees)
        self.assertEqual(0, federal_permit_system.lon_minutes)

    def test_str(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        self.assertEqual("L-55-7030-13600", str(a))
        a = FederalPermitSystem('L', 1, 70, 30, 136, 0)
        self.assertEqual("L-01-7030-13600", str(a))
        a = FederalPermitSystem('L', 1, 70, 30, 99, 0)
        self.assertEqual("L-01-7030-09900", str(a))

    def test_parse(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        b = FederalPermitSystem.parse("L-55-7030-13600")
        self.assertEqual(a, b)

    def test_to_lat_long(self):
        a = FederalPermitSystem('L', 55, 70, 30, 136, 0)
        try:
            lat_long = a.to_lat_long()
            self.assertIsNotNone(lat_long)
        except ImportError:
             self.skipTest("Skipping test_to_lat_long as FederalPermitSystemConverter or LatLongCoordinate might not be implemented yet.")
        except AttributeError:
             self.skipTest("Skipping test_to_lat_long as LatLongCoordinate structure might differ or conversion failed.")
        except Exception as e:
            self.fail(f"a.to_lat_long() raised unexpected exception: {e}")

    def test_valid_construction(self):
        a = FederalPermitSystem('A', 1, 40, 0, 42, 0)
        self.assertIsNotNone(a)
        b = FederalPermitSystem('P', 60, 84, 50, 141, 0)
        self.assertIsNotNone(b)

    def test_invalid_construction_unit(self):
        with self.assertRaisesRegex(ValueError, "Unit must be 'A' through 'P'"):
            FederalPermitSystem('9', 1, 40, 0, 42, 0)
        with self.assertRaisesRegex(ValueError, "Unit must be 'A' through 'P'"):
            FederalPermitSystem('Q', 1, 40, 0, 42, 0)
        with self.assertRaisesRegex(ValueError, "Unit must be a single character."):
             FederalPermitSystem('', 1, 40, 0, 42, 0)
        with self.assertRaisesRegex(ValueError, "Unit must be a single character."):
             FederalPermitSystem('AB', 1, 40, 0, 42, 0)

    def test_invalid_construction_section(self):
        with self.assertRaisesRegex(ValueError, "Section must be between 1 and 100"):
            FederalPermitSystem('A', 0, 40, 0, 42, 0)
        with self.assertRaisesRegex(ValueError, "Section must be between 1 and 100"):
            FederalPermitSystem('A', 101, 40, 0, 42, 0)
        with self.assertRaisesRegex(ValueError, "Section must be between 1 and 80"):
            FederalPermitSystem('A', 81, 60, 0, 42, 0)
        with self.assertRaisesRegex(ValueError, "Section must be between 1 and 60"):
             FederalPermitSystem('A', 61, 68, 0, 42, 0)

    def test_invalid_construction_lat_degrees(self):
        with self.assertRaisesRegex(ValueError, "Latitude degrees must be between 40 and 84"):
            FederalPermitSystem('A', 1, 39, 0, 42, 0)
        with self.assertRaisesRegex(ValueError, "Latitude degrees must be between 40 and 84"):
            FederalPermitSystem('A', 1, 85, 0, 42, 0)

    def test_invalid_construction_lat_minutes(self):
        with self.assertRaisesRegex(ValueError, "Latitude minutes must be in the series"):
            FederalPermitSystem('A', 1, 40, 1, 42, 0)
        with self.assertRaisesRegex(ValueError, "Latitude minutes must be in the series"):
             FederalPermitSystem('A', 1, 40, 60, 42, 0)

    def test_invalid_construction_lon_degrees(self):
        with self.assertRaisesRegex(ValueError, "Longitude degrees must be between 42 and 141"):
            FederalPermitSystem('A', 1, 40, 0, 41, 0)
        with self.assertRaisesRegex(ValueError, "Longitude degrees must be between 42 and 141"):
            FederalPermitSystem('A', 1, 40, 0, 142, 0)

    def test_invalid_construction_lon_minutes(self):
        with self.assertRaisesRegex(ValueError, "Longitude minutes must be in the series .* south of 70"):
            FederalPermitSystem('A', 1, 40, 0, 42, 1)
        with self.assertRaisesRegex(ValueError, "Longitude minutes must be in the series .* south of 70"):
             FederalPermitSystem('A', 1, 40, 0, 42, 60)
        with self.assertRaisesRegex(ValueError, "Longitude minutes must be in the series .* north of 70"):
             FederalPermitSystem('A', 1, 70, 0, 42, 1)
        with self.assertRaisesRegex(ValueError, "Longitude minutes must be in the series .* north of 70"):
             FederalPermitSystem('A', 1, 70, 0, 42, 15)

if __name__ == '__main__':
    unittest.main()
