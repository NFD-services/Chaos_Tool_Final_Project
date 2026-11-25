# CLAUDE.md

Context for Claude Code. Read this first, then `README.md`, `CONTRIBUTING.md`,
`docs/decisions.md` and `docs/schema.md`.

## The project

BGU Computer Science final project (team of students, approved Nov 2026).
An automated **security chaos engineering** tool for microservice systems:

1. **Discover** - map dependencies statically (`docker-compose.yml` + source hints)
   and dynamically (Docker SDK, Jaeger/OpenTelemetry traces).
2. **Hypothesize** - an LLM (cheap model, e.g. gpt-4o-mini or Claude Haiku) gets
   the gaps between the static and dynamic maps and proposes chaos experiments.
3. **Execute** - inject faults under a controlled blast radius (startup delay,
   network block via iptables / docker commands).
4. **Judge** - compare behavior to baseline, decide if a security weakness was
   exposed (e.g. sensitive data returned instead of failing quietly).

Must eventually run on the university HPC (Apptainer + SLURM, single allocation).

**Targets:** Semester A - Docker Example Voting App only.
Semester B (if all goes well) - Google Online Boutique (Kubernetes manifests, gRPC).

## Current status

- Voting app runs locally (`~/example-voting-app`, `docker compose up`).
- Load generation works with Locust (`locustfile.py` in the voting app folder:
  each user GETs `/`, POSTs a random vote a/b, clears cookies so every vote is a
  new voter; run `locust -f locustfile.py --host http://localhost:8080`, UI on
  `:8089`; 20-50 users is enough for steady traffic).
- This repo: **Stage 0 (repo setup) and Stage 1 (model + schema) are done.**
  12 tests pass; 4 ground-truth tests are skipped until Stage 2.
- **Next: Stage 2 - the compose parser** (`src/chaos_tool/parsers/compose.py`).

## Static-analysis plan (stages)

Order of work: 0 -> 1 -> 2 -> 7 (end-to-end skeleton) -> 8 (ground truth) -> 4 -> 3 -> 5 -> 6.
One branch + PR per stage.

| # | Stage | File(s) | Status |
|---|---|---|---|
| 0 | Repo setup | `pyproject.toml`, CI, docs | done |
| 1 | Model + schema | `model.py`, `docs/schema.md` | done |
| 2 | Compose parser | `parsers/compose.py` | **next** |
| 3 | Source hints | `hints/source_hints.py` | stub |
| 4 | Graph metrics | `analyzers/graph_metrics.py` | stub |
| 5 | Suspicion rules | `analyzers/rules/` | stub (registry done) |
| 6 | HTML report | `report/html_report.py`, `template.html` | stub |
| 7 | CLI | `cli.py` | done (wires all stages) |
| 8 | Tests | `tests/` | model/cli done, ground truth waiting |

### Stage 2 requirements (compose parser)

- Primary: read YAML ourselves with PyYAML - **no hard dependency on Docker**.
  `docker compose config` only as optional fallback (`--use-docker`).
- Handle all spellings: `depends_on` list/mapping (keep `condition`), `ports`
  short/long/with host IP, `networks` list/mapping (no networks -> `default`),
  named volumes vs bind mounts, `environment` list/mapping, `${VAR}` /
  `${VAR:-default}` interpolation, `profiles` (-> `optional=True`), `build`
  string/mapping (keep context for Stage 3).
- Keep line numbers in `Evidence` (use `yaml.compose` node marks).
- Produce: service / network / volume / `external:host` nodes; `depends_on`,
  `member_of`, `mounts`, `exposes`, `env_reference` edges.
- Must pass `tests/test_ground_truth.py` against `tests/fixtures/voting/`.
- `seed` service (profile `seed`) appears with `optional: true`.

### Stage 5 rules (agreed - keep it easy to add more later)

| rule id | severity |
|---|---|
| `network_overreach` (vote/result on back-tier can reach db/redis without reason) | high |
| `plaintext_secret` (e.g. `POSTGRES_PASSWORD: postgres`) | high |
| `exposed_sensitive_port` (debug 9229, DB ports) | medium |
| `silent_failure` (nothing depends on it, no healthcheck - e.g. worker) | medium |
| `missing_healthcheck` | low |

Severity: three levels (low / medium / high). No rule config file for now.

## Key design decisions (details in docs/decisions.md)

- Separate repo for the tool; the target system is an input.
- Analyze declared architecture + light text-search hints in source code; no
  per-language parsing. Deep code understanding is left to the LLM.
- Three layers: parsers -> model -> analyzers/reporters. Only parsers know input
  formats. Not generic up front - just separated so Online Boutique needs a new
  parser, not a rewrite.
- Edges point client -> server (matches Jaeger). The voting app diagram shows
  data flow, so some of its arrows point the other way.
- Networks are nodes (`member_of` edges), not pairwise edges.
- Node ids are `<kind>:<name>`; `name` is the bare compose service name.
- Facts (nodes/edges) and suspicions (findings) are kept separate.
- `dataclasses`, Python >= 3.10, deterministic sorted JSON with no timestamp.
- HTML report is one self-contained offline file; Cytoscape.js is vendored.

## Conventions

- Python 3.10+ (HPC compatibility). Type hints, module docstrings.
- `ruff format . && ruff check . && pytest` must pass before every PR.
- Code, comments and docs in **English**.
- Branches: `feat/`, `fix/`, `test/`, `docs/`, `chore/`. Conventional Commit
  messages. Never push directly to `main`; open a PR, a partner reviews.
- If JSON output changes: update `docs/schema.md` and bump `SCHEMA_VERSION`.
- New design decision -> add an entry to `docs/decisions.md`.

## How to work with the user

- The user writes in Hebrew - reply in Hebrew (code and docs stay English).
- The user wants to be actively involved: before writing code, break the work
  into parts, explain each part and the choices made, and ask design/code
  questions. Wait for approval before implementing.
- Explain which languages/files are involved and what each new file does.

## Environment

- Windows + WSL 2 (Ubuntu 24.04). Python packages go in a venv
  (`python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`);
  system pip is blocked (externally-managed-environment).
- Voting app: `~/example-voting-app` (vote :8080, result :8081).
