import unittest
from UniqueWellIdentifier import UniqueWellIdentifier, SurveySystemCode
from LatLongCoordinate import LatLongCoordinate
from CoordinateConversionException import CoordinateConversionException
from CoordinateParseException import CoordinateParseException

class TestUniqueWellIdentifier(unittest.TestCase):

    # Test UWI strings corresponding to C# constructors
    NTS_UWI_STR = "200d096h094a1500"
    DLS_UWI_STR = "100000000000A00A" # Note: Seems invalid but matches C# test

    DLS_VALID_W6 = "100143608517W600"
    DLS_VALID_W5 = "100143608517W500"
    DLS_EVENT_SEQ_2 = "100162512315W602"
    NTS_VALID = "200D096H094A1500"
    FEDERAL_VALID = "300F556220121450"
    GEODETIC_VALID = "4007999910499900"

    def test_equality(self):
        a = UniqueWellIdentifier.parse(self.NTS_UWI_STR)
        b = UniqueWellIdentifier.parse(self.NTS_UWI_STR)
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        self.assertEqual(hash(a), hash(b))

    def test_nts_constructor_equivalent(self):
        a = UniqueWellIdentifier.parse(self.NTS_UWI_STR)
        self.assertIsNotNone(a)
        self.assertEqual(SurveySystemCode.NATIONAL_TOPOGRAPHIC_SERIES, a.survey_system)

    def test_dls_constructor_equivalent(self):
        b = UniqueWellIdentifier.parse(self.DLS_UWI_STR)
        self.assertIsNotNone(b)
        self.assertEqual(SurveySystemCode.DOMINION_LAND_SURVEY, b.survey_system)

    def test_nts_to_string(self):
        a = UniqueWellIdentifier.parse(self.NTS_UWI_STR)
        self.assertEqual(self.NTS_UWI_STR, str(a))

    def test_dls_to_string(self):
        a = UniqueWellIdentifier.parse(self.DLS_UWI_STR)
        self.assertEqual(self.DLS_UWI_STR, str(a))

    def test_parse_dls(self):
        a = UniqueWellIdentifier.parse(self.DLS_VALID_W6)
        self.assertEqual(SurveySystemCode.DOMINION_LAND_SURVEY, a.survey_system)
        self.assertEqual("00", a.location_exception_code)
        self.assertEqual("143608517W60", a.legal_survey_system)
        self.assertEqual('0', a.event_sequence_code)

        b = UniqueWellIdentifier.parse(self.DLS_EVENT_SEQ_2)
        self.assertEqual(SurveySystemCode.DOMINION_LAND_SURVEY, b.survey_system)
        self.assertEqual('2', b.event_sequence_code)

    def test_parse_nts(self):
        well_identifier = UniqueWellIdentifier.parse(self.NTS_VALID)
        self.assertEqual(SurveySystemCode.NATIONAL_TOPOGRAPHIC_SERIES, well_identifier.survey_system)
        self.assertEqual("00", well_identifier.location_exception_code)
        self.assertEqual("D096H094A150", well_identifier.legal_survey_system)
        self.assertEqual('0', well_identifier.event_sequence_code)

    def test_parse_federal(self):
        well_identifier = UniqueWellIdentifier.parse(self.FEDERAL_VALID)
        self.assertEqual(SurveySystemCode.FEDERAL_PERMIT_SYSTEM, well_identifier.survey_system)
        self.assertEqual("00", well_identifier.location_exception_code)
        self.assertEqual("F55622012145", well_identifier.legal_survey_system)
        self.assertEqual('0', well_identifier.event_sequence_code)

    def test_parse_geodetic(self):
        well_identifier = UniqueWellIdentifier.parse(self.GEODETIC_VALID)
        self.assertEqual(SurveySystemCode.GEODETIC_COORDINATES, well_identifier.survey_system)
        self.assertEqual("00", well_identifier.location_exception_code)
        self.assertEqual("799991049990", well_identifier.legal_survey_system)
        self.assertEqual('0', well_identifier.event_sequence_code)

    @unittest.skip("Skipping conversion tests until dependent classes are implemented/mocked")
    def test_geodetic_to_lat_long(self):
        a = UniqueWellIdentifier.parse(self.GEODETIC_VALID)
        ll = a.to_lat_long_coordinate()
        self.assertAlmostEqual(79.999, ll.latitude, places=3)
        self.assertAlmostEqual(104.999, ll.longitude, places=3)

    @unittest.skip("Skipping conversion tests until dependent classes are implemented/mocked")
    def test_nts_to_lat_long(self):
        a = UniqueWellIdentifier.parse(self.NTS_VALID)
        lat_long_coordinate = a.to_lat_long_coordinate()
        self.assertAlmostEqual(-120.5656280, lat_long_coordinate.longitude, places=7)
        self.assertAlmostEqual(56.914585, lat_long_coordinate.latitude, places=6)

    @unittest.skip("Skipping conversion tests until dependent classes are implemented/mocked")
    def test_dls_to_lat_long_with_exception(self):
        a = UniqueWellIdentifier.parse(self.DLS_VALID_W6)
        with self.assertRaises(CoordinateConversionException):
            a.to_lat_long_coordinate()

    @unittest.skip("Skipping conversion tests until dependent classes are implemented/mocked")
    def test_dls_to_lat_long(self):
        a = UniqueWellIdentifier.parse(self.DLS_VALID_W5)
        lat_long_coordinate = a.to_lat_long_coordinate()
        self.assertAlmostEqual(56.4191398, lat_long_coordinate.latitude, places=6)
        self.assertAlmostEqual(-116.5479126, lat_long_coordinate.longitude, places=6)

    @unittest.skip("Skipping conversion tests until dependent classes are implemented/mocked")
    def test_fps_to_lat_long(self):
        a = UniqueWellIdentifier.parse(self.FEDERAL_VALID)
        lat_long_coordinate = a.to_lat_long_coordinate()
        self.assertAlmostEqual(62.404167, lat_long_coordinate.latitude, places=6)
        self.assertAlmostEqual(-121.921875, lat_long_coordinate.longitude, places=6)

    def test_parse_invalid_length(self):
        with self.assertRaisesRegex(CoordinateParseException, "UWI must contain 16 characters"):
            UniqueWellIdentifier.parse("12345")
        with self.assertRaisesRegex(CoordinateParseException, "UWI must contain 16 characters"):
            UniqueWellIdentifier.parse("100143608517W600EXTRA")

    def test_parse_invalid_start_char(self):
        with self.assertRaisesRegex(CoordinateParseException, "Expected UWI to start with '1', '2', '3', or '4'"):
            UniqueWellIdentifier.parse("X00143608517W600")

    def test_parse_invalid_15th_char(self):
        with self.assertRaisesRegex(CoordinateParseException, "The 15th character must be zero for DLS UWI."):
            UniqueWellIdentifier.parse("100143608517W60X")
        with self.assertRaisesRegex(CoordinateParseException, "The 15th character must be zero for NTS UWI."):
            UniqueWellIdentifier.parse("200D096H094A150X")
        with self.assertRaisesRegex(CoordinateParseException, "The 15th character must be zero for Geodetic UWI."):
            UniqueWellIdentifier.parse("400799991049990X")

if __name__ == '__main__':
    unittest.main()
