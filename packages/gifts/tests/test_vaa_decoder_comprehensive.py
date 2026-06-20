"""Comprehensive tests for vaaDecoder module"""

from gifts.vaaDecoder import Decoder


class TestVaaDecoderBasic:
    """Test basic VAA decoder functionality"""

    def test_decoder_init(self):
        """Test decoder initialization"""
        decoder = Decoder()
        assert decoder is not None
        # vaa dict only exists after calling decoder

    def test_decoder_call_with_empty_string(self):
        """Test decoding empty string"""
        decoder = Decoder()
        result = decoder("")

        assert isinstance(result, dict)
        assert "err_msg" in result
        assert "VA ADVISORY line not found" in result["err_msg"]

    def test_decoder_call_with_no_va_advisory_header(self):
        """Test decoding text without VA ADVISORY header"""
        decoder = Decoder()
        result = decoder("Some random text without the proper header")

        assert isinstance(result, dict)
        assert "err_msg" in result

    def test_vaa_decoder_is_a_test_method(self):
        """Test _is_a_test method"""
        decoder = Decoder()
        decoder.vaa = {}

        # Not marked as test
        assert decoder._is_a_test() is False

        # Marked as test
        decoder.vaa["status"] = "TEST"
        assert decoder._is_a_test() is True

        # Test status
        decoder.vaa["status"] = "OTHER"
        assert decoder._is_a_test() is False


class TestVaaDecoderExercise:
    """Test VAA decoder with EXERCISE status"""

    def test_decode_exercise_vaa(self):
        """Test decoding an EXERCISE status VAA"""
        exercise_vaa = """FVAU03 ADRM 150252
VA ADVISORY
STATUS: EXERCISE
DTG: 20251215/0000Z
VAAC: NONE
VOLCANO: UNKNOWN
PSN: UNKNOWN
AREA: UNKNOWN
SOURCE ELEV: UNKNOWN
ADVISORY NR: 0000/0
INFO SOURCE: NONE
ERUPTION DETAILS: NONE
EST VA DTG: NOT PROVIDED
EST VA CLD: NOT PROVIDED
FCST VA CLD +6HR: 15/0600Z NOT PROVIDED
FCST VA CLD +12HR: 15/1200Z NOT AVBL
FCST VA CLD +18HR: 15/1800Z NO VA EXP
RMK: NONE
NXT ADVISORY: NO FURTHER ADVISORIES"""

        decoder = Decoder()
        result = decoder(exercise_vaa)

        assert isinstance(result, dict)
        # Exercise messages should not produce err_msg
        assert "err_msg" not in result or result.get("err_msg") is None

    def test_decode_test_vaa(self):
        """Test decoding TEST status VAA"""
        test_vaa = """FVXX23 KNES 171857
VA ADVISORY
STATUS: TEST
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 12346 FT AMSL
ADVISORY NR: 2025/682
INFO SOURCE: GOES-19. NWP MODELS.
ERUPTION DETAILS: ONGOING VA EMS
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 - N1428 W09052 - N1427 W09105 - N1431 W09105 MOV W 10KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053 - N1428 W09052 - N1426 W09105 - N1432 W09105
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053 - N1428 W09052 - N1426 W09105 - N1432 W09105
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053 - N1428 W09053 - N1426 W09105 - N1432 W09105
RMK: TEST MESSAGE
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(test_vaa)

        assert isinstance(result, dict)
        # Test messages should not produce err_msg
        assert "err_msg" not in result or result.get("err_msg") is None


class TestVaaDecoderValidMessage:
    """Test VAA decoder with valid messages"""

    def test_decode_fuego_vaa(self):
        """Test decoding Fuego VAA"""
        fuego_vaa = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 12346 FT AMSL
ADVISORY NR: 2025/682
INFO SOURCE: GOES-19. NWP MODELS.
ERUPTION DETAILS: ONGOING VA EMS
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 - N1428 W09052 - N1427 W09105 - N1431 W09105 MOV W 10KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053 - N1428 W09052 - N1426 W09105 - N1432 W09105
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053 - N1428 W09052 - N1426 W09105 - N1432 W09105
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053 - N1428 W09053 - N1426 W09105 - N1432 W09105
RMK: VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA.
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(fuego_vaa)

        assert isinstance(result, dict)
        assert "volcanoName" in result
        assert "FUEGO" in result["volcanoName"]  # Includes volcano number in output
        assert "advisoryNumber" in result
        assert "clouds" in result

    def test_decode_semeru_vaa(self):
        """Test decoding Semeru VAA"""
        semeru_vaa = """FVAU03 ADRM 150252
