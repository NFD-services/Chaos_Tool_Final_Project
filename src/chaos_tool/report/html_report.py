"""Interactive HTML report.  (Stage 6 - not implemented yet)

Takes ``template.html``, inlines the vendored Cytoscape.js library and the map
JSON, and writes one self-contained file that opens in any browser offline.

Planned features: clickable graph, filter by edge kind, highlight the blast
radius of a selected service, and a findings panel.
"""

from __future__ import annotations

from pathlib import Path

from chaos_tool.model import SystemMap

TEMPLATE = Path(__file__).with_name("template.html")
CYTOSCAPE_JS = Path(__file__).parent / "vendor" / "cytoscape.min.js"


def write_html(system: SystemMap, path: Path) -> Path:
    """Write the self-contained HTML report."""
    raise NotImplementedError("Stage 6: HTML report")
