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
Sample = tuple[str | None, str | None, Path]

LANGUAGE_CODES = {
    "arabic": "ar",
    "belarusian": "be",
    "breton": "br",
    "bulgarian": "bg",
    "catalan": "ca",
    "chinese": "zh",
    "croatian": "hr",
    "czech": "cs",
    "danish": "da",
    "dutch": "nl",
    "english": "en",
    "esperanto": "eo",
    "estonian": "et",
    "finnish": "fi",
    "farsi": "fa",
    "french": "fr",
    "georgian": "ka",
    "gaelic": "gd",
    "german": "de",
    "greek": "el",
    "hebrew": "he",
    "hindi": "hi",
    "hungarian": "hu",
    "icelandic": "is",
    "indonesian": "id",
    "irish": "ga",
    "italian": "it",
    "japanese": "ja",
    "kazakh": "kk",
    "korean": "ko",
    "latvian": "lv",
    "lithuanian": "lt",
    "macedonian": "mk",
    "maltese": "mt",
    "malay": "ms",
    "norwegian": "no",
    "polish": "pl",
    "portuguese": "pt",
    "romanian": "ro",
    "russian": "ru",
    "serbian": "sr",
    "slovak": "sk",
    "slovene": "sl",
    "slovenian": "sl",
    "spanish": "es",
    "swedish": "sv",
    "tajik": "tg",
    "thai": "th",
    "turkish": "tr",
    "ukrainian": "uk",
    "urdu": "ur",
    "vietnamese": "vi",
    "welsh": "cy",
}


def _normalize_language(language: object) -> str | None:
    if not isinstance(language, str) or not language.strip():
        return None
    normalized = language.strip().lower().replace("_", "-")
    if len(normalized) == 2:
        return normalized
    return LANGUAGE_CODES.get(normalized)


def _uchardet_samples(root: Path) -> list[Sample]:
    return [
        (path.name.split(".", 1)[0], path.parent.name, path)
        for path in sorted(root.glob("[a-z][a-z]/*"))
        if path.is_file()
    ]


def _chardet_samples(root: Path) -> list[Sample]:
    samples: list[Sample] = []
    for encoding_dir in sorted(root.iterdir()):
        if not encoding_dir.is_dir() or encoding_dir.name.startswith("."):
            continue
        encoding, separator, language = encoding_dir.name.rpartition("-")
        if not separator:
            continue
        expected = None if encoding == "None" else encoding
        samples.extend(
            (expected, _normalize_language(language), path)
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
            (expected, None, path)
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
    language_files = language_correct = language_no_result = joint_correct = 0
    for expected, expected_language, path in samples:
        data = path.read_bytes()
        result = detector(data)
        detected_encoding = result.get("encoding")
        encoding_correct = is_correct(expected, detected_encoding)
        no_result += detected_encoding is None
        exact += is_exact_match(expected, detected_encoding)
        compatible += encoding_correct
        equivalent += is_equivalent_detection(data, expected, detected_encoding)
        if expected_language is not None:
            detected_language = _normalize_language(result.get("language"))
            language_files += 1
            language_no_result += detected_language is None
            language_match = detected_language == expected_language
            language_correct += language_match
            joint_correct += encoding_correct and language_match
    total = len(samples)
    metrics: dict[str, int | float] = {
        "files": total,
        "exact": exact,
        "exact_percent": round(100 * exact / total, 2),
        "compatible": compatible,
        "compatible_percent": round(100 * compatible / total, 2),
        "decode_equivalent": equivalent,
        "decode_equivalent_percent": round(100 * equivalent / total, 2),
        "no_result": no_result,
    }
    if language_files:
        metrics.update(
            {
                "language_files": language_files,
                "language_correct": language_correct,
                "language_correct_percent": round(100 * language_correct / language_files, 2),
                "language_no_result": language_no_result,
                "joint_correct": joint_correct,
                "joint_correct_percent": round(100 * joint_correct / language_files, 2),
            }
        )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uchardet-corpus", type=Path)
    parser.add_argument("--chardet-corpus", type=Path)
    parser.add_argument("--charset-normalizer-corpus", type=Path)
    args = parser.parse_args()
    if not args.uchardet_corpus and not args.chardet_corpus and not args.charset_normalizer_corpus:
        parser.error("at least one corpus must be supplied")

    corpora: dict[str, list[Sample]] = {}
    if args.uchardet_corpus:
        corpora["uchardet-test-data"] = _uchardet_samples(args.uchardet_corpus)
    if args.chardet_corpus:
        corpora["chardet-test-data"] = _chardet_samples(args.chardet_corpus)
    if args.charset_normalizer_corpus:
        corpora["charset-normalizer-char-dataset"] = _charset_normalizer_samples(
            args.charset_normalizer_corpus
        )
    if any(not samples for samples in corpora.values()):
        parser.error("a supplied corpus contained no samples")

    detectors, metadata = _detectors()
    metadata["uchardet_corpus"] = (
        str(args.uchardet_corpus.resolve()) if args.uchardet_corpus else "not supplied"
    )
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
