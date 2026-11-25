"""Acceptance test: the static map of the voting app must match the architecture diagram.

Skipped until the compose parser (Stage 2) exists - then it becomes the main check.
"""

import json
from pathlib import Path

import pytest

from chaos_tool.model import EdgeKind, NodeKind

FIXTURE = Path(__file__).parent / "fixtures" / "voting"

pytest.importorskip("chaos_tool.parsers.compose")


@pytest.fixture
def system():
    from chaos_tool.parsers.compose import parse_compose

    try:
        return parse_compose(FIXTURE / "docker-compose.yml", target="voting")
    except NotImplementedError:
        pytest.skip("Stage 2: compose parser not implemented yet")


@pytest.fixture
def expected():
    return json.loads((FIXTURE / "expected.json").read_text())


def test_services(system, expected):
    assert sorted(n.name for n in system.nodes_of(NodeKind.SERVICE)) == expected["services"]
    optional = sorted(n.name for n in system.nodes_of(NodeKind.SERVICE) if n.optional)
    assert optional == expected["optional_services"]


def test_dependency_edges(system, expected):
    found = {(e.source, e.target) for e in system.edges_of(EdgeKind.DEPENDS_ON)}
    for edge in expected["dependency_edges"]:
        assert (edge["source"], edge["target"]) in found


def test_entry_points(system, expected):
    exposed = sorted({e.target for e in system.edges_of(EdgeKind.EXPOSES)})
    assert exposed == expected["entry_points"]


def test_networks(system, expected):
    assert sorted(n.name for n in system.nodes_of(NodeKind.NETWORK)) == expected["networks"]
