# chaos-tool

Automated **security chaos engineering** for microservice systems.

The tool maps a system's dependencies (statically from configuration and
dynamically from live traffic), uses graph analysis and an LLM to guess where
weaknesses may hide, injects targeted network and timing faults under a
controlled blast radius, and reports how the system behaved.

The first target is the [Docker Example Voting App](https://github.com/dockersamples/example-voting-app).

## Pipeline

| Stage | What it does | Status |
|---|---|---|
| **Discover - static** | Read `docker-compose.yml` (+ hints from source code) into a dependency graph | in progress |
| Discover - dynamic | Observe real traffic (Docker SDK, Jaeger) | planned |
| Hypothesize | LLM proposes chaos experiments from static/dynamic gaps | planned |
| Execute | Inject faults (startup delay, network block) | planned |
| Judge | Compare behavior to baseline, write findings | planned |

## Install

Requires Python 3.10+.

```bash
git clone <repo-url> chaos-tool
cd chaos-tool
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

```bash
chaos-tool static --compose ../example-voting-app/docker-compose.yml --out out/
```

Outputs:

* `out/static_map.json` - the dependency map (format: [docs/schema.md](docs/schema.md))
* `out/static_map.html` - interactive report, open it in a browser

Run `chaos-tool static --help` for all options.

## Develop

```bash
ruff check .          # lint
ruff format .         # format
pytest                # tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the branch / PR workflow and
[docs/decisions.md](docs/decisions.md) for design decisions.

## Layout

```
src/chaos_tool/
  model.py              shared graph model (Node, Edge, Finding, SystemMap)
  cli.py                command-line entry point
  parsers/compose.py    docker-compose.yml -> SystemMap
  hints/source_hints.py text search for service references in source code
  analyzers/            graph metrics and suspicion rules
  report/               JSON and HTML output
tests/
  fixtures/voting/      snapshot of the voting app compose file + expected result
docs/
  schema.md             the static_map.json format
  decisions.md          why things are the way they are
```
