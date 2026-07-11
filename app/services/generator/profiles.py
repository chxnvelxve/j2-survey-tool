"""Success-criteria profiles by location vertical.

🟡 PLACEHOLDER thresholds — confirm real J2 values when Josh provides them.
Lookup table + per-job override (override wins field-by-field when set).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, replace
from typing import Any

DEFAULT_PROFILE_KEY = "office"

# 🟡 PLACEHOLDER — confirm real J2 thresholds before activation.
PROFILES: dict[str, "SuccessCriteria"] = {}


@dataclass(frozen=True)
class SuccessCriteria:
    """Resolved thresholds for the Success Criteria report section."""

    profile_key: str
    label: str
    min_rssi_dbm: int
    min_snr_db: int
    min_data_rate_mbps: int
    max_co_channel_aps: int
    is_override: bool = False

    def as_context(self) -> dict[str, Any]:
        return asdict(self)


def _seed_profiles() -> None:
    """Populate PROFILES once. Values are PLACEHOLDER sample thresholds."""
    if PROFILES:
        return
    samples = (
        SuccessCriteria("warehouse", "Warehouse", -67, 25, 144, 3),
        SuccessCriteria("office", "Office", -65, 25, 300, 3),
        SuccessCriteria("hospital", "Hospital", -62, 30, 300, 2),
        SuccessCriteria("outdoor_yard", "Outdoor Yard", -72, 20, 54, 4),
    )
    for row in samples:
        PROFILES[row.profile_key] = row


_seed_profiles()

_OVERRIDE_FIELDS = frozenset(
    {
        "min_rssi_dbm",
        "min_snr_db",
        "min_data_rate_mbps",
        "max_co_channel_aps",
        "label",
    },
)


def normalize_profile_key(vertical: str | None) -> str | None:
    if vertical is None:
        return None
    key = vertical.strip().casefold().replace(" ", "_").replace("-", "_")
    return key or None


def resolve_profile(
    vertical: str | None,
    override: dict[str, Any] | None = None,
) -> SuccessCriteria:
    """Resolve success criteria from vertical key + optional per-job override.

    Unknown/missing vertical → default ``office``. Override dict wins
    field-by-field for known threshold/label keys when set.
    """
    key = normalize_profile_key(vertical)
    base = PROFILES.get(key) if key else None
    if base is None:
        base = PROFILES[DEFAULT_PROFILE_KEY]

    if not override:
        return base

    updates: dict[str, Any] = {}
    for field in fields(SuccessCriteria):
        if field.name not in _OVERRIDE_FIELDS:
            continue
        if field.name not in override:
            continue
        value = override[field.name]
        if value is None:
            continue
        updates[field.name] = value

    if not updates:
        return base

    return replace(base, is_override=True, **updates)
