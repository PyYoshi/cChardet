# SPDX-License-Identifier: MIT
"""Native per-sample failure evidence, not automatic causal diagnosis."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import re
import struct
import subprocess
from collections import Counter
from pathlib import Path

from chardet.evaluation import is_correct, is_equivalent_detection, is_exact_match

if __package__ in (None, ""):
    from encoding_families import (
        FAMILY_MAPPING_VERSION,
        canonical_encoding,
        cause_status,
        encoding_family,
        family_observation,
    )
else:
    from benchmarks.encoding_families import (
        FAMILY_MAPPING_VERSION,
        canonical_encoding,
        cause_status,
        encoding_family,
        family_observation,
    )


def classify(data: bytes, expected: str, candidates: list[dict]) -> dict:
    predicted = candidates[0]["encoding"] if candidates else None
    codec_available = True
    structurally_valid = True
    try:
        data.decode(expected, errors="strict")
    except LookupError:
        codec_available = False
        structurally_valid = None
    except UnicodeError:
        structurally_valid = False
    exact = bool(is_exact_match(expected, predicted))
    compatible = bool(is_correct(expected, predicted))
    equivalent = (
        bool(is_equivalent_detection(data, expected, predicted)) if codec_available else None
    )
    ranks = [i + 1 for i, c in enumerate(candidates) if is_exact_match(expected, c["encoding"])]
    if exact:
        category = "EXACT_MATCH"
    elif not codec_available:
        category = "EVALUATOR_CODEC_UNAVAILABLE"
    elif not structurally_valid:
        category = "LABEL_OR_INPUT_REQUIRES_REVIEW"
    elif compatible or equivalent:
        category = "COMPATIBLE_OR_DECODE_EQUIVALENT"
    elif not candidates:
        category = "NO_CANDIDATE"
    elif ranks:
        category = "RANKING_FAILURE"
    else:
        category = "EXPECTED_CANDIDATE_ABSENT"
    return dict(
        exact=exact,
        compatible=compatible,
        decode_equivalent=equivalent,
        evaluator_codec_available=codec_available,
        expected_decodes=structurally_valid,
        exact_candidate_rank=ranks[0] if ranks else None,
        top_k={str(k): bool(ranks and ranks[0] <= k) for k in (1, 3, 5)},
        category=category,
        cause_status=cause_status(
            category, expected_decodes=structurally_valid, evaluator_codec_available=codec_available
        ),
        **family_observation(expected, predicted),
    )


def size_bucket(length: int) -> str:
    for size in (16, 32, 64, 128, 256, 512, 1024, 4096, 16384, 65536, 262144):
        if length <= size:
            return f"<={size}B"
    return ">262144B"


LEGACY_LABEL_SOURCE = "legacy fixture path; not independently verified"


def saved_observations(report_path: Path, root: Path, paths: list[Path]) -> tuple[list[dict], dict]:
    """Validate saved legacy observations against every byte of the specified corpus."""
    raw = report_path.read_bytes()
    report = json.loads(raw)
    if report.get("schema_version") != 1 or report.get("corpus") != "uchardet-legacy":
        raise ValueError("requires a schema 1 uchardet-legacy observation report")
    revision, tool_hash = report.get("native_revision"), report.get("tool_sha256")
    if not isinstance(revision, str) or not revision.strip():
        raise ValueError("saved report requires native_revision")
    if not isinstance(tool_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", tool_hash):
        raise ValueError("saved report requires tool_sha256")
    samples = report.get("samples")
    if not isinstance(samples, list) or len(samples) != len(paths):
        raise ValueError("saved observation count mismatch")
    records = []
    for index, (sample, path) in enumerate(zip(samples, paths, strict=True)):
        expected, language = path.name.split(".", 1)[0], path.parent.name
        if sample.get("path") != path.relative_to(root).as_posix():
            raise ValueError("saved observation path/order mismatch")
        if not path.resolve().is_relative_to(root):
            raise ValueError("corpus fixture escapes root")
        data = path.read_bytes()
        if (
            sample.get("byte_length") != len(data)
            or sample.get("sha256") != hashlib.sha256(data).hexdigest()
        ):
            raise ValueError("saved observation corpus byte length/hash mismatch")
        if (
            sample.get("expected_encoding") != expected
            or sample.get("expected_language") != language
            or sample.get("expected_label_source") != LEGACY_LABEL_SOURCE
            or sample.get("split") != "legacy-validation"
        ):
            raise ValueError("saved observation label/split mismatch")
        candidates = sample.get("candidates")
        if not isinstance(candidates, list):
            raise ValueError("saved candidates must be a list")
        records.append(
            dict(
                schema_version=1,
                input_index=index,
                candidate_count=len(candidates),
                candidates=candidates,
                byte_length=len(data),
                sha256=sample["sha256"],
            )
        )
    return records, dict(
        native_revision=revision,
        tool_sha256=tool_hash,
        observation_source=dict(
            mode="saved-legacy-report",
            report_sha256=hashlib.sha256(raw).hexdigest(),
            evaluator_version=report.get("evaluator_version"),
            evaluation=report.get("evaluation"),
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--native-tool", type=Path)
    mode.add_argument("--observations", type=Path)
    parser.add_argument("--native-revision")
    parser.add_argument("--uchardet-corpus", type=Path, required=True)
    args = parser.parse_args()
    if args.native_tool and not args.native_revision:
        parser.error("--native-tool requires --native-revision")
    if args.observations and args.native_revision:
        parser.error(
            "--observations preserves the saved revision; do not specify --native-revision"
        )
    root = args.uchardet_corpus.resolve()
    paths = sorted(p for p in root.glob("[a-z][a-z]/*") if p.is_file())
    if not paths:
        parser.error("corpus contains no fixtures")
    if args.observations:
        records, provenance = saved_observations(args.observations, root, paths)
    else:
        executable = args.native_tool.resolve()
        result = subprocess.run(
            [str(executable), "fresh", "0", *map(str, paths)],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        records = [json.loads(line) for line in result.stdout.splitlines()]
        provenance = dict(
            native_revision=args.native_revision,
            tool_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
            observation_source=dict(mode="native-execution"),
        )
    if len(records) != len(paths):
        raise ValueError("native observation count mismatch")
    samples = []
    grouped: dict[str, Counter] = {}
    for index, (path, observation) in enumerate(zip(paths, records, strict=True)):
        if observation["schema_version"] != 1 or observation["input_index"] != index:
            raise ValueError("native observation schema/order mismatch")
        candidates = observation["candidates"]
        if observation["candidate_count"] != len(candidates):
            raise ValueError("native candidate count mismatch")
        data = path.read_bytes()
        if args.observations and (
            observation["byte_length"] != len(data)
            or observation["sha256"] != hashlib.sha256(data).hexdigest()
        ):
            raise ValueError("corpus changed since observation validation")
        expected, language = path.name.split(".", 1)[0], path.parent.name
        canonical = canonical_encoding(expected)
        for candidate in candidates:
            if not isinstance(candidate.get("encoding"), str) or not candidate["encoding"]:
                raise ValueError("candidate encoding must be a nonempty string")
            bits = candidate.get("confidence_bits")
            if not isinstance(bits, str) or not re.fullmatch(r"[0-9a-fA-F]{8}", bits):
                raise ValueError("expected binary32 confidence bits")
            candidate["confidence"] = struct.unpack("!f", bytes.fromhex(bits))[0]
            if not math.isfinite(candidate["confidence"]):
                raise ValueError("non-finite candidate confidence")
        evidence = classify(data, expected, candidates)
        sample = dict(
            path=path.relative_to(root).as_posix(),
            sha256=hashlib.sha256(data).hexdigest(),
            byte_length=len(data),
            size_bucket=size_bucket(len(data)),
            expected_encoding=expected,
            canonical_encoding=canonical,
            encoding_family=encoding_family(expected),
            corpus="uchardet-legacy",
            source_kind="unknown",
            format="unknown",
            expected_language=language,
            expected_label_source=LEGACY_LABEL_SOURCE,
            split="legacy-validation",
            candidates=candidates,
            **evidence,
        )
        sample["language_correct"] = bool(candidates and candidates[0]["language"] == language)
        samples.append(sample)
        for key in (
            "all",
            f"encoding:{canonical}",
            f"family:{sample['encoding_family']}",
            "corpus:uchardet-legacy",
            "source_kind:unknown",
            "format:unknown",
            f"language:{language}",
            f"size:{sample['size_bucket']}",
        ):
            count = grouped.setdefault(key, Counter())
            count["files"] += 1
            count[sample["category"]] += 1
            count[f"cause_status:{sample['cause_status']}"] += 1
            count[f"family_relation:{sample['family_relation']}"] += 1
            for metric in ("exact", "compatible", "decode_equivalent", "language_correct"):
                count[metric] += bool(sample[metric])
            count["decode_equivalent_evaluable"] += sample["decode_equivalent"] is not None
    print(
        json.dumps(
            dict(
                schema_version=1,
                family_mapping_version=FAMILY_MAPPING_VERSION,
                corpus="uchardet-legacy",
                **provenance,
                sample_order="lexicographic relative fixture path; candidate order preserved",
                evaluator_version=importlib.metadata.version("chardet"),
                evaluation="chardet.evaluation: exact/compatible/decode-equivalent separately",
                limitations=[
                    "Candidate absence does not prove unsupported encoding or missing model.",
                    "Ranking failure identifies a lower exact candidate, not its root cause.",
                    "Legacy fixtures are not independent holdout or new-model training data.",
                    "Encoding family groups are reporting buckets, not compatibility or causality.",
                ],
                grouped=grouped,
                samples=samples,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
