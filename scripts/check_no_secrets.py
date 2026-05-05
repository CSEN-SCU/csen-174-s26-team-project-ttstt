"""Fail CI/local checks when likely secrets are present in tracked files."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


PATTERNS = {
    "elevenlabs_api_key": re.compile(r"\bsk_[A-Za-z0-9]{20,}\b"),
    "dotenv_key_assign": re.compile(r"ELEVENLABS_API_KEY\s*=\s*['\"]?[A-Za-z0-9_\-]{10,}"),
}

SKIP_PATH_PARTS = {".git", ".venv", "__pycache__", "node_modules"}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp3", ".wav", ".lock"}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def should_skip(path: Path) -> bool:
    if any(part in SKIP_PATH_PARTS for part in path.parts):
        return True
    return path.suffix.lower() in SKIP_SUFFIXES


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings: list[str] = []

    for rel_path in tracked_files():
        abs_path = root / rel_path
        if should_skip(rel_path) or not abs_path.exists() or not abs_path.is_file():
            continue
        try:
            content = abs_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for name, pattern in PATTERNS.items():
            if pattern.search(content):
                findings.append(f"{rel_path}: matched {name}")

    if findings:
        print("Potential secrets detected:")
        for finding in findings:
            print(f" - {finding}")
        return 1

    print("No obvious secrets detected in tracked files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
