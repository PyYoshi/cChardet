# SPDX-License-Identifier: MIT
import hashlib
import json
import struct

import pytest

from benchmarks.confidence_analysis import analyze, confidence, summarize
from benchmarks.failure_analysis import LEGACY_LABEL_SOURCE


def sample(score, exact=True, equivalent=True):
    return dict(confidence=score, exact=exact, compatible=exact, decode_equivalent=equivalent)


def fixture(tmp_path):
    corpus = tmp_path / "corpus"
    (corpus / "fr").mkdir(parents=True)
    data = "café".encode()
    (corpus / "fr/utf-8.txt").write_bytes(data)
    report = dict(
        schema_version=1,
        corpus="uchardet-legacy",
        native_revision="fixture-only",
        tool_sha256="1" * 64,
        samples=[
            dict(
                path="fr/utf-8.txt",
                byte_length=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
                expected_encoding="utf-8",
                expected_language="fr",
                expected_label_source=LEGACY_LABEL_SOURCE,
                split="legacy-validation",
                candidates=[dict(encoding="UTF-8", language="fr", confidence_bits="3f800000")],
            )
        ],
    )
    path = tmp_path / "observations.json"
    path.write_text(json.dumps(report))
    return corpus, path, report


def test_thresholds_and_unscored_denominator():
    result = summarize([sample(1), sample(0.5, False), sample(None, False, None)])
    assert result["scored"] == 2
    assert result["unscored"] == 1
    row = next(r for r in result["selective"] if r["threshold"] == 0.5)
    assert row["selected"]["files"] == 2
    assert row["selected"]["exact"] == 1
    assert row["coverage"] == {"numerator": 2, "denominator": 3}
    assert row["rejected_or_unscored"] == 1
    assert sum(b["files"] for b in result["bins"]) == 2


def test_scores_not_clamped_or_called_probabilities():
    result = summarize([sample(-0.1), sample(1.1)])
    assert result["outside_unit_interval"] == 2
    assert result["bins"][0]["files"] == 1
    assert result["bins"][-1]["files"] == 1
    assert result["selective"][-1]["selected"]["files"] == 1


def test_evaluable_denominator_and_empty_selection():
    result = summarize([sample(0.2, equivalent=None)])
    assert result["all"]["decode_equivalent_evaluable"] == 0
    assert result["selective"][-1]["selected"]["files"] == 0
    assert summarize([])["all"]["files"] == 0


@pytest.mark.parametrize("bits", [None, "bad", "7fc00000", "7f800000", "ff800000"])
def test_invalid_confidence(bits):
    with pytest.raises(ValueError):
        confidence({"confidence_bits": bits})


def test_binary32_is_authoritative():
    assert confidence({"confidence_bits": "3f000000", "confidence": 0.9}) == 0.5
    bits = struct.pack("!f", 0.99).hex()
    assert confidence({"confidence_bits": bits}) == struct.unpack("!f", bytes.fromhex(bits))[0]


def test_saved_reanalysis_no_native(tmp_path, monkeypatch):
    corpus, path, _ = fixture(tmp_path)
    monkeypatch.setattr(
        "benchmarks.failure_analysis.subprocess.run",
        lambda *a, **kw: pytest.fail("must not execute native tool"),
    )
    result = analyze(path, corpus)
    assert result == analyze(path, corpus)
    assert result["native_executed"] is False
    assert result["groups"]["all"]["all"]["exact"] == 1
    assert result["groups"]["expected_family:utf-8"]["all"]["files"] == 1


def test_corpus_mutation_rejected(tmp_path):
    corpus, path, _ = fixture(tmp_path)
    (corpus / "fr/utf-8.txt").write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        analyze(path, corpus)


def test_nonleading_invalid_candidate_rejected(tmp_path):
    corpus, path, report = fixture(tmp_path)
    report["samples"][0]["candidates"].append(dict(encoding="ascii", confidence_bits="7fc00000"))
    path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="non-finite"):
        analyze(path, corpus)


def test_no_candidates_preserves_denominator(tmp_path):
    corpus, path, report = fixture(tmp_path)
    report["samples"][0]["candidates"] = []
    path.write_text(json.dumps(report))
    result = analyze(path, corpus)["groups"]["all"]
    assert result["all"]["files"] == result["unscored"] == 1
    assert result["scored"] == 0
