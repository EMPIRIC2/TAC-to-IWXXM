"""Targeted encoder coverage tests for 98% package threshold."""

from __future__ import annotations

from unittest.mock import patch

import gifts.common.xmlConfig as des
import gifts.swaEncoder as swa_enc_mod
import gifts.tafEncoder as taf_enc_mod
import gifts.tcaEncoder as tca_enc_mod
import pytest


@pytest.fixture(autouse=True)
def _restore_translator() -> None:
    original = des.TRANSLATOR
    yield
    des.TRANSLATOR = original


def test_swa_encoder_handles_observation_exception() -> None:
    encoder = swa_enc_mod.Encoder()
    decoded = {
        "bbb": "A",
        "translationTime": "2020-01-01T00:00:00Z",
        "translatedBulletinReceptionTime": "2020-01-01T00:00:00Z",
        "translatedBulletinID": "ID",
    }
    with patch.object(encoder, "observations", side_effect=RuntimeError("encode failed")):
        with patch.object(encoder._Logger, "exception") as mock_log:
            encoder(decoded, "SWX TAC")
    assert mock_log.call_count >= 1


def test_swa_encoder_exercise_status_preamble() -> None:
    encoder = swa_enc_mod.Encoder()
    decoded = {
        "status": "EXERCISE",
        "bbb": "A",
        "translationTime": "2020-01-01T00:00:00Z",
        "translatedBulletinReceptionTime": "2020-01-01T00:00:00Z",
        "translatedBulletinID": "ID",
    }
    des.TRANSLATOR = True
    encoder(decoded, "SWX TAC")
    assert encoder.XMLDocument.get("permissibleUsageReason") == "EXERCISE"


def test_swa_encoder_skips_translator_metadata_when_disabled() -> None:
    encoder = swa_enc_mod.Encoder()
    decoded = {"bbb": "A"}
    des.TRANSLATOR = False
    encoder(decoded, "SWX TAC")
    assert encoder.XMLDocument.get("translationCentreName") is None


def test_taf_encoder_handles_missing_bbb() -> None:
    encoder = taf_enc_mod.Encoder()
    des.TRANSLATOR = False
    decoded = {"ident": {"alternate": "KJFK", "str": "KJFK", "name": "JFK Airport"}, "bbb": ""}
    encoder(decoded, "TAF TEST")
    assert encoder.XMLDocument.get("reportStatus") == "NORMAL"


def test_taf_encoder_nil_state() -> None:
    encoder = taf_enc_mod.Encoder()
    des.TRANSLATOR = False
    decoded = {"state": "nil", "bbb": "A", "itime": {"value": 1782085786}, "ident": {"alternate": "KJFK", "str": "KJFK", "name": "JFK Airport"}}
    encoder(decoded, "TAF NIL")
    assert encoder.nilPresent is True


def test_taf_encoder_cancelled_state() -> None:
    encoder = taf_enc_mod.Encoder()
    des.TRANSLATOR = False
    decoded = {
        "state": "canceled",
        "bbb": "A",
        "ident": {"alternate": "KJFK", "str": "KJFK", "name": "JFK Airport"},
        "vtime": {"from": 1782085786, "to": 1782089386},
    }
    encoder(decoded, "TAF CNL")
    assert encoder.canceled is True
    assert encoder.XMLDocument.get("isCancelReport") == "true"


def test_tca_encoder_handles_observation_exception() -> None:
    encoder = tca_enc_mod.Encoder()
    decoded = {
        "bbb": "A",
        "cycloneName": "ALICE",
        "advisoryNumber": "1",
        "fcst": {"0": {}},
        "issueTime": {"str": "2020-01-01T00:00:00Z"},
        "centre": "KNHC",
    }
    with patch.object(encoder, "result", side_effect=RuntimeError("result failed")):
        with patch.object(encoder._Logger, "exception") as mock_log:
            encoder(decoded, "TCA TAC")
    assert mock_log.call_count >= 1


def test_tca_encoder_exercise_status_preamble() -> None:
    encoder = tca_enc_mod.Encoder()
    decoded = {
        "status": "EXERCISE",
        "bbb": "A",
        "translationTime": "2020-01-01T00:00:00Z",
        "translatedBulletinReceptionTime": "2020-01-01T00:00:00Z",
        "translatedBulletinID": "ID",
        "cycloneName": "ALICE",
        "advisoryNumber": "1",
        "fcst": {"0": {}},
        "issueTime": {"str": "2020-01-01T00:00:00Z"},
        "centre": "KNHC",
    }
    des.TRANSLATOR = True
    encoder(decoded, "TCA TAC")
    assert encoder.XMLDocument.get("permissibleUsageReason") == "EXERCISE"


def test_taf_encoder_missing_state_uses_operational_defaults() -> None:
    encoder = taf_enc_mod.Encoder()
    des.TRANSLATOR = False
    decoded = {
        "bbb": "A",
        "ident": {"alternate": "KJFK", "str": "KJFK", "name": "JFK Airport"},
    }
    encoder(decoded, "TAF TEST")
    assert encoder.XMLDocument.get("permissibleUsage") == "OPERATIONAL"


def test_tca_encoder_test_status_without_issue_time() -> None:
    encoder = tca_enc_mod.Encoder()
    decoded = {
        "status": "TEST",
        "bbb": "A",
        "cycloneName": "ALICE",
        "advisoryNumber": "1",
        "fcst": {"0": {}},
        "centre": "KNHC",
    }
    des.TRANSLATOR = False
    encoder(decoded, "TCA TAC")
    assert encoder.nilPresent is True
