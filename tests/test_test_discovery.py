# SPDX-License-Identifier: MIT
"""Default collection includes native tests but not downloaded runtime archives."""

import json
import subprocess
import sys
import tomllib
from pathlib import Path


def test_default_collection_roots(tmp_path):
    root = Path(__file__).resolve().parents[1]
    config = tomllib.loads((root / "pyproject.toml").read_text())
    roots = config["tool"]["pytest"]["ini_options"]["testpaths"]
    (tmp_path / "pyproject.toml").write_text(
        "[tool.pytest.ini_options]\ntestpaths = " + json.dumps(roots) + "\n"
    )
    for directory in ("tests", "src/ext/uchardet/corpus", "archives/python/lib"):
        path = tmp_path / directory
        path.mkdir(parents=True)
        (path / "test_example.py").write_text("def test_example(): pass\n")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "--import-mode=importlib", "-q"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    assert "tests/test_example.py::test_example" in result.stdout
    assert "src/ext/uchardet/corpus/test_example.py::test_example" in result.stdout
    assert "archives" not in result.stdout
