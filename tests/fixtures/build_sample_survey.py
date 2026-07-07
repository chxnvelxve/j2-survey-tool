"""Build tests/fixtures/sample_survey.esx — run once to regenerate the fixture."""
import json
import shutil
import zipfile
from pathlib import Path

OUT = Path(__file__).with_name("sample_survey.esx")
ALIAS = Path(__file__).with_name("sample.esx")

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
        "name": " AP-02-SW ",
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

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("project.json", json.dumps(project))
    zf.writestr("floorPlans.json", json.dumps(floors))
    zf.writestr("accessPoints.json", json.dumps(aps))
    zf.writestr("simulatedRadios.json", json.dumps(radios))
    zf.writestr("floor1.png", b"\x89PNG\r\n\x1a\n")

print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
shutil.copy(OUT, ALIAS)
print(f"Wrote {ALIAS} ({ALIAS.stat().st_size} bytes)")
