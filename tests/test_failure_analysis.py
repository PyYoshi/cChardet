# SPDX-License-Identifier: MIT
import copy
import hashlib
import json
import subprocess
import sys

import pytest

from benchmarks import failure_analysis
from benchmarks.encoding_families import canonical_encoding, encoding_family, family_observation
from benchmarks.failure_analysis import classify, size_bucket


def test_ranking_evidence():
    data = "日本語".encode("utf-8")
    result = classify(data, "utf-8", [{"encoding": "cp1251"}, {"encoding": "utf-8"}])
    assert result["category"] == "RANKING_FAILURE"
    assert result["exact_candidate_rank"] == 2
    assert result["top_k"] == {"1": False, "3": True, "5": True}
    assert result["cause_status"] == "UNRESOLVED"
    assert result["family_relation"] == "DIFFERENT_FAMILY"


def test_absence_is_not_unsupported():
    result = classify("日本語".encode(), "utf-8", [{"encoding": "cp1251"}])
    assert result["category"] == "EXPECTED_CANDIDATE_ABSENT"
    assert result["cause_status"] == "UNRESOLVED"


def test_invalid_label_or_truncated_input():
    result = classify(b"\xff", "utf-8", [{"encoding": "cp1251"}])
    assert result["category"] == "LABEL_OR_INPUT_REQUIRES_REVIEW"


def test_unknown_codec_is_evaluator_limitation():
    result = classify(b"abc", "made-up-encoding", [])
    assert result["decode_equivalent"] is None
    assert result["expected_decodes"] is None
    assert result["category"] == "EVALUATOR_CODEC_UNAVAILABLE"


def test_size_bucket_boundaries():
    assert size_bucket(0) == "<=16B"
    assert size_bucket(1024) == "<=1024B"
    assert size_bucket(1025) == "<=4096B"


def test_explicit_family_mapping_aliases_and_unknowns():
    assert canonical_encoding("Windows-1251") == "cp1251"
    assert encoding_family("Windows-1251") == encoding_family("CP1251") == "cyrillic"
    assert encoding_family("latin1") == encoding_family("ISO-8859-1") == "latin-western"
    assert encoding_family("ISO-8859-5") == "cyrillic"
    assert encoding_family("ISO-8859-7") == "greek"
    assert encoding_family("Windows-1253") == "greek"
    assert encoding_family("ISO-8859-3") == "unknown"  # Valid codec not yet explicitly mapped.
    assert encoding_family("windows-made-up") == "unknown"
    assert encoding_family(None) == "unknown"
    assert encoding_family("utf-16-le") != encoding_family("utf-8")
    assert family_observation("cp932", "euc_jp")["family_relation"] == "SAME_FAMILY"


def test_cause_status_is_not_automatic_diagnosis():
    assert classify("日本語".encode(), "utf-8", [])["cause_status"] == "UNRESOLVED"
    assert classify(b"abc", "made-up", [])["cause_status"] == "UNRESOLVED"
    result = classify(b"abc", "ascii", [{"encoding": "ascii"}])
    assert result["category"] == "EXACT_MATCH"
    assert result["cause_status"] == "NOT_APPLICABLE"
    assert result["family_relation"] == "SAME_FAMILY"


def test_legacy_report_uses_explicit_unknown_workload_and_family(tmp_path, monkeypatch, capsys):
    corpus = tmp_path / "corpus"
    (corpus / "fr").mkdir(parents=True)
    (corpus / "fr/UTF-8.txt").write_bytes("café".encode())
    tool = tmp_path / "mock-tool"
    tool.write_bytes(b"not executable; subprocess is mocked")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "failure_analysis",
            "--native-tool",
            str(tool),
            "--native-revision",
            "test-only",
            "--uchardet-corpus",
            str(corpus),
        ],
    )
    record = dict(schema_version=1, input_index=0, candidate_count=0, candidates=[])
    monkeypatch.setattr(
        failure_analysis.subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess(a, 0, stdout=json.dumps(record)),
    )
    failure_analysis.main()
    report = json.loads(capsys.readouterr().out)
    assert report["family_mapping_version"] == "codec-family-v1"
    for key in ("family:utf-8", "corpus:uchardet-legacy", "source_kind:unknown", "format:unknown"):
        assert report["grouped"][key]["files"] == 1
        assert report["grouped"][key]["cause_status:UNRESOLVED"] == 1
    sample = report["samples"][0]
    assert sample["category"] == "NO_CANDIDATE"
    assert sample["family_relation"] == "UNKNOWN"


def test_exact_label_does_not_hide_invalid_or_unavailable_input():
    result = classify(b"\xff", "utf-8", [{"encoding": "utf-8"}])
    assert result["exact"] and result["category"] == "EXACT_MATCH"
    assert result["expected_decodes"] is False
    assert result["cause_status"] == "UNRESOLVED"
    result = classify(b"abc", "made-up", [{"encoding": "made-up"}])
    assert result["expected_decodes"] is None
    assert result["cause_status"] == "UNRESOLVED"


