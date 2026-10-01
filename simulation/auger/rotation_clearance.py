from __future__ import annotations

import json
from pathlib import Path

from cad.auger import ROTATION_SAMPLE_DEGREES, build_housing, build_screw


def intersection_volume_mm3(a, b) -> float:
    result = a.intersect(b)
    return sum(float(solid.Volume()) for solid in result.solids().vals())


def run() -> dict:
    screw = build_screw()
    housing = build_housing()
    samples = []
    for angle in range(0, 360, ROTATION_SAMPLE_DEGREES):
        rotated = screw.rotate((0, 0, 0), (1, 0, 0), angle)
        volume = intersection_volume_mm3(rotated, housing)
        samples.append({"angle_deg": angle, "interference_mm3": round(volume, 9)})

    maximum = max(x["interference_mm3"] for x in samples)
    return {
        "schema_version": 1,
        "simulation": "sampled_rotational_clearance",
        "component": "auger-meter-v1",
        "sample_step_deg": ROTATION_SAMPLE_DEGREES,
        "sample_count": len(samples),
        "max_interference_mm3": maximum,
        "status": "PASS" if maximum < 1e-6 else "FAIL",
        "samples": samples,
        "scope": "geometry/kinematics only; no powder physics",
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    output = root / "simulation" / "auger" / "results" / "phase-01-rotation-clearance.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = run()
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
