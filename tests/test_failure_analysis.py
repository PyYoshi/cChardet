# SPDX-License-Identifier: MIT
from benchmarks.failure_analysis import classify, size_bucket


def test_ranking_evidence():
    data = "日本語".encode("utf-8")
    result = classify(data, "utf-8", [{"encoding": "cp1251"}, {"encoding": "utf-8"}])
    assert result["category"] == "RANKING_FAILURE"
    assert result["exact_candidate_rank"] == 2
    assert result["top_k"] == {"1": False, "3": True, "5": True}


def test_absence_is_not_unsupported():
    result = classify("日本語".encode(), "utf-8", [{"encoding": "cp1251"}])
    assert result["category"] == "EXPECTED_CANDIDATE_ABSENT"


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
