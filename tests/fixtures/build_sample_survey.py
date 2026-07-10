"""Build tests/fixtures/*.esx — run to regenerate all survey fixtures."""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path
from typing import Any

DIR = Path(__file__).parent
MINIMAL_PNG = b"\x89PNG\r\n\x1a\n"


def _write_esx(
    path: Path,
    *,
    project: dict[str, Any],
    floors: list[dict[str, Any]],
    aps: list[dict[str, Any]],
    radios: list[dict[str, Any]] | None = None,
    extra_files: dict[str, bytes] | None = None,
) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("project.json", json.dumps(project))
        zf.writestr("floorPlans.json", json.dumps(floors))
        zf.writestr("accessPoints.json", json.dumps(aps))
        if radios is not None:
            zf.writestr("simulatedRadios.json", json.dumps(radios))
        for name, content in (extra_files or {}).items():
            zf.writestr(name, content)


def _build_clean() -> None:
    project = {"name": "Test Building Survey"}
    floors = [{"id": "fp1", "name": "Floor 1", "image": "floor1.png"}]
    aps = [
        {
            "id": "ap1",
            "name": "AP-01-NE",
            "model": "C9136I",
            "vendor": "Cisco",
            "floorId": "fp1",
            "x": 12.5,
            "y": 34.0,
        },
        {
            "id": "ap2",
            "name": "AP-02-SW",
            "model": "MR46",
            "vendor": "Meraki",
            "floorId": "fp1",
            "x": 88.0,
            "y": 42.5,
        },
    ]
    radios = [
        {"accessPointId": "ap1", "band": "5GHz", "channel": 36, "txPower": 17.0},
        {"accessPointId": "ap2", "band": "2.4GHz", "channel": 11, "txPower": 14.5},
    ]
    _write_esx(
        DIR / "sample_survey_clean.esx",
        project=project,
        floors=floors,
        aps=aps,
        radios=radios,
        extra_files={"floor1.png": MINIMAL_PNG},
    )


def _build_edge_cases() -> None:
    project = {"name": "Edge Case Survey"}
    floors = [
        {
            "id": "fp1",
            "name": "Floor 1",
            "image": "floor1.png",
            "heatmap": "heatmap_fp1.png",
        },
    ]
    aps = [
        {
            "id": "ap1",
            "name": "AP-01-NE",
            "model": "C9136I",
            "vendor": "Cisco",
            "floorId": "fp1",
            "x": 12.5,
            "y": 34.0,
        },
        {
            "id": "ap2",
            "name": " AP-02-SW ",
            "model": "MR46",
            "vendor": "Meraki",
            "floorId": "fp1",
            "x": 88.0,
            "y": 42.5,
        },
        {
            "id": "ap3",
            "name": "AP-03-Café",
            "model": "C9136I",
            "vendor": "Cisco",
            "floorId": "fp1",
            "x": 50.0,
            "y": 50.0,
        },
        {
            "id": "ap4",
            "name": "AP-04-NO-RADIO",
            "model": "MR46",
            "vendor": "Meraki",
            "floorId": "fp1",
            "x": 10.0,
            "y": 10.0,
        },
    ]
    radios = [
        {"accessPointId": "ap1", "band": "5GHz", "channel": 36, "txPower": 17.0},
        {"accessPointId": "ap2", "band": "2.4GHz", "channel": 11, "txPower": 14.5},
        {"accessPointId": "ap3", "band": "5GHz", "channel": 40, "txPower": 15.0},
    ]
    _write_esx(
        DIR / "sample_survey_edge_cases.esx",
        project=project,
        floors=floors,
        aps=aps,
        radios=radios,
        extra_files={"floor1.png": MINIMAL_PNG, "heatmap_fp1.png": MINIMAL_PNG},
    )


def _build_dup_a() -> None:
    project = {"name": "Building A Survey"}
    floors = [{"id": "fp_a", "name": "Building A - Floor 1", "image": "floor_a.png"}]
    aps = [
        {
            "id": "ap_dup_a",
            "name": "AP-DUP-01",
            "model": "C9136I",
            "vendor": "Cisco",
            "floorId": "fp_a",
            "x": 20.0,
            "y": 30.0,
        },
    ]
    radios = [
        {"accessPointId": "ap_dup_a", "band": "5GHz", "channel": 36, "txPower": 17.0},
    ]
    _write_esx(
        DIR / "sample_survey_dup_a.esx",
        project=project,
        floors=floors,
        aps=aps,
        radios=radios,
        extra_files={"floor_a.png": MINIMAL_PNG},
    )


def _build_dup_b() -> None:
    project = {"name": "Building B Survey"}
    floors = [{"id": "fp_b", "name": "Building B - Floor 1", "image": "floor_b.png"}]
    aps = [
        {
            "id": "ap_dup_b",
            "name": "AP-DUP-01",
            "model": "MR46",
            "vendor": "Meraki",
            "floorId": "fp_b",
            "x": 45.0,
            "y": 55.0,
        },
    ]
    radios = [
        {"accessPointId": "ap_dup_b", "band": "2.4GHz", "channel": 6, "txPower": 12.0},
    ]
    _write_esx(
        DIR / "sample_survey_dup_b.esx",
        project=project,
        floors=floors,
        aps=aps,
        radios=radios,
        extra_files={"floor_b.png": MINIMAL_PNG},
    )


def main() -> None:
    _build_clean()
    _build_edge_cases()
    _build_dup_a()
    _build_dup_b()

    edge = DIR / "sample_survey_edge_cases.esx"
    for alias in (DIR / "sample_survey.esx", DIR / "sample.esx"):
        shutil.copy(edge, alias)
        print(f"Wrote {alias} ({alias.stat().st_size} bytes) [alias of edge_cases]")

    for name in (
        "sample_survey_clean.esx",
        "sample_survey_edge_cases.esx",
        "sample_survey_dup_a.esx",
        "sample_survey_dup_b.esx",
    ):
        path = DIR / name
        print(f"Wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
