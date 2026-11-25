import json

import pytest

from chaos_tool.model import (
    Edge,
    EdgeKind,
    Evidence,
    EvidenceSource,
    Finding,
    ModelError,
    Node,
    NodeKind,
    Severity,
    SystemMap,
)
from chaos_tool.report.json_export import to_json


def small_map() -> SystemMap:
    system = SystemMap(target="demo", inputs=["docker-compose.yml"])
    system.add_node(Node(NodeKind.SERVICE, "worker"))
    system.add_node(Node(NodeKind.SERVICE, "redis", attrs={"image": "redis:alpine"}))
    system.ensure_node(NodeKind.NETWORK, "back-tier")
    ev = Evidence(EvidenceSource.COMPOSE, "depends_on: redis", file="docker-compose.yml", line=47)
    system.add_edge(
        Edge(EdgeKind.DEPENDS_ON, "service:worker", "service:redis", {"condition": "healthy"}, [ev])
    )
    system.add_edge(Edge(EdgeKind.MEMBER_OF, "service:worker", "network:back-tier"))
    return system


def test_ids_have_kind_prefix():
    system = small_map()
    assert "service:worker" in system.nodes
    assert system.node("service:redis").name == "redis"
    assert "depends_on:service:worker->service:redis" in system.edges


def test_duplicate_node_is_rejected():
    system = small_map()
    with pytest.raises(ModelError):
        system.add_node(Node(NodeKind.SERVICE, "worker"))


def test_ensure_node_returns_existing():
    system = small_map()
    assert system.ensure_node(NodeKind.NETWORK, "back-tier") is system.node("network:back-tier")


def test_edge_to_unknown_node_is_rejected():
    system = small_map()
    with pytest.raises(ModelError):
        system.add_edge(Edge(EdgeKind.DEPENDS_ON, "service:worker", "service:db"))


def test_same_edge_twice_merges_evidence():
    system = small_map()
    extra = Evidence(EvidenceSource.SOURCE_CODE, "redis://redis", file="worker/Program.cs", line=3)
    system.add_edge(Edge(EdgeKind.DEPENDS_ON, "service:worker", "service:redis", evidence=[extra]))
    edges = system.edges_of(EdgeKind.DEPENDS_ON)
    assert len(edges) == 1
    assert len(edges[0].evidence) == 2


def test_finding_on_unknown_node_is_rejected():
    system = small_map()
    bad = Finding("x", Severity.LOW, "t", "d", nodes=["service:nope"])
    with pytest.raises(ModelError):
        system.add_finding(bad)


def test_findings_sorted_high_first():
    system = small_map()
    system.add_finding(Finding("b_rule", Severity.LOW, "t", "d", nodes=["service:worker"]))
    system.add_finding(Finding("a_rule", Severity.HIGH, "t", "d", nodes=["service:redis"]))
    severities = [f["severity"] for f in system.to_dict()["findings"]]
    assert severities == ["high", "low"]


def test_round_trip_through_json():
    system = small_map()
    system.add_finding(Finding("r", Severity.MEDIUM, "t", "d", nodes=["service:worker"]))
    data = json.loads(to_json(system))
    again = SystemMap.from_dict(data)
    assert again.to_dict() == system.to_dict()


def test_output_is_deterministic():
    assert to_json(small_map()) == to_json(small_map())


def test_wrong_schema_major_version_is_rejected():
    data = small_map().to_dict()
    data["schema_version"] = "9.0.0"
    with pytest.raises(ModelError):
        SystemMap.from_dict(data)
