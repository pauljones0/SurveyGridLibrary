import unittest
from SurveyGridLibrary.UniqueWellIdentifier import UniqueWellIdentifier
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.CoordinateConversionException import CoordinateConversionException

class TestUniqueWellIdentifier(unittest.TestCase):

    def test_equality(self):
        a = UniqueWellIdentifier('0', 'd', 96, 'h', 94, 'a', 15, '0')
        b = UniqueWellIdentifier('0', 'd', 96, 'h', 94, 'a', 15, '0')
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        self.assertTrue(a.equals(b))
        self.assertTrue(b.equals(a))
        self.assertTrue(a.get_hash_code() == b.get_hash_code())

    def test_nts_constructor(self):
        a = UniqueWellIdentifier('0', 'd', 96, 'h', 94, 'a', 15, '0')
        self.assertIsNotNone(a)

    def test_dls_constructor(self):
        b = UniqueWellIdentifier("00", 0, 0, 0, 0, 'A', 0, 'A')
        self.assertIsNotNone(b)

    def test_nts_to_string(self):
        a = UniqueWellIdentifier('0', 'd', 96, 'h', 94, 'a', 15, '0')
        self.assertEqual("200d096h094a1500", a.to_string())

    def test_dls_to_string(self):
        a = UniqueWellIdentifier("00", 0, 0, 0, 0, 'A', 0, 'A')
        self.assertEqual("100000000000A00A", a.to_string())

    def test_parse_dls(self):
        a = UniqueWellIdentifier.parse("100143608517W600")
        self.assertEqual(UniqueWellIdentifier.SurveySystemCode.DOMINION_LAND_SURVEY, a.survey_system)
        self.assertEqual("00", a.location_exception_code)
        self.assertEqual("143608517W60", a.legal_survey_system)
        self.assertEqual('0', a.event_sequence_code)

        b = UniqueWellIdentifier.parse("100162512315W602")
        self.assertEqual(UniqueWellIdentifier.SurveySystemCode.DOMINION_LAND_SURVEY, b.survey_system)

    def test_parse_nts(self):
        well_identifier = UniqueWellIdentifier.parse("200D096H094A1500")
        self.assertEqual(UniqueWellIdentifier.SurveySystemCode.NATIONAL_TOPOGRAPHIC_SERIES, well_identifier.survey_system)
        self.assertEqual("00", well_identifier.location_exception_code)
        self.assertEqual("D096H094A150", well_identifier.legal_survey_system)
        self.assertEqual('0', well_identifier.event_sequence_code)

    def test_parse_federal(self):
        well_identifier = UniqueWellIdentifier.parse("300F556220121450")
        self.assertEqual(UniqueWellIdentifier.SurveySystemCode.FEDERAL_PERMIT_SYSTEM, well_identifier.survey_system)
        self.assertEqual("00", well_identifier.location_exception_code)
        self.assertEqual("F55622012145", well_identifier.legal_survey_system)
        self.assertEqual('0', well_identifier.event_sequence_code)

    def test_parse_geodetic(self):
        well_identifier = UniqueWellIdentifier.parse("4007999910499900")
        self.assertEqual(UniqueWellIdentifier.SurveySystemCode.GEODETIC_COORDINATES, well_identifier.survey_system)
        self.assertEqual("00", well_identifier.location_exception_code)
        self.assertEqual("799991049990", well_identifier.legal_survey_system)
        self.assertEqual('0', well_identifier.event_sequence_code)

    def test_geodetic_to_lat_long(self):
        a = UniqueWellIdentifier.parse("4007999910499900")
        ll = UniqueWellIdentifier.to_lat_long_coordinate(a)
        self.assertAlmostEqual(79.999, ll.latitude, places=3)
        self.assertAlmostEqual(104.999, ll.longitude, places=3)

    def test_nts_to_lat_long(self):
        a = UniqueWellIdentifier.parse("200D096H094A1500")
        lat_long_coordinate = UniqueWellIdentifier.to_lat_long_coordinate(a)
        self.assertAlmostEqual(-120.5656280, lat_long_coordinate.longitude, places=7)
        self.assertAlmostEqual(56.914585, lat_long_coordinate.latitude, places=6)

    def test_dls_to_lat_long_with_exception(self):
        a = UniqueWellIdentifier.parse("100143608517W600")
        with self.assertRaises(CoordinateConversionException):
            UniqueWellIdentifier.to_lat_long_coordinate(a)

    def test_dls_to_lat_long(self):
        a = UniqueWellIdentifier.parse("100143608517W500")
        lat_long_coordinate = UniqueWellIdentifier.to_lat_long_coordinate(a)
        self.assertAlmostEqual(56.4191398, lat_long_coordinate.latitude, places=6)
        self.assertAlmostEqual(-116.5479126, lat_long_coordinate.longitude, places=6)

    def test_fps_to_lat_long(self):
        a = UniqueWellIdentifier.parse("300F556220121450")
        lat_long_coordinate = UniqueWellIdentifier.to_lat_long_coordinate(a)
        self.assertAlmostEqual(62.404167, lat_long_coordinate.latitude, places=6)
        self.assertAlmostEqual(-121.921875, lat_long_coordinate.longitude, places=6)

if __name__ == '__main__':
    unittest.main()
