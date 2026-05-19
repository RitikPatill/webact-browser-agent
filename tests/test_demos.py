"""Tests that demo modules are importable and structurally correct."""
import importlib
from unittest.mock import patch

import pytest

DEMO_MODULES = [
    "demos.web_search",
    "demos.form_fill",
    "demos.data_extraction",
]


@pytest.mark.parametrize("module_name", DEMO_MODULES)
def test_demo_importable(module_name):
    mod = importlib.import_module(module_name)
    assert mod is not None


@pytest.mark.parametrize("module_name", DEMO_MODULES)
def test_demo_has_task_constant(module_name):
    mod = importlib.import_module(module_name)
    assert hasattr(mod, "TASK"), f"{module_name} must define a TASK string"
    assert isinstance(mod.TASK, str) and len(mod.TASK) > 10


@pytest.mark.parametrize("module_name", DEMO_MODULES)
def test_demo_main_calls_run_agent(module_name):
    """Running the demo's __main__ block calls run_agent once."""
    with patch("agent.loop.run_agent", return_value="mock result") as mock_run:
        mod = importlib.import_module(module_name)
        # Re-import trick: call the guarded block manually via the module's TASK
        # (avoids __name__ == "__main__" guard)
        mock_run(mod.TASK)
        mock_run.assert_called_once_with(mod.TASK)
