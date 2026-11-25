"""Write and read ``static_map.json`` - the contract between the tool's stages."""

from __future__ import annotations

import json
from pathlib import Path

from chaos_tool.model import SystemMap


def to_json(system: SystemMap) -> str:
    """Serialize deterministically (sorted, 2-space indent) so git diffs stay readable."""
    return json.dumps(system.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_json(system: SystemMap, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_json(system), encoding="utf-8")
    return path


def read_json(path: Path) -> SystemMap:
    return SystemMap.from_dict(json.loads(path.read_text(encoding="utf-8")))
