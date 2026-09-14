"""Compare detector accuracy on independently maintained public corpora.

This reports several definitions of correctness instead of choosing the one
that makes a particular detector look best.  The comparison predicates come
from chardet's public ``chardet.evaluation`` module and are applied identically
to every detector.
"""

from __future__ import annotations

import argparse
import importlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from chardet.evaluation import (
    is_correct,
    is_equivalent_detection,
    is_exact_match,
)

Detector = Callable[[bytes], dict[str, Any]]
Sample = tuple[str | None, Path]


def _chardet_samples(root: Path) -> list[Sample]:
    samples: list[Sample] = []
    for encoding_dir in sorted(root.iterdir()):
        if not encoding_dir.is_dir() or encoding_dir.name.startswith("."):
            continue
        encoding, separator, _language = encoding_dir.name.rpartition("-")
        if not separator:
            continue
        expected = None if encoding == "None" else encoding
        samples.extend(
            (expected, path)
            for path in sorted(encoding_dir.iterdir())
            if path.is_file() and not path.name.startswith(".")
        )
    return samples


def _charset_normalizer_samples(root: Path) -> list[Sample]:
    samples: list[Sample] = []
    for encoding_dir in sorted(root.iterdir()):
        if not encoding_dir.is_dir() or encoding_dir.name.startswith("."):
            continue
        expected = None if encoding_dir.name.lower() == "none" else encoding_dir.name
        samples.extend(
            (expected, path)
            for path in sorted(encoding_dir.iterdir())
            if path.is_file() and not path.name.startswith(".")
        )
    return samples


def _module_path(module_name: str) -> str:
    module = importlib.import_module(module_name)
    return str(Path(module.__file__).resolve())


def _detectors() -> tuple[dict[str, Detector], dict[str, str]]:
    cchardet = importlib.import_module("cchardet")
    chardet = importlib.import_module("chardet")
    charset_normalizer = importlib.import_module("charset_normalizer")
    detectors = {
        "cchardet": cchardet.detect,
        "chardet": chardet.detect,
        "charset_normalizer": charset_normalizer.detect,
    }
    metadata = {
        "cchardet_version": cchardet.__version__,
        "cchardet_module": _module_path("cchardet._cchardet"),
        "chardet_version": chardet.__version__,
        "chardet_module": _module_path("chardet._kernel"),
        "charset_normalizer_version": charset_normalizer.__version__,
        "charset_normalizer_mess": _module_path("charset_normalizer.md"),
        "charset_normalizer_coherence": _module_path("charset_normalizer.cd"),
    }
    return detectors, metadata


def _evaluate(detector: Detector, samples: list[Sample]) -> dict[str, int | float]:
    exact = compatible = equivalent = no_result = 0
    for expected, path in samples:
        data = path.read_bytes()
        detected = detector(data).get("encoding")
        no_result += detected is None
        exact += is_exact_match(expected, detected)
        compatible += is_correct(expected, detected)
        equivalent += is_equivalent_detection(data, expected, detected)
    total = len(samples)
    return {
        "files": total,
        "exact": exact,
        "exact_percent": round(100 * exact / total, 2),
        "compatible": compatible,
        "compatible_percent": round(100 * compatible / total, 2),
        "decode_equivalent": equivalent,
        "decode_equivalent_percent": round(100 * equivalent / total, 2),
        "no_result": no_result,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chardet-corpus", type=Path)
    parser.add_argument("--charset-normalizer-corpus", type=Path)
    args = parser.parse_args()
    if not args.chardet_corpus and not args.charset_normalizer_corpus:
        parser.error("at least one corpus must be supplied")

    corpora: dict[str, list[Sample]] = {}
    if args.chardet_corpus:
        corpora["chardet-test-data"] = _chardet_samples(args.chardet_corpus)
    if args.charset_normalizer_corpus:
        corpora["charset-normalizer-char-dataset"] = _charset_normalizer_samples(
            args.charset_normalizer_corpus
        )
    if any(not samples for samples in corpora.values()):
        parser.error("a supplied corpus contained no samples")

    detectors, metadata = _detectors()
    metadata["chardet_corpus"] = (
        str(args.chardet_corpus.resolve()) if args.chardet_corpus else "not supplied"
    )
    metadata["charset_normalizer_corpus"] = (
        str(args.charset_normalizer_corpus.resolve())
        if args.charset_normalizer_corpus
        else "not supplied"
    )
    results = {
        corpus_name: {
            detector_name: _evaluate(detector, samples)
            for detector_name, detector in detectors.items()
        }
        for corpus_name, samples in corpora.items()
    }
    print(json.dumps({"metadata": metadata, "results": results}, indent=2))


if __name__ == "__main__":
    main()
