import pytest

from chaos_tool.cli import main


def test_help_exits_cleanly():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_missing_compose_file_returns_error(tmp_path):
    assert main(["static", "--compose", str(tmp_path / "nope.yml")]) == 1
