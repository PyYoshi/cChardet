# SPDX-License-Identifier: MIT
"""Offline confidence evidence from byte-verified saved legacy observations."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import re
import struct
from pathlib import Path

from benchmarks.failure_analysis import (
    classify,
    fixture_sort_key,
    saved_observations,
    size_bucket,
)

THRESHOLDS = (0.0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0)


def confidence(candidate: dict) -> float:
    bits = candidate.get("confidence_bits")
    if not isinstance(bits, str) or not re.fullmatch(r"[0-9a-fA-F]{8}", bits):
        raise ValueError("expected binary32 confidence bits")
    value = struct.unpack("!f", bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise ValueError("non-finite confidence")
    return value


def counts(samples: list[dict]) -> dict:
    return {
        "files": len(samples),
        "exact": sum(s["exact"] for s in samples),
        "compatible": sum(s["compatible"] for s in samples),
        "decode_equivalent": sum(s["decode_equivalent"] is True for s in samples),
        "decode_equivalent_evaluable": sum(s["decode_equivalent"] is not None for s in samples),
    }


def summarize(samples: list[dict]) -> dict:
    scored = [s for s in samples if s["confidence"] is not None]
    bins = []
    edges = (-math.inf, *THRESHOLDS, math.inf)
    for lower, upper in zip(edges, edges[1:]):
        selected = [s for s in scored if lower <= s["confidence"] < upper]
        bins.append(
            {
                "lower_inclusive": lower if math.isfinite(lower) else None,
                "upper_exclusive": upper if math.isfinite(upper) else None,
                **counts(selected),
            }
        )
    selective = []
    for threshold in THRESHOLDS:
        selected = [s for s in scored if s["confidence"] >= threshold]
        selective.append(
            {
                "threshold": threshold,
                "selected": counts(selected),
                "rejected_or_unscored": len(samples) - len(selected),
                "coverage": {"numerator": len(selected), "denominator": len(samples)},
            }
        )
    return {
        "all": counts(samples),
        "scored": len(scored),
        "unscored": len(samples) - len(scored),
        "outside_unit_interval": sum(not 0 <= s["confidence"] <= 1 for s in scored),
        "bins": bins,
        "selective": selective,
    }


def analyze(observations: Path, corpus: Path) -> dict:
    root = corpus.resolve()
    paths = sorted(
        (p for p in root.glob("[a-z][a-z]/*") if p.is_file()),
        key=lambda path: fixture_sort_key(path, root),
    )
    if not paths:
        raise ValueError("corpus contains no fixtures")
    records, provenance = saved_observations(observations, root, paths)
    samples = []
    for path, record in zip(paths, records, strict=True):
        data = path.read_bytes()
        if (
            hashlib.sha256(data).hexdigest() != record["sha256"]
            or len(data) != record["byte_length"]
        ):
            raise ValueError("corpus changed after validation")
        candidates = record["candidates"]
        for candidate in candidates:
            if not isinstance(candidate.get("encoding"), str) or not candidate["encoding"]:
                raise ValueError("candidate encoding must be a nonempty string")
            confidence(candidate)
        evidence = classify(data, path.name.split(".", 1)[0], candidates)
        samples.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": record["sha256"],
                "size_bucket": size_bucket(len(data)),
                "language": path.parent.name,
                "confidence": confidence(candidates[0]) if candidates else None,
                "confidence_bits": candidates[0]["confidence_bits"] if candidates else None,
                **evidence,
            }
        )
    groups = {"all": summarize(samples)}
    for field in ("expected_family", "size_bucket", "language"):
        # Family evidence is produced by the existing versioned mapping.
        for value in sorted({s[field] for s in samples}):
            groups[f"{field}:{value}"] = summarize([s for s in samples if s[field] == value])
    dependencies = {}
    for name in ("confidence_analysis.py", "failure_analysis.py", "encoding_families.py"):
        dependencies[name] = hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
    result = {
        "schema_version": 1,
        "profile": "saved-legacy-confidence-v1",
        "corpus": "uchardet-legacy",
        **provenance,
        "evaluator_version": importlib.metadata.version("chardet"),
        "dependencies": dependencies,
        "native_executed": False,
        "threshold_policy": "fixed diagnostic thresholds; not optimized",
        "limitations": [
            "Confidence is a score, not an assumed probability.",
            "Legacy labels are not independently verified.",
            "No new detector run, independent holdout, or threshold tuning.",
            "Small per-group denominators do not establish calibration.",
        ],
        "groups": groups,
        "samples": samples,
    }
    result["content_hash"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--uchardet-corpus", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = (
        json.dumps(
            analyze(args.observations, args.uchardet_corpus),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    if args.output:
        if args.output.exists():
            if args.output.read_text(encoding="utf-8") != text:
                raise ValueError("refusing to overwrite different report")
        else:
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
