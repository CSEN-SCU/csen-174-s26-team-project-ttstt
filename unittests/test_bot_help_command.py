"""Unit tests for /help command and Netlify help site config."""

from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = REPO_ROOT / "apps" / "bot" / "main.py"
HELP_INDEX = REPO_ROOT / "docs" / "help" / "index.html"
NETLIFY_TOML = REPO_ROOT / "netlify.toml"


def test_no_github_pages_workflows() -> None:
    workflows = REPO_ROOT / ".github" / "workflows"
    assert not (workflows / "pages.yml").exists()
    for path in workflows.glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        assert "deploy-pages" not in text
        assert "upload-pages-artifact" not in text


def test_netlify_publishes_docs_help() -> None:
    data = tomllib.loads(NETLIFY_TOML.read_text(encoding="utf-8"))
    assert data["build"]["publish"] == "docs/help"
    assert data["build"]["command"] == ""


def test_help_url_required_at_startup() -> None:
    text = MAIN_PY.read_text(encoding="utf-8")
    assert "HELP_URL must be set in .env" in text
    assert "github.io" not in text


def test_help_command_registered_in_setup_hook() -> None:
    text = MAIN_PY.read_text(encoding="utf-8")
    assert "self.tree.add_command(help_command)" in text
    assert '@app_commands.command(name="help"' in text


def test_help_site_documents_slash_help() -> None:
    html = HELP_INDEX.read_text(encoding="utf-8")
    assert "<code>/help</code>" in html
    assert "TTSTT Help" in html
