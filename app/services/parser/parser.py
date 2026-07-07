"""Parser stage: .esx -> SurveyModel. See .cursor/skills/esx-parser/SKILL.md.

Provisional mapping — unverified against real J2 .esx (blocked on Josh).
Re-run debug recipe when real file arrives:
  1. unzip -l file.esx
  2. pretty-print each JSON's top-level keys
  3. map real keys -> SurveyModel fields; update parser + fixture test
"""
from __future__ import annotations

import json
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO

from app.schemas.survey import (
    SurveyAP,
    SurveyFloor,
    SurveyModel,
    SurveyProject,
    SurveyRadio,
)
from app.services.parser.errors import ParseError

_REQUIRED_JSON = ("project.json", "floorPlans.json", "accessPoints.json")
_OPTIONAL_JSON = ("simulatedRadios.json", "measuredRadios.json")


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ParseError(f"Invalid JSON in {path.name}: {exc}") from exc


def _require_dict(data: Any, *, label: str, source_name: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ParseError(f"{label} must be a JSON object", source_name=source_name)
    return data


def _require_list(data: Any, *, label: str, source_name: str) -> list[Any]:
    if not isinstance(data, list):
        raise ParseError(f"{label} must be a JSON array", source_name=source_name)
    return data


def _first_key(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in record:
            return record[key]
    return None


def _parse_project(data: dict[str, Any], *, source_name: str) -> SurveyProject:
    name = data.get("name")
    if not isinstance(name, str):
        raise ParseError("project.json missing required string key 'name'", source_name=source_name)
    return SurveyProject(name=name)


def _parse_floors(data: list[Any], *, source_name: str) -> list[SurveyFloor]:
    floors: list[SurveyFloor] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ParseError(
                f"floorPlans.json[{idx}] must be an object",
                source_name=source_name,
            )
        floor_id = _first_key(item, "id")
        floor_name = _first_key(item, "name")
        if not isinstance(floor_id, str):
            raise ParseError(
                f"floorPlans.json[{idx}] missing required string key 'id'",
                source_name=source_name,
            )
        if not isinstance(floor_name, str):
            raise ParseError(
                f"floorPlans.json[{idx}] missing required string key 'name'",
                source_name=source_name,
            )
        image_ref = _first_key(item, "image", "imageRef")
        if image_ref is not None and not isinstance(image_ref, str):
            raise ParseError(
                f"floorPlans.json[{idx}] key 'image'/'imageRef' must be a string",
                source_name=source_name,
            )
        floors.append(
            SurveyFloor(id=floor_id, name=floor_name, image_ref=image_ref),
        )
    return floors


def _parse_radios_by_ap_id(extract_dir: Path, *, source_name: str) -> dict[str, list[SurveyRadio]]:
    radios_by_ap: dict[str, list[SurveyRadio]] = {}
    for filename in _OPTIONAL_JSON:
        path = extract_dir / filename
        if not path.is_file():
            continue
        raw = _read_json(path)
        records = _require_list(raw, label=filename, source_name=source_name)
        for idx, item in enumerate(records):
            if not isinstance(item, dict):
                raise ParseError(
                    f"{filename}[{idx}] must be an object",
                    source_name=source_name,
                )
            ap_id = _first_key(item, "accessPointId", "apId")
            if not isinstance(ap_id, str):
                raise ParseError(
                    f"{filename}[{idx}] missing required string key 'accessPointId'/'apId'",
                    source_name=source_name,
                )
            band = _first_key(item, "band")
            if not isinstance(band, str):
                raise ParseError(
                    f"{filename}[{idx}] missing required string key 'band'",
                    source_name=source_name,
                )
            channel = _first_key(item, "channel")
            if channel is not None and not isinstance(channel, int):
                raise ParseError(
                    f"{filename}[{idx}] key 'channel' must be an integer",
                    source_name=source_name,
                )
            tx_power = _first_key(item, "txPower", "tx_power")
            if tx_power is not None and not isinstance(tx_power, (int, float)):
                raise ParseError(
                    f"{filename}[{idx}] key 'txPower'/'tx_power' must be a number",
                    source_name=source_name,
                )
            radio = SurveyRadio(
                band=band,
                channel=channel,
                tx_power=float(tx_power) if tx_power is not None else None,
            )
            radios_by_ap.setdefault(ap_id, []).append(radio)
    return radios_by_ap


def _parse_aps(
    data: list[Any],
    *,
    source_name: str,
    radios_by_ap: dict[str, list[SurveyRadio]],
) -> list[SurveyAP]:
    aps: list[SurveyAP] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ParseError(
                f"accessPoints.json[{idx}] must be an object",
                source_name=source_name,
            )
        name = item.get("name")
        if not isinstance(name, str):
            raise ParseError(
                f"accessPoints.json[{idx}] missing required string key 'name'",
                source_name=source_name,
            )
        model = _first_key(item, "model")
        if model is not None and not isinstance(model, str):
            raise ParseError(
                f"accessPoints.json[{idx}] key 'model' must be a string",
                source_name=source_name,
            )
        vendor = _first_key(item, "vendor")
        if vendor is not None and not isinstance(vendor, str):
            raise ParseError(
                f"accessPoints.json[{idx}] key 'vendor' must be a string",
                source_name=source_name,
            )
        floor_id = _first_key(item, "floorId", "floor_id")
        if floor_id is not None and not isinstance(floor_id, str):
            raise ParseError(
                f"accessPoints.json[{idx}] key 'floorId'/'floor_id' must be a string",
                source_name=source_name,
            )
        x = _first_key(item, "x")
        if x is not None and not isinstance(x, (int, float)):
            raise ParseError(
                f"accessPoints.json[{idx}] key 'x' must be a number",
                source_name=source_name,
            )
        y = _first_key(item, "y")
        if y is not None and not isinstance(y, (int, float)):
            raise ParseError(
                f"accessPoints.json[{idx}] key 'y' must be a number",
                source_name=source_name,
            )
        ap_record_id = _first_key(item, "id")
        ap_radios: list[SurveyRadio] = []
        if isinstance(ap_record_id, str):
            ap_radios = radios_by_ap.get(ap_record_id, [])
        aps.append(
            SurveyAP(
                name=name,
                model=model,
                vendor=vendor,
                floor_id=floor_id,
                x=float(x) if x is not None else None,
                y=float(y) if y is not None else None,
                radios=ap_radios,
            ),
        )
    return aps


def _parse_extracted_dir(extract_dir: Path, *, source_name: str) -> SurveyModel:
    for filename in _REQUIRED_JSON:
        if not (extract_dir / filename).is_file():
            raise ParseError(f"Missing required file {filename}", source_name=source_name)

    project_raw = _read_json(extract_dir / "project.json")
    floors_raw = _read_json(extract_dir / "floorPlans.json")
    aps_raw = _read_json(extract_dir / "accessPoints.json")

    project = _parse_project(
        _require_dict(project_raw, label="project.json", source_name=source_name),
        source_name=source_name,
    )
    floors = _parse_floors(
        _require_list(floors_raw, label="floorPlans.json", source_name=source_name),
        source_name=source_name,
    )
    radios_by_ap = _parse_radios_by_ap_id(extract_dir, source_name=source_name)
    aps = _parse_aps(
        _require_list(aps_raw, label="accessPoints.json", source_name=source_name),
        source_name=source_name,
        radios_by_ap=radios_by_ap,
    )

    return SurveyModel(
        project=project,
        floors=floors,
        aps=aps,
        source_filename=source_name,
    )


def parse_esx(fileobj: BinaryIO, *, source_name: str) -> SurveyModel:
    """Parse one .esx (ZIP of JSON + images) into a normalized SurveyModel."""
    fileobj.seek(0)
    data = fileobj.read()
    if not data:
        raise ParseError("Empty file", source_name=source_name)
    if not zipfile.is_zipfile(BytesIO(data)):
        preview = data[:256].lower()
        if preview.startswith(b"#") or b"placeholder" in preview or b"fake esx" in preview:
            raise ParseError(
                "Not a valid Ekahau .esx (expected ZIP archive). "
                "This file looks like a Phase 1 upload placeholder — "
                "re-upload tests/fixtures/sample_survey.esx to test the parser.",
                source_name=source_name,
            )
        raise ParseError("Not a valid ZIP archive (.esx)", source_name=source_name)

    with tempfile.TemporaryDirectory() as tmp:
        extract_dir = Path(tmp)
        try:
            with zipfile.ZipFile(BytesIO(data)) as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile as exc:
            raise ParseError("Corrupt ZIP archive", source_name=source_name) from exc

        return _parse_extracted_dir(extract_dir, source_name=source_name)
