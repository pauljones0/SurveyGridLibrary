import unittest
from ReferenceEllipsoid import ReferenceEllipsoid

class TestReferenceEllipsoid(unittest.TestCase):

    def test_method1(self):
        self.assertIsNotNone(ReferenceEllipsoid.Wgs84)
        self.assertIsNotNone(ReferenceEllipsoid.Clarke1866)
        self.assertIsNotNone(ReferenceEllipsoid.Grs80)

    def test_inverse_flattening(self):
        self.assertAlmostEqual(ReferenceEllipsoid.Wgs84.inverse_flattening, 1 / 298.257223563, places=17) # Corrected value based on C# definition
        self.assertAlmostEqual(ReferenceEllipsoid.Clarke1866.inverse_flattening, 1 / 294.978698214, places=17) # Corrected value based on C# definition
        self.assertAlmostEqual(ReferenceEllipsoid.Grs80.inverse_flattening, 1 / 298.257222101, places=17) # Corrected value based on C# definition

if __name__ == '__main__':
    unittest.main()
