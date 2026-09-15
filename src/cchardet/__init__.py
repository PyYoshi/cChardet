import math
from collections.abc import Mapping
from types import TracebackType
from typing import Literal, Self, TypeAlias, TypedDict

from . import _cchardet

BytesLike: TypeAlias = bytes | bytearray | memoryview
LanguageWeights: TypeAlias = Mapping[str, float]


class ResultDict(TypedDict):
    """Result returned by cChardet's detection APIs."""

    encoding: str | None
    confidence: float | None
    language: str | None


version: tuple[int, int, int] = (2, 2, 0)
__version__ = "2.2.0"


def _as_bytes(data: BytesLike) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, (bytearray, memoryview)):
        return bytes(data)
    raise TypeError("data must be bytes-like")


def _decode(value: bytes | None) -> str | None:
    return value.decode() if value is not None else None


def _normalize_encoding(value: bytes | None) -> str | None:
    encoding = _decode(value)
    return "maccentraleurope" if encoding == "MAC-CENTRALEUROPE" else encoding


def _validate_language_weights(weights: LanguageWeights | None) -> dict[str, float] | None:
    if weights is None:
        return None
    validated: dict[str, float] = {}
    for language, weight in weights.items():
        if not isinstance(language, str):
            raise TypeError("language weight keys must be ISO 639-1 strings")
        normalized = language.lower()
        if len(normalized) != 2 or not normalized.isascii() or not normalized.isalpha():
            raise ValueError("language weight keys must be two-letter ISO 639-1 codes")
        numeric_weight = float(weight)
        if not math.isfinite(numeric_weight) or not 0 <= numeric_weight <= 1:
            raise ValueError("language weights must be finite values between 0 and 1")
        validated[normalized] = numeric_weight
    return validated


def detect(
    msg: BytesLike,
    *,
    max_bytes: int | None = None,
    language_weights: LanguageWeights | None = None,
) -> ResultDict:
    """
    Args:
        msg: bytes-like object
        max_bytes: optional maximum number of bytes to examine
        language_weights: optional ISO 639-1 language downweights from 0 to 1
    Returns:
        {
            "encoding": str,
            "confidence": float,
            "language": str
        }
    """
    encoding, language, confidence = _cchardet.detect_with_details(
        _as_bytes(msg), max_bytes, _validate_language_weights(language_weights)
    )
    return {
        "encoding": _normalize_encoding(encoding),
        "confidence": confidence,
        "language": _decode(language),
    }


def detect_all(
    msg: BytesLike,
    *,
    max_bytes: int | None = None,
    language_weights: LanguageWeights | None = None,
) -> list[ResultDict]:
    """Return every uchardet candidate in descending confidence order."""
    results: list[ResultDict] = []
    for encoding, language, confidence in _cchardet.detect_all(
        _as_bytes(msg), max_bytes, _validate_language_weights(language_weights)
    ):
        results.append(
            {
                "encoding": _normalize_encoding(encoding),
                "confidence": confidence,
                "language": _decode(language),
            }
        )
    return results


class UniversalDetector:
    def __init__(self, *, language_weights: LanguageWeights | None = None) -> None:
        self._detector = _cchardet.UniversalDetector(_validate_language_weights(language_weights))

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        self.close()
        return False

    def reset(self) -> None:
        self._detector.reset()

    def feed(self, data: BytesLike) -> None:
        self._detector.feed(_as_bytes(data))

    def close(self) -> None:
        self._detector.close()

    @property
    def done(self) -> bool:
        return self._detector.done

    @property
    def result(self) -> ResultDict:
        encoding, language, confidence = self._detector.result
        return {
            "encoding": _normalize_encoding(encoding),
            "confidence": confidence,
            "language": _decode(language),
        }
