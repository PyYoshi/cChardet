# SPDX-License-Identifier: MIT
import json
import subprocess
import sys

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
