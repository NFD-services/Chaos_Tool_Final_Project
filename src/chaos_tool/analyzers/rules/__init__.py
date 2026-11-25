"""Suspicion rules: each rule looks at the SystemMap and returns Findings.

A rule is a plain function ``(SystemMap) -> list[Finding]``, one rule per file.
To add a rule: write the function in a new file here and append it to RULES.

Planned rules (Stage 5):

=========================  ========  ==================================================
rule id                    severity  what it flags
=========================  ========  ==================================================
network_overreach          high      a service can reach another over a shared network,
                                     but nothing says it needs to (no depends_on, env or
                                     code reference) - e.g. vote -> db
plaintext_secret           high      password / secret / token in plain environment
exposed_sensitive_port     medium    debug or database port published to the host
silent_failure             medium    nothing depends on the service and it has no
                                     healthcheck, so nobody notices if it dies
missing_healthcheck        low       service without a healthcheck
=========================  ========  ==================================================
"""

from __future__ import annotations

from collections.abc import Callable

from chaos_tool.model import Finding, SystemMap

Rule = Callable[[SystemMap], list[Finding]]

# Filled in during Stage 5.
RULES: list[Rule] = []


def run_rules(system: SystemMap, rules: list[Rule] | None = None) -> list[Finding]:
    """Run every rule and add its findings to ``system``. Returns the new findings."""
    new: list[Finding] = []
    for rule in RULES if rules is None else rules:
        for finding in rule(system):
            system.add_finding(finding)
            new.append(finding)
    return new
