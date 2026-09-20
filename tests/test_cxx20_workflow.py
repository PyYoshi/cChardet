# SPDX-License-Identifier: MIT
"""Focused structural guards; actionlint validates the complete YAML syntax."""

from pathlib import Path

WORKFLOW = (Path(__file__).resolve().parents[1] / ".github/workflows/cxx20-wheels.yml").read_text(
    encoding="utf-8"
)


def test_only_opt_in_events():
    events = WORKFLOW.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
    assert (
        events.strip()
        == """workflow_dispatch:
  pull_request:
    types: [labeled]
    branches: [dev]
    paths-ignore:
      - '**.md'
      - '**.rst'"""
    )


def test_job_guard_and_non_cancelling_labels():
    guard = WORKFLOW.split("    if: >-\n", 1)[1].split("    name:", 1)[0]
    assert " ".join(guard.split()) == (
        "(github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/dev') || "
        "(github.event_name == 'pull_request' && github.event.action == 'labeled' && "
        "github.event.label.name == 'v3-cxx20-validation')"
    )
    assert (
        "group: cxx20-wheels-${{ github.event_name }}-${{ github.ref }}-"
        "${{ github.event.label.name }}"
    ) in WORKFLOW


def test_read_only_shared_matrix():
    permissions = WORKFLOW.split("\npermissions:\n", 1)[1].split("\nconcurrency:", 1)[0]
    assert permissions.strip() == "contents: read"
    assert "os: [ubuntu-latest, macos-latest, windows-latest]" in WORKFLOW
    assert 'CCHARDET_CXX_STANDARD: "20"' in WORKFLOW
    assert "CIBW_ENVIRONMENT_PASS_LINUX: CCHARDET_CXX_STANDARD" in WORKFLOW
    assert "uses: ./.github/actions/build-wheels" in WORKFLOW
