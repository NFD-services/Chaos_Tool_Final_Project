"""Docker Compose parser: docker-compose.yml -> SystemMap.  (Stage 2 - not implemented yet)

Primary path: read the YAML ourselves with PyYAML, so the tool works without
Docker. Optional path (``use_docker=True``): run ``docker compose config`` to
let Docker normalize the file, used as a fallback / cross-check.

What the parser must handle (compose allows several spellings of each):

* ``depends_on``  - list form ``[redis]`` or mapping form ``{redis: {condition: ...}}``
* ``ports``       - short ``"8080:80"``, ``"127.0.0.1:9229:9229"``, or long mapping form
* ``networks``    - list or mapping; services with no networks join ``default``
* ``volumes``     - named volumes (``db-data:/path``) vs bind mounts (``./dir:/path``)
* ``environment`` - list ``["A=1"]`` or mapping ``{A: 1}``
* ``${VAR}``, ``${VAR:-default}`` interpolation from the environment / ``.env``
* ``profiles``    - services with profiles become ``optional=True`` nodes
* ``build``       - string or mapping; the build context is kept for the source-hints stage

Output: service, network, volume and external nodes; depends_on, member_of,
mounts, exposes and env_reference edges, each with Evidence (file + line).
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from chaos_tool.model import SystemMap


def parse_compose(
    path: Path,
    *,
    target: str | None = None,
    use_docker: bool = False,
    env: Mapping[str, str] | None = None,
) -> SystemMap:
    """Parse a compose file into a SystemMap.

    Args:
        path: the docker-compose.yml file.
        target: name for the system; defaults to the compose file's folder name.
        use_docker: normalize with ``docker compose config`` instead of our own parser.
        env: variables for ``${VAR}`` interpolation; defaults to ``os.environ`` + ``.env``.
    """
    raise NotImplementedError("Stage 2: compose parser")
