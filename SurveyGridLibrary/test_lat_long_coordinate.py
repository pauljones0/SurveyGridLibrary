import unittest
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.ReferenceEllipsoid import ReferenceEllipsoid
from SurveyGridLibrary.BcNtsGridSystem import BcNtsGridSystem
from SurveyGridLibrary.DlsSystem import DlsSystem
from SurveyGridLibrary.Angle import Angle

class TestLatLongCoordinate(unittest.TestCase):

    def test_construct_dms(self):
        lat_long_coordinate = LatLongCoordinate(50, 3, 4, 100, 1, 2)
        self.assertAlmostEqual(lat_long_coordinate.latitude, 50.0511093139648, places=7)
        self.assertAlmostEqual(lat_long_coordinate.longitude, 100.017219543457, places=7)

    def test_construct_dm(self):
        lat_long_coordinate = LatLongCoordinate(50, 3, 100, 1)
        self.assertAlmostEqual(lat_long_coordinate.latitude, 50.0499992370605, places=7)
        self.assertAlmostEqual(lat_long_coordinate.longitude, 100.016670227051, places=7)

    def test_from_radians(self):
        lat_long_coordinate = LatLongCoordinate.from_radians(math.pi, math.pi / 2)
        self.assertEqual(lat_long_coordinate.latitude, 90)
        self.assertEqual(lat_long_coordinate.longitude, 90)
        self.assertAlmostEqual(lat_long_coordinate.radians_lat, math.pi / 2, places=6)
        self.assertAlmostEqual(lat_long_coordinate.radians_lon, math.pi / 2, places=6)

    def test_clone(self):
        lat_long_coordinate = LatLongCoordinate.from_radians(math.pi, math.pi / 2)
        cloned = lat_long_coordinate.clone()
        self.assertNotEqual(lat_long_coordinate, cloned)
        self.assertEqual(lat_long_coordinate, cloned)

    def test_equality(self):
        a = LatLongCoordinate(1, 10)
        b = LatLongCoordinate(1, 10)
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        self.assertTrue(a.equals(b))
        self.assertTrue(b.equals(a))

    def test_inequality(self):
        a = LatLongCoordinate(1, 10)
        b = LatLongCoordinate(2, 10)
        self.assertFalse(a == b)
        self.assertTrue(a != b)
        self.assertFalse(a.equals(b))
        self.assertFalse(b.equals(a))

    def test_hash_code(self):
        self.assertEqual(hash(LatLongCoordinate(1, 10)), hash(LatLongCoordinate(1, 10)))

    def test_to_dms_string(self):
        a = LatLongCoordinate(1, 10)
        self.assertEqual(a.to_string(), "1, 10")
        self.assertEqual(a.to_string_format("g"), "1, 10")
        self.assertEqual(a.to_string_format("dm"), "N1 00.000 E10 00.000")
        self.assertEqual(a.to_string_format("dms"), "N1° 0' 0.0\" E10° 0' 0.0\"")

        b = LatLongCoordinate(-1, 10)
        self.assertEqual(b.to_string(), "-1, 10")
        self.assertEqual(b.to_string_format("g"), "-1, 10")
        self.assertEqual(b.to_string_format("dm"), "S1 00.000 E10 00.000")
        self.assertEqual(b.to_string_format("dms"), "S1° 0' 0.0\" E10° 0' 0.0\"")

        c = LatLongCoordinate(1, -10)
        self.assertEqual(c.to_string(), "1, -10")
        self.assertEqual(c.to_string_format("g"), "1, -10")
        self.assertEqual(c.to_string_format("dm"), "N1 00.000 W10 00.000")
        self.assertEqual(c.to_string_format("dms"), "N1° 0' 0.0\" W10° 0' 0.0\"")

        d = LatLongCoordinate(-1, -10)
        self.assertEqual(d.to_string(), "-1, -10")
        self.assertEqual(d.to_string_format("g"), "-1, -10")
        self.assertEqual(d.to_string_format("dm"), "S1 00.000 W10 00.000")
        self.assertEqual(d.to_string_format("dms"), "S1° 0' 0.0\" W10° 0' 0.0\"")

    def test_from_convertible(self):
        lat_long_coordinate = LatLongCoordinate.from_convertible_string("-1, -10")
        self.assertEqual(lat_long_coordinate.latitude, -1)
        self.assertEqual(lat_long_coordinate.longitude, -10)

    def test_parse(self):
        lat_long_coordinate = LatLongCoordinate.parse("n 54 30 w 100 15")
        self.assertEqual(lat_long_coordinate.latitude, 54.5)
        self.assertEqual(lat_long_coordinate.longitude, -100.25)

    def test_from_decimal_degrees(self):
        lat_long_coordinate = LatLongCoordinate.from_decimal_degrees("N54.5 W100.25")
        self.assertEqual(lat_long_coordinate.latitude, 54.5)
        self.assertEqual(lat_long_coordinate.longitude, -100.25)

    def test_to_bc_geographic_system(self):
        bc = LatLongCoordinate(54, -112).to_bc_nts_grid_system()
        self.assertIsNotNone(bc)
        self.assertEqual(bc.quarter_unit, 'A')
        self.assertEqual(bc.unit, 1)
        self.assertEqual(bc.block, 'A')
        self.assertEqual(bc.series, 83)
        self.assertEqual(bc.map_area, 'I')
        self.assertEqual(bc.sheet, 1)

    def test_direction_to(self):
        a = LatLongCoordinate(30, 30)
        b = LatLongCoordinate(30, 30)
        self.assertEqual(a.direction_to(b), Angle.from_radians(0))
        self.assertEqual(b.direction_to(a), Angle.from_radians(0))

        c = LatLongCoordinate(0, 0)
        self.assertAlmostEqual(a.direction_to(c).degrees, Angle.from_radians(3.903035).degrees, places=4)
        self.assertAlmostEqual(c.direction_to(a).degrees, Angle.from_radians(0.7614422).degrees, places=4)

    def test_distance_to(self):
        a = LatLongCoordinate(30, 30)
        b = LatLongCoordinate(40, 31)
        self.assertAlmostEqual(a.distance_to(b, ReferenceEllipsoid.Wgs84), 1113141.546, places=6)

    def test_sphere_distance_to(self):
        a = LatLongCoordinate(30, 30)
        b = LatLongCoordinate(40, 31)
        self.assertAlmostEqual(a.sphere_distance_to(b), 1116900.07417898, places=6)

    def test_great_circle_angle(self):
        a = LatLongCoordinate(30, 30)
        b = LatLongCoordinate(40, 31)
        d = LatLongCoordinate.great_circle_angle(a, b)
        self.assertAlmostEqual(d.degrees, 10.033284074692, places=6)

    def test_bc_geographic_system1(self):
        a = LatLongCoordinate(51, -114)
        nts = a.to_bc_nts_grid_system()
        self.assertEqual(nts.quarter_unit, 'A')
        self.assertEqual(nts.unit, 1)
        self.assertEqual(nts.block, 'A')
        self.assertEqual(nts.series, 82)
        self.assertEqual(nts.map_area, 'O')
        self.assertEqual(nts.sheet, 1)

    def test_bc_geographic_system2(self):
        nts = LatLongCoordinate(54, -115).to_bc_nts_grid_system()
        self.assertEqual(nts.quarter_unit, 'A')
        self.assertEqual(nts.unit, 1)
        self.assertEqual(nts.block, 'A')
        self.assertEqual(nts.series, 83)
        self.assertEqual(nts.map_area, 'J')
        self.assertEqual(nts.sheet, 3)

    def test_dls_system_near_fifth(self):
        coordinate = LatLongCoordinate(51, -114)
        dls = LatLongCoordinate.to_dls_system(coordinate)
        self.assertEqual(dls.township, 23)
        self.assertEqual(dls.range, 29)
        self.assertEqual(dls.direction, 'W')
        self.assertEqual(dls.meridian, 4)
        self.assertEqual(dls.section, 33)
        self.assertEqual(dls.quarter, "SW")
        self.assertEqual(dls.legal_subdivision, 5)

    def test_dls_system2(self):
        dls = LatLongCoordinate(54, -115).to_dls_system()
        self.assertEqual(dls.direction, 'W')
        self.assertEqual(dls.meridian, 5)
        self.assertEqual(dls.township, 58)
        self.assertEqual(dls.range, 7)
        self.assertEqual(dls.section, 8)
        self.assertEqual(dls.quarter, "NE")
        self.assertEqual(dls.legal_subdivision, 9)

if __name__ == '__main__':
    unittest.main()
