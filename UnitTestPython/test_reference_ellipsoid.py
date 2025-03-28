import unittest
from SurveyGridLibrary.ReferenceEllipsoid import ReferenceEllipsoid

class TestReferenceEllipsoid(unittest.TestCase):

    def test_method1(self):
        self.assertIsNotNone(ReferenceEllipsoid.Wgs84)
        self.assertIsNotNone(ReferenceEllipsoid.Clarke1866)
        self.assertIsNotNone(ReferenceEllipsoid.Grs80)

    def test_inverse_flattening(self):
        self.assertAlmostEqual(ReferenceEllipsoid.Wgs84.inverse_flattening, 0.00335281066474748, places=17)
        self.assertAlmostEqual(ReferenceEllipsoid.Clarke1866.inverse_flattening, 0.00339007530392762, places=17)
        self.assertAlmostEqual(ReferenceEllipsoid.Grs80.inverse_flattening, 0.00335281068118232, places=17)

if __name__ == '__main__':
    unittest.main()
