# Contributing

## Workflow

`main` is always working: CI is green and the tool runs. All changes go
through a pull request.

1. Update main and branch off it:

   ```bash
   git switch main
   git pull
   git switch -c feat/compose-parser
   ```

2. Commit in small steps. Before pushing:

   ```bash
   ruff format .
   ruff check .
   pytest
   ```

3. Push and open a PR:

   ```bash
   git push -u origin feat/compose-parser
   ```

   Fill in the PR template. One partner reviews and approves, then merge
   with **Squash and merge** and delete the branch.

## Branch names

| prefix | for |
|---|---|
| `feat/` | new functionality (`feat/compose-parser`) |
| `fix/` | bug fixes (`fix/port-parsing`) |
| `test/` | tests only |
| `docs/` | documentation only |
| `chore/` | tooling, CI, dependencies |

## Commit messages

Short imperative summary with a type prefix
([Conventional Commits](https://www.conventionalcommits.org/)):

```
feat: parse depends_on in list and mapping form
fix: handle ports with host IP
test: add ground-truth test for voting app
docs: describe edge kinds in schema.md
```

## Code style

* Python 3.10+, type hints on public functions, a docstring on every module.
* `ruff` decides formatting - don't argue with it.
* Parsers are the only code that knows about input formats; analyzers and
  reporters work only with `chaos_tool.model`.
* Output must be deterministic (sorted), so diffs between runs are meaningful.
* If the JSON output changes, update `docs/schema.md` and bump `SCHEMA_VERSION`
  in `model.py`.
