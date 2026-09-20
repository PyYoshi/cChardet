# SPDX-License-Identifier: MIT
import copy
import hashlib
import json
import os
import subprocess
import sys

import pytest

from benchmarks.report_attribution import analyze


def candidate(language="fr", bits="3f400000"):
    return dict(encoding="UTF-8", language=language, confidence_bits=bits)


def observation(raw, final=None):
    trace = [
        dict(schema_version=1, event="initial", offset=0, done=False),
        dict(schema_version=1, event="after_feed", offset=3, done=False),
        *[dict(schema_version=1, event="raw_report", offset=3, **row) for row in raw],
        dict(schema_version=1, event="after_end", offset=3, done=False),
    ]
    candidates = raw if final is None else final
    final_row = dict(
        schema_version=1,
        input_index=0,
        byte_length=3,
        feed_calls=1,
        initial_done=False,
        final_done=False,
        candidate_count=len(candidates),
        candidates=candidates,
    )
    return trace, final_row


def test_duplicate_values_are_ambiguous_not_deduplicated_by_analyzer():
    trace, final = observation([candidate(), candidate()], [candidate()])
    before = copy.deepcopy((trace, final))
    report = analyze(trace, final)
    assert report["final_candidates"][0]["exact_raw_event_indices"] == [2, 3]
    assert report["ranking_reason"] == "UNRESOLVED"
    assert report["unmatched_raw_event_indices"] == []
    assert (trace, final) == before


def test_changed_score_is_not_automatically_attributed_to_weights():
    report = analyze(*observation([candidate()], [candidate(bits="3f000000")]))
    row = report["final_candidates"][0]
    assert row["status"] == "NO_EXACT_RAW_VALUE"
    assert row["same_label_raw_event_indices"] == [2]
    assert row["exact_raw_event_indices"] == []
    assert report["unmatched_raw_event_indices"] == [2]


def test_null_language_and_binary32_spelling_preserve_exact_observation():
    report = analyze(*observation([candidate(None, "3F400000")]))
    row = report["final_candidates"][0]
    assert row["language"] is None
    assert row["confidence_bits"] == "3f400000"
    assert row["status"] == "EXACT_RAW_VALUE_OBSERVED"


def test_rank_is_final_order_not_raw_order_or_score_sort():
    low, high = candidate(bits="3f000000"), candidate(bits="3f400000")
    report = analyze(*observation([low, high], [high, low]))
    assert [c["exact_raw_event_indices"] for c in report["final_candidates"]] == [[3], [2]]
    assert [c["rank"] for c in report["final_candidates"]] == [1, 2]


@pytest.mark.parametrize("bits", ["bad", "7fc00000", "7f800000", "ff800000", None])
def test_invalid_confidence_rejected(bits):
    with pytest.raises(ValueError, match="confidence"):
        analyze(*observation([candidate(bits=bits)]))


@pytest.mark.parametrize(
    "field,value",
    [
        ("byte_length", 4),
        ("feed_calls", 2),
        ("feed_calls", True),
        ("candidate_count", 2),
        ("initial_done", True),
        ("final_done", 0),
        ("input_index", 1),
    ],
)
def test_mismatched_metadata_rejected(field, value):
    trace, final = observation([candidate()])
    final[field] = value
    with pytest.raises(ValueError):
        analyze(trace, final)


def test_incomplete_and_unknown_events_rejected():
    trace, final = observation([candidate()])
    with pytest.raises(ValueError):
        analyze(trace[:-1], final)
    trace[1]["event"] = "invented"
    with pytest.raises(ValueError):
        analyze(trace, final)


def test_empty_candidate_sets_are_valid():
    report = analyze(*observation([]))
    assert report["final_candidates"] == []
    assert report["raw_report_count"] == 0


def test_cli_records_artifact_hashes(tmp_path):
    trace, final = observation([candidate()])
    trace_path, final_path = tmp_path / "trace.jsonl", tmp_path / "final.json"
    trace_path.write_text("\n".join(json.dumps(row) for row in trace), encoding="utf-8")
    final_path.write_text(json.dumps(final), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "benchmarks.report_attribution",
            "--trace",
            str(trace_path),
            "--final",
            str(final_path),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    report = json.loads(result.stdout)
    assert (
        report["artifacts"]["trace_sha256"] == hashlib.sha256(trace_path.read_bytes()).hexdigest()
    )
    assert (
        report["artifacts"]["final_sha256"] == hashlib.sha256(final_path.read_bytes()).hexdigest()
    )


@pytest.mark.skipif(
    not (os.environ.get("UCHARDET_TRACE") and os.environ.get("UCHARDET_CONFORMANCE")),
    reason="set trace and conformance tools for existing tiny fixtures",
)
@pytest.mark.parametrize("data", [b"", b"plain text\n", "日本語の文章です。".encode() * 5])
@pytest.mark.parametrize("chunk", ["0", "1", "7"])
def test_existing_native_fixtures(tmp_path, data, chunk):
    path = tmp_path / "input"
    path.write_bytes(data)
    trace_output = subprocess.run(
        [os.environ["UCHARDET_TRACE"], chunk, str(path)],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout
    final_output = subprocess.run(
        [os.environ["UCHARDET_CONFORMANCE"], "fresh", chunk, str(path)],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout
    report = analyze(
        [json.loads(line) for line in trace_output.splitlines()], json.loads(final_output)
    )
    assert all(row["status"] == "EXACT_RAW_VALUE_OBSERVED" for row in report["final_candidates"])
    assert report["ranking_reason"] == "UNRESOLVED"
