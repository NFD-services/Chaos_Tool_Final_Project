# Design decisions

Short records of decisions and why we made them. Newest at the bottom.

## D1 - Separate repository for the tool

The tool lives in its own repo; the target system (voting app, later Online
Boutique) lives in its own. The target is an input to the tool, not part of it.

## D2 - Analyze the architecture, plus light source hints

Static analysis reads the declared architecture (`docker-compose.yml`), which
is language-independent. On top of it, a plain text search over source code
finds references to other services. We do not parse source code properly:
that would need a parser per language (3 in voting, 5+ in Online Boutique).
Deep code understanding is left to the LLM in the Hypothesize stage.

## D3 - Three layers: parsers -> model -> analyzers

Only parsers know input formats. Analyzers and reporters only use
`chaos_tool.model`. Moving to Online Boutique (Kubernetes manifests) means
writing one new parser, not rewriting the analysis. We do not build a fully
generic system up front.

## D4 - No hard dependency on Docker

The compose parser reads the YAML itself (PyYAML) and handles the different
compose spellings. `docker compose config` is an optional fallback
(`--use-docker`). Bonus: reading the YAML ourselves gives line numbers for
evidence.

## D5 - Edges point client -> server

`worker -> redis` means worker relies on redis. This matches what tracing
(Jaeger) shows, so static and dynamic maps can be compared directly. Note that
the voting app's diagram draws data flow, so some of its arrows point the
other way.

## D6 - Networks are nodes, not pairwise edges

A service joins a network with a `member_of` edge. "Who can reach whom" is
computed when needed. Pairwise edges would add n*(n-1)/2 edges per network
and clutter the graph.

## D7 - Node ids carry their kind

Ids look like `service:vote`, `network:back-tier`. This keeps ids unique when
a service and a volume share a name. `Node.name` keeps the bare compose
service name (`vote`) for matching with Jaeger and the dynamic map.

## D8 - Suspicion rules are separate from facts

Facts (nodes, edges) and suspicions (findings) are stored separately. Each
rule is one small function in its own file, with an id, a severity
(low / medium / high) and a suggested experiment. No rule config file for
now - we'll add one if we need to turn rules on and off.

## D9 - dataclasses, deterministic JSON, Python 3.10+

`dataclasses` (standard library) over pydantic: fewer dependencies, simpler
to explain. JSON is sorted and has no timestamp, so two runs on the same
input are identical and diffs are meaningful. Python 3.10 for compatibility
with the university HPC.

## D10 - Self-contained HTML report

The report is a single HTML file with Cytoscape.js and the data inlined, so it
opens offline. Cytoscape.js (MIT license) is vendored in
`src/chaos_tool/report/vendor/`.

## D11 - `seed` is an optional node

The voting app's `seed` service only runs with `--profile seed`. It appears in
the map with `optional: true`, so it is visible but not mistaken for an
always-running service.
