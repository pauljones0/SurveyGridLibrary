import unittest
import math
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fromAngle import Angle

class TestAngle(unittest.TestCase):

    def test_from_radians(self):
        angle = Angle.from_radians(math.pi * 2)
        self.assertAlmostEqual(angle.gradians, 400)
        self.assertAlmostEqual(angle.radians, 6.28318530717959, places=9)
        self.assertAlmostEqual(angle.milliradians, 6283.18530717959, places=9)
        self.assertAlmostEqual(angle.degrees, 360)
        self.assertAlmostEqual(angle.minutes, 0)
        self.assertAlmostEqual(angle.seconds, 0)

    def test_from_degrees(self):
        angle = Angle.from_degrees(360.0)
        self.assertAlmostEqual(angle.gradians, 400)
        self.assertAlmostEqual(angle.radians, 6.28318530717959, places=9)
        self.assertAlmostEqual(angle.milliradians, 6283.18530717959, places=9)
        self.assertAlmostEqual(angle.minutes, 0)
        self.assertAlmostEqual(angle.seconds, 0)
        self.assertAlmostEqual(angle.degrees, 360)

    def test_equality(self):
        a = Angle.from_radians(math.pi)
        b = Angle.from_radians(math.pi)
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        self.assertTrue(a.equals(b))
        self.assertTrue(b.equals(a))

    def test_inequality(self):
        a = Angle.from_radians(math.pi)
        b = Angle.from_radians(math.pi + 0.25)
        self.assertFalse(a == b)
        self.assertTrue(a != b)
        self.assertFalse(a.equals(b))
        self.assertFalse(b.equals(a))

    def test_hash_code(self):
        self.assertEqual(Angle.from_radians(math.pi).get_hash_code(), Angle.from_radians(math.pi).get_hash_code())

    def test_to_string(self):
        a = Angle.from_radians(math.pi)
        self.assertEqual("3.141593", a.to_string())
        self.assertEqual("3.141593", a.to_string_format("g"))
        self.assertEqual("180°", a.to_string_format("d"))
        self.assertEqual("180 00.000", a.to_string_format("DD MM.MMM"))

    def test_comparison(self):
        a = Angle.from_degrees(100)
        b = Angle.from_degrees(200)
        c = Angle.from_degrees(300)
        self.assertEqual(a.compare_to(b), -1)
        self.assertEqual(b.compare_to(b), 0)
        self.assertEqual(c.compare_to(b), 1)

if __name__ == '__main__':
    unittest.main()
