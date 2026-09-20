# SPDX-License-Identifier: MIT
import copy
import json
import subprocess
import sys

import pytest

from benchmarks import manifest_analysis as analysis


@pytest.fixture
def corpus(tmp_path):
    framework = analysis.framework_module()
    sources = []
    for split in ("training", "validation", "independent"):
        data = (split + " café " * 12).encode()
        (tmp_path / f"{split}.txt").write_bytes(data)
        sources.append(
            dict(
                id=split,
                path=f"{split}.txt",
                language="fr",
                license="MIT",
                license_reference="synthetic test",
                revision="1",
                origin=split,
                kind="synthetic",
                sha256=framework.digest(data),
                split=split,
            )
        )
    config = dict(
        sources=sources,
        encodings=["utf-8"],
        byte_limits=[None, 16],
        boundaries=["complete", "truncated"],
        formats=["text"],
    )
    framework.generate(config, tmp_path, tmp_path / "out")
    return tmp_path / "out" / "manifest.json"


def test_selection_and_report_purity(corpus):
    manifests = analysis.load_manifests([corpus])
    samples = analysis.select_samples(manifests, {"validation"}, 16)
    before = copy.deepcopy(samples)
    seen = []

    def observer(sample):
        seen.append(sample["id"])
        assert sample["split"] == "validation"
        return dict(
            category="EXACT",
            exact=True,
            compatible=True,
            decode_equivalent=None,
            language_correct=True,
            encoding_and_language_correct=True,
            top_k={"1": True, "3": True, "5": True},
        )

    report = analysis.make_report(manifests, samples, observer)
    assert len(seen) == 1
    assert samples == before
    assert report["groups"]["all"]["available"] == 12
    assert report["groups"]["all"]["evaluated"] == 1
    assert report["groups"]["all"]["decode_equivalent_evaluable"] == 0
    assert report["corpora"][0]["generation_counts"] == {
        "attempted": 12,
        "successful": 12,
        "skipped": 0,
    }
    assert all("_absolute_path" not in sample for sample in report["samples"])
    inventory = analysis.make_report(manifests, report["samples"])
    assert not any("prediction" in sample for sample in inventory["samples"])
    assert "evaluated" not in inventory["groups"]["all"]


def test_duplicate_and_invalid_selection(corpus):
    with pytest.raises(ValueError, match="duplicate corpus"):
        analysis.load_manifests([corpus, corpus])
    for splits, limit in [
        (set(), None),
        ({"wrong"}, 1),
        ({"validation"}, True),
        ({"validation"}, 0),
    ]:
        with pytest.raises(ValueError):
            analysis.select_samples([], splits, limit)


def test_legacy_manifest_without_generation_report(corpus):
    framework = analysis.framework_module()
    manifest = json.loads(corpus.read_text(encoding="utf-8"))
    del manifest["generation_report"]
    for sample in manifest["samples"]:
        del sample["ground_truth"]
    manifest["content_hash"] = framework.content_hash(manifest)
    corpus.write_text(json.dumps(manifest), encoding="utf-8")
    manifests = analysis.load_manifests([corpus])
    samples = analysis.select_samples(manifests, {"validation"}, 16)
    report = analysis.make_report(manifests, samples)
    assert report["corpora"][0]["generation_counts"] is None
    assert report["samples"][0]["ground_truth"] == {"provenance": "legacy-schema1"}


def test_cross_manifest_leakage(corpus, tmp_path):
    framework = analysis.framework_module()
    manifest = json.loads(corpus.read_text(encoding="utf-8"))
    source = manifest["sources"][0]
    data = b"Different content with the same origin"
    (tmp_path / "second.txt").write_bytes(data)
    source = dict(source, path="second.txt", sha256=framework.digest(data), split="tuning")
    framework.generate(dict(sources=[source], encodings=["utf-8"]), tmp_path, tmp_path / "two")
    with pytest.raises(ValueError, match="split leakage"):
        analysis.load_manifests([corpus, tmp_path / "two/manifest.json"])


def test_observer_errors_abort(corpus):
    manifests = analysis.load_manifests([corpus])
    samples = analysis.select_samples(manifests, {"validation"}, 16)

    def fail(sample):
        raise RuntimeError("observation failed")

    with pytest.raises(RuntimeError, match="observation failed"):
        analysis.make_report(manifests, samples, fail)


def test_native_protocol_and_modified_sample(corpus, monkeypatch):
    samples = analysis.select_samples(analysis.load_manifests([corpus]), {"validation"}, 16)
    sample = next(sample for sample in samples if sample["selected"])
    record = dict(
        schema_version=1,
        input_index=0,
        byte_length=sample["byte_length"],
        candidate_count=1,
        candidates=[dict(encoding="UTF-8", language="fr", confidence_bits="3f800000")],
    )
    monkeypatch.setattr(
        analysis.subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess(a, 0, stdout=json.dumps(record)),
    )
    assert analysis.observe(corpus, sample)["exact"]
    record["candidate_count"] = 2
    with pytest.raises(ValueError, match="count mismatch"):
        analysis.observe(corpus, sample)
    record["candidate_count"] = 1
    record["candidates"][0]["confidence_bits"] = "7fc00000"
    with pytest.raises(ValueError, match="non-finite"):
        analysis.observe(corpus, sample)
    sample["_absolute_path"].write_bytes(b"changed")
    with pytest.raises(ValueError, match="sample changed"):
        analysis.observe(corpus, sample)


def test_cli_inventory_and_guards(corpus):
    command = [sys.executable, "-m", "benchmarks.manifest_analysis", "--manifest", str(corpus)]
    result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    report = json.loads(result.stdout)
    assert report["mode"] == "inventory-only"
    assert report["selection"]["splits"] == ["validation"]
    for args in [
        ["--native-tool", "missing"],
        [
            "--native-tool",
            "missing",
            "--native-revision",
            "fixture",
            "--max-input-bytes",
            "16",
            "--split",
            "independent",
        ],
    ]:
        result = subprocess.run(command + args, capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == 2
        assert "requires explicit" in result.stderr
