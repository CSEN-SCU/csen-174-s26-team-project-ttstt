"""
Future-facing unit test for transient retry policy behavior.
"""

from __future__ import annotations

import importlib
from typing import Callable

import pytest


MODULE_PATH = "apps.bot.resilience"
FUNCTION_NAME = "run_with_retries"


def _load_run_with_retries() -> Callable:
    try:
        module = importlib.import_module(MODULE_PATH)
    except ModuleNotFoundError:
        pytest.skip(
            f"{MODULE_PATH!r} does not exist yet. "
            "Unskip this test after resilience utilities are implemented."
        )

    if not hasattr(module, FUNCTION_NAME):
        pytest.skip(
            f"{MODULE_PATH!r} exists, but {FUNCTION_NAME!r} is not implemented yet."
        )

    return getattr(module, FUNCTION_NAME)


def test_run_with_retries_retries_transient_error_then_succeeds() -> None:
    # As a server admin, temporary provider failures are retried so the bot recovers without manual intervention.

    # Arrange
    run_with_retries = _load_run_with_retries()
    attempts = {"count": 0}

    class FakeTransientError(Exception):
        pass

    def flaky_operation() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise FakeTransientError("temporary failure")
        return "ok"

    # Action
    result = run_with_retries(flaky_operation, max_attempts=3)

    # Assert
    assert attempts["count"] == 3
    assert result == "ok"
