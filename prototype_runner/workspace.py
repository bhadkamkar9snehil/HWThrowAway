from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def build_manifest(config: dict[str, Any]) -> dict[str, Any]:
    parts: list[dict[str, Any]] = [
        {
            "id": "system-assembly-v1",
            "name": "Rangoli dispenser assembly",
            "type": "assembly",
            "components": ["hopper-shell-v1", "auger-meter-v1"],
            "visible": True,
            "view": "system",
        }
    ]

    for component in config.get("components", []):
        module = importlib.import_module(component["module"])
        factory = getattr(module, "viewer_spec", None)
        if not factory:
            continue
        spec = factory()
        if isinstance(spec, list):
            parts.extend(spec)
        else:
            parts.append(spec)

    return {
        "project": config.get("project", {}).get("name", "Prototype"),
        "units": config.get("project", {}).get("units", "mm"),
        "default": "system-assembly-v1",
        "geometry_version": 1,
        "parts": parts,
    }


def write_manifest(config: dict[str, Any]) -> Path:
    output = ROOT / "docs" / "models.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_manifest(config), indent=2) + "\n",
        encoding="utf-8",
    )
    return output
