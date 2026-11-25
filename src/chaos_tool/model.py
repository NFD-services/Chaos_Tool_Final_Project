"""Core data model shared by every part of chaos-tool.

A system is described as a directed graph:

* ``Node``    - something that exists in the system: a service, a network,
                a volume, or the outside world.
* ``Edge``    - a relationship between two nodes. Edges always point from the
                side that relies on something to the thing it relies on
                (client -> server), e.g. ``worker -> redis``.
* ``Finding`` - a suspicion raised by a rule. Findings are not facts; they are
                the input for the Hypothesize stage.

Nothing in this module knows about Docker Compose, Kubernetes or the voting
app. Parsers translate their input into these classes, and analyzers and
reporters only work with these classes. That is what lets us add a new parser
(e.g. Kubernetes manifests) later without touching the analysis code.

The JSON produced by ``SystemMap.to_dict`` is documented in ``docs/schema.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

SCHEMA_VERSION = "0.1.0"


class ModelError(ValueError):
    """Raised when the graph would become inconsistent."""


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class NodeKind(str, Enum):
    """What a node represents."""

    SERVICE = "service"
    NETWORK = "network"
    VOLUME = "volume"
    EXTERNAL = "external"  # the outside world (the host / users)


class EdgeKind(str, Enum):
    """What a relationship means. Direction is always client -> server."""

    DEPENDS_ON = "depends_on"  # service -> service, declared startup dependency
    MEMBER_OF = "member_of"  # service -> network
    MOUNTS = "mounts"  # service -> volume
    EXPOSES = "exposes"  # external -> service, reachable from outside
    ENV_REFERENCE = "env_reference"  # service -> service, named in an env variable
    CODE_REFERENCE = "code_reference"  # service -> service, named in source code


class Severity(str, Enum):
    """How serious a finding is."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @property
    def rank(self) -> int:
        """Numeric rank for sorting; higher is more severe."""
        return {"low": 1, "medium": 2, "high": 3}[self.value]


class EvidenceSource(str, Enum):
    """Where a piece of information came from."""

    COMPOSE = "compose"  # read from a docker-compose file
    SOURCE_CODE = "source_code"  # found by the source-hints text search
    ANALYSIS = "analysis"  # derived by an analyzer, not read from a file


def make_id(kind: NodeKind, name: str) -> str:
    """Build a node id such as ``service:vote``.

    The kind prefix keeps ids unique even when a service and a volume share a
    name. ``Node.name`` keeps the bare name (``vote``), which is what other
    tools such as Jaeger will use.
    """
    return f"{kind.value}:{name}"


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Evidence:
    """Why we believe something: where it was found and what was seen."""

    source: EvidenceSource
    detail: str
    file: str | None = None
    line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.value,
            "detail": self.detail,
            "file": self.file,
            "line": self.line,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Evidence:
        return cls(
            source=EvidenceSource(data["source"]),
            detail=data["detail"],
            file=data.get("file"),
            line=data.get("line"),
        )


@dataclass
class Node:
    """A thing in the system.

    ``attrs`` holds kind-specific details (ports, image, healthcheck, ...).
    The allowed keys for each kind are listed in ``docs/schema.md``.
    ``optional`` marks nodes that do not always run (e.g. compose profiles).
    """

    kind: NodeKind
    name: str
    attrs: dict[str, Any] = field(default_factory=dict)
    optional: bool = False
    evidence: list[Evidence] = field(default_factory=list)

    @property
    def id(self) -> str:
        return make_id(self.kind, self.name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "name": self.name,
            "optional": self.optional,
            "attrs": self.attrs,
            "evidence": [e.to_dict() for e in self.evidence],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Node:
        return cls(
            kind=NodeKind(data["kind"]),
            name=data["name"],
            attrs=dict(data.get("attrs", {})),
            optional=bool(data.get("optional", False)),
            evidence=[Evidence.from_dict(e) for e in data.get("evidence", [])],
        )


@dataclass
class Edge:
    """A directed relationship between two nodes (by node id)."""

    kind: EdgeKind
    source: str
    target: str
    attrs: dict[str, Any] = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)

    @property
    def id(self) -> str:
        return f"{self.kind.value}:{self.source}->{self.target}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "source": self.source,
            "target": self.target,
            "attrs": self.attrs,
            "evidence": [e.to_dict() for e in self.evidence],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Edge:
        return cls(
            kind=EdgeKind(data["kind"]),
            source=data["source"],
            target=data["target"],
            attrs=dict(data.get("attrs", {})),
            evidence=[Evidence.from_dict(e) for e in data.get("evidence", [])],
        )


