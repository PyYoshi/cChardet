# SPDX-License-Identifier: MIT
"""Structural guards for dev-only wheel deduplication and docs-only skipping."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def workflow(name):
    return (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")


def events(text):
    block = text.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
    return "\n".join(line for line in block.splitlines() if not line.lstrip().startswith("#"))


def test_dev_wheels_only_run_automatically_for_pull_requests():
    assert events(workflow("build-dev.yml")).strip() == """pull_request:
    branches: [dev]
    paths-ignore:
      - '**.md'
      - '**.rst'"""


def test_dev_retains_post_merge_tests_and_docs_only_skips():
    block = events(workflow("test-dev.yml"))
    assert block.strip() == """push:
    branches: [dev]
    paths-ignore:
      - '**.md'
      - '**.rst'
  pull_request:
    branches: [dev]
    paths-ignore:
      - '**.md'
      - '**.rst'"""
    assert "uses: ./.github/workflows/test.yml" in workflow("test-dev.yml")


def test_full_wheel_matrix_and_read_only_permissions_remain():
    text = workflow("build-dev.yml")
    assert "os: [ubuntu-latest, windows-latest, macos-latest]" in text
    assert "uses: ./.github/actions/build-wheels" in text
    assert "submodules: recursive" in text
    assert "permissions:\n  contents: read" in text


def test_master_release_and_explicit_rebuild_events_remain():
    assert events(workflow("build.yaml")).strip() == """push:
    branches: [master]
    tags: ["v*"]
  pull_request:
    branches-ignore: [dev]
  workflow_dispatch:"""
    assert events(workflow("test.yml")).strip() == """push:
    branches: [master]
  pull_request:
    branches-ignore: [dev]
  workflow_dispatch:
  workflow_call:"""
