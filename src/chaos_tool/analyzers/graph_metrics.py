"""Graph metrics computed with networkx.  (Stage 4 - not implemented yet)

Results are stored on each service node under ``attrs["metrics"]``:

* ``startup_order``  - position in a topological sort of depends_on edges
                       (a cycle is reported as an error)
* ``blast_radius``   - services that depend on this one, directly or
                       transitively: what breaks if it goes down
* ``is_bridge``      - member of more than one network
* ``is_entry_point`` - has an ``exposes`` edge from the outside world
* ``reachable``      - services it can reach because they share a network
"""

from __future__ import annotations

from chaos_tool.model import EdgeKind, SystemMap


def to_networkx(system: SystemMap, kinds: set[EdgeKind] | None = None):
    """Build a networkx MultiDiGraph of the map, optionally only some edge kinds."""
    raise NotImplementedError("Stage 4: graph metrics")


def compute_metrics(system: SystemMap) -> None:
    """Compute all metrics and store them on the service nodes in place."""
    raise NotImplementedError("Stage 4: graph metrics")
