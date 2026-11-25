"""Source hints: find references to other services in source code.  (Stage 3 - not implemented yet)

For every service that has a build context (e.g. ``./vote``), scan its source
files for the names and ports of the *other* services. A match becomes a
``code_reference`` edge with Evidence pointing to the file and line, and a
``confidence`` attr:

* high - the name appears in a connection-like pattern
         (``redis://``, ``Host=db``, ``"db:5432"``, ``host='redis'``)
* low  - the bare name appears in a string literal

This is plain text matching, not real code parsing: it works the same way for
Python, JavaScript and C#, and only needs new extensions for Go/Java later.
"""

from __future__ import annotations

from pathlib import Path

from chaos_tool.model import SystemMap

DEFAULT_EXTENSIONS: tuple[str, ...] = (".py", ".js", ".cs")
SKIP_DIRS: frozenset[str] = frozenset(
    {".git", ".venv", "__pycache__", "node_modules", "bin", "obj", "dist", "build"}
)


def add_source_hints(
    system: SystemMap,
    source_root: Path,
    *,
    extensions: tuple[str, ...] = DEFAULT_EXTENSIONS,
) -> None:
    """Scan source code and add ``code_reference`` edges to ``system`` in place."""
    raise NotImplementedError("Stage 3: source hints")
