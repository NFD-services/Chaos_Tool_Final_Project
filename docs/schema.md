# `static_map.json` format

Schema version: **0.1.0** (see `SCHEMA_VERSION` in `src/chaos_tool/model.py`).

This file is the contract between the static stage and everything after it
(dynamic comparison, Hypothesize, the HTML report). If you change it, bump the
version and update this page.

## Top level

```json
{
  "schema_version": "0.1.0",
  "target": "voting",
  "inputs": ["docker-compose.yml"],
  "nodes": [ ... ],
  "edges": [ ... ],
  "findings": [ ... ]
}
```

All lists are sorted (nodes and edges by `id`, findings by severity then
`id`), and there is no timestamp, so the same input always gives the same file.

## Evidence

Used by nodes, edges and findings to say where information came from.

| field | type | meaning |
|---|---|---|
| `source` | `"compose"` \| `"source_code"` \| `"analysis"` | where it was found |
| `detail` | string | what was seen, e.g. `"depends_on: redis (service_healthy)"` |
| `file` | string \| null | file path, relative to the input |
| `line` | int \| null | line number |

## Nodes

```json
{
  "id": "service:vote",
  "kind": "service",
  "name": "vote",
  "optional": false,
  "attrs": { ... },
  "evidence": [ ... ]
}
```

`id` is `<kind>:<name>`. `name` is the bare name used in compose (and later in
Jaeger). `optional` is true for services that only run with a compose profile.

### Node kinds and their `attrs`

| kind | meaning | attrs |
|---|---|---|
| `service` | a container / microservice | see below |
| `network` | a network services can join | `driver`, `external` (bool) |
| `volume` | a named volume | `driver`, `external` (bool) |
| `external` | the outside world; one node, `external:host` | none |

Service `attrs` (missing keys mean "not set in the input"):

| key | type | example |
|---|---|---|
| `image` | string | `"redis:alpine"` |
| `build_context` | string | `"./vote"` |
| `ports` | list of `{published, target, host_ip, protocol}` | `[{"published": 8080, "target": 80, "host_ip": null, "protocol": "tcp"}]` |
| `environment` | object | `{"POSTGRES_USER": "postgres"}` |
| `healthcheck` | object \| null | `{"test": [...], "interval": "5s"}` |
| `restart` | string | `"no"` |
| `profiles` | list of strings | `["seed"]` |
| `command` / `entrypoint` | string \| list | `"nodemon --inspect=0.0.0.0 server.js"` |
| `bind_mounts` | list of `{source, target}` | `[{"source": "./vote", "target": "/usr/local/app"}]` |
| `metrics` | object | added by the analyzers (Stage 4), see below |

`metrics` (added by `analyzers/graph_metrics.py`):

| key | type | meaning |
|---|---|---|
| `startup_order` | int | position in startup order (0 = first) |
| `blast_radius` | list of node ids | services that break if this one goes down |
| `is_bridge` | bool | member of more than one network |
| `is_entry_point` | bool | reachable from outside |
| `reachable` | list of node ids | services it can reach over shared networks |

## Edges

```json
{
  "id": "depends_on:service:worker->service:redis",
  "kind": "depends_on",
  "source": "service:worker",
  "target": "service:redis",
  "attrs": { "condition": "service_healthy" },
  "evidence": [ ... ]
}
```

Direction is always **client -> server**: the source relies on the target.
The same relationship found twice is stored once, with both evidence entries.

| kind | from -> to | meaning | attrs |
|---|---|---|---|
| `depends_on` | service -> service | declared startup dependency | `condition` |
| `member_of` | service -> network | service joins the network | `aliases` |
| `mounts` | service -> volume | service mounts a named volume | `target`, `read_only` |
| `exposes` | external -> service | a port is published to the host | `published`, `target`, `host_ip` |
| `env_reference` | service -> service | another service is named in an env variable | `variable` |
| `code_reference` | service -> service | another service is named in source code | `confidence` (`high` \| `low`) |

## Findings

```json
{
  "id": "network_overreach:service:db,service:vote",
  "rule_id": "network_overreach",
  "severity": "high",
  "title": "vote can reach db but has no reason to",
  "description": "...",
  "nodes": ["service:db", "service:vote"],
  "edges": [],
  "evidence": [ ... ],
  "suggested_experiment": "..."
}
```

A finding is a **suspicion**, not a fact. `suggested_experiment` is a short
hint for the Hypothesize stage. `severity` is `low`, `medium` or `high`.