@dataclass
class Finding:
    """A suspicion raised by a rule - a candidate for a chaos experiment."""

    rule_id: str
    severity: Severity
    title: str
    description: str
    nodes: list[str] = field(default_factory=list)
    edges: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    suggested_experiment: str | None = None

    @property
    def id(self) -> str:
        return f"{self.rule_id}:{','.join(sorted(self.nodes))}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "nodes": sorted(self.nodes),
            "edges": sorted(self.edges),
            "evidence": [e.to_dict() for e in self.evidence],
            "suggested_experiment": self.suggested_experiment,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Finding:
        return cls(
            rule_id=data["rule_id"],
            severity=Severity(data["severity"]),
            title=data["title"],
            description=data["description"],
            nodes=list(data.get("nodes", [])),
            edges=list(data.get("edges", [])),
            evidence=[Evidence.from_dict(e) for e in data.get("evidence", [])],
            suggested_experiment=data.get("suggested_experiment"),
        )


# ---------------------------------------------------------------------------
# The whole map
# ---------------------------------------------------------------------------


@dataclass
class SystemMap:
    """The full static picture of one target system."""

    target: str
    inputs: list[str] = field(default_factory=list)
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: dict[str, Edge] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)

    # -- nodes ---------------------------------------------------------------

    def add_node(self, node: Node) -> Node:
        """Add a new node. Adding the same id twice is an error."""
        if node.id in self.nodes:
            raise ModelError(f"duplicate node: {node.id}")
        self.nodes[node.id] = node
        return node

    def ensure_node(self, kind: NodeKind, name: str, **kwargs: Any) -> Node:
        """Return the node if it exists, otherwise create it.

        Useful for networks and volumes, which several services mention.
        """
        node_id = make_id(kind, name)
        if node_id in self.nodes:
            return self.nodes[node_id]
        return self.add_node(Node(kind=kind, name=name, **kwargs))

    def node(self, node_id: str) -> Node:
        try:
            return self.nodes[node_id]
        except KeyError:
            raise ModelError(f"unknown node: {node_id}") from None

    def nodes_of(self, kind: NodeKind) -> list[Node]:
        """All nodes of one kind, sorted by id."""
        return sorted((n for n in self.nodes.values() if n.kind == kind), key=lambda n: n.id)

    # -- edges ---------------------------------------------------------------

    def add_edge(self, edge: Edge) -> Edge:
        """Add an edge between two existing nodes.

        Adding the same relationship again (same kind, source and target)
        does not create a second edge: the new evidence and attrs are merged
        into the existing one.
        """
        for end in (edge.source, edge.target):
            if end not in self.nodes:
                raise ModelError(f"edge {edge.id} points to unknown node: {end}")

        existing = self.edges.get(edge.id)
        if existing is None:
            self.edges[edge.id] = edge
            return edge

        existing.attrs.update(edge.attrs)
        for ev in edge.evidence:
            if ev not in existing.evidence:
                existing.evidence.append(ev)
        return existing

    def edges_of(
        self,
        kind: EdgeKind | None = None,
        *,
        source: str | None = None,
        target: str | None = None,
    ) -> list[Edge]:
        """Edges filtered by kind / source / target, sorted by id."""
        result = [
            e
            for e in self.edges.values()
            if (kind is None or e.kind == kind)
            and (source is None or e.source == source)
            and (target is None or e.target == target)
        ]
        return sorted(result, key=lambda e: e.id)

    # -- findings ------------------------------------------------------------

    def add_finding(self, finding: Finding) -> Finding:
        for node_id in finding.nodes:
            if node_id not in self.nodes:
                raise ModelError(f"finding {finding.id} refers to unknown node: {node_id}")
        self.findings.append(finding)
        return finding

    # -- serialization -------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Plain-dict form, sorted so that two runs produce identical output."""
        findings = sorted(self.findings, key=lambda f: (-f.severity.rank, f.id))
        return {
            "schema_version": SCHEMA_VERSION,
            "target": self.target,
            "inputs": sorted(self.inputs),
            "nodes": [self.nodes[k].to_dict() for k in sorted(self.nodes)],
            "edges": [self.edges[k].to_dict() for k in sorted(self.edges)],
            "findings": [f.to_dict() for f in findings],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SystemMap:
        """Load a map written by ``to_dict`` (e.g. for the dynamic stage)."""
        version = str(data.get("schema_version", ""))
        if version.split(".")[0] != SCHEMA_VERSION.split(".")[0]:
            raise ModelError(f"unsupported schema_version {version!r} (expected {SCHEMA_VERSION})")
        system = cls(target=data["target"], inputs=list(data.get("inputs", [])))
        for n in data.get("nodes", []):
            system.add_node(Node.from_dict(n))
        for e in data.get("edges", []):
            system.add_edge(Edge.from_dict(e))
        for f in data.get("findings", []):
            system.add_finding(Finding.from_dict(f))
        return system
