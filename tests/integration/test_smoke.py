"""Smoke test (spec §10.2). Owner: M6.

Passes against the kickoff skeleton, so CI is green from day 1. It only checks that
everything imports and the app runs; behaviour is covered by unit and integration tests.
"""
import importlib
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

pytestmark = pytest.mark.integration

APP_PATH = Path(__file__).resolve().parents[2] / "app.py"

MODULES = [
    "swap.models",
    "swap.engine",
    "swap.scenarios",
    "swap.validation",
    "swap.export",
    "ui.formatting",
    "ui.inputs",
    "ui.rates_editor",
    "ui.results",
    "ui.chart",
    "ui.explainer",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_module_imports(module_name: str) -> None:
    importlib.import_module(module_name)


def test_app_runs_without_exception() -> None:
    at = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
    assert not at.exception