VA ADVISORY
DTG: 20200615/0252Z
VAAC: DARWIN
VOLCANO: SEMERU 263300
PSN: S0806 E11255
AREA: INDONESIA
SOURCE ELEV: 3676M AMSL
ADVISORY NR: 2020/96
INFO SOURCE: CVGHM, HIMAWARI-8
ERUPTION DETAILS: GROUND REPORT OF VA ERUPTION TO FL130 AT 15/0237Z
OBS VA DTG: 15/0252Z
OBS VA CLD: SFC/FL180 S0806 E11255 MOV E 10KT
FCST VA CLD +6HR: 15/0852Z SFC/FL200 S0806 E11255
FCST VA CLD +12HR: 15/1452Z SFC/FL200 S0806 E11255
FCST VA CLD +18HR: 16/0052Z SFC/FL200 S0806 E11255
RMK: VOLCANIC ASH ADVISORY NOT ISSUED.
NXT ADVISORY: WILL BE ISSUED BY 20200615/0852Z"""

        decoder = Decoder()
        result = decoder(semeru_vaa)

        assert isinstance(result, dict)
        assert "volcanoName" in result


class TestVaaDecoderHeaderParsing:
    """Test VAA header/message structure parsing"""

    def test_decoder_header_extraction(self):
        """Test that decoder correctly extracts header"""
        vaa_with_header = """SOMEHDR TEXT
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: TEST
PSN: N1428 W09052
AREA: TEST
SOURCE ELEV: 1000 M AMSL
ADVISORY NR: 2025/1
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: NOT PROVIDED
FCST VA CLD +6HR: 18/0030Z NOT PROVIDED
FCST VA CLD +12HR: 18/0630Z NOT PROVIDED
FCST VA CLD +18HR: 18/1230Z NOT PROVIDED
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa_with_header)

        assert isinstance(result, dict)

    def test_decoder_with_multiline_remarks(self):
        """Test decoding with multiline remarks"""
        vaa_multiline = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 12346 FT AMSL
ADVISORY NR: 2025/682
INFO SOURCE: GOES-19. NWP MODELS.
ERUPTION DETAILS: ONGOING VA EMS
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 - N1428 W09052 - N1427 W09105 - N1431 W09105 MOV W 10KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053 - N1428 W09052 - N1426 W09105 - N1432 W09105
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053 - N1428 W09052 - N1426 W09105 - N1432 W09105
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053 - N1428 W09053 - N1426 W09105 - N1432 W09105
RMK: MULTILINE REMARK LINE ONE
LINE TWO OF REMARKS HERE
LINE THREE CONTINUES HERE
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa_multiline)

        assert isinstance(result, dict)
        assert "remarks" in result


class TestVaaDecoderCloudInfo:
    """Test cloud information parsing"""

    def test_decoder_cloud_layers(self):
        """Test parsing cloud layer information"""
        vaa_clouds = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 12346 FT AMSL
ADVISORY NR: 2025/682
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: FL100/FL200 N1431 W09105 - N1428 W09052 MOV W 10KT
FCST VA CLD +6HR: 18/0030Z FL100/FL200 N1432 W09105 - N1428 W09053
FCST VA CLD +12HR: 18/0630Z FL100/FL200 N1432 W09105 - N1428 W09053
FCST VA CLD +18HR: 18/1230Z FL100/FL200 N1432 W09105 - N1428 W09053
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa_clouds)

        assert isinstance(result, dict)
        if "clouds" in result:
            assert isinstance(result["clouds"], dict)

    def test_decoder_no_ash_expected(self):
        """Test parsing NO ASH EXPECTED statement"""
        vaa_no_ash = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 12346 FT AMSL
ADVISORY NR: 2025/682
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: NOT PROVIDED
FCST VA CLD +6HR: 18/0030Z NO VA EXP
FCST VA CLD +12HR: 18/0630Z NO VA EXP
FCST VA CLD +18HR: 18/1230Z NO VA EXP
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa_no_ash)

        assert isinstance(result, dict)

    def test_decoder_not_available(self):
        """Test parsing NOT AVBL statement"""
        vaa_not_avbl = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 12346 FT AMSL
ADVISORY NR: 2025/682
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: NOT AVBL
FCST VA CLD +6HR: 18/0030Z NOT AVBL
FCST VA CLD +12HR: 18/0630Z NOT AVBL
FCST VA CLD +18HR: 18/1230Z NOT AVBL
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa_not_avbl)

        assert isinstance(result, dict)


class TestVaaDecoderMovement:
    """Test ash cloud movement parsing"""

    def test_decoder_movement_cardinal(self):
        """Test parsing cardinal direction movement"""
        vaa_movement = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 12346 FT AMSL
ADVISORY NR: 2025/682
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 MOV N 15KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa_movement)

        assert isinstance(result, dict)

    def test_decoder_movement_compound_direction(self):
        """Test parsing compound direction movement (NW, NE, SW, SE)"""
        vaa_nw = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 12346 FT AMSL
ADVISORY NR: 2025/682
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 MOV NW 20KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa_nw)

        assert isinstance(result, dict)


class TestVaaDecoderElevation:
    """Test source elevation parsing"""

    def test_decoder_elevation_meters(self):
        """Test elevation in meters"""
        vaa_elevation = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 3676 M AMSL
ADVISORY NR: 2025/682
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 MOV W 10KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa_elevation)

        assert isinstance(result, dict)

    def test_decoder_elevation_feet(self):
        """Test elevation in feet"""
        vaa_elevation = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 12346 FT AMSL
