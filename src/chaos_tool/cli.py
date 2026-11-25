"""Command-line entry point: ``chaos-tool <command> ...``.

Today there is one command, ``static``. Later stages add ``dynamic``,
``hypothesize`` and ``inject`` as more subcommands of the same tool.

Example::

    chaos-tool static --compose ../example-voting-app/docker-compose.yml --out out/
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from chaos_tool import __version__

log = logging.getLogger("chaos_tool")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chaos-tool", description=__doc__.splitlines()[0])
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="show debug logging")
    sub = parser.add_subparsers(dest="command", required=True)

    static = sub.add_parser("static", help="static analysis of a docker-compose system")
    static.add_argument("--compose", type=Path, required=True, help="path to docker-compose.yml")
    static.add_argument("--out", type=Path, default=Path("out"), help="output directory")
    static.add_argument(
        "--source-root",
        type=Path,
        default=None,
        help="root of the service source code (default: the compose file's folder)",
    )
    static.add_argument("--target", default=None, help="system name (default: folder name)")
    static.add_argument("--no-hints", action="store_true", help="skip the source-code text search")
    static.add_argument(
        "--use-docker",
        action="store_true",
        help="normalize the compose file with 'docker compose config' instead of our parser",
    )
    static.set_defaults(func=run_static)
    return parser


def run_static(args: argparse.Namespace) -> int:
    # Imports are local so that `--help` works even before every stage exists.
    from chaos_tool.analyzers.graph_metrics import compute_metrics
    from chaos_tool.analyzers.rules import run_rules
    from chaos_tool.hints.source_hints import add_source_hints
    from chaos_tool.parsers.compose import parse_compose
    from chaos_tool.report.html_report import write_html
    from chaos_tool.report.json_export import write_json

    compose: Path = args.compose
    if not compose.is_file():
        log.error("compose file not found: %s", compose)
        return 1

    system = parse_compose(compose, target=args.target, use_docker=args.use_docker)
    if not args.no_hints:
        add_source_hints(system, args.source_root or compose.parent)
    compute_metrics(system)
    run_rules(system)

    json_path = write_json(system, args.out / "static_map.json")
    html_path = write_html(system, args.out / "static_map.html")

    services = len([n for n in system.nodes.values() if n.kind.value == "service"])
    print(f"{services} services, {len(system.edges)} edges, {len(system.findings)} findings")
    print(f"wrote {json_path}")
    print(f"wrote {html_path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )
    try:
        return args.func(args)
    except NotImplementedError as exc:
        log.error("not implemented yet: %s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
