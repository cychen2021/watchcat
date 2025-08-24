import runpy
from pathlib import Path


def _load_fill_out():
    # Load the prompt module by running its __init__.py directly to avoid package install
    mod_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "watchcat"
        / "prompt"
        / "__init__.py"
    )
    # The tests run with tests/conftest.py adding the repo src/ to sys.path, but run_path keeps things isolated.
    return runpy.run_path(str(mod_path))["fill_out_prompt"]


def test_fill_out_string_and_json():
    fill_out = _load_fill_out()
    assert fill_out("Hello ?<NAME>?", NAME="Alice") == "Hello Alice"
    assert fill_out("Data: ?<DATA>?", DATA={"a": 1}) == 'Data: {"a": 1}'


def test_fill_out_missing_placeholder_raises():
    fill_out = _load_fill_out()
    import pytest

    with pytest.raises(KeyError):
        fill_out("Missing ?<X>?", Y=1)