ADVISORY NR: 2025/682
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 MOV W 10KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa_elevation)

        assert isinstance(result, dict)

    def test_decoder_elevation_unknown(self):
        """Test unknown elevation"""
        vaa_elevation = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: UNKNOWN
PSN: N1428 W09052
AREA: TEST
SOURCE ELEV: UNKNOWN
ADVISORY NR: 2025/682
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: NOT PROVIDED
FCST VA CLD +6HR: 18/0030Z NOT PROVIDED
FCST VA CLD +12HR: 18/0630Z NOT PROVIDED
FCST VA CLD +18HR: 18/1230Z NOT PROVIDED
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa_elevation)

        assert isinstance(result, dict)


class TestVaaDecoderDataFields:
    """Test various VAA data fields"""

    def test_decoder_volcano_name(self):
        """Test volcano name parsing"""
        vaa = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: FUEGO 342090
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 12346 FT AMSL
ADVISORY NR: 2025/682
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 MOV W 10KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa)

        assert isinstance(result, dict)
        assert "volcanoName" in result

    def test_decoder_advisory_number(self):
        """Test advisory number parsing"""
        vaa = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: TEST
PSN: N1428 W09052
AREA: GUATEMALA
SOURCE ELEV: 1000 M AMSL
ADVISORY NR: 2025/682
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 MOV W 10KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa)

        assert isinstance(result, dict)
        assert "advisoryNumber" in result

    def test_decoder_vaac_center(self):
        """Test VAAC center parsing"""
        vaa = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: LONDON
VOLCANO: TEST
PSN: N1428 W09052
AREA: TEST
SOURCE ELEV: 1000 M AMSL
ADVISORY NR: 2025/1
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 MOV W 10KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa)

        assert isinstance(result, dict)


class TestVaaDecoderEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_decoder_no_forecast(self):
        """Test VAA with minimal forecast info"""
        vaa = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: TEST
PSN: N1428 W09052
AREA: TEST
SOURCE ELEV: 1000 M AMSL
ADVISORY NR: 2025/1
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: NOT PROVIDED
FCST VA CLD +6HR: 18/0030Z NOT PROVIDED
FCST VA CLD +12HR: 18/0630Z NOT PROVIDED
FCST VA CLD +18HR: 18/1230Z NOT PROVIDED
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa)

        assert isinstance(result, dict)

    def test_decoder_special_characters_in_remarks(self):
        """Test remarks with special characters"""
        vaa = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: TEST
PSN: N1428 W09052
AREA: TEST
SOURCE ELEV: 1000 M AMSL
ADVISORY NR: 2025/1
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: NOT PROVIDED
FCST VA CLD +6HR: 18/0030Z NOT PROVIDED
FCST VA CLD +12HR: 18/0630Z NOT PROVIDED
FCST VA CLD +18HR: 18/1230Z NOT PROVIDED
RMK: TEST/REMARKS WITH SPECIAL CHARS: @#$%
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa)

        assert isinstance(result, dict)

    def test_decoder_long_latitude_longitude(self):
        """Test with 4-digit lat/lon values"""
        vaa = """FVXX23 KNES 171857
VA ADVISORY
DTG: 20251217/1857Z
VAAC: WASHINGTON
VOLCANO: TEST
PSN: N1428 W09052
AREA: TEST
SOURCE ELEV: 1000 M AMSL
ADVISORY NR: 2025/1
INFO SOURCE: TEST
ERUPTION DETAILS: TEST
OBS VA DTG: 17/1830Z
OBS VA CLD: SFC/FL140 N1431 W09105 - N1428 W09052 MOV W 10KT
FCST VA CLD +6HR: 18/0030Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +12HR: 18/0630Z SFC/FL140 N1432 W09105 - N1428 W09053
FCST VA CLD +18HR: 18/1230Z SFC/FL140 N1432 W09105 - N1428 W09053
RMK: TEST
NXT ADVISORY: WILL BE ISSUED BY 20251218/0115Z"""

        decoder = Decoder()
        result = decoder(vaa)

        assert isinstance(result, dict)


class TestVaaDecoderAttributes:
    """Test VAA decoder initialization and attributes"""

    def test_decoder_has_header_regex(self):
        """Test that decoder has header regex"""
        decoder = Decoder()
        assert hasattr(decoder, "header")
        assert decoder.header is not None

    def test_decoder_has_winds_regex(self):
        """Test that decoder has winds regex"""
        decoder = Decoder()
        assert hasattr(decoder, "_reWinds")
        assert decoder._reWinds is not None

    def test_decoder_has_tokeninenerglish(self):
        """Test that decoder has _tokenInEnglish mapping"""
        decoder = Decoder()
        assert hasattr(decoder, "_tokenInEnglish")
        assert isinstance(decoder._tokenInEnglish, dict)

    def test_decoder_vaa_dict_structure(self):
        """Test initial VAA dictionary structure"""
        decoder = Decoder()
        # Trigger call to initialize vaa dict
        decoder("")

        # Check structure of vaa dict
        assert "bbb" in decoder.vaa
        assert "translationTime" in decoder.vaa
        assert "volcanoName" in decoder.vaa
        assert "clouds" in decoder.vaa
        assert "remarks" in decoder.vaa
