# SPDX-License-Identifier: MIT
"""Inventory generated corpora; explicitly opt into bounded validation detection."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import struct
import subprocess
from collections import Counter
from pathlib import Path

from benchmarks.encoding_families import (
    FAMILY_MAPPING_VERSION,
    canonical_encoding,
    cause_status,
    encoding_family,
    family_observation,
)
from benchmarks.failure_analysis import classify, size_bucket


def framework_module():
    path = Path(__file__).resolve().parents[1] / "src/ext/uchardet/corpus/framework.py"
    if not path.is_file():
        raise ValueError("requires a repository checkout with the native corpus framework")
    spec = importlib.util.spec_from_file_location("cchardet_corpus_framework", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_manifests(paths: list[Path]) -> list[dict]:
    framework = framework_module()
    manifests, origins, hashes, identities = [], {}, {}, set()
    for path in paths:
        path = path.resolve()
        manifest = json.loads(path.read_text(encoding="utf-8"))
        framework.validate(manifest, path.parent)
        identity = manifest["content_hash"]
        if identity in identities:
            raise ValueError("duplicate corpus manifest")
        identities.add(identity)
        sources = {source["id"]: source for source in manifest["sources"]}
        for source in sources.values():
            # An origin must be stable across translation, normalization and encoding.
            for groups, key in ((origins, source["origin"]), (hashes, source["sha256"])):
                if key in groups and groups[key] != source["split"]:
                    raise ValueError("cross-manifest source split leakage")
                groups[key] = source["split"]
        manifests.append(dict(path=path, manifest=manifest, sources=sources))
    return manifests


def select_samples(manifests: list[dict], splits: set[str], max_bytes: int | None) -> list[dict]:
    if not splits or not splits <= {"training", "tuning", "validation", "independent"}:
        raise ValueError("invalid or empty split selection")
    if max_bytes is not None and (type(max_bytes) is not int or max_bytes <= 0):
        raise ValueError("maximum input bytes must be positive")
    samples = []
    for corpus in manifests:
        identity = corpus["manifest"]["content_hash"]
        for record in corpus["manifest"]["samples"]:
            source = corpus["sources"][record["source_id"]]
            reason = None
            if record["split"] not in splits:
                reason = "SPLIT_NOT_SELECTED"
            elif record["boundary"] != "complete":
                reason = "TRUNCATED_VARIANT_NOT_SELECTED"
            elif max_bytes is not None and record["byte_length"] > max_bytes:
                reason = "INPUT_SIZE_LIMIT"
            sample = dict(
                corpus_hash=identity,
                id=record["id"],
                path=record["path"],
                source_id=record["source_id"],
                source_origin=source["origin"],
                source_sha256=source["sha256"],
                source_kind=source["kind"],
                language=source["language"],
                encoding=record["encoding"],
                canonical_encoding=canonical_encoding(record["encoding"]),
                encoding_family=encoding_family(record["encoding"]),
                split=record["split"],
                format=record["format"],
                declared_encoding=record.get("declared_encoding"),
                boundary=record["boundary"],
                byte_length=record["byte_length"],
                size_bucket=size_bucket(record["byte_length"]),
                sha256=record["sha256"],
                ground_truth=record.get("ground_truth", {"provenance": "legacy-schema1"}),
                selected=reason is None,
                exclusion_reason=reason,
                _absolute_path=corpus["path"].parent / record["path"],
            )
            samples.append(sample)
    return samples


def observe(executable: Path, sample: dict) -> dict:
    path = sample["_absolute_path"]
    data = path.read_bytes()
    if len(data) != sample["byte_length"] or hashlib.sha256(data).hexdigest() != sample["sha256"]:
        raise ValueError("sample changed since manifest validation")
    result = subprocess.run(
        [str(executable), "fresh", "0", str(path)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    lines = result.stdout.splitlines()
    if len(lines) != 1:
        raise ValueError("expected one native observation")
    record = json.loads(lines[0])
    if record["schema_version"] != 1 or record["input_index"] != 0:
        raise ValueError("unexpected native schema or input index")
    if record["byte_length"] != len(data) or record["candidate_count"] != len(record["candidates"]):
        raise ValueError("native input length or candidate count mismatch")
    candidates = record["candidates"]
    for candidate in candidates:
        bits = candidate["confidence_bits"]
        if not isinstance(bits, str) or len(bits) != 8:
            raise ValueError("expected binary32 confidence bits")
        confidence = struct.unpack("!f", bytes.fromhex(bits))[0]
        if not math.isfinite(confidence):
            raise ValueError("non-finite native confidence")
        candidate["confidence"] = confidence
    metrics = classify(data, sample["encoding"], candidates)
    language_correct = bool(candidates and candidates[0]["language"] == sample["language"])
    return dict(
        candidates=candidates,
        **metrics,
        language_correct=language_correct,
        encoding_and_language_correct=metrics["exact"] and language_correct,
    )


def make_report(manifests: list[dict], samples: list[dict], observer=None) -> dict:
    # Reports must not retain predictions from a previous evaluation invocation.
    samples = [{k: v for k, v in sample.items() if k != "prediction"} for sample in samples]
    groups = {}
    for sample in samples:
        sample["canonical_encoding"] = canonical_encoding(sample["encoding"])
        sample["encoding_family"] = encoding_family(sample["encoding"])
        if sample["selected"] and observer is not None:
            # Abort on execution errors. Never turn them into skipped or wrong predictions.
            prediction = dict(observer(sample))
            candidates = prediction.get("candidates", [])
            prediction.update(
                cause_status=cause_status(
                    prediction["category"],
                    expected_decodes=prediction.get("expected_decodes"),
                    evaluator_codec_available=prediction.get("evaluator_codec_available"),
                ),
                **family_observation(
                    sample["encoding"], candidates[0]["encoding"] if candidates else None
                ),
            )
            sample["prediction"] = prediction
        keys = [
            "all",
            f"corpus:{sample['corpus_hash']}",
            f"split:{sample['split']}",
            f"language:{sample['language']}",
            f"encoding:{sample['canonical_encoding']}",
            f"family:{sample['encoding_family']}",
            f"source_kind:{sample['source_kind']}",
            f"workload:{sample['corpus_hash']}:{sample['source_kind']}:{sample['format']}",
            f"size:{sample['size_bucket']}",
            f"format:{sample['format']}",
        ]
        for key in keys:
            count = groups.setdefault(key, Counter())
            count["available"] += 1
            count["selected"] += sample["selected"]
            if sample["exclusion_reason"]:
                count[sample["exclusion_reason"]] += 1
            if "prediction" in sample:
                prediction = sample["prediction"]
                count["evaluated"] += 1
                count[prediction["category"]] += 1
                count[f"cause_status:{prediction['cause_status']}"] += 1
                count[f"family_relation:{prediction['family_relation']}"] += 1
                for metric in (
                    "exact",
                    "compatible",
                    "decode_equivalent",
                    "language_correct",
                    "encoding_and_language_correct",
                ):
                    count[metric] += bool(prediction[metric])
                count["decode_equivalent_evaluable"] += prediction["decode_equivalent"] is not None
                for k, correct in prediction["top_k"].items():
                    count[f"top_{k}"] += correct
    return dict(
        report_schema_version=1,
        family_mapping_version=FAMILY_MAPPING_VERSION,
        mode="evaluation" if observer is not None else "inventory-only",
        evaluator_version=importlib.metadata.version("chardet"),
        corpora=[
            dict(
                content_hash=c["manifest"]["content_hash"],
                source_count=len(c["sources"]),
                generated_count=len(c["manifest"]["samples"]),
                generation_counts=c["manifest"].get("generation_report", {}).get("counts"),
            )
            for c in manifests
        ],
        groups=groups,
        samples=[{k: v for k, v in sample.items() if not k.startswith("_")} for sample in samples],
        limitations=[
            "Selected subset metrics do not describe excluded sizes or splits.",
            "Translated chapters from one book are not independent-author evaluation.",
            "Candidate absence is not a diagnosis of missing model coverage.",
            "Encoding family groups are reporting buckets, not compatibility or causality.",
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, action="append", required=True)
    parser.add_argument(
        "--split", choices=["training", "tuning", "validation", "independent"], action="append"
    )
    parser.add_argument("--max-input-bytes", type=int)
    parser.add_argument("--native-tool", type=Path)
    parser.add_argument("--native-revision")
    parser.add_argument("--allow-independent-evaluation", action="store_true")
    args = parser.parse_args()
    splits = set(args.split or ["validation"])
    if args.native_tool and (args.max_input_bytes is None or not args.native_revision):
        parser.error("native evaluation requires explicit --max-input-bytes and --native-revision")
    if args.native_tool and "independent" in splits and not args.allow_independent_evaluation:
        parser.error("independent evaluation requires explicit --allow-independent-evaluation")
    manifests = load_manifests(args.manifest)
    samples = select_samples(manifests, splits, args.max_input_bytes)
    executable = args.native_tool.resolve() if args.native_tool else None
    report = make_report(
        manifests, samples, (lambda sample: observe(executable, sample)) if executable else None
    )
    report["selection"] = dict(
        splits=sorted(splits), max_input_bytes=args.max_input_bytes, boundaries=["complete"]
    )
    if executable:
        report["native"] = dict(
            revision=args.native_revision,
            tool_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
        )
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
