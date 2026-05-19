"""Unit tests for /help command configuration (no discord import)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = REPO_ROOT / "apps" / "bot" / "main.py"
HELP_INDEX = REPO_ROOT / "docs" / "help" / "index.html"


def test_default_help_url_points_at_github_pages() -> None:
    text = MAIN_PY.read_text(encoding="utf-8")
    assert 'DEFAULT_HELP_URL = "https://csen-scu.github.io/csen-174-s26-team-project-ttstt/"' in text


def test_help_command_registered_in_setup_hook() -> None:
    text = MAIN_PY.read_text(encoding="utf-8")
    assert "self.tree.add_command(help_command)" in text
    assert '@app_commands.command(name="help"' in text


def test_help_site_documents_slash_help() -> None:
    html = HELP_INDEX.read_text(encoding="utf-8")
    assert "<code>/help</code>" in html
    assert "TTSTT Help" in html