@pytest.fixture
def saved_legacy(tmp_path):
    corpus = tmp_path / "corpus"
    (corpus / "fr").mkdir(parents=True)
    samples = []
    for name, data in (("UTF-8.txt", "café".encode()), ("ascii.txt", b"hello")):
        (corpus / "fr" / name).write_bytes(data)
        samples.append(
            dict(
                path=f"fr/{name}",
                byte_length=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
                expected_encoding=name.split(".")[0],
                expected_language="fr",
                expected_label_source=failure_analysis.LEGACY_LABEL_SOURCE,
                split="legacy-validation",
                candidates=[dict(encoding="UTF-8", language="fr", confidence_bits="3f800000")],
            )
        )
    report = dict(
        schema_version=1,
        corpus="uchardet-legacy",
        native_revision="retained-revision",
        tool_sha256="a" * 64,
        samples=samples,
    )
    path = tmp_path / "saved.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    return corpus, path, report


def test_saved_observations_cli_never_launches_process(saved_legacy, monkeypatch, capsys):
    corpus, path, original = saved_legacy
    monkeypatch.setattr(
        sys,
        "argv",
        ["failure_analysis", "--observations", str(path), "--uchardet-corpus", str(corpus)],
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("saved observation mode must never launch a process")

    monkeypatch.setattr(failure_analysis.subprocess, "run", forbidden)
    failure_analysis.main()
    report = json.loads(capsys.readouterr().out)
    assert report["native_revision"] == original["native_revision"]
    assert report["tool_sha256"] == original["tool_sha256"]
    assert (
        report["observation_source"]["report_sha256"]
        == hashlib.sha256(path.read_bytes()).hexdigest()
    )
    assert report["observation_source"]["evaluator_version"] is None
    assert report["observation_source"]["mode"] == "saved-legacy-report"
    assert report["sample_order"].startswith("lexicographic")
    assert [s["path"] for s in report["samples"]] == [s["path"] for s in original["samples"]]
    assert all(
        s["expected_label_source"] == failure_analysis.LEGACY_LABEL_SOURCE
        for s in report["samples"]
    )


@pytest.mark.parametrize(
    "change",
    [
        "order",
        "path",
        "hash",
        "length",
        "encoding",
        "language",
        "label_source",
        "split",
        "corpus",
        "count",
        "revision",
        "tool",
    ],
)
def test_saved_observations_reject_mismatch(saved_legacy, change):
    corpus, path, original = saved_legacy
    report = copy.deepcopy(original)
    sample = report["samples"][0]
    if change == "order":
        report["samples"].reverse()
    elif change == "path":
        sample["path"] = "../UTF-8.txt"
    elif change == "hash":
        sample["sha256"] = "0" * 64
    elif change == "length":
        sample["byte_length"] += 1
    elif change == "encoding":
        sample["expected_encoding"] = "cp1251"
    elif change == "language":
        sample["expected_language"] = "ja"
    elif change == "label_source":
        sample["expected_label_source"] = "external holdout"
    elif change == "split":
        sample["split"] = "independent"
    elif change == "corpus":
        report["corpus"] = "independent"
    elif change == "count":
        report["samples"].pop()
    elif change == "revision":
        del report["native_revision"]
    else:
        report["tool_sha256"] = "invalid"
    path.write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(ValueError):
        failure_analysis.saved_observations(path, corpus, sorted((corpus / "fr").iterdir()))


def test_observation_cli_modes_are_exclusive(saved_legacy, monkeypatch):
    corpus, path, _ = saved_legacy
    base = ["failure_analysis", "--observations", str(path), "--uchardet-corpus", str(corpus)]
    for extra in (["--native-tool", "unused"], ["--native-revision", "replacement"]):
        monkeypatch.setattr(sys, "argv", base + extra)
        with pytest.raises(SystemExit) as error:
            failure_analysis.main()
        assert error.value.code == 2


def test_saved_observations_reject_changed_corpus_bytes(saved_legacy):
    corpus, path, _ = saved_legacy
    target = corpus / "fr/UTF-8.txt"
    target.write_bytes(b"x" * len(target.read_bytes()))
    with pytest.raises(ValueError, match="byte length/hash"):
        failure_analysis.saved_observations(path, corpus, sorted((corpus / "fr").iterdir()))


@pytest.mark.parametrize("bits", ["3f80", "not-hex!", "7fc00000"])
def test_saved_observations_reject_invalid_confidence(saved_legacy, monkeypatch, bits):
    corpus, path, report = saved_legacy
    report["samples"][0]["candidates"][0]["confidence_bits"] = bits
    path.write_text(json.dumps(report), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["failure_analysis", "--observations", str(path), "--uchardet-corpus", str(corpus)],
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("must not launch a process")

    monkeypatch.setattr(failure_analysis.subprocess, "run", forbidden)
    with pytest.raises(ValueError, match="confidence"):
        failure_analysis.main()
