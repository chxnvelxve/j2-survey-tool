"""Unit tests for success-criteria profile resolution (Phase 9)."""
from __future__ import annotations

from app.services.generator.profiles import (
    DEFAULT_PROFILE_KEY,
    PROFILES,
    normalize_profile_key,
    resolve_profile,
)


def test_known_vertical_resolves() -> None:
    criteria = resolve_profile("warehouse")
    assert criteria.profile_key == "warehouse"
    assert criteria.min_rssi_dbm == -67
    assert criteria.min_snr_db == 25
    assert criteria.min_data_rate_mbps == 144
    assert criteria.max_co_channel_aps == 3
    assert criteria.is_override is False


def test_case_and_spacing_normalize() -> None:
    assert normalize_profile_key(" Outdoor Yard ") == "outdoor_yard"
    criteria = resolve_profile("Outdoor-Yard")
    assert criteria.profile_key == "outdoor_yard"
    assert criteria.min_rssi_dbm == -72


def test_unknown_or_missing_defaults_to_office() -> None:
    assert resolve_profile(None).profile_key == DEFAULT_PROFILE_KEY
    assert resolve_profile("").profile_key == DEFAULT_PROFILE_KEY
    assert resolve_profile("retail_mall").profile_key == DEFAULT_PROFILE_KEY
    assert resolve_profile(None).min_rssi_dbm == PROFILES["office"].min_rssi_dbm


def test_override_wins_field_by_field() -> None:
    criteria = resolve_profile(
        "office",
        {"min_rssi_dbm": -60, "min_snr_db": 35, "label": "Custom Office"},
    )
    assert criteria.profile_key == "office"
    assert criteria.min_rssi_dbm == -60
    assert criteria.min_snr_db == 35
    assert criteria.min_data_rate_mbps == 300  # unchanged from base
    assert criteria.label == "Custom Office"
    assert criteria.is_override is True


def test_empty_override_dict_is_noop() -> None:
    criteria = resolve_profile("hospital", {})
    assert criteria.is_override is False
    assert criteria.min_rssi_dbm == -62
