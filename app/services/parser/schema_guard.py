"""Ekahau .esx schema shape validation — see docs/esx_schema.md."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from app.services.parser.errors import ParseError

RootType = Literal["object", "array"]

_PROJECT_KEYS = frozenset({"name", "version", "created", "modified"})
_FLOOR_KEYS = frozenset({"id", "name", "image", "imageRef", "heatmap", "heatmapRef"})
_AP_KEYS = frozenset({"id", "name", "model", "vendor", "floorId", "floor_id", "x", "y"})
_RADIO_KEYS = frozenset({"accessPointId", "apId", "band", "channel", "txPower", "tx_power"})


@dataclass(frozen=True)
class EsxSchemaProfile:
    fingerprint: str
    required_json: tuple[str, ...]
    optional_json: tuple[str, ...]
    allowed_keys: dict[str, frozenset[str]]
    root_types: dict[str, RootType]


FIXTURE_V1 = EsxSchemaProfile(
    fingerprint="fixture_v1",
    required_json=("project.json", "floorPlans.json", "accessPoints.json"),
    optional_json=("simulatedRadios.json", "measuredRadios.json"),
    allowed_keys={
        "project.json": _PROJECT_KEYS,
        "floorPlans.json": _FLOOR_KEYS,
        "accessPoints.json": _AP_KEYS,
        "simulatedRadios.json": _RADIO_KEYS,
        "measuredRadios.json": _RADIO_KEYS,
    },
    root_types={
        "project.json": "object",
        "floorPlans.json": "array",
        "accessPoints.json": "array",
        "simulatedRadios.json": "array",
        "measuredRadios.json": "array",
    },
)

KNOWN_PROFILES: tuple[EsxSchemaProfile, ...] = (FIXTURE_V1,)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ParseError(f"Invalid JSON in {path.name}: {exc}") from exc


def _unknown_keys(record: dict[str, Any], allowed: frozenset[str]) -> list[str]:
    return sorted(key for key in record if key not in allowed)


def _collect_unknown_keys(
    records: list[Any],
    *,
    filename: str,
    allowed: frozenset[str],
) -> list[str]:
    """Return sorted unique unknown keys; record non-object items as violations."""
    unknown: set[str] = set()
    for idx, item in enumerate(records):
        if not isinstance(item, dict):
            return [f"{filename}[{idx}] must be an object"]
        unknown.update(_unknown_keys(item, allowed))
    return sorted(unknown)


def _profile_violations(
    extract_dir: Path,
    profile: EsxSchemaProfile,
    *,
    source_name: str,
) -> list[str]:
    """Return human-readable violation messages; empty if profile matches."""
    violations: list[str] = []

    for filename in profile.required_json:
        if not (extract_dir / filename).is_file():
            violations.append(f"missing required file {filename}")

    if violations:
        return violations

    for filename in (*profile.required_json, *profile.optional_json):
        path = extract_dir / filename
        if not path.is_file():
            continue

        data = _read_json(path)
        expected_root = profile.root_types[filename]
        if expected_root == "object":
            if not isinstance(data, dict):
                violations.append(f"{filename} must be a JSON object")
                continue
            unknown = _unknown_keys(data, profile.allowed_keys[filename])
            if unknown:
                violations.append(f"{filename}: unknown key(s): {unknown}")
        else:
            if not isinstance(data, list):
                violations.append(f"{filename} must be a JSON array")
                continue
            unknown = _collect_unknown_keys(
                data,
                filename=filename,
                allowed=profile.allowed_keys[filename],
            )
            if unknown:
                if len(unknown) == 1 and unknown[0].endswith("must be an object"):
                    violations.append(unknown[0])
                else:
                    violations.append(f"{filename}: unknown key(s): {unknown}")

    return violations


def detect_and_validate(extract_dir: Path, *, source_name: str) -> str:
    """Validate extracted .esx contents against known schema profiles.

    Returns the matched fingerprint string. Raises ParseError on unknown shape.
    """
    for profile in KNOWN_PROFILES:
        violations = _profile_violations(extract_dir, profile, source_name=source_name)
        if not violations:
            return profile.fingerprint

    # Re-run first profile to produce actionable errors for the most likely target.
    violations = _profile_violations(extract_dir, FIXTURE_V1, source_name=source_name)
    if violations:
        detail = "; ".join(violations)
        raise ParseError(
            f"Unrecognized .esx schema shape (expected {FIXTURE_V1.fingerprint}): {detail}",
            source_name=source_name,
        )

    raise ParseError("Unrecognized .esx schema shape", source_name=source_name)
