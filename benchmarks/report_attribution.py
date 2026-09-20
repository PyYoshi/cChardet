# SPDX-License-Identifier: MIT
"""Join saved raw Report events to final candidates, without replaying ranking."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from pathlib import Path
from typing import Any


def candidate_key(value: dict[str, Any]) -> tuple[str, str | None, str]:
    encoding, language, bits = (
        value.get("encoding"),
        value.get("language"),
        value.get("confidence_bits"),
    )
    if not isinstance(encoding, str) or not encoding:
        raise ValueError("candidate encoding must be nonempty")
    if language is not None and (not isinstance(language, str) or not language):
        raise ValueError("candidate language must be null or nonempty")
    if not isinstance(bits, str) or not re.fullmatch(r"[0-9a-fA-F]{8}", bits):
        raise ValueError("candidate confidence must be binary32 bits")
    if not math.isfinite(struct.unpack("!f", bytes.fromhex(bits))[0]):
        raise ValueError("candidate confidence must be finite")
    return encoding, language, bits.lower()


def analyze(trace: list[dict[str, Any]], final: dict[str, Any]) -> dict[str, Any]:
    """Exact observed-value attribution, not codec equivalence or a causal model."""
    if (
        not isinstance(trace, list)
        or not trace
        or any(
            not isinstance(row, dict)
            or type(row.get("schema_version")) is not int
            or row["schema_version"] != 1
            for row in trace
        )
    ):
        raise ValueError("requires nonempty schema 1 trace")
    if trace[0].get("event") != "initial" or trace[-1].get("event") != "after_end":
        raise ValueError("requires complete initial-to-after_end trace")
    if (
        not isinstance(final, dict)
        or type(final.get("schema_version")) is not int
        or final.get("schema_version") != 1
        or type(final.get("input_index")) is not int
        or final.get("input_index") != 0
    ):
        raise ValueError("requires one schema 1 final observation for input_index 0")
    snapshots, raw = [], []
    for name in ("byte_length", "feed_calls"):
        if type(final.get(name)) is not int or final[name] < (1 if name == "feed_calls" else 0):
            raise ValueError("final length/feed count must be nonnegative/positive integers")
    if any(type(final.get(name)) is not bool for name in ("initial_done", "final_done")):
        raise ValueError("final completion flags must be boolean")
    for index, row in enumerate(trace):
        if row.get("event") == "raw_report":
            raw.append((index, candidate_key(row)))
        elif row.get("event") in ("initial", "after_feed", "after_end"):
            snapshots.append(row)
        else:
            raise ValueError("unknown trace event")
    if [row["event"] for row in snapshots] != ["initial"] + ["after_feed"] * (
        len(snapshots) - 2
    ) + ["after_end"]:
        raise ValueError("unexpected snapshot order")
    offsets: list[int] = []
    for row in snapshots:
        offset = row.get("offset")
        if type(offset) is not int or offset < 0:
            raise ValueError("snapshot offsets must be nonnegative integers")
        offsets.append(offset)
    if len(snapshots) < 3 or offsets[-1] != offsets[-2]:
        raise ValueError("after_end must follow the last feed at the same offset")
    if offsets != sorted(offsets) or offsets[0] != 0 or offsets[-1] != final.get("byte_length"):
        raise ValueError("trace/final length mismatch")
    if len(snapshots) - 2 != final.get("feed_calls"):
        raise ValueError("trace/final feed count mismatch")
    if any(type(row.get("done")) is not bool for row in snapshots):
        raise ValueError("snapshot done must be boolean")
    if snapshots[0]["done"] != final.get("initial_done") or snapshots[-1]["done"] != final.get(
        "final_done"
    ):
        raise ValueError("trace/final completion mismatch")
    candidates = final.get("candidates")
    if (
        not isinstance(candidates, list)
        or type(final.get("candidate_count")) is not int
        or final["candidate_count"] != len(candidates)
    ):
        raise ValueError("final candidate count mismatch")
    matches = []
    matched_indices = set()
    for rank, candidate in enumerate(candidates, 1):
        if not isinstance(candidate, dict):
            raise ValueError("candidate must be an object")
        key = candidate_key(candidate)
        exact = [index for index, other in raw if other == key]
        same_label = [index for index, other in raw if other[:2] == key[:2]]
        matched_indices.update(exact)
        matches.append(
            dict(
                rank=rank,
                encoding=key[0],
                language=key[1],
                confidence_bits=key[2],
                exact_raw_event_indices=exact,
                same_label_raw_event_indices=same_label,
                status="EXACT_RAW_VALUE_OBSERVED" if exact else "NO_EXACT_RAW_VALUE",
            )
        )
    return dict(
        schema_version=1,
        raw_report_count=len(raw),
        final_candidate_count=len(candidates),
        final_candidates=matches,
        unmatched_raw_event_indices=[index for index, _ in raw if index not in matched_indices],
        ranking_reason="UNRESOLVED",
        limitations=[
            "Matching values do not authenticate that files came from the same input/build.",
            "Duplicate equal raw values cannot identify which event supplied a candidate.",
            "No deduplication, tie-breaking, weighting or ranking algorithm is replayed.",
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--final", type=Path, required=True)
    args = parser.parse_args()
    trace_bytes, final_bytes = args.trace.read_bytes(), args.final.read_bytes()
    trace = [json.loads(line) for line in trace_bytes.splitlines()]
    final = json.loads(final_bytes)
    report = analyze(trace, final)
    report["artifacts"] = dict(
        trace_sha256=hashlib.sha256(trace_bytes).hexdigest(),
        final_sha256=hashlib.sha256(final_bytes).hexdigest(),
        analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
